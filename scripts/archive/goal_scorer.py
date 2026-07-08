"""
goal_scorer.py — 鋮馨租賃 /goal 規格 §4 評審模組 (v1.0)
================================================================

把這支當成迴圈的「評審腦」。它本身不跑 Playwright、不跑 git——你的 harness
負責「渲染 + commit/revert」，這支只負責「打分 + 判 COMMIT/REVERT」。

最小接法（你的 harness 是大寫的部分）：

    from goal_scorer import score_page, append_score

    html = PLAYWRIGHT_RENDER(url)              # 你的
    lh   = RUN_LIGHTHOUSE(url)                 # 你的（可選，餵了才解鎖技術分滿分）
    res  = score_page(html, url,
                      target_queries=["中和 二胎房貸 條件", "中和 二胎房貸 是什麼"],
                      lighthouse=lh,
                      prev_score=PREV_TOTAL)    # 上一版總分，None=建立基線
    append_score("goal-scores.jsonl", res.to_jsonl_row(commit_hash=CURRENT_HASH))

    if res.verdict == "COMMIT":
        GIT_COMMIT(); PREV_TOTAL = res.total
    else:
        GIT_REVERT()                           # git checkout -- .

兩個必填：
  1. CANONICAL["phone"]  ← 填正式電話，NAP gate 才會檢查電話漂移
  2. 環境變數 ANTHROPIC_API_KEY  ← judge 用

成本設計（CP 值）：
  - Hard Gate 純 deterministic，先判；任一掛 → 直接 REVERT，**不呼叫 LLM**（省錢）。
  - judge=False 進「triage 模式」：只跑 gate，不評分——就是你掃 99 頁合規那種快篩。

依賴： pip install beautifulsoup4 anthropic

★ 鋮馨在地化修正（2026-06-25 by Hao）：
  - CANONICAL["phone"] 已填 02-2249-0517（NAP 標準值，CLAUDE.md / 公司資料）。
  - schema gate 的 entity 集合改為 RealEstateAgent/LocalBusiness/ProfessionalService/Organization，
    **移除 FinancialService**——鋮馨非金融機構，紅線不可自稱金融機構（CLAUDE.md §7、
    memory feedback_no_financialservice_schema）。官網實際用 RealEstateAgent/LocalBusiness。
"""

from __future__ import annotations

import json
import os
import re
import datetime
from dataclasses import dataclass, field
from typing import Optional

try:
    from bs4 import BeautifulSoup
except ImportError as e:  # pragma: no cover
    raise SystemExit("需要 beautifulsoup4：pip install beautifulsoup4") from e

try:
    import anthropic
except ImportError:
    anthropic = None  # 允許 deterministic-only / triage 模式


# ───────────────────────── 常數（單一真相） ─────────────────────────

SCORER_VERSION = "1.0"
JUDGE_MODEL = "claude-sonnet-4-6"   # 評審用 sonnet（CP 值）；要做抽查稽核可臨時換 opus
COMMIT_MARGIN = 0.5                 # 總分要贏過上一版至少這麼多才 commit，避免雜訊亂提交

# 對應 goal.md §6.2 的 NAP 標準值
CANONICAL = {
    "name": "鋮馨租賃有限公司",
    "address": "新北市中和區中正路468號",
    "phones": ["02-2249-0517", "0931-087-996"],   # 公司合法兩支（CLAUDE.md）；空 list=略過電話檢查
    "site": "cx468.com.tw",
}

# 同心圓行政區（goal.md §3）；用來量在地脈絡密度
CONCENTRIC_DISTRICTS = ["中和", "永和", "板橋", "新店", "三重", "土城", "新莊", "泰山", "蘆洲"]
AUTHORITY_TERMS = ["中央銀行", "央行", "聯徵", "聯合徵信", "金管會", "地政", "內政部", "財政部"]

# rubric 權重 = goal.md §4
WEIGHTS = {"aeo": 30, "local_eeat": 25, "topic_cluster": 20, "technical": 15, "conversion": 10}
LLM_DIMS = ["aeo", "local_eeat", "topic_cluster", "conversion"]  # technical 用量測，不交給 LLM

