#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全站 SEO/GEO/AEO 體檢：掃所有真實頁面，逐頁打分、列缺漏。"""
import os, re, glob, json, subprocess
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def has(s, pat): return re.search(pat, s, re.I|re.S) is not None

# --- 新鮮度：JSON-LD dateModified vs git 最後實質 commit 日 ---
# 實質 commit＝排除 [datemod-sync]（update_schema_datemod.py 的同步 commit）與 [nofresh]（純版型／analytics 批次，pre-commit 同標記免 bump；2026-09-23 加，否則 146 頁掛 fluid.css 那天 27 頁被判假腐爛），
# 否則同步一跑，git 日期永遠是同步日，比對失去意義。偏差 > 容差天數記 flag。
# 2026-08-19 晚審：容差 30→7 天。30 天太寬，改內容卻沒 bump dateModified 的頁
# 可以躺整整一個月才被抓到（4b09011 五頁補 FAQ 未 bump 就是被 30 天容差蓋過去的）。
# 項目名保留 fresh30 不改（改名會斷掉既有分數表與健檢 regex 的欄位對照），
# 實際門檻一律以 FRESH_TOLERANCE_DAYS 為準。
FRESH_TOLERANCE_DAYS = 7
LDJSON_RE = re.compile(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.I|re.S)
DATEMOD_RE = re.compile(r'"dateModified"\s*:\s*"(\d{4}-\d{2}-\d{2})')

