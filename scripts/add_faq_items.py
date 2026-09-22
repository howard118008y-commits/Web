#!/usr/bin/env python3
"""主戰場五頁 FAQ 補題（媽祖 2026-08-19 已核）——同源生成器 ＋ 全站同源閘門。

草稿正本：行銷產出/官網文章草稿/2026-08-19-主戰場FAQ補題草稿-FINAL.md
鐵則（memory feedback_faq_schema_same_source）：可見 FAQ DOM 與 FAQPage JSON-LD
必須由同一份資料結構渲染，禁止手寫兩份。

用法：
  python3 scripts/add_faq_items.py                 # 插入（冪等：已含新題的頁跳過）
  python3 scripts/add_faq_items.py --verify        # 驗 NEW_FAQS 那幾頁
  python3 scripts/add_faq_items.py --verify --all  # 驗全站每一個含 FAQPage 的頁

--verify 的沿革（2026-09-23）：原本用寫死的 DOM 選擇器抓可見 Q/A
（`<div class="sec-text">常見問題 · FAQ</div>` 等），Better 版型改版後選擇器
全部落空 → 閘門直接 IndexError 拋出，等於零把關。改成版型無關的做法：
把整頁去標籤後的可見文字正規化（去空白、還原 HTML entity），逐題檢查
schema 的 Q 與 A 是否逐字出現在可見文字裡。不改任何頁面內容，只回報。
"""
import datetime
import html as html_mod
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ── 同源資料結構：媽祖已核逐字稿，一字不改 ────────────────────────────────
NEW_FAQS = {
    "topic-a.html": [
        ("頁面上的「房貸利率」跟我實際拿到的利率一樣嗎？",
         "不一定一樣。頁面顯示的是全體銀行新承做房貸的加權平均，屬市場參考值；個人利率由銀行依信用狀況、收入、擔保品條件核定，可能高於或低於平均。實際條件依個案評估，最終核貸由金融機構決定。"),
        ("新增房貸金額變多或變少，代表什麼？",
         "它反映市場購屋需求與銀行放款意願的強度。快速增長常見於市場轉熱，也可能引來央行信用管制；縮量則代表授信趨於保守。單月數字波動較大，判讀時建議看趨勢方向，不看單點。"),
        ("什麼是選擇性信用管制（限貸令）？對一般人有影響嗎？",
         "這是央行針對特定對象或區域調整貸款成數、寬限期等條件的工具。若名下已有房貸、或購買受管制區域的物件，可貸條件可能受影響。實際適用範圍以央行公告為準，最終核貸由金融機構決定。"),
        ("央行升息，已經在繳的房貸月付會馬上變多嗎？",
         "多數房貸採機動計息，利率會隨指標利率調整，通常在銀行公告調整後的下一期反映到月付；若在固定利率期間內則暫不受影響。實際調整時點與幅度，依各銀行契約條款與個案而定。"),
        ("銀行授信環境緊縮時，準備貸款的人可以怎麼因應？",
         "授信趨緊時，銀行對成數、利率與收入證明的要求通常更嚴。可先整理收入與信用資料、確認自身負債狀況，並預留較充裕的申辦時間。實際條件依個案評估，最終核貸由金融機構決定。"),
    ],
    "topic-b.html": [
        ("買賣移轉棟數有包含繼承或贈與嗎？",
         "沒有。買賣移轉棟數統計的是以「買賣」為登記原因的所有權移轉；繼承、贈與屬其他移轉原因，另行統計。判讀市場交易熱度時，用買賣棟數較能反映真實的成交活動。"),
        ("移轉棟數為什麼跟現在感覺到的市況有落差？",
         "因為它以「完成所有權移轉登記」的時間計算，從簽約到登記通常有一到兩個月的作業時間，統計反映的是稍早之前的成交。市況急轉時，這個數字會晚一步跟上，判讀要注意時間差。"),
        ("六都成交量比較，能看出什麼？",
         "能看出交易熱度的區域差異：哪些都會區量能相對熱絡、哪些正在降溫。搭配六都均價比較一起看，可以大致掌握「量與價」在不同城市的走向，作為觀察區域市況的參考。"),
        ("房價指數和實價登錄的成交價，哪個比較有參考性？",
         "兩者用途不同。實價登錄是逐筆成交紀錄，反映個案價格；房價指數是統計處理後的趨勢線，消除了個案差異。看整體走向用指數，查特定區域行情用實價登錄，兩者互為補充。"),
        ("成交量萎縮時，想賣房或申請貸款的人要注意什麼？",
         "量縮期買方通常觀望，銷售期可能拉長，銀行估價也可能趨於保守，進而影響可貸金額。若有資金規劃需求，建議提早評估、預留時間。實際條件依個案評估，最終核貸由金融機構決定。"),
    ],
    "topic-c.html": [
        ("「建照 vs 使照差距」是什麼？為什麼要看？",
         "建照代表未來要開工的供給，使照代表完工交屋的供給。兩者差距擴大，表示已請照但尚未完工的量在累積，未來交屋潮可能集中出現，是觀察供給端壓力的一項參考訊號。"),
        ("風險預警指標亮訊號，代表房市要崩盤了嗎？",
         "不是。預警指標的作用是提早提醒市場壓力正在累積，不等於預測崩盤。單一指標轉差可能只是短期波動，通常要多項指標同方向惡化、且持續一段時間，才比較有參考意義。"),
        ("房貸逾放比上升，對想貸款的人有什麼影響？",
         "逾放比上升代表銀行房貸資產品質轉差，銀行放款通常會更審慎，對成數、利率與收入審核可能趨嚴。實際影響依各銀行政策與個案條件而定，最終核貸由金融機構決定。"),
        ("房價所得比高，就等於我買不起房嗎？",
         "不完全是。房價所得比衡量的是整體房價相對所得的倍數，屬總體指標；個人負擔能力還要看利率、貸款年限、自備款與家庭支出。總體數字供參考，個人購屋負擔仍需依自身財務狀況試算。"),
        ("這些預警指標，一般人多久看一次就夠？",
         "多數指標為月報或季報，一般自住者每季掃一次即可；若正準備購屋、換屋或申辦貸款，建議在決策前再更新一次數據。指標僅供研判市場環境，非投資或貸款建議。"),
    ],
    "topic-d.html": [
        ("美元台幣匯率變動，跟房市有什麼關係？",
         "匯率牽動外資與台商資金的進出。台幣升值階段常伴隨資金流入，市場資金相對寬鬆；貶值階段資金流出，資金面可能承壓。它是間接影響房市的資金面訊號之一，需搭配其他指標判讀。"),
        ("台股漲跌會影響房市嗎？",
         "市場上有「財富效應」的說法：股市走多時，部分獲利資金可能轉入房市帶動置產需求；股市重挫則可能使購屋決策轉趨保守。兩者並非同步連動，僅屬觀察資金情緒的參考訊號。"),
        ("美國聯準會的決策，為什麼台灣要跟著看？",
         "台灣是高度開放的小型經濟體，聯準會升降息會影響全球資金流向、美債殖利率與美元匯率，進而牽動台灣的利率環境與央行政策空間，間接影響房貸利率的走向。"),
        ("通膨高的時候，買房可以「抗通膨」嗎？",
         "不動產常被視為抗通膨資產之一，但通膨升溫也常伴隨升息，會墊高貸款成本、壓抑購買力，兩股力量方向相反。是否置產仍應依自身財務狀況與需求評估，本頁資訊非投資建議。"),
        ("D 系列和 A 系列（房貸金融）指標差在哪？",
         "D 系列看「外部環境」：美債殖利率、匯率、股市與通膨等國際訊號；A 系列看「內部管道」：央行利率與銀行放款行為。國際訊號通常先影響央行決策與資金成本，再傳導到房貸條件。"),
    ],
    "radar-index.html": [
        ("這個儀表板是給誰看的？需要金融背景嗎？",
         "為一般屋主與購屋族設計，不需要金融背景。每項指標都附白話解讀，頁面下方另有名詞解釋，目的是讓你在做房貸或資金相關決策前，能快速掌握市場環境的大方向。"),
        ("LTV、DBR、DSR 這些名詞是什麼意思？",
         "三個銀行審核常見名詞：LTV 是貸款成數（貸款占房價的比例）、DBR 是無擔保負債比、DSR 是每月還款占收入的比例。本頁名詞解釋區有完整說明，實際認定依各金融機構規定與個案而定。"),
        ("指標之間互相矛盾時，該以哪個為準？",
         "指標本來就可能不同調，例如量縮但價穩。沒有單一指標能代表全局，建議以系列為單位看方向、多項指標交叉印證，並留意各指標的資料時間點不同，避免用單一數字下結論。"),
        ("儀表板的資訊可以直接當成買房或貸款的依據嗎？",
         "不建議。本頁是公開統計的整理與呈現，僅供了解市場環境，非投資或貸款建議。個人決策仍需依自身財務狀況評估；本公司非金融機構、不放貸，最終核貸由金融機構決定。"),
    ],
}