# 實體 schema 型別（鋮馨：非金融機構，用 RealEstateAgent/LocalBusiness，不用 FinancialService）
ENTITY_TYPES = {"RealEstateAgent", "LocalBusiness", "ProfessionalService", "Organization"}

# 反詐／否定線索：命中詞的「上下文窗口」內有這些 → 屬好用法（反詐警語/法務免責），不判違規（媽祖的誤殺防線）
NEG_CUES = ["不要", "別", "勿", "切勿", "非", "無法", "不能", "不會", "沒有", "並非", "不是",
            "避免", "謹防", "提防", "小心", "詐騙", "詐欺", "假的", "陷阱", "話術", "謊言",
            "高風險", "失敗", "收高額", "騙", "當心", "不得", "禁止"]
NEG_WINDOW = 80   # 命中詞前後各 80 字內找否定線索（跨句，貼近人的判讀）

# 高精度違規樣式（低誤殺）。模糊的留給 LLM compliance flag。
INDUCEMENT_PATTERNS = [
    re.compile(r"核貸(成功率|機率|通過率)[^。！？\n]{0,8}\d{1,3}\s*[%％]"),  # 「核貸成功率提升40%」
    re.compile(r"\d{1,3}\s*[%％][^。！？\n]{0,6}(過件|核准|核貸|放款|成功)"),     # 「95%過件」
    re.compile(r"(保證|絕對|100\s*[%％]|百分百)[^。！？\n]{0,6}(過件|核准|核貸|放款|成功|下款)"),
    re.compile(r"(成功|核貸成功|過件)[^。！？\n]{0,4}才收費"),                     # 「成功核貸才收費」
    re.compile(r"(包|一定能|必能)[^。！？\n]{0,4}(過件|下款|核貸)"),
]

# 嚴格台灣電話格式：須含分隔符（避免誤抓 FB ID 61590175174751、日期 2026-06-22 等數字串）
PHONE_RE = re.compile(r"0\d{1,3}[-\s]\d{3,4}[-\s]\d{3,4}")
ZHONGZHENG_NUM_RE = re.compile(r"中正路\s*(\d+)\s*號")

# triage / 流程用語
VERDICT_COMMIT = "COMMIT"
VERDICT_REVERT = "REVERT"
VERDICT_PASS_GATES = "PASS_GATES"   # triage 模式：過 gate 但沒評分（不可用於 commit 決策）
VERDICT_ERROR = "ERROR"             # judge 失敗等異常 → 當作不提交


# ───────────────────────── 資料結構 ─────────────────────────

@dataclass
class GateResult:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class DimResult:
    score: Optional[float]      # 0–100；triage 模式下為 None
    weight: int
    rationale: str = ""
    evidence: dict = field(default_factory=dict)


@dataclass
class ScoreResult:
    url: str
    target_queries: list
    gates: list                 # list[GateResult]
    gates_passed: bool
    dimensions: dict            # dim_id -> DimResult
    total: Optional[float]      # 加權 0–100；缺維度則 None
    prev_total: Optional[float]
    verdict: str
    reasons: list
    judge_model: Optional[str]
    round: Optional[int] = None

    @property
    def gate_failures(self) -> list:
        return [g.name for g in self.gates if not g.passed]

    @property
    def delta(self) -> Optional[float]:
        if self.total is None or self.prev_total is None:
            return None
        return round(self.total - self.prev_total, 2)

    def to_jsonl_row(self, commit_hash: Optional[str] = None) -> dict:
        return {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "round": self.round,
            "commit_hash": commit_hash,
            "url": self.url,
            "target_queries": self.target_queries,
            "gates_passed": self.gates_passed,
            "gate_failures": self.gate_failures,
            "dimensions": {
                k: {"score": v.score, "weight": v.weight} for k, v in self.dimensions.items()
            },
            "total": self.total,
            "prev_total": self.prev_total,
            "delta": self.delta,
            "verdict": self.verdict,
            "reasons": self.reasons,
            "scorer_version": SCORER_VERSION,
            "judge_model": self.judge_model,
        }


# ───────────────────────── 抽取（只看可見文字 + 結構訊號） ─────────────────────────