def git_real_date(relpath):
    out = subprocess.run(
        ["git","log","-1","--format=%cs","--invert-grep","--grep","datemod-sync","--grep","nofresh","--",relpath],
        cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return out or None

stale_detail = {}  # relpath -> (dateModified, git_date, 偏差天數)

# --- speakable／dateModified：只認 JSON-LD 結構，不再純字串 grep（2026-09-28 收緊，C10）---
# 舊判準 has(s, r'[Ss]peakable') 與 has(s, r'dateModified|datePublished') 都是不驗結構的字串命中：
# 前者 CSS／JS 註解、空 cssSelector 都放行；後者未帶引號（JS 的 d.dateModified 也中）、datePublished 也算過、值不是日期也算過。
# 新判準：speakable＝任一 JSON-LD 物件有 speakable 鍵，且其 cssSelector 或 xpath 有非空內容；
#         datemod＝任一 JSON-LD 區塊含帶引號的 "dateModified" 且值為合法 ISO 日期（沿用 DATEMOD_RE，與 check_fresh 同源）。
# 2026-09-28 實測全站 163 頁：兩項收緊前後缺口都是 0→0（現況無假陽性），改的是量尺不是分數。

def ldjson_objects(s):
    """攤平頁內所有 JSON-LD 區塊裡的 dict（含 @graph／巢狀）；解析失敗的區塊跳過（Google 也讀不了）。"""
    out = []
    def walk(o):
        if isinstance(o, dict):
            out.append(o)
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    for block in LDJSON_RE.findall(s):
        try: walk(json.loads(block))
        except ValueError: pass
    return out

def check_speakable(s):
    """JSON-LD 內真的有 speakable 結構，且 cssSelector 或 xpath 有內容才算過。"""
    for o in ldjson_objects(s):
        sp = o.get('speakable')
        for spec in (sp if isinstance(sp, list) else [sp]):
            if not isinstance(spec, dict):
                continue
            for key in ('cssSelector', 'xpath'):
                v = spec.get(key)
                if isinstance(v, str) and v.strip():
                    return True
                if isinstance(v, list) and any(isinstance(x, str) and x.strip() for x in v):
                    return True
    return False

def check_datemod(s):
    """JSON-LD 內有帶引號的 "dateModified" 且值是合法日期才算過（datePublished 不算）。"""
    for block in LDJSON_RE.findall(s):
        for d in DATEMOD_RE.findall(block):
            try:
                date.fromisoformat(d)
                return True
            except ValueError:
                pass
    return False

def check_fresh(s, relpath):
    """有 dateModified 且與 git 實質 commit 日偏差 ≤ FRESH_TOLERANCE_DAYS（7 天）才算新鮮。"""
    dates = []
    for block in LDJSON_RE.findall(s):
        dates += DATEMOD_RE.findall(block)
    if not dates:
        return False  # 連 dateModified 都沒有，datemod 項也會 fail
    gd = git_real_date(relpath)
    if not gd:
        return True  # 無 git 歷史（未 commit 新檔）不誤判為腐爛
    dm = max(dates)
    drift = abs((date.fromisoformat(dm) - date.fromisoformat(gd)).days)
    if drift > FRESH_TOLERANCE_DAYS:
        stale_detail[relpath] = (dm, gd, drift)
        return False
    return True

# --- AEO 答案卡：要「有容器元素」且「在頁面前段」才算能被 AI 直接擷取 ---
# 2026-09-27 收緊。舊判準 has(s, r'快速答案|一句話|answer-card|tldr|quick-answer') 是純字串 grep，
# 不驗結構也不驗版位，三種假陽性全放行：①<style> 裡的 CSS 註解 /* 快速答案 */（corporate-loan 唯一命中點就是它）、
# ②JSON-LD speakable cssSelector 寫了 "#quick-answer" 但頁面上沒有這個元素、③正文中段的散句（「不是一句話能說死」）。
# 新判準兩條都要過：①剝掉 script/style/註解後，body 內有 id/class 帶 answer-card/quick-answer/tldr/bt-qa 的元素
#（bt-qa 是站上 Better 版型的答案卡 class，漏掉會誤殺 realestate-tax-calculator 這種只有 class 沒有 id 的卡）；
# ②該元素落在可見文字的前 CARD_MAX_DEPTH（實測：沒被埋的卡最深 27%，被埋在正文中後段的最淺 36%，門檻取在空隙中間）。
CARD_EL_RE = re.compile(r'<[^>]+(?:id|class)=["\'][^"\']*(?:answer-card|quick-answer|tldr|bt-qa)', re.I)
CARD_NOISE_RE = re.compile(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>|<!--[\s\S]*?-->', re.I)
CARD_MAX_DEPTH = 0.30

def visible_len(s):
    """可見文字長度（去標籤、去空白），當作頁面深度的分母。"""
    return len(re.sub(r'\s+', '', re.sub(r'<[^>]+>', ' ', s)))

def check_answercard(s):
    """有答案卡容器元素，且該元素在可見文字前 30% 內才算過。"""
    i = s.lower().find('<body')
    body = CARD_NOISE_RE.sub(' ', s[i:] if i >= 0 else s)
    m = CARD_EL_RE.search(body)
    if not m:
        return False
    total = visible_len(body)
    return total == 0 or visible_len(body[:m.start()]) / total <= CARD_MAX_DEPTH


def audit(path):
    s = open(path, encoding="utf-8", errors="ignore").read()
    # 判斷是否真實頁面（有完整 doc 結構），排除 include 片段
    is_page = has(s, r'<html') and has(s, r'<head')
    if not is_page:
        return None
    # 排除 noindex 頁（demo/封存頁不是 SEO/GEO/AEO 目標，不應計入信號覆蓋率）
    head = s[:s.lower().find('</head>')] if '</head>' in s.lower() else s
    if has(head, r'name=["\']robots["\'][^>]*noindex'):
        return None
    # 排除 meta-refresh 轉址樁頁（舊網址留的空殼：未進 sitemap、非索引內容頁，只有 title/canonical/轉址一行）
    # 2026-09-27：90de4f3 新增 article-loan-integration / article-sale-leaseback-guide 兩支樁頁被算進真實頁面，
    # 母體 162→164 且兩頁 AEO 全缺，把 SEO 100%→99.39%、AEO 98.06%→96.86% 拖成「像內容退步」，其實是分母髒了。
    refresh = re.findall(r'<meta[^>]*http-equiv=["\']refresh["\'][^>]*>', head, re.I)
    if any('url=' in t.lower() for t in refresh):
        return None
    r = {}
    # --- SEO ---
    r['title']       = has(s, r'<title>[^<]{5,}</title>')
    r['desc']        = has(s, r'name=["\']description["\'][^>]*content=["\'][^"\']{20,}')
    r['canonical']   = has(s, r'rel=["\']canonical["\']')
    r['og']          = has(s, r'property=["\']og:title["\']')
    r['twitter']     = has(s, r'name=["\']twitter:card["\']')
    h1 = re.findall(r'<h1[\s>]', s, re.I)
    r['h1_single']   = (len(h1) == 1)
    r['viewport']    = has(s, r'name=["\']viewport["\']')
    r['lang']        = has(s, r'<html[^>]*lang=')
    # --- AEO ---
    r['faq']         = has(s, r'"FAQPage"')
    r['speakable']   = check_speakable(s)  # JSON-LD 內有 speakable 結構且 cssSelector/xpath 有內容（判準見上方註解）
    r['definedterm'] = has(s, r'"DefinedTerm"')
    r['breadcrumb']  = has(s, r'"BreadcrumbList"')
    r['answercard']  = check_answercard(s)  # 快速答案卡（容器元素＋版位，判準見上方 CARD_* 註解）
    r['datemod']     = check_datemod(s)  # 鮮度：JSON-LD 內帶引號 "dateModified" 且值為合法日期（datePublished 不算）
    r['fresh30']     = check_fresh(s, os.path.relpath(path, ROOT))  # 鮮度真實性（vs git）
    # --- GEO ---
    r['org_schema']  = has(s, r'"Organization"|"RealEstateAgent"|"LocalBusiness"')
    # 紅線：不可用 FinancialService
    r['no_finsvc']   = not has(s, r'"FinancialService"')
    return r

# 權重（衝分用：缺的越多分越低）
SEO = ['title','desc','canonical','og','twitter','h1_single','viewport','lang']
AEO = ['faq','speakable','definedterm','breadcrumb','answercard','datemod','fresh30']
GEO = ['org_schema','no_finsvc']

pages = {}
# 掃描母體含全部子目錄（en/world/tools-lab…），跟著站點結構長，勿只掃頂層
EXCLUDE_DIRS = {".git", "node_modules", "scripts"}
for p in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)):
    rel = os.path.relpath(p, ROOT)
    if rel.split(os.sep)[0] in EXCLUDE_DIRS:
        continue
    r = audit(p)
    if r: pages[rel] = r

