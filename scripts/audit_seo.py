#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全站 SEO/GEO/AEO 體檢：掃所有真實頁面，逐頁打分、列缺漏。"""
import os, re, glob, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def has(s, pat): return re.search(pat, s, re.I|re.S) is not None

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
    # --- GEO ---
    r['org_schema']  = has(s, r'"Organization"|"RealEstateAgent"|"LocalBusiness"')
    # 紅線：不可用 FinancialService
    r['no_finsvc']   = not has(s, r'"FinancialService"')
    return r

# 權重（衝分用：缺的越多分越低）
SEO = ['title','desc','canonical','og','twitter','h1_single','viewport','lang']
AEO = ['faq','speakable','definedterm','breadcrumb','answercard','datemod']
GEO = ['org_schema','no_finsvc']

pages = {}
for p in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
    r = audit(p)
    if r: pages[os.path.basename(p)] = r

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
out = os.path.join(ROOT, "..", "行銷產出", "週報", "seo-audit-latest.json")
json.dump({"pages":pages,"summary":{"total_pages":len(pages)}}, open(out,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n明細存：{out}")