def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def extract_visible_text(soup: BeautifulSoup) -> str:
    """去 CSS/JS/標籤，留可見文字。不破壞 soup（否則後續 parse_jsonld 會抓不到 schema）。"""
    bad = {"script", "style", "noscript", "template"}
    parts = []
    for s in soup.find_all(string=True):
        if s.parent is not None and s.parent.name in bad:
            continue
        t = s.strip()
        if t:
            parts.append(t)
    return "\n".join(parts)


def jsonld_raw(soup: BeautifulSoup) -> str:
    """串接所有 JSON-LD 原始字串——NAP 一致性掃描會把 schema 裡的 NAP 也納入。"""
    out = []
    for block in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = block.string or block.get_text() or ""
        if raw.strip():
            out.append(raw)
    return "\n".join(out)


def parse_jsonld(soup: BeautifulSoup) -> tuple[list, list]:
    """回傳 (出現的 @type 清單, JSON 解析錯誤清單)。"""
    types, errors = [], []
    for block in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = block.string or block.get_text() or ""
        if not raw.strip():
            continue
        try:
            data = json.loads(raw)
        except Exception as ex:
            errors.append(str(ex)[:120])
            continue
        for node in (data if isinstance(data, list) else [data]):
            t = node.get("@type") if isinstance(node, dict) else None
            if isinstance(t, list):
                types.extend(t)
            elif t:
                types.append(t)
    return types, errors


def _split_sentences(text: str) -> list:
    return [s for s in re.split(r"[。！？!?\n]", text) if s.strip()]


# ───────────────────────── Hard Gates（deterministic） ─────────────────────────

def scan_inducement(text: str) -> list:
    """否定感知的違規掃描：命中詞『上下文窗口』內有反詐／否定線索就放行（避免誤殺反詐警語/法務免責）。"""
    hits = []
    for pat in INDUCEMENT_PATTERNS:
        for m in pat.finditer(text):
            window = text[max(0, m.start() - NEG_WINDOW): m.end() + NEG_WINDOW]
            if any(cue in window for cue in NEG_CUES):
                continue  # 反詐警語 / 法務免責 → 好用法，跳過
            snippet = text[max(0, m.start() - 10): m.end() + 20].replace("\n", " ").strip()
            hits.append(snippet[:60])
    return hits


def _nap_check(corpus: str) -> GateResult:
    """Hard Gate = NAP『無漂移』(出現了就必須對)，不是『必須出現』。
    缺地址/缺公司名 → 不擋 gate(屬 rubric 維度2 內容缺口)；只有真正漂移(門牌號錯、出現非清單電話)才擋。
    corpus = 可見文字 + JSON-LD 原始字串。"""
    problems = []
    text = corpus
    # 中正路門牌號漂移（出現中正路就必須是 468）
    for num in ZHONGZHENG_NUM_RE.findall(text):
        if num != "468":
            problems.append(f"門牌漂移(中正路{num}號)")
    # 電話漂移：頁面出現的市話/手機，若不在合法清單 → 漂移
    canon_digits = {re.sub(r"\D", "", p) for p in CANONICAL.get("phones", []) if p}
    if canon_digits:
        for cand in PHONE_RE.findall(text):
            d = re.sub(r"\D", "", cand)
            # 只比對像市話(09/02開頭、8-10碼)的號碼，避免誤抓其他數字串
            if 9 <= len(d) <= 10 and (d.startswith("0")) and d not in canon_digits:
                problems.append(f"電話漂移({cand.strip()})")
                break
    detail = "；".join(dict.fromkeys(problems)) if problems else "NAP 無漂移"
    return GateResult("nap_consistent", not problems, detail)