def score(r, keys): return sum(1 for k in keys if r[k]), len(keys)

print(f"真實頁面數：{len(pages)}\n")
# 逐維度缺漏統計
def gaps(keys, label):
    print(f"=== {label} 缺漏統計（缺的頁數 / {len(pages)}）===")
    for k in keys:
        miss = [n for n,r in pages.items() if not r[k]]
        flag = "🔴" if len(miss) > len(pages)*0.5 else ("🟡" if miss else "🟢")
        print(f"  {flag} {k:12s} 缺 {len(miss):3d} 頁")
    print()
gaps(SEO, "SEO"); gaps(AEO, "AEO"); gaps(GEO, "GEO")

# 鮮度腐爛清單：dateModified 與 git 實質 commit 日偏差 >30 天
if stale_detail:
    print(f"=== 🕰 鮮度腐爛（dateModified vs git 偏差 >{FRESH_TOLERANCE_DAYS} 天，共 {len(stale_detail)} 頁）===")
    for n,(dm,gd,drift) in sorted(stale_detail.items(), key=lambda x:-x[1][2]):
        print(f"  {drift:4d} 天  dateModified={dm}  git={gd}  {n}")
    print("  → 跑 scripts/update_schema_datemod.py 同步\n")

# 紅線：用了 FinancialService 的頁（嚴重）
fin = [n for n,r in pages.items() if not r['no_finsvc']]
if fin: print("🚨 用了 FinancialService schema(紅線):", fin)

# 每頁總分，列最弱 15 頁
scored = []
for n,r in pages.items():
    s1,_=score(r,SEO); s2,_=score(r,AEO); s3,_=score(r,GEO)
    tot = s1+s2+s3; mx = len(SEO)+len(AEO)+len(GEO)
    scored.append((tot, mx, n, s1, s2, s3))
scored.sort()
print(f"=== 最弱 15 頁（總分/{scored[0][1]}）===")
for tot,mx,n,s1,s2,s3 in scored[:15]:
    print(f"  {tot:2d}/{mx}  SEO{s1}/{len(SEO)} AEO{s2}/{len(AEO)} GEO{s3}/{len(GEO)}  {n}")

# 存 JSON 供後續比對
# 2026-07-31 repo 遷出 iCloud 後，ROOT/.. 不再是專案夾，寫檔會 FileNotFoundError。
# 2026-09-24 再搬：原本寫進 iCloud 的「行銷產出/週報」，檔案被 iCloud 逐出未下載時
# 會丟 Resource deadlock avoided（09-22 實際發生，統計跑完但 JSON 沒落地），
# 且 launchd 起的程序列不到 iCloud 目錄。改寫進 repo 內 scripts/（機器產出流水，
# 比照 scripts/goal-scores.jsonl 由 .gitignore 排除，不進版控）。
out = os.path.join(ROOT, "scripts", "seo-audit-latest.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump({"pages":pages,"summary":{"total_pages":len(pages)}}, open(out,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n明細存：{out}")
