#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B1：topic-a/b/c/d 加 快速答案卡 + 可見FAQ + 可見名詞解釋 + FAQPage/DefinedTermSet schema + speakable改指#quick-answer。
   數值引 cx_data.json 既有值；市場意涵框架、帶免責、無我方業務口吻；可見文字與 schema 文字同源保證一致。"""
import re, json, html

CONTENT = {
"topic-a.html": {
  "termset_name": "房貸金融指標名詞解釋",
  "qa_lead": "想知道「銀行願不願意放款、利率往哪走」，先看這 5 個房貸金融面指標。",
  "qa_body": "A 系列追蹤央行政策利率、實際房貸利率、新增房貸量、不動產放款集中度與新青安占比，是研判台灣房貸授信環境鬆緊的第一道訊號。",
  "qa_bullets": [
    ("央行重貼現率 2.00%", "政策基準利率，2024-03 升到此後凍漲，定錨整體利率走向。"),
    ("房貸利率 2.322%（2026-05）", "銀行實際核貸的加權平均，已站上 2%，直接影響每月月付。"),
    ("新增房貸 469 億/月（2026-05）", "反映市場購屋需求與信用擴張的強度。"),
    ("不動產放款集中度 35.17%（2026-05）", "銀行對房市的曝險程度，金管會設有警戒上限。"),
    ("新青安占比 下滑中（2026-01）", "政策補貼房貸，方案 2026-07-31 到期，退場風險需留意。"),
  ],
  "faqs": [
    ("央行重貼現率跟我的房貸利率有什麼關係？",
     "央行重貼現率是政策基準利率（目前 2.00%），決定銀行資金成本，房貸利率通常隨它連動。央行升降息會牽動未來月付，但實際房貸利率仍由各銀行依個案核定。"),
    ("「不動產放款集中度」過高代表什麼？",
     "它是銀行總放款中不動產貸款的占比（目前約 35.17%）。比率過高代表銀行體系對房市曝險偏高，金管會設有警戒上限，可能促使銀行收緊房貸條件或降低成數。"),
    ("新青安占比下滑，對首購族有什麼影響？",
     "新青安是政策補貼房貸，占比下滑反映方案階段性退場（2026-07-31 到期）。退場後首購族可能少了一個低利選項，建議重新評估自身負擔與其他可行方案。"),
  ],
  "terms": [
    ("央行重貼現率", "中央銀行對銀行融通資金的基準利率，是房貸利率的政策定錨。"),
    ("不動產放款集中度", "銀行總放款中不動產相關貸款的占比，金管會設有警戒上限。"),
    ("新青安貸款", "政府「新青年安心成家」政策性房貸方案，提供首購族補貼利率。"),
    ("選擇性信用管制", "央行針對特定對象或區域調整貸款成數與條件的工具，俗稱限貸令。"),
  ],
},
"topic-b.html": {
  "termset_name": "房市量價指標名詞解釋",
  "qa_lead": "想知道「現在房市是熱還是冷、價格撐不撐得住」，看這組量價指標。",
  "qa_body": "B 系列追蹤買賣移轉棟數、信義與國泰房價指數、六都移轉與房價所得比，量（成交）與價（房價）一起看，才不會被單一數字誤導。",
  "qa_bullets": [
    ("買賣移轉 80,476 棟（2026-04）", "全國成交量，量縮通常領先價格鬆動。"),
    ("六都移轉 62,687 棟（2026-04）", "六大都會成交量，占全國多數。"),
    ("信義房價指數 量縮價穩（2026-Q1）", "以純住中古屋為主，目前量縮但價格緩穩。"),
    ("國泰房價指數 預售趨緩（2026-Q1）", "含預售與新成屋，預售市場轉趨保守。"),
    ("六都房價所得比 14.62 倍（2025-Q4）", "房價約等於 14.62 年家庭可支配所得，負擔概略指標。"),
  ],
  "faqs": [
    ("買賣移轉棟數下降，代表房價要跌嗎？",
     "不必然。移轉棟數（目前 80,476 棟）是成交量，量縮通常領先價格鬆動，但價格還受利率、供給與政策影響。量與價要一起看，不宜用單一數字判斷。"),
    ("信義和國泰房價指數有什麼不同？",
     "信義指數以純住宅中古屋為主（目前量縮價穩）；國泰指數涵蓋預售與新成屋（目前預售趨緩）。兩者編製口徑不同，分別反映成屋與預售市場。"),
    ("房價所得比 14.62 倍是什麼意思？",
     "指房價約等於家庭 14.62 年的可支配所得（六都，2025-Q4）。數字越高代表購屋負擔越重，是衡量房市可負擔性的常用指標之一。"),
  ],
  "terms": [
    ("買賣移轉棟數", "一定期間內完成所有權移轉登記的不動產棟數，反映市場成交量。"),
    ("房價所得比", "房價中位數相對家庭年可支配所得中位數的倍數，衡量購屋負擔。"),
    ("信義房價指數", "以純住宅中古屋成交價編製的房價走勢指數。"),
    ("國泰房價指數", "涵蓋預售與新成屋的房價走勢指數。"),
  ],
},
"topic-c.html": {
  "termset_name": "房市風險指標名詞解釋",
  "qa_lead": "想提前看出「房市風險在累積還是緩解」，看這組風險預警指標。",
  "qa_body": "C 系列追蹤房貸逾放比、房價所得比與建照核發，從「還款違約、買房負擔、未來供給」三個角度提前示警。",
  "qa_bullets": [
    ("房貸逾放比 0.08%（2026-Q1）", "房貸違約比率，目前極低，銀行資產品質良好。"),
    ("房價所得比 9.32 倍（2025-Q4）", "全國買房負擔倍數，偏高代表可負擔性吃緊。"),
    ("建照核發 31,573 戶（2026-04）", "未來新增供給的領先指標。"),
    ("建照 vs 使照 42,905 戶（2026-04）", "開工與完工落差，反映建商推案節奏。"),
  ],
  "faqs": [
    ("房貸逾放比 0.08% 算高還是低？",
     "偏低。逾放比是房貸逾期放款金額占房貸餘額的比率，0.08%（2026-Q1）代表整體房貸違約極少、銀行資產品質良好。這個數字往上走，才是風險升高的訊號。"),
    ("房價所得比 9.32 倍代表什麼？",
     "全國房價約等於 9.32 年的家庭可支配所得（2025-Q4）。比率偏高代表購屋負擔吃緊，是觀察房市可負擔性與泡沫風險的指標之一。"),
    ("建照核發數量能預測房市嗎？",
     "建照是未來房屋供給的領先指標（目前 31,573 戶，2026-04）。核發大增預示未來推案量上升，可能影響供需與價格，但從核發到完工有時間落差，需搭配其他指標一起看。"),
  ],
  "terms": [
    ("房貸逾放比", "房貸逾期放款金額占房貸總餘額的比率，衡量銀行房貸資產品質。"),
    ("建照核發", "主管機關核發建造執照的戶數，是未來房屋供給的領先指標。"),
    ("使用執照", "建物完工檢驗合格後核發、可合法使用的證照。"),
    ("房價所得比", "房價相對家庭年所得的倍數，衡量購屋負擔輕重。"),
  ],
},
"topic-d.html": {
  "termset_name": "國際資金指標名詞解釋",
  "qa_lead": "想知道「國際資金與物價怎麼牽動台灣房貸」，看這組總體環境指標。",
  "qa_body": "D 系列追蹤美十年期公債殖利率、美元台幣匯率、台股與台灣 CPI；外部資金與通膨會透過利率與資金流，間接影響台灣房市與房貸條件。",
  "qa_bullets": [
    ("美十年期公債殖利率 4.493%（2026-06）", "全球利率定錨，牽動台灣資金成本與長天期利率。"),
    ("美元台幣匯率 31.71（2026-06）", "影響資金流向與輸入性通膨。"),
    ("台股加權指數 47,101 點（2026-06）", "資產與財富效果，間接影響購屋力。"),
    ("台灣 CPI 2.20%（2026-05）", "通膨水準，是央行升降息的關鍵依據。"),
  ],
  "faqs": [
    ("美國公債殖利率，關台灣房貸什麼事？",
     "美十年期公債殖利率（目前 4.493%）被視為全球利率定錨，會牽動台灣的資金成本與長天期利率，間接影響房貸利率走向與央行的政策空間。"),
    ("CPI（消費者物價指數）和房貸利率有關係嗎？",
     "有。CPI 反映通膨（目前 2.20%，2026-05），是央行決定升降息的關鍵依據；通膨升溫常使央行傾向升息，進而牽動房貸利率與每月月付。"),
    ("看這些國際指標，對買房有什麼用？",
     "它們是房市的「外部環境」訊號：利率、匯率、股市與通膨會透過資金面影響購屋力與房貸條件。僅供研判大方向，實際貸款條件仍依個案與銀行決定。"),
  ],
  "terms": [
    ("美十年期公債殖利率", "美國 10 年期公債的市場殖利率，被視為全球長天期利率的定錨。"),
    ("消費者物價指數（CPI）", "衡量一般物價變動的指標，是中央銀行貨幣政策的重要依據。"),
    ("輸入性通膨", "因進口商品或原物料價格上漲，透過匯率傳導至國內的物價上升。"),
    ("選擇性信用管制", "央行針對特定對象或區域調整貸款成數與條件的工具，俗稱限貸令。"),
  ],
},
}

DISCLAIMER = "本頁資訊僅供市場參考，非投資或貸款建議；本公司非金融機構，最終核貸由金融機構決定。"

def esc(s): return html.escape(s, quote=True)

def build_answer_card(c):
    bullets = "".join(
        f'<li><strong style="color:#E8E3D5">{esc(t)}</strong>：{esc(d)}</li>' for t,d in c["qa_bullets"])
    return (
'<div id="quick-answer" style="background:var(--bg-panel);border:1px solid rgba(255,255,255,0.12);border-left:2px solid #C61B1C;padding:24px 26px;margin-bottom:48px">\n'
'  <div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;font-weight:500;color:#ff6b6b;letter-spacing:0.35em;margin-bottom:12px">快速答案 · QUICK ANSWER</div>\n'
f'  <p style="font-size:16px;line-height:1.85;color:#E8E3D5;margin:0 0 14px"><strong style="color:#fff">{esc(c["qa_lead"])}</strong>{esc(c["qa_body"])}</p>\n'
f'  <ul style="margin:0 0 12px;padding-left:20px;font-size:13.5px;color:#B0AB9A;line-height:2">{bullets}</ul>\n'
f'  <div style="font-size:11.5px;color:#7A7565;line-height:1.7">{esc(DISCLAIMER)}</div>\n'
'</div>\n')

def build_faq_visible(c):
    items = "".join(
'  <div style="border:1px solid rgba(255,255,255,0.12);background:var(--bg-panel);padding:22px 24px;margin-bottom:12px">\n'
f'    <div style="font-family:\'Noto Serif TC\',serif;font-weight:700;font-size:16px;color:#fff;margin-bottom:10px">{esc(q)}</div>\n'
f'    <div style="font-size:14px;line-height:1.9;color:#B0AB9A">{esc(a)}</div>\n'
'  </div>\n' for q,a in c["faqs"])
    return (
'  <div class="sec-head"><div class="sec-line"></div><div class="sec-text">常見問題 · FAQ</div><div class="sec-line"></div></div>\n'
f'  <div style="margin-bottom:56px">\n{items}  </div>\n')

def build_glossary_visible(c):
    items = "".join(
f'    <div style="border-left:2px solid rgba(255,255,255,0.22);padding:7px 0 7px 16px"><strong style="color:#E8E3D5;font-size:14px">{esc(t)}</strong><span style="color:#7A7565;font-size:13.5px;line-height:1.85"> — {esc(d)}</span></div>\n'
        for t,d in c["terms"])
    return (
'  <div class="sec-head"><div class="sec-line"></div><div class="sec-text">名詞解釋 · GLOSSARY</div><div class="sec-line"></div></div>\n'
f'  <div style="margin-bottom:56px;display:grid;gap:10px">\n{items}  </div>\n')

def build_faq_schema(c):
    return {"@context":"https://schema.org","@type":"FAQPage",
        "mainEntity":[{"@type":"Question","name":q,
            "acceptedAnswer":{"@type":"Answer","text":a}} for q,a in c["faqs"]]}

def build_termset_schema(c):
    return {"@context":"https://schema.org","@type":"DefinedTermSet","name":c["termset_name"],
        "hasDefinedTerm":[{"@type":"DefinedTerm","name":t,"description":d} for t,d in c["terms"]]}

for fn,c in CONTENT.items():
    s=open(fn,encoding="utf-8").read()
    # 1) 答案卡 插在 sec-head(監測指標) 前
    anchor='  <div class="sec-head">'
    i=s.find(anchor)
    s=s[:i]+build_answer_card(c)+s[i:]
    # 2) 可見 FAQ + 名詞解釋 插在 cta-box 前
    anchor2='  <div class="cta-box">'
    j=s.find(anchor2)
    s=s[:j]+build_faq_visible(c)+build_glossary_visible(c)+s[j:]
    # 3) schema：FAQPage + DefinedTermSet 插在 </head> 前
    sch=('<script type="application/ld+json">\n'+json.dumps(build_faq_schema(c),ensure_ascii=False,indent=1)+'\n</script>\n'
         '<script type="application/ld+json">\n'+json.dumps(build_termset_schema(c),ensure_ascii=False,indent=1)+'\n</script>\n')
    k=s.rfind('</head>')
    s=s[:k]+sch+s[k:]
    # 4) speakable 改指 #quick-answer（topic 模板的 cssSelector 是換行的 "h1"）
    s=s.replace('"cssSelector": [\n   "h1"\n  ]','"cssSelector": [\n   "#quick-answer",\n   "h1"\n  ]')
    open(fn,"w",encoding="utf-8").write(s)
    print(f"✅ {fn}: 答案卡+{len(c['faqs'])}FAQ+{len(c['terms'])}名詞+schema+speakable")
print("done")
