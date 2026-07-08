#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""補 answer card/FAQ/definedterm 到 genuine 內容頁(同源生成)。各頁內容不同。
   只加缺的信號；售後回租三要件;二胎場景免費諮詢;market-meaning不踩禁語。"""
import json, html, re
esc=lambda x:html.escape(x,quote=True)

# 每頁: (答案卡lead, 答案卡body, [FAQ], [(term,def)], accent)
P={
"services.html":dict(accent="#C61B1C",
 lead="名下有房、被銀行拒或缺現金？鋮馨提供五條合法的資金規劃路。",
 body="售後回租（過戶＋簽租約續住＋可依約買回）、二胎房貸、貸款整合、民間轉銀行、包租代管，依你的不動產與財務狀況評估最適合的方向。鋮馨是諮詢與媒合服務、非金融機構、不放貸，最終核貸由金融機構決定。",
 faqs=[("鋮馨提供哪些服務？","售後回租、二胎房貸、貸款整合、民間轉銀行與包租代管。售後回租是把房子過戶給投資方、同時簽租約繼續居住、並保有日後依約買回的權利；其餘為貸款規劃與不動產管理協助。本公司非金融機構。"),
   ("信用有瑕疵也能評估嗎？","可以。不同方案對信用條件要求不同，名下有房時即使曾被銀行拒貸，仍可重新評估可行方向；能否成案、條件如何，依個案與金融機構決定。"),
   ("諮詢要收費嗎？","免費諮詢，不申請不收費、面談不收費。鋮馨提供諮詢與媒合協助，不是放貸方。")],
 terms=[("售後回租","屋主將不動產過戶給投資方、同時簽租約繼續居住，並保有日後依約買回權利的資金規劃方式。"),
   ("二胎房貸","在既有第一順位房貸之外再設定第二順位抵押取得資金，產權不移轉。"),
   ("貸款整合","將多筆高利率債務整併為一筆銀行貸款，目標降低每月還款。"),
   ("民間轉銀行","將高利率民間借款分階段轉回銀行體系以降低利息負擔。"),
   ("包租代管","將房屋出租與管理委外，穩定收租並減少自行管理負擔。")]),
"market-insight.html":dict(accent="#1a3a6b",
 lead="想看懂台北新北房市與銀行放貸鬆緊？看這幾個指標。",
 body="房市走勢與銀行授信受央行政策利率、選擇性信用管制（限貸令）、不動產放款集中度與 DBR／DSR 規範影響。本頁整理公開市場資訊供研判，非投資或貸款建議；實際貸款條件依個案與各銀行核定。",
 faqs=[("現在銀行房貸放得鬆還是緊？","受央行選擇性信用管制與不動產放款集中度上限影響，銀行對房貸成數與條件時有調整。實際鬆緊依各銀行政策與個案而定，本頁僅供市場研判參考。"),
   ("選擇性信用管制（限貸令）是什麼？","央行針對特定對象或區域調整貸款成數與條件的工具，目的在抑制房市過熱；會影響購屋族可貸成數，是觀察房市政策的重要指標。"),
   ("DBR／DSR 對申貸有什麼影響？","DBR 是無擔保負債相對月收入的倍數、DSR 是總債務月付佔月收入比，銀行用來評估還款能力；比率偏高會影響核貸，可評估貸款整合改善現金流。")],
 terms=[("選擇性信用管制","央行針對特定對象或區域調整貸款成數與條件的工具，俗稱限貸令。"),
   ("不動產放款集中度","銀行總放款中不動產相關貸款的占比，金管會設有警戒上限。"),
   ("DBR（無擔保負債比）","信用卡、信貸等無擔保債務相對月收入的倍數，金管會原則上限 22 倍。"),
   ("DSR（總費用支出比）","含房貸在內所有債務的每月還款佔月收入比率，銀行評估還款能力的指標。")]),
"financing-data.html":dict(accent="#0369a1", lead=None, body=None, faqs=None,  # 只補 definedterm
 terms=[("DBR（無擔保負債比）","信用卡、信貸等無擔保債務相對月收入倍數，金管會原則上限 22 倍。"),
   ("DSR（總費用支出比）","含房貸所有債務月付佔月收入比率，銀行評估還款能力。"),
   ("聯徵","金融聯合徵信中心，記錄個人信用與授信查詢；短期多筆查詢會影響信用評分。"),
   ("售後回租成數","售後回租可取得的資金相對不動產市值的比例，常見約 7–9 成、依個案而定。")]),
"lvr-observatory.html":dict(accent="#2563EB",
 lead="想查台北、新北、台中、桃園的成屋成交行情？看實價登錄即時觀察。",
 body="本頁整理內政部不動產實價登錄近期成交的單價中位、總價中位與屋齡，每月自動更新。數字為區域中位數、僅供參考，非投資建議；實際成交依個案而定。",
 faqs=[("實價登錄是什麼？","內政部要求不動產成交後申報實際價格並公開的制度，可查區域真實成交行情，避免資訊不對稱。"),
   ("單價中位數和平均數差在哪？","中位數是把成交案件由低到高排序取正中間值，較不受極端高價或低價拉動，比平均數更能反映一般行情。"),
   ("查到行情後想活化資產怎麼辦？","名下有房可評估售後回租（過戶＋簽租約續住＋可依約買回）、二胎或貸款整合等方向取得資金；是否適合依個案評估，本公司非金融機構。")],
 terms=[("實價登錄","內政部公開的不動產實際成交價格登錄資料，可查區域行情。"),
   ("單價中位數","成交單價由低到高排序的中間值，較不受極端值影響。"),
   ("總價中位數","成交總價的中位數，反映該區一般成交總價水準。")]),
"lvr-presale.html":dict(accent="#F59E0B",
 lead="想看雙北、台中、桃園的預售屋成交單價？看預售實價觀察。",
 body="本頁整理內政部實價登錄的預售屋成交單價，每月更新。預售屋為興建中、交屋有時間差，價格與成屋脈絡不同；數字為區域參考、非投資建議。",
 faqs=[("預售屋實價登錄看什麼？","看預售案的成交單價與區域分布。預售屋自簽約到交屋有時間差，單價走勢反映建商定價與市場預期，與成屋中古行情口徑不同。"),
   ("預售屋和成屋的價格為什麼不同？","預售屋是未來交屋的新成屋、含建商品牌與規劃溢價，通常單價高於同區中古屋；兩者屬不同市場區隔，比較時要分開看。"),
   ("買預售屋資金不足可以怎麼規劃？","若名下另有不動產，可評估二胎或售後回租（過戶＋簽租約續住＋可依約買回）等合法管道取得資金；依個案與金融機構決定，本公司非金融機構。")],
 terms=[("預售屋","尚未完工、以未來交屋為條件銷售的房屋，實價登錄申報其成交單價。"),
   ("實價登錄","內政部公開的不動產實際成交價格登錄資料。"),
   ("換約","預售屋交屋前將購買權利轉讓他人，需符合相關規定。")]),
"lvr-rental.html":dict(accent="#16A34A",
 lead="想看雙北、台中、桃園的租金行情與投報率？看租金報酬觀察。",
 body="本頁整理實價登錄租賃資料的月租中位與年化報酬率，每月更新。報酬率為概略估算、未扣完整持有成本與空租期，僅供參考、非投資保證。",
 faqs=[("年化報酬率怎麼算？","概略為年租金 ÷ 房屋總價。這是「總報酬」，未扣房屋稅、地價稅、管理費、修繕與空租期；扣掉後的「淨報酬」會更低，評估時要一起看。"),
   ("租金報酬率多少算合理？","台灣都會區住宅總投報常見約 1.5–2.5%、因地段與屋況差異大，本頁數字僅供參考；報酬偏低時要連同增值性與資金成本一起評估。"),
   ("名下房子想出租或變現怎麼安排？","可評估包租代管協助出租收租，或以售後回租（過戶＋簽租約續住＋可依約買回）、二胎等方式活化資產；依個案評估，本公司非金融機構。")],
 terms=[("年化報酬率","年租金相對房屋總價的比率，未扣持有成本前的概略報酬。"),
   ("月租中位數","區域住宅月租金的中位數，較不受極端值影響。"),
   ("淨報酬","年租金扣除稅費、管理、修繕與空租期等持有成本後的實際報酬。")]),
}

def card(accent,lead,body):
    return (f'<div id="quick-answer" style="max-width:760px;margin:18px auto 0;padding:20px 22px;background:#f6f5f3;border:1px solid #e3e3e6;border-left:3px solid {accent};border-radius:8px">\n'
     f'  <div style="font-size:12px;font-weight:700;color:{accent};letter-spacing:.18em;margin-bottom:8px">快速答案</div>\n'
     f'  <p style="font-size:15.5px;line-height:1.8;color:#1d1d1f;margin:0">{"<strong>"+esc(lead)+"</strong>"+esc(body)}</p>\n</div>\n')
def faq_block(faqs):
    its="".join(f'  <div style="border:1px solid #e7e0d3;border-radius:8px;padding:16px 20px;margin-bottom:10px;background:#fff"><h3 style="font-size:15.5px;font-weight:700;color:#1d1d1f;margin:0 0 8px">{esc(q)}</h3><p style="font-size:14px;line-height:1.85;color:#515154;margin:0">{esc(a)}</p></div>\n' for q,a in faqs)
    return f'<section style="max-width:760px;margin:28px auto 0;padding:0 16px"><h2 style="font-size:20px;font-weight:700;color:#1d1d1f;margin:0 0 14px">常見問題</h2>\n{its}</section>\n'
def gloss_block(terms):
    its="".join(f'    <div style="border-left:2px solid #d2d2d7;padding:7px 0 7px 16px;margin-bottom:8px"><strong style="color:#1d1d1f;font-size:14.5px">{esc(t)}</strong><span style="color:#6e6e73;font-size:13.5px;line-height:1.85"> — {esc(d)}</span></div>\n' for t,d in terms)
    return f'<section style="max-width:760px;margin:28px auto 0;padding:0 16px"><h2 style="font-size:20px;font-weight:700;color:#1d1d1f;margin:0 0 14px">名詞解釋</h2>\n{its}</section>\n'

for fn,c in P.items():
    s=open(fn,encoding="utf-8").read()
    add_html=""; schemas=[]
    if c.get("lead") and 'id="quick-answer"' not in s:
        add_html+=card(c["accent"],c["lead"],c["body"])
    if c.get("faqs") and 'FAQPage' not in s:
        add_html+=faq_block(c["faqs"])
        schemas.append({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in c["faqs"]]})
    if c.get("terms") and 'DefinedTerm' not in s:
        add_html+=gloss_block(c["terms"])
        schemas.append({"@context":"https://schema.org","@type":"DefinedTermSet","name":"名詞解釋","hasDefinedTerm":[{"@type":"DefinedTerm","name":t,"description":d} for t,d in c["terms"]]})
    if not add_html: print("無新增",fn); continue
    anchor='<div data-include="line-qr"></div>' if '<div data-include="line-qr"></div>' in s else '<div data-include="footer"></div>'
    s=s.replace(anchor, add_html+anchor,1) if anchor in s else s.replace('</body>',add_html+'</body>',1)
    for sch in schemas:
        k=s.rfind('</head>'); s=s[:k]+'<script type="application/ld+json">\n'+json.dumps(sch,ensure_ascii=False)+'\n</script>\n'+s[k:]
    open(fn,"w",encoding="utf-8").write(s)
    print(f"✅ {fn}: 答案卡{'✓' if c.get('lead') else '-'} FAQ{'✓' if c.get('faqs') else '-'} 名詞{'✓' if c.get('terms') else '-'}")
print("done")