def check_gates(soup, text, jsonld_types, jsonld_errors,
                lighthouse, rich_results, target_queries, archived) -> list:
    gates = []

    # 1) 可索引（封存頁不檢查）
    # 只看 <head> 的 robots meta：include 片段(nav/footer)自帶 noindex 會被 innerHTML 注入 body，
    # 但 body 的 meta robots Google 會忽略，不可當作本頁 noindex。
    head = soup.head or soup
    robots = head.find("meta", attrs={"name": re.compile("robots", re.I)})
    noindex = bool(robots and "noindex" in (robots.get("content", "")).lower())
    canonical = soup.find("link", attrs={"rel": re.compile("canonical", re.I)})
    if archived:
        gates.append(GateResult("indexable", True, "封存頁（noindex 預期），略過"))
    else:
        ok = (not noindex) and canonical is not None
        why = []
        if noindex:
            why.append("被 noindex")
        if canonical is None:
            why.append("缺 canonical")
        gates.append(GateResult("indexable", ok, "；".join(why) or "可索引"))

    # 2) schema 有效：JSON-LD 全解析成功 + 有實體型別（或外部 Rich Results 判 pass）
    if rich_results is not None:
        rr_ok = bool(rich_results.get("valid", False))
        gates.append(GateResult("schema_valid", rr_ok,
                                "Rich Results: " + ("pass" if rr_ok else "fail")))
    else:
        # Hard Gate = schema『無錯誤』，不是『必須有 Organization』(缺實體屬 rubric 維度扣分)。
        ok = not jsonld_errors
        why = []
        if jsonld_errors:
            why.append(f"JSON-LD 解析錯誤×{len(jsonld_errors)}")
        # 紅線：用了 FinancialService → gate 失敗（自稱金融機構）
        if "FinancialService" in jsonld_types:
            ok = False
            why.append("紅線：用了 FinancialService schema（非金融機構，改用 RealEstateAgent/LocalBusiness）")
        gates.append(GateResult("schema_valid", ok, "；".join(why) or "schema 解析無錯誤"))

    # 3) NAP 一致（含 schema 內的 NAP）
    nap_corpus = text + "\n" + jsonld_raw(soup)
    gates.append(_nap_check(nap_corpus))

    # 4) 無誘導數字 / 無虛假承諾（否定感知）
    hits = scan_inducement(text)
    gates.append(GateResult("no_inducement", not hits,
                            ("命中違規：" + " / ".join(hits[:3])) if hits else "無誘導／虛假承諾樣式"))

    # 5) 無關鍵字堆砌（保守門檻，避免誤殺）
    stuff = []
    tlen = max(len(text), 1)
    for q in (target_queries or []):
        c = text.count(q)
        density = c * len(q) / tlen
        if c >= 8 and density > 0.03:
            stuff.append(f"{q}×{c}({density:.1%})")
    gates.append(GateResult("no_stuffing", not stuff,
                            ("疑似堆砌：" + "，".join(stuff)) if stuff else "關鍵字密度正常"))

    return gates


# ───────────────────────── 技術分（量測；非 LLM） ─────────────────────────

def technical_score(soup, jsonld_types, jsonld_errors, lighthouse, rich_results) -> DimResult:
    """有餵 Lighthouse 才解鎖滿分；沒餵最高約 60，提示『去跑 Lighthouse』。"""
    ev, score = {}, 0.0

    schema_ok = (rich_results.get("valid") if rich_results else (not jsonld_errors and jsonld_types))
    ev["schema_ok"] = bool(schema_ok)
    if schema_ok:
        score += 25

    viewport = soup.find("meta", attrs={"name": re.compile("viewport", re.I)}) is not None
    ev["viewport"] = viewport
    if viewport:
        score += 10

    canonical = soup.find("link", attrs={"rel": re.compile("canonical", re.I)}) is not None
    ev["canonical"] = canonical
    if canonical:
        score += 10

    if lighthouse and lighthouse.get("seo") is not None:
        seo = float(lighthouse["seo"])
        seo = seo * 100 if seo <= 1 else seo
        ev["lighthouse_seo"] = seo
        score += min(seo, 100) / 100 * 30
    else:
        ev["lighthouse_seo"] = None
        score += 15  # 半額；餵了 Lighthouse 才拿滿

    if lighthouse and "cwv_pass" in lighthouse:
        ev["cwv_pass"] = bool(lighthouse["cwv_pass"])
        score += 25 if lighthouse["cwv_pass"] else 0
    else:
        ev["cwv_pass"] = None  # 無法驗證 → 0；提示去量

    note = "技術分由量測值構成"
    if not lighthouse:
        note = "未餵 Lighthouse/CWV，技術分上限約 60——接上 runner 解鎖滿分"
    return DimResult(round(score, 1), WEIGHTS["technical"], note, ev)