# ── 渲染模板（沿用各頁既有 FAQ DOM 樣式） ────────────────────────────────
TOPIC_ITEM = (
    '  <div style="border:1px solid rgba(0,0,0,0.08);background:var(--bg-panel);padding:22px 24px;margin-bottom:12px">\n'
    '    <div style="font-family:\'Noto Serif TC\',serif;font-weight:700;font-size:16px;color:#1d1d1f;margin-bottom:10px">{q}</div>\n'
    '    <div style="font-size:14px;line-height:1.9;color:#5a5750">{a}</div>\n'
    '  </div>\n'
)
RADAR_ITEM = (
    '    <div style="{box}">\n'
    '      <h3 style="font-family:\'Noto Serif TC\',serif;font-weight:600;font-size:17px;color:var(--ink);margin:0 0 8px">{q}</h3>\n'
    '      <p style="font-size:14px;line-height:1.85;color:var(--ink-mid);margin:0">{a}</p>\n'
    '    </div>\n'
)
RADAR_BOX_MID = 'border-bottom:1px solid rgba(0,0,0,0.07);padding:20px 0'
RADAR_BOX_LAST = 'padding:20px 0'

TOPIC_ANCHOR = '  </div>\n  <div class="sec-head"><div class="sec-line"></div><div class="sec-text">名詞解釋 · GLOSSARY</div>'
RADAR_ANCHOR = '  </div>\n  <!-- ════════════ 常見問題 END ════════════ -->'

