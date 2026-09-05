# -*- coding: utf-8 -*-
"""AEO 區塊產生器 — lvr 三頁（observatory / presale / rental）

鐵則（memory feedback_faq_schema_same_source）：FAQPage / DefinedTermSet 的 schema
與可見文字必須「同一份資料」生成，本模組是唯一來源；改任何字都要重送 /媽祖把關。
注入六信號：faq、speakable、definedterm、breadcrumb、answercard(#quick-answer)、dateModified。
文案版本：2026-07-06 媽祖批核（observatory 快速答案修正句已套用、經複驗）。
"""
import json

SITE = "https://cx468.com.tw"

PAGES = {
    "observatory": {
        "url": f"{SITE}/lvr-observatory.html",
        "title": "實價登錄觀察室 2026｜北中桃四縣市房價追蹤",
        "crumb": "實價登錄觀察室",
        "quick": (
            "這一頁在追蹤什麼？",
            "台北、新北、台中、桃園四縣市各行政區的實價登錄「正常住宅」成交：單價中位數、"
            "年增率與行政區排名，資料來自內政部開放資料，每月 2、12、22 日自動更新。"
            "實價登錄公告有約 30–50 天的申報延遲，判讀行情以 90／180 天窗較穩。"
        ),
        "faqs": [
            ("實價登錄觀察室的資料多久更新一次？",
             "內政部每月 1、11、21 日公告新資料，本站於每月 2、12、22 日自動同步重建，"
             "頁首的「更新於」時間會隨每次重建自動更新。"),
            ("為什麼最近 30 天的時間窗常顯示無資料或筆數很少？",
             "實價登錄從成交到公告約有 30–50 天的申報與作業延遲，最近一至兩個月的筆數會"
             "系統性偏低，屬正常現象，不代表市場急凍。"),
            ("單價中位數和平均單價有什麼不同？",
             "中位數取排序後的中間值，不會被少數豪宅或極端低價拉動，更能代表一般成交的"
             "行情水準；本站排名一律採用中位數。"),
            ("這些數字可以直接當成我家的房價嗎？",
             "不行。行政區中位數反映整區樣本，個別物件的屋齡、樓層、臨路與屋況差異很大；"
             "實際估值與可貸條件依個案評估，本公司非金融機構，最終核貸由金融機構決定。"),
        ],
        "terms": [
            ("實價登錄", "內政部不動產交易實際資訊制度，買賣移轉後 30 日內申報登錄，供大眾查詢實際成交價格。"),
            ("正常住宅", "本站清洗規則下的住宅樣本：限房地交易、主要用途含「住」、排除親友員工等關係人與特殊交易、排除極端單價。"),
            ("單價中位數", "把統計窗內的成交依每坪單價排序取中間值，比平均數更不受豪宅或極端值影響。"),
            ("YoY 年增率", "與去年同期相同統計窗的單價中位數相比的變動幅度。"),
            ("時間窗", "以資料日回推 30、90、180 或 365 天的取樣範圍；窗越短越即時，但樣本越少越容易波動。"),
            ("每旬增量資料包（mini-package）", "內政部每旬發布的最新 10 天增量資料包，本站以交易編號去重後併入季度資料。"),
        ],
    },
    "presale": {
        "url": f"{SITE}/lvr-presale.html",
        "title": "預售屋觀察｜雙北台中桃園預售實價追蹤",
        "crumb": "預售屋觀察",
        "quick": (
            "這一頁在追蹤什麼？",
            "台北、新北、台中、桃園四縣市的預售屋實價登錄：各行政區預售單價中位數與排名，"
            "已排除解約案件，資料來自內政部開放資料，每月 2、12、22 日自動更新。"
            "預售登錄的是簽約價，交屋在未來，與成屋行情比較時要注意口徑不同。"
        ),
        "faqs": [
            ("預售屋實價登錄和成屋登錄有什麼不同？",
             "預售屋自 2021 年 7 月起納入即時申報，建案簽約後 30 日內就要登錄，統計的是"
             "「簽約價」；成屋登錄的則是所有權移轉時點的成交價，兩者時間基準不同。"),
            ("為什麼預售單價通常比中古屋高？",
             "預售價格反映新建案的營建成本、公設規劃與未來交屋時點的預期，付款結構也與"
             "成屋不同；直接相減會高估價差，比較時應以同區段、同類型產品為基準。"),
            ("預售的數字可以拿來議價嗎？",
             "可以作為同區新案的行情參考，但各建案的基地條件、樓層、面向與附帶項目差異"
             "很大，本頁資料僅供市場觀察參考，非投資建議。"),
        ],
        "terms": [
            ("預售屋", "尚未完工即銷售的建案，簽約後 30 日內須申報實價登錄，登錄價為簽約價。"),
            ("解除契約", "簽約後解約的預售案件；本頁排名已排除標註解除契約的紀錄，避免重複與失真。"),
            ("單價中位數", "把統計窗內的成交依每坪單價排序取中間值，比平均數更不受極端值影響。"),
            ("建坪", "登錄面積換算的建物坪數，含主建物、附屬建物與公共設施的申報面積。"),
        ],
    },
    "rental": {
        "url": f"{SITE}/lvr-rental.html",
        "title": "租金報酬觀察｜雙北台中桃園月租與年化報酬",
        "crumb": "租金報酬觀察",
        "quick": (
            "這一頁在追蹤什麼？",
            "台北、新北、台中、桃園四縣市的租賃實價登錄：各行政區月租中位數，並以"
            "「年租金中位 ÷ 買賣單價中位」估算年化報酬率作為參考。租賃登錄樣本以"
            "租賃住宅服務業申報為主，與街頭開價存在結構差異，數字僅供參考估算。"
        ),
        "faqs": [
            ("租屋實價登錄涵蓋哪些資料？",
             "2021 年 7 月起，包租代管與租賃住宅服務業經手的租賃案件須申報實價登錄；"
             "一般房東自行出租的物件多數不在其中，因此樣本偏向機構管理型物件。"),
            ("月租中位數為什麼和我看到的開價差很多？",
             "登錄的是實際成交租金，市場開價通常高於成交價；加上各區樣本的房型結構"
             "（整層住家與套房比例）不同，中位數與個別物件開價會有落差。"),
            ("年化報酬率是怎麼算的？",
             "以同一行政區「年租金中位數 ÷ 買賣單價中位數」估算，未扣持有稅費、修繕"
             "與空置期，屬於毛報酬概念，供參考估算，並非投報承諾。"),
        ],
        "terms": [
            ("租賃實價登錄", "2021 年 7 月起由租賃住宅服務業（含包租代管）申報的成交租金資料。"),
            ("月租中位數", "統計窗內成交月租依金額排序取中間值，較不受豪宅租金或極端值影響。"),
            ("年化報酬率", "年租金中位數除以同區買賣單價中位數的毛報酬估算，未扣稅費修繕與空置。"),
            ("樣本少", "該行政區統計窗內筆數低於門檻，中位數易受單筆交易影響，判讀需保守。"),
        ],
    },
}