# ───────────────────────── 證據包（給 LLM 評審當依據） ─────────────────────────

def collect_evidence(soup, text, jsonld_types) -> dict:
    headings = [h.get_text(strip=True) for h in soup.find_all(["h2", "h3"])]
    q_markers = ("?", "？", "嗎", "如何", "怎麼", "什麼", "為什麼", "可以", "多少", "幾")
    q_headings = [h for h in headings if any(m in h for m in q_markers)]

    tel = soup.select('a[href^="tel:"]')
    line = [a for a in soup.find_all("a", href=True)
            if any(k in a["href"].lower() for k in ("line.me", "lin.ee")) or "line" in a.get_text().lower()]
    def _is_internal(h):
        h = (h or "").strip()
        if not h or h.startswith(("#", "mailto:", "tel:", "javascript:")):
            return False
        if h.startswith("http"):
            return CANONICAL["site"] in h
        return h.startswith("/") or h.endswith(".html")  # 站內相對連結(如 second-mortgage.html)也算
    internal = [a for a in soup.find_all("a", href=True) if _is_internal(a["href"])]
    tables = soup.find_all("table")
    lists = [u for u in soup.find_all(["ul", "ol"]) if len(u.find_all("li")) >= 3]

    has_update = bool(
        re.search(r"(最後更新|更新日期|Last updated|更新於)", text, re.I)
        or soup.find("time")
        or "dateModified" in str(jsonld_types)
    )

    return {
        "h2h3_total": len(headings),
        "question_headings": q_headings[:12],
        "question_heading_ratio": round(len(q_headings) / max(len(headings), 1), 2),
        "has_faqpage_schema": "FAQPage" in jsonld_types,
        "jsonld_types": sorted(set(jsonld_types)),
        "has_last_updated": has_update,
        "tables": len(tables),
        "rich_lists": len(lists),
        "tel_cta": len(tel),
        "line_cta": len(line),
        "internal_links": len(internal),
        "district_mentions": {d: text.count(d) for d in CONCENTRIC_DISTRICTS if text.count(d) > 0},
        "authority_mentions": [t for t in AUTHORITY_TERMS if t in text],
        "visible_text_len": len(text),
    }


# ───────────────────────── LLM 評審（aeo / local_eeat / topic_cluster / conversion + 合規） ─────────────────────────

JUDGE_SYSTEM = (
    "你是嚴格的在地 SEO / GEO / AEO 評審，熟台灣民間融資（二胎房貸、售後回租、貸款整合、包租代管）"
    "的內容合規。你只輸出 JSON。評分要狠、避免分數通膨，讓優化迴圈有訊號可走。"
    "所有分數必須建立在提供的『證據包』與頁面文字上，不可臆測。"
)

JUDGE_RUBRIC = """\
依下列四維度各打 0–100（整數），並各給一句 rationale（中文、引用具體證據）：

aeo（答案可抽取性）：每個 target query 是否有 40–60 字、緊接問句的「直接答案區塊」？
  H2/H3 是否=真實問句？關鍵資訊是否表格／列表化？是否有 FAQPage schema 與「最後更新」？
local_eeat（在地實體與信任）：在地脈絡（目標行政區）夠不夠深？專業背書（證照／經驗／去識別化案例）？
  是否引用權威來源（央行／聯徵／地政／法規）？陳述是否合規（區間／條件式，無誘導數字、無虛假承諾）？
topic_cluster（主題叢集與內鏈）：是否有 pillar↔cluster 的內鏈成網？query intent 漏斗覆蓋？有無孤兒感／關鍵字自蠶食？
conversion（轉換就緒）：CTA 是否清楚、行動端可一鍵撥號／加 LINE？CTA 旁是否有信任元素？是否低摩擦？

另輸出 compliance：{"violation": bool, "detail": str}
  violation=true 僅限：誘導性具體利率／額度數字、保證／包過件、虛假成功率、未成功仍暗示保證等。
  ★絕不可把以下判為違規（這些是該保留的好用法）：反詐警語（如「不要相信保證過件」）、
  法務免責（如「無法保證核貸結果」「不保證絕對安全」）、銀行邏輯的客觀描述（如「換工作核貸機率會下降」）。

只輸出這個 JSON（不要 markdown、不要多餘文字）：
{"dimensions":{"aeo":{"score":int,"rationale":str},"local_eeat":{"score":int,"rationale":str},
"topic_cluster":{"score":int,"rationale":str},"conversion":{"score":int,"rationale":str}},
"compliance":{"violation":bool,"detail":str}}"""