JSONLD_RE = re.compile(r'(<script type="application/ld\+json">\n)(\{.*?\})(\n</script>)', re.S)
# 插入用的 JSONLD_RE 綁死「換行＋縮排」那種寫法；驗證要掃全站，多數頁的 JSON-LD 是單行，
# 用嚴格版會整頁抓不到、被誤判成「JSON-LD 壞了」，所以驗證另用寬鬆版。
LD_ANY_RE = re.compile(r'(?is)<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>')


DATEMOD_RE = re.compile(r'("dateModified"\s*:\s*")(\d{4}-\d{2}-\d{2})(")')


def bump_datemod(html: str, today: str) -> tuple[str, int]:
    """改完內容一併把該頁 JSON-LD dateModified 設為今日。

    2026-08-19 晚審踩坑：本腳本補了五頁 FAQ 內容卻沒動 dateModified，
    schema 上仍掛 7/24～8/14，等於對 Google 宣稱「內容沒更新」——
    改內容不 bump 就是假鮮度（memory feedback_no_hardcoded_freshness_stamp）。
    只改 dateModified，datePublished 與可見文字一律不碰。
    之後全站再跑 scripts/update_schema_datemod.py 也會得到同一個日期（git 實質 commit 日＝今天）。
    """
    n = 0

    def repl(m):
        nonlocal n
        if m.group(2) == today:
            return m.group(0)
        n += 1
        return m.group(1) + today + m.group(3)

    return DATEMOD_RE.sub(repl, html), n


def extend_jsonld(html: str, faqs) -> str:
    """把 faqs 附加進頁內 FAQPage JSON-LD（同一資料結構，重新序列化保持 indent=1 風格）。"""
    hit = 0

    def repl(m):
        nonlocal hit
        try:
            data = json.loads(m.group(2))
        except Exception:
            return m.group(0)
        if not (isinstance(data, dict) and data.get("@type") == "FAQPage"):
            return m.group(0)
        hit += 1
        for q, a in faqs:
            data["mainEntity"].append({
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            })
        return m.group(1) + json.dumps(data, ensure_ascii=False, indent=1) + m.group(3)

    out = JSONLD_RE.sub(repl, html)
    assert hit == 1, f"FAQPage JSON-LD 命中 {hit} 次（預期 1）"
    return out


def insert_page(fname: str) -> str:
    path = ROOT / fname
    html = path.read_text(encoding="utf-8")
    faqs = NEW_FAQS[fname]
    if faqs[0][0] in html:
        return "skip（已含新題，冪等跳過）"

    html = extend_jsonld(html, faqs)

    if fname == "radar-index.html":
        # 既有末題補回 border-bottom（新題接在後面）
        old_last = '    <div style="padding:20px 0">\n      <h3'
        assert html.count(old_last) == 1, "radar 既有末題 anchor 不唯一"
        html = html.replace(old_last, f'    <div style="{RADAR_BOX_MID}">\n      <h3')
        block = "".join(
            RADAR_ITEM.format(box=(RADAR_BOX_LAST if i == len(faqs) - 1 else RADAR_BOX_MID), q=q, a=a)
            for i, (q, a) in enumerate(faqs)
        )
        assert html.count(RADAR_ANCHOR) == 1, "radar FAQ 容器 anchor 不唯一"
        html = html.replace(RADAR_ANCHOR, block + RADAR_ANCHOR)
    else:
        block = "".join(TOPIC_ITEM.format(q=q, a=a) for q, a in faqs)
        assert html.count(TOPIC_ANCHOR) == 1, f"{fname} FAQ 容器 anchor 不唯一"
        html = html.replace(TOPIC_ANCHOR, block + TOPIC_ANCHOR)

    today = datetime.date.today().isoformat()
    html, bumped = bump_datemod(html, today)
    path.write_text(html, encoding="utf-8")
    return f"+{len(faqs)} 題，dateModified→{today}（{bumped} 處）"


