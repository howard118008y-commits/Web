#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B3：地價稅城市頁加「差異化」快速答案卡（用各市累進起點地價，天然不同非mass-template）。
   城市計算頁+guide頁+hub。城市頁不加blanket FAQ；FAQ只放hub一頁。speakable改指#quick-answer。"""
import re, glob, json, html
esc=lambda x:html.escape(x,quote=True)

def get_name(s):
    m=re.search(r'<meta name="description" content="([^，、地]+?)地價稅', s)
    if m: return m.group(1)
    m=re.search(r'og:title" content="([^地]+?)地價稅', s)
    return m.group(1) if m else ""
def get_T(s):
    m=re.search(r'累進起點地價\s*([0-9,]+)\s*元', s)
    return m.group(1) if m else ""

def speakable_fix(s):
    return s.replace('"cssSelector": [\n   "h1"\n  ]','"cssSelector": [\n   "#quick-answer",\n   "h1"\n  ]')\
            .replace('"cssSelector":["h1"]','"cssSelector":["#quick-answer","h1"]')

def city_card(name,T):
    return (f'<div id="quick-answer" style="max-width:720px;margin:18px auto 0;padding:20px 22px;background:#fff;border:1px solid #e7e0d3;border-left:3px solid #0369a1;border-radius:8px">\n'
    f'  <div style="font-size:12px;font-weight:700;color:#0369a1;letter-spacing:.18em;margin-bottom:8px">快速答案</div>\n'
    f'  <p style="font-size:15.5px;line-height:1.8;color:#1d1d1f;margin:0 0 10px"><strong>{esc(name)}地價稅怎麼算？關鍵看「累進起點地價」{esc(T)} 元。</strong>自用住宅用地適用 2‰ 優惠稅率；一般用地以申報地價總額對照累進起點，超過部分採六級累進（10‰–55‰）。本工具支援行政區・地段・地號查詢，輸入即可估算當年度應納稅額。</p>\n'
    f'  <div style="font-size:11px;color:#86868b;line-height:1.65">累進起點地價依{esc(name)}每年公告為準；本試算僅供參考，實際稅額以稅捐稽徵機關核定為準。</div>\n</div>\n')

done=[]
# ── 1) 20 個城市計算頁 ──
for fn in sorted(glob.glob("*-land-value-tax.html")):
    s=open(fn,encoding="utf-8").read()
    if 'id="quick-answer"' in s: continue
    name,T=get_name(s),get_T(s)
    if not (name and T): print("⚠ 抽不到 name/T:",fn); continue
    s=s.replace('<div class="wrap">', city_card(name,T)+'<div class="wrap">',1)
    s=speakable_fix(s)
    open(fn,"w",encoding="utf-8").write(s); done.append(f"{fn}({name} {T})")

# ── 2) 4 個 guide 頁（城市專屬 h1，用該市值）──
GUIDE_T={"taipei":("台北市","43,957,000"),"taichung":("台中市","1,741,000"),
         "taoyuan":("桃園市","3,439,000"),"new-taipei":("新北市","7,878,000")}
for slug,(name,T) in GUIDE_T.items():
    fn=f"{slug}-land-value-tax-guide.html"
    s=open(fn,encoding="utf-8").read()
    if 'id="quick-answer"' in s: continue
    card=(f'<div id="quick-answer" style="max-width:760px;margin:20px auto 0;padding:20px 22px;background:#f6f5f3;border:1px solid #e3e3e6;border-left:3px solid #0369a1;border-radius:8px">\n'
    f'  <div style="font-size:12px;font-weight:700;color:#0369a1;letter-spacing:.18em;margin-bottom:8px">快速答案</div>\n'
    f'  <p style="font-size:15.5px;line-height:1.8;color:#1d1d1f;margin:0 0 10px"><strong>{name}地價稅怎麼算？</strong>先把名下{name}土地的申報地價加總，對照{name}當年「累進起點地價」{T} 元：自用住宅用地（符合條件）適用 2‰；一般用地未達起點課 10‰，超過部分按 15‰～55‰ 六級累進。每年 11 月開徵、繳納至 11/30。</p>\n'
    f'  <div style="font-size:11px;color:#86868b;line-height:1.65">累進起點地價與自用資格依{name}每年公告及稅捐機關認定為準；本文僅供參考，實際稅額以核定為準。</div>\n</div>\n')
    # 插在 h1 區塊後（hero 之後第一個容器前）；用 h1 結尾後插入
    s=re.sub(r'(</h1>\s*(?:</div>|</header>|</section>)?)', r'\1\n'+card, s, count=1)
    s=speakable_fix(s)
    open(fn,"w",encoding="utf-8").write(s); done.append(f"{fn}(guide {name})")