def build_judge_prompt(url, target_queries, visible_text, evidence) -> str:
    excerpt = visible_text[:6000]  # 控 token；過長截斷
    return (
        f"{JUDGE_RUBRIC}\n\n"
        f"=== 頁面 URL ===\n{url}\n\n"
        f"=== target queries ===\n{json.dumps(target_queries, ensure_ascii=False)}\n\n"
        f"=== 證據包（deterministic 抽出）===\n{json.dumps(evidence, ensure_ascii=False, indent=1)}\n\n"
        f"=== 可見文字（截斷 6000 字）===\n{excerpt}"
    )


def _extract_json(resp_text: str) -> dict:
    s = resp_text.strip()
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s).strip()
    return json.loads(s)


def run_judge(url, target_queries, visible_text, evidence, model, client) -> dict:
    if anthropic is None:
        raise RuntimeError("未安裝 anthropic：pip install anthropic（或用 judge=False 跑 triage）")
    client = client or anthropic.Anthropic()  # 讀 ANTHROPIC_API_KEY
    resp = client.messages.create(
        model=model,
        max_tokens=2000,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": build_judge_prompt(url, target_queries, visible_text, evidence)}],
    )
    text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
    return _extract_json(text)


# ───────────────────────── 主入口 ─────────────────────────

def score_page(html: str, url: str, *,
               target_queries: Optional[list] = None,
               lighthouse: Optional[dict] = None,
               rich_results: Optional[dict] = None,
               prev_score: Optional[float] = None,
               loop_round: Optional[int] = None,
               archived: bool = False,
               judge: bool = True,
               judge_model: str = JUDGE_MODEL,
               client=None) -> ScoreResult:
    """
    對單一頁面評分並裁決 COMMIT/REVERT。

    lighthouse:    {"seo": 0-100 或 0-1, "cwv_pass": bool}（可選；餵了技術分才滿）
    rich_results:  {"valid": bool}（可選；外部 Rich Results 驗證結果，優先於本地 JSON-LD 判斷）
    prev_score:    上一版總分；None=建立基線（過 gate 即 COMMIT）
    archived:      封存/noindex 頁設 True（不檢查 indexable）；正常迴圈不該優化封存頁
    judge=False:   triage 模式——只跑 gate、不評分、不呼叫 LLM（你掃 99 頁那種快篩）
    """
    target_queries = target_queries or []
    soup = _soup(html)
    text = extract_visible_text(soup)
    jsonld_types, jsonld_errors = parse_jsonld(soup)

    gates = check_gates(soup, text, jsonld_types, jsonld_errors,
                        lighthouse, rich_results, target_queries, archived)
    gates_passed = all(g.passed for g in gates)
    reasons = [f"GATE {g.name}: {g.detail}" for g in gates if not g.passed]

    dims: dict = {k: DimResult(None, WEIGHTS[k]) for k in WEIGHTS}

    # ── triage 模式：只看 gate ──
    if not judge:
        return ScoreResult(url, target_queries, gates, gates_passed, dims,
                           None, prev_score,
                           VERDICT_REVERT if not gates_passed else VERDICT_PASS_GATES,
                           reasons or ["triage：gate 全過（未評分）"], None, loop_round)

    # ── gate 掛掉 → 直接 REVERT，省下 LLM 成本 ──
    if not gates_passed:
        return ScoreResult(url, target_queries, gates, False, dims,
                           None, prev_score, VERDICT_REVERT,
                           reasons + ["gate 未過 → 直接 REVERT（略過 LLM 評審）"], None, loop_round)

    # ── 技術分（量測） ──
    dims["technical"] = technical_score(soup, jsonld_types, jsonld_errors, lighthouse, rich_results)

    # ── LLM 評審四維 + 合規旗標 ──
    evidence = collect_evidence(soup, text, jsonld_types)
    try:
        j = run_judge(url, target_queries, text, evidence, judge_model, client)
    except Exception as ex:
        return ScoreResult(url, target_queries, gates, gates_passed, dims,
                           None, prev_score, VERDICT_ERROR,
                           reasons + [f"judge 失敗：{ex}"], judge_model, loop_round)

    comp = j.get("compliance", {}) or {}
    if comp.get("violation"):
        gates.append(GateResult("no_inducement_llm", False, f"LLM 合規旗標：{comp.get('detail', '')[:80]}"))
        return ScoreResult(url, target_queries, gates, False, dims,
                           None, prev_score, VERDICT_REVERT,
                           reasons + [f"LLM 判定合規違規 → REVERT：{comp.get('detail', '')[:80]}"],
                           judge_model, loop_round)

    for k in LLM_DIMS:
        node = (j.get("dimensions", {}) or {}).get(k, {}) or {}
        sc = node.get("score")
        dims[k] = DimResult(float(sc) if sc is not None else None,
                            WEIGHTS[k], node.get("rationale", ""), {})

    # ── 加權總分（需五維齊全） ──
    if any(dims[k].score is None for k in WEIGHTS):
        return ScoreResult(url, target_queries, gates, gates_passed, dims,
                           None, prev_score, VERDICT_ERROR,
                           reasons + ["維度分數不齊，無法計總分"], judge_model, loop_round)
    total = round(sum(dims[k].score * WEIGHTS[k] for k in WEIGHTS) / 100, 2)

    # ── 裁決 ──
    if prev_score is None:
        verdict, why = VERDICT_COMMIT, f"建立基線（總分 {total}）"
    elif total > prev_score + COMMIT_MARGIN:
        verdict, why = VERDICT_COMMIT, f"總分 {prev_score} → {total}（+{round(total - prev_score, 2)}）"
    else:
        verdict, why = VERDICT_REVERT, f"總分未進步（{prev_score} → {total}），REVERT"

    return ScoreResult(url, target_queries, gates, gates_passed, dims,
                       total, prev_score, verdict, [why], judge_model, loop_round)