def head_jsonld(page_key: str, date_iso: str) -> str:
    """BreadcrumbList + WebPage(dateModified/speakable) + FAQPage + DefinedTermSet"""
    p = PAGES[page_key]
    blocks = [
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首頁", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": p["crumb"], "item": p["url"]},
        ]},
        {"@context": "https://schema.org", "@type": "WebPage", "@id": p["url"], "url": p["url"],
         "name": p["title"], "dateModified": date_iso, "inLanguage": "zh-TW",
         "speakable": {"@type": "SpeakableSpecification", "cssSelector": ["#quick-answer"]}},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faqs"]]},
        {"@context": "https://schema.org", "@type": "DefinedTermSet",
         "name": f"{p['crumb']}名詞解釋",
         "hasDefinedTerm": [{"@type": "DefinedTerm", "name": t, "description": d}
                            for t, d in p["terms"]]},
    ]
    return "\n".join(
        '<script type="application/ld+json">\n' + json.dumps(b, ensure_ascii=False) + "\n</script>"
        for b in blocks)


def quick_answer_html(page_key: str) -> str:
    head, text = PAGES[page_key]["quick"]
    return (f'<div id="quick-answer" class="notes" style="margin:0 0 24px;'
            f'border-left:3px solid #c8102e">\n'
            f'  <h4>快速答案｜{head}</h4>\n  <p style="margin:0">{text}</p>\n</div>')


def faq_terms_html(page_key: str) -> str:
    p = PAGES[page_key]
    terms_li = "\n".join(f"      <li><b>{t}</b>：{d}</li>" for t, d in p["terms"])
    faq_items = "\n".join(
        f'    <h4 style="margin-top:14px">{q}</h4>\n    <p style="margin:0">{a}</p>'
        for q, a in p["faqs"])
    return f"""  <div class="section-title">名詞解釋</div>
  <div class="notes">
    <ul>
{terms_li}
    </ul>
  </div>

  <div class="section-title">常見問題</div>
  <div class="notes">
{faq_items}
  </div>
"""


# ---- Better 版型（2026-09-05）：字仍取自 PAGES（與 head JSON-LD 同源），只換外層標記 ----
# 標記與 build_observatory.py 內嵌版逐字相同；observatory 仍用自己的內嵌版，這兩個 helper 給 build_extras.py 用。

def quick_answer_bt_html(page_key: str) -> str:
    head, text = PAGES[page_key]["quick"]
    return (f'<div id="quick-answer" class="bt-card bt-qa">\n'
            f'  <h4>快速答案｜{head}</h4>\n  <p style="margin:0">{text}</p>\n</div>')


def faq_terms_bt_html(page_key: str) -> str:
    p = PAGES[page_key]
    terms_html = "\n".join(
        f'      <div class="bt-term"><strong>{t}</strong><span>：{d}</span></div>'
        for t, d in p["terms"])
    faq_html = "\n".join(
        f'    <details{" open" if i == 0 else ""}>\n'
        f'      <summary><h3>{q}</h3></summary>\n'
        f'      <p>{a}</p>\n'
        f'    </details>'
        for i, (q, a) in enumerate(p["faqs"]))
    return f"""<!-- 3. 名詞解釋（與 DefinedTermSet JSON-LD 同源） -->
<section class="bt-sec">
  <div class="bt-narrow">
    <h2 class="bt-h2">名詞解釋</h2>
    <div class="bt-terms">
{terms_html}
    </div>
  </div>
</section>

<!-- 4. FAQ（與 FAQPage JSON-LD 逐字同源） -->
<section class="bt-faq bt-sec">
  <div class="bt-narrow">
    <h2 class="bt-h2 bt-center">常見問題</h2>

{faq_html}
  </div>
</section>
"""