# ── 3) hub: land-value-tax-calculator.html（總頁：通用答案卡 + 3題FAQ + FAQPage schema）──
fn="land-value-tax-calculator.html"; s=open(fn,encoding="utf-8").read()
if 'id="quick-answer"' not in s:
    hub_card=('<div id="quick-answer" style="max-width:720px;margin:18px auto 0;padding:20px 22px;background:#fff;border:1px solid #e7e0d3;border-left:3px solid #0369a1;border-radius:8px">\n'
    '  <div style="font-size:12px;font-weight:700;color:#0369a1;letter-spacing:.18em;margin-bottom:8px">快速答案</div>\n'
    '  <p style="font-size:15.5px;line-height:1.8;color:#1d1d1f;margin:0 0 10px"><strong>地價稅怎麼算？</strong>把名下同一縣市的土地申報地價加總，對照該縣市當年「累進起點地價」：自用住宅用地（符合條件）適用 2‰ 優惠稅率；一般用地未達起點課 10‰，超過部分按 15‰～55‰ 六級累進。各縣市起點不同，選你的縣市即可分別試算。每年 11 月開徵。</p>\n'
    '  <div style="font-size:11px;color:#86868b;line-height:1.65">累進起點地價依各縣市每年公告為準；本試算僅供參考，實際稅額以稅捐稽徵機關核定為準。</div>\n</div>\n')
    faqs=[("地價稅和房屋稅有什麼不同？","地價稅是針對「土地」按申報地價課徵、每年 11 月開徵；房屋稅是針對「房屋」按房屋評定現值課徵、每年 5 月開徵。兩者稅基與開徵時間都不同。"),
          ("自用住宅用地的 2‰ 優惠稅率怎麼適用？","土地需符合自用住宅用地條件（如本人或配偶、直系親屬設籍且無出租營業、面積上限等），並於每年（地價稅 9/22 前）向稅捐機關申請核准，才適用 2‰；否則按一般用地稅率。實際以稅捐機關認定為準。"),
          ("各縣市的累進起點地價為什麼差很多？","累進起點地價是依各縣市「平均地價」計算公告，地價高的都會區（如台北市）起點明顯高於非都會縣市，因此同樣地價在不同縣市的稅率級距可能不同。")]
    faqv="".join(f'  <div style="border:1px solid #e7e0d3;border-radius:8px;padding:18px 20px;margin-bottom:10px;background:#fff"><div style="font-weight:700;font-size:15.5px;color:#1d1d1f;margin-bottom:8px">{esc(q)}</div><div style="font-size:14px;line-height:1.85;color:#515154">{esc(a)}</div></div>\n' for q,a in faqs)
    faq_section=f'<div style="max-width:720px;margin:32px auto 0;padding:0 16px"><h2 style="font-size:20px;font-weight:700;color:#1d1d1f;margin:24px 0 14px">常見問題</h2>\n{faqv}</div>\n'
    s=s.replace('<div class="wrap">', hub_card+'<div class="wrap">',1)
    # FAQ 區插在 wrap 結束前較難定位，改插在 </body> 前的內容尾；簡單放在 footer include 前
    if '<div data-include="footer"></div>' in s:
        s=s.replace('<div data-include="footer"></div>', faq_section+'<div data-include="footer"></div>',1)
    else:
        s=s.replace('</body>', faq_section+'</body>',1)
    faq_sch={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}
    k=s.rfind('</head>'); s=s[:k]+'<script type="application/ld+json">\n'+json.dumps(faq_sch,ensure_ascii=False,indent=1)+'\n</script>\n'+s[k:]
    s=speakable_fix(s)
    open(fn,"w",encoding="utf-8").write(s); done.append(f"{fn}(hub+FAQ)")

print(f"✅ 處理 {len(done)} 頁:")
for d in done: print("  ",d)