# ───────────────────────── jsonl 寫入 ─────────────────────────

def append_score(path: str, row: dict) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


# ───────────────────────── 範例（大寫=你的 harness，這段只是示範接法） ─────────────────────────

if __name__ == "__main__":
    DEMO_HTML = """
    <html><head>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <link rel="canonical" href="https://cx468.com.tw/market-insight.html">
      <script type="application/ld+json">
        {"@type":["LocalBusiness","RealEstateAgent"],"name":"鋮馨租賃有限公司",
         "address":"新北市中和區中正路468號","telephone":"02-2249-0517"}</script>
      <script type="application/ld+json">{"@type":"FAQPage"}</script>
    </head><body>
      <h2>中和二胎房貸是什麼？</h2>
      <p>二胎房貸是在既有房貸之上，以同一不動產設定第二順位抵押所取得的資金；
         額度與條件依不動產殘值與個人條件而定，最終核貸由金融機構決定。</p>
      <p>提醒：不要相信「保證過件」的說法，那通常是詐騙。</p>
      <time datetime="2026-06-25">最後更新：2026-06-25</time>
      <a href="tel:0222490517">電話諮詢</a>
      <a href="https://lin.ee/abc">加 LINE 諮詢</a>
    </body></html>
    """
    # judge=False → 只示範 gate（不需 API key）
    res = score_page(DEMO_HTML, "https://cx468.com.tw/market-insight.html",
                     target_queries=["中和 二胎房貸 是什麼"], judge=False)
    print("verdict:", res.verdict, "| gates_passed:", res.gates_passed)
    for g in res.gates:
        print(f"  [{'PASS' if g.passed else 'FAIL'}] {g.name}: {g.detail}")
    print("jsonl row:")
    print(json.dumps(res.to_jsonl_row(commit_hash="demo123"), ensure_ascii=False, indent=2))
