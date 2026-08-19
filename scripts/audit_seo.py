#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全站 SEO/GEO/AEO 體檢：掃所有真實頁面，逐頁打分、列缺漏。"""
import os, re, glob, json, subprocess
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def has(s, pat): return re.search(pat, s, re.I|re.S) is not None

# --- 新鮮度：JSON-LD dateModified vs git 最後實質 commit 日 ---
# 實質 commit＝排除 [datemod-sync]（update_schema_datemod.py 的同步 commit），
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
        ["git","log","-1","--format=%cs","--invert-grep","--grep","datemod-sync","--",relpath],
        cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return out or None

stale_detail = {}  # relpath -> (dateModified, git_date, 偏差天數)

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
    r['speakable']   = has(s, r'[Ss]peakable')
    r['definedterm'] = has(s, r'"DefinedTerm"')
    r['breadcrumb']  = has(s, r'"BreadcrumbList"')
    r['answercard']  = has(s, r'快速答案|一句話|answer-card|tldr|quick-answer')  # 快速答案卡
    r['datemod']     = has(s, r'dateModified|datePublished')  # 鮮度
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
# 改為絕對路徑（可用 CX468_MARKETING_DIR 覆寫），並自動建目錄。
MARKETING_DIR = os.environ.get(
    "CX468_MARKETING_DIR",
    os.path.expanduser(
        "~/Library/Mobile Documents/com~apple~CloudDocs/鋮馨cloud code/行銷產出"
    ),
)
out = os.path.join(MARKETING_DIR, "週報", "seo-audit-latest.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump({"pages":pages,"summary":{"total_pages":len(pages)}}, open(out,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n明細存：{out}")
