#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tier A 第2批：4 工具頁補 可見FAQ(語意h2/h3)+FAQPage schema+缺的tel CTA；tools.html另補答案卡。"""
import re, json, html
esc=lambda x:html.escape(x,quote=True)
CTA=('<div style="max-width:720px;margin:20px auto 0;padding:0 16px;display:flex;gap:10px;flex-wrap:wrap">'
 '<a href="tel:0222490517" style="font-size:14px;font-weight:600;color:#fff;background:#1d1d1f;padding:10px 20px;border-radius:980px;text-decoration:none">☎ 電話諮詢</a>'
 '<a href="https://lin.ee/PHIfSoY" style="font-size:14px;font-weight:600;color:#fff;background:#06c755;padding:10px 20px;border-radius:980px;text-decoration:none">加 LINE 免費諮詢</a></div>\n')

FAQS={
"rental-yield-calculator.html":[
 ("總投報率和淨投報率差在哪？","總投報率＝年租金 ÷ 房屋總價，未扣成本；淨投報率再扣掉持有成本（房屋稅、地價稅、管理費、修繕、空租期），更接近實際到手的報酬。"),
 ("租金報酬率多少算合理？","台灣都會區住宅總投報常見約 1.5–2.5%，因地段與屋況差異大；報酬率偏低時，增值性與資金成本要一起評估，本工具僅供參考。"),
 ("算投報率要注意什麼？","別只看總投報，務必扣掉持有成本與空租期看淨投報，並把房貸利息與稅費一起算進資金成本，才不會高估報酬。"),
],
"affordability-calculator.html":[
 ("DBR 和 DSR 是什麼？","DBR（無擔保負債比）是信用卡、信貸等無擔保債務月付 ÷ 月收入；DSR（總費用支出比）含房貸等所有債務月付 ÷ 月收入。銀行用來評估還款能力。"),
 ("DBR 22 倍是什麼意思？","金管會規定個人無擔保債務（信貸＋卡循等）總額原則不宜超過月收入的 22 倍，超過會明顯影響信貸核貸；房貸屬有擔保，不計入此 22 倍。"),
 ("月付佔收入多少才安全？","一般建議房貸月付不超過月收入 1/3、總負債月付不超過 40–50%；超過代表現金流吃緊，可評估貸款整合降低月付，實際仍依個案與銀行而定。"),
],
"new-taipei-house-tax.html":[
 ("房屋稅怎麼算？","房屋稅＝房屋評定現值 × 適用稅率。房屋評定現值由地方政府按構造、用途、屋齡、路段率核定，並非市價或成交價。"),
 ("自住房屋稅率多少？","自住住家用房屋（本人、配偶、未成年子女全國合計 3 戶以內，設籍且無出租營業）適用 1.2% 優惠稅率；非自住住家採較高稅率（囤房稅累進），實際依各地方政府規定。"),
 ("房屋稅什麼時候繳？","每年 5 月開徵，課徵期間為前一年 7 月至當年 6 月；逾期會加徵滯納金，實際以稅捐稽徵機關核定為準。"),
],
"tools.html":[
 ("這些試算工具要收費或留資料嗎？","全部免費、在瀏覽器即時計算，不需註冊或留個資，計算結果不會上傳。"),
 ("試算結果可以當正式依據嗎？","為估算參考，實際稅費與貸款條件以各主管機關／金融機構核定為準；本公司非金融機構。"),
 ("算完之後想諮詢怎麼辦？","可加 LINE 或來電免費諮詢，由顧問協助評估你的個案方向；不申請不收費。"),
],
}
TOOLS_CARD=('<div id="quick-answer" style="max-width:720px;margin:18px auto 0;padding:20px 22px;background:#f6f5f3;border:1px solid #e3e3e6;border-left:3px solid #C61B1C;border-radius:8px">\n'
 '  <div style="font-size:12px;font-weight:700;color:#C61B1C;letter-spacing:.18em;margin-bottom:8px">快速答案</div>\n'
 '  <p style="font-size:15.5px;line-height:1.8;color:#1d1d1f;margin:0 0 8px"><strong>買房、賣房、持有、貸款的每一筆數字，先自己算清楚再決策。</strong>鋮馨整理了 10+ 個免費房產試算工具：房貸試算、二胎可貸額度、房地合一稅、土地增值稅、地價稅、房屋稅、購屋總費用、租金報酬、空屋成本、負擔能力等，全部免費即時、不需留資料。</p>\n'
 '  <div style="font-size:11px;color:#86868b;line-height:1.65">試算為估算參考，實際稅費與貸款條件以各主管機關／金融機構核定為準；本公司非金融機構。</div>\n</div>\n')

def faq_section(faqs):
    items="".join(
      f'  <div style="border:1px solid #e7e0d3;border-radius:8px;padding:16px 20px;margin-bottom:10px;background:#fff">'
      f'<h3 style="font-size:15.5px;font-weight:700;color:#1d1d1f;margin:0 0 8px">{esc(q)}</h3>'
      f'<p style="font-size:14px;line-height:1.85;color:#515154;margin:0">{esc(a)}</p></div>\n' for q,a in faqs)
    return (f'<section style="max-width:720px;margin:28px auto 0;padding:0 16px">\n'
            f'  <h2 style="font-size:20px;font-weight:700;color:#1d1d1f;margin:0 0 14px">常見問題</h2>\n{items}</section>\n')

for fn,faqs in FAQS.items():
    s=open(fn,encoding="utf-8").read()
    if '常見問題' in s and '<h3' in s and 'FAQPage' in s: print("似已有FAQ,跳過",fn); continue
    has_tel = 'href="tel:' in s
    has_card = 'id="quick-answer"' in s
    add=""
    if fn=="tools.html" and not has_card:
        s=s.replace('<div class="wrap">','<div class="wrap">\n'+TOOLS_CARD,1)
    block = (CTA if not has_tel else "") + faq_section(faqs)
    if '<div data-include="footer"></div>' in s:
        s=s.replace('<div data-include="footer"></div>', block+'<div data-include="footer"></div>',1)
    else:
        s=s.replace('</body>', block+'</body>',1)
    sch={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}
    k=s.rfind('</head>'); s=s[:k]+'<script type="application/ld+json">\n'+json.dumps(sch,ensure_ascii=False,indent=1)+'\n</script>\n'+s[k:]
    open(fn,"w",encoding="utf-8").write(s)
    print(f"✅ {fn}: +{len(faqs)}FAQ(h2/h3)+schema {'+CTA' if not has_tel else ''} {'+答案卡' if fn=='tools.html' else ''}")
print("done")
