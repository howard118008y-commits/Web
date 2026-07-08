#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tier A：3 個計算機頁加 快速答案卡 + 可見FAQ(語意h2/h3) + FAQPage schema + 小CTA(tel/LINE)。
   稅/費用事實、條件式、帶免責；可見文字與 schema 同源一致。"""
import re, json, html
esc=lambda x:html.escape(x,quote=True)

C = {
"purchase-cost-calculator.html": {
  "accent":"#b45309",
  "lead":"買房除了成交價，通常還要多準備約 2–8% 的相關費用。",
  "body":"包含契稅、印花稅、代書（地政士）費、登記規費、仲介費（買方常見 1–2%）、火險與地震險；若要裝潢、搬家再另計。本工具一次幫你估出購屋總費用，避免簽約後才發現現金不夠。",
  "faqs":[
    ("買房的契稅怎麼算？","契稅以房屋評定現值（非成交價）為稅基，買賣移轉稅率為 6%，由買方繳納；實際以稅捐稽徵機關核定為準。"),
    ("仲介費有上限嗎？","依不動產經紀業管理規定，向買賣雙方收取的仲介報酬合計上限為成交價 6%；實務上買方常見 1–2%，可與業者議定。"),
    ("代書（地政士）費用大約多少？","視案件複雜度而定，常見數千至上萬元，過戶、設定、謄本等登記規費另計；以實際報價與規費標準為準。"),
  ]},
"vacancy-cost-calculator.html": {
  "accent":"#1e3a5f",
  "lead":"房子空著，不是「沒收入」而已，是每個月真的在燒錢。",
  "body":"空屋成本主要兩塊：①持有成本（房貸利息、管理費、地價稅與房屋稅分攤、保險）②機會成本（這間房若出租可收的租金）。本工具把兩者加總，估出空置每月的隱形損失，幫你判斷該調整租金、加速出租，還是另作資金規劃。",
  "faqs":[
    ("空屋最大的隱形成本是什麼？","通常是「機會成本」——原本可收的租金；再加上房貸利息照繳，空一個月等於雙重損失。"),
    ("空屋會被課比較重的稅嗎？","房屋稅對非自住住家用房屋採較高稅率（各縣市不同，部分採囤房稅累進）；空置且未出租可能適用較高稅率，實際依各地方政府規定與認定。"),
    ("空屋太久該怎麼辦？","可評估調整租金、委託包租代管加速出租；若同時有資金壓力，也可評估名下不動產的其他資金規劃方式，依個案而定。"),
  ]},
"land-tax-calculator.html": {
  "accent":"#C61B1C",
  "lead":"賣房時的土地增值稅，是依「土地公告現值的漲幅」課徵，不是看成交價。",
  "body":"稅基＝移轉時土地公告現值 −（前次移轉現值 × 物價指數調整）。一般用地按漲幅採 20%／30%／40% 三級累進；符合自用住宅用地條件可適用 10% 優惠稅率（一生一次，另有「一生一屋」可再適用）。本工具幫你快速估算。",
  "faqs":[
    ("自用住宅優惠稅率 10% 怎麼適用？","需符合本人或配偶、直系親屬設籍、無出租或營業使用、都市土地 3 公畝（非都市 7 公畝）以內等條件，並於申報時提出；「一生一次」用過後，符合條件可再用「一生一屋」。實際以稅捐稽徵機關核定為準。"),
    ("土地增值稅和地價稅有什麼不同？","地價稅是「持有」期間每年課徵；土地增值稅是「移轉（賣出）」時才課，課的是土地公告現值的漲價部分。"),
    ("重購自用住宅可以退稅嗎？","出售自用住宅後一定期間內重購、且符合條件者，可申請退還已繳土地增值稅；依稅法規定與稽徵機關核定。"),
  ]},
}
CTA = ('<div style="margin-top:14px;display:flex;gap:10px;flex-wrap:wrap">'
 '<a href="tel:0222490517" style="font-size:14px;font-weight:600;color:#fff;background:#1d1d1f;padding:9px 18px;border-radius:980px;text-decoration:none">☎ 電話諮詢</a>'
 '<a href="https://lin.ee/PHIfSoY" style="font-size:14px;font-weight:600;color:#fff;background:#06c755;padding:9px 18px;border-radius:980px;text-decoration:none">加 LINE 免費諮詢</a></div>')

for fn,c in C.items():
    s=open(fn,encoding="utf-8").read()
    if 'id="quick-answer"' in s: print("已有,跳過",fn); continue
    ac=c["accent"]
    card=(f'<div id="quick-answer" style="max-width:720px;margin:18px auto 0;padding:20px 22px;background:#f6f5f3;border:1px solid #e3e3e6;border-left:3px solid {ac};border-radius:8px">\n'
     f'  <div style="font-size:12px;font-weight:700;color:{ac};letter-spacing:.18em;margin-bottom:8px">快速答案</div>\n'
     f'  <p style="font-size:15.5px;line-height:1.8;color:#1d1d1f;margin:0 0 8px"><strong>{esc(c["lead"])}</strong>{esc(c["body"])}</p>\n'
     f'  <div style="font-size:11px;color:#86868b;line-height:1.65">本工具為試算參考，實際稅費以各主管／稅捐稽徵機關核定為準；本公司非金融機構。</div>\n{CTA}\n</div>\n')
    # 可見 FAQ：語意 h2/h3
    faqv="".join(
      f'  <div style="border:1px solid #e7e0d3;border-radius:8px;padding:16px 20px;margin-bottom:10px;background:#fff">'
      f'<h3 style="font-size:15.5px;font-weight:700;color:#1d1d1f;margin:0 0 8px">{esc(q)}</h3>'
      f'<p style="font-size:14px;line-height:1.85;color:#515154;margin:0">{esc(a)}</p></div>\n'
      for q,a in c["faqs"])
    faq_sec=(f'<section style="max-width:720px;margin:28px auto 0;padding:0 16px">\n'
     f'  <h2 style="font-size:20px;font-weight:700;color:#1d1d1f;margin:0 0 14px">常見問題</h2>\n{faqv}</section>\n')
    # 插入：答案卡在 wrap 開頭後；FAQ 放在 footer include 前(或 </body> 前)
    s=s.replace('<div class="wrap">', '<div class="wrap">\n'+card, 1)
    if '<div data-include="footer"></div>' in s:
        s=s.replace('<div data-include="footer"></div>', faq_sec+'<div data-include="footer"></div>',1)
    else:
        s=s.replace('</body>', faq_sec+'</body>',1)
    # FAQPage schema(與可見文字同源)
    sch={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in c["faqs"]]}
    k=s.rfind('</head>'); s=s[:k]+'<script type="application/ld+json">\n'+json.dumps(sch,ensure_ascii=False,indent=1)+'\n</script>\n'+s[k:]
    open(fn,"w",encoding="utf-8").write(s)
    print(f"✅ {fn}: 答案卡+CTA+{len(c['faqs'])}FAQ(h2/h3)+schema")
print("done")