# ── 驗證：JSON-LD Q/A 與可見 DOM Q/A 逐題精確比對（sch==vis） ─────────────
def extract_schema(html: str):
    for m in JSONLD_RE.finditer(html):
        try:
            data = json.loads(m.group(2))
        except Exception as e:
            raise SystemExit(f"JSON-LD 解析失敗: {e}")
        if isinstance(data, dict) and data.get("@type") == "FAQPage":
            return [(q["name"], q["acceptedAnswer"]["text"]) for q in data["mainEntity"]]
    raise SystemExit("找不到 FAQPage JSON-LD")


def visible_text(html: str) -> str:
    """整頁可見文字（去 script/style/註解/標籤、還原 entity、去掉所有空白）。
    中文沒有詞間空白，兩邊都去空白比對最穩，也讓 en/ 頁的排版換行不會造成假不一致。"""
    h = re.sub(r"(?is)<script.*?</script>", " ", html)
    h = re.sub(r"(?is)<style.*?</style>", " ", h)
    h = re.sub(r"(?s)<!--.*?-->", " ", h)
    h = re.sub(r"<[^>]+>", " ", h)
    return _norm(h)


def _norm(s: str) -> str:
    return re.sub(r"\s+", "", html_mod.unescape(s))


def all_faq_schemas(html: str):
    """回傳頁內所有 FAQPage 的 (Q, A) 清單（含包在 @graph 裡的）。"""
    faqs = []
    for m in LD_ANY_RE.finditer(html):
        try:
            data = json.loads(m.group(1))
        except Exception:
            continue                      # 壞 JSON 由 --verify 另行報，不讓整批中斷
        nodes = data if isinstance(data, list) else [data]          # 頂層陣列型也要吃
        flat = []
        for n in nodes:
            flat += (n.get("@graph", []) if isinstance(n, dict) else []) + [n]
        for node in flat:
            if isinstance(node, dict) and node.get("@type") == "FAQPage":
                for q in node.get("mainEntity", []):
                    faqs.append((q.get("name", ""), q.get("acceptedAnswer", {}).get("text", "")))
    return faqs


def verify(files=None) -> bool:
    ok = True
    files = list(files or NEW_FAQS)
    bad = []
    for fname in files:
        html = (ROOT / fname).read_text(encoding="utf-8")
        if "FAQPage" not in html:
            continue
        sch = all_faq_schemas(html)
        if not sch:
            # 「FAQPage」出現在註解或內文、但 JSON-LD 裡根本沒有 → 不是不同源，是這頁沒 schema
            in_ld = any("FAQPage" in m.group(1) for m in LD_ANY_RE.finditer(html))
            if in_ld:
                print(f"FAIL {fname}: JSON-LD 裡有 FAQPage 但解不出 Q/A（JSON 壞了或結構非預期）")
                ok = False
                bad.append(fname)
            else:
                print(f"SKIP {fname}: 全頁無 FAQPage schema（只在註解／內文出現字樣）")
            continue
        vis = visible_text(html)
        miss = []
        for i, (q, a) in enumerate(sch, 1):
            if _norm(q) not in vis:
                miss.append(f"第 {i} 題問題未出現在可見內容：{q[:40]}")
            if _norm(a) not in vis:
                miss.append(f"第 {i} 題答案未出現在可見內容：{a[:40]}")
        if miss:
            ok = False
            bad.append(fname)
            print(f"FAIL {fname}: schema {len(sch)} 題，{len(miss)} 處不同源")
            for line in miss:
                print(f"    - {line}")
        else:
            print(f"PASS {fname}: schema {len(sch)} 題，Q/A 逐字都在可見內容裡")
    print(f"\n=== 共驗 {len(files)} 頁｜不同源 {len(bad)} 頁 ===")
    if bad:
        print("不一致清單：" + ", ".join(bad))
    return ok


def all_faq_pages():
    pages = sorted(p.relative_to(ROOT).as_posix()
                   for p in list(ROOT.glob("*.html")) + list(ROOT.glob("en/*.html"))
                   if "FAQPage" in p.read_text(encoding="utf-8"))
    return pages


if __name__ == "__main__":
    if "--verify" in sys.argv:
        files = all_faq_pages() if "--all" in sys.argv else None
        sys.exit(0 if verify(files) else 1)
    for fname in NEW_FAQS:
        print(f"{fname}: {insert_page(fname)}")
