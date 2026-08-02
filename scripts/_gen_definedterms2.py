#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""definedterm 第二批：23 頁地價稅頁 + en/index.html。
   沿用 _gen_definedterms.py 模式：可見名詞解釋 + DefinedTermSet schema 同源生成，
   插在 line-qr/footer 前、schema 塞 </head> 前。縣市頁帶各自累進起點地價（取自各頁既有內容）。"""
import json, html, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
esc = lambda x: html.escape(x, quote=True)

# 縣市試算頁：(檔名前綴, 縣市名, 累進起點地價字串——與各頁頁面內容一致)
CITIES = [
    ("changhua", "彰化縣", "965,000"),
    ("chiayi-city", "嘉義市", "3,957,000"),
    ("chiayi-county", "嘉義縣", "683,000"),
    ("hsinchu-city", "新竹市", "5,808,000"),
    ("hsinchu-county", "新竹縣", "1,765,000"),
    ("hualien", "花蓮縣", "702,000"),
    ("kaohsiung", "高雄市", "4,032,000"),
    ("miaoli", "苗栗縣", "1,181,000"),
    ("nantou", "南投縣", "672,000"),
    ("new-taipei", "新北市", "7,878,000"),
    ("penghu", "澎湖縣", "410,000"),
    ("pingtung", "屏東縣", "775,000"),
    ("taichung", "台中市", "1,741,000"),
    ("tainan", "台南市", "2,195,000"),
    ("taipei", "台北市", "43,957,000"),
    ("taitung", "台東縣", "463,000"),
    ("taoyuan", "桃園市", "3,439,000"),
    ("yilan", "宜蘭縣", "1,241,000"),
    ("yunlin", "雲林縣", "988,000"),
]
GUIDES = [("new-taipei", "新北市", "7,878,000"), ("taichung", "台中市", "1,741,000"),
          ("taipei", "台北市", "43,957,000"), ("taoyuan", "桃園市", "3,439,000")]

# 年度一律取自 tax-config.json（唯一真實來源）。曾寫死 115-116，害 4 個縣市頁
# 名詞解釋年度與 hero／免責聲明打架（宜蘭 107-108、花蓮 109-110、嘉義縣/台東 113-114）。
_CFG_YEAR = {v['name']: v['year'] for v in
             json.load(open('scripts/tax-config.json', encoding='utf-8'))['cities'].values()}

def city_year(city):
    return _CFG_YEAR[city]

def calc_terms(city, num):
    return [
        ("公告地價", "直轄市或縣市政府每兩年公告一次的地價，是地價稅稅基的計算基礎；未自行申報者，以公告地價的 80% 作為申報地價。"),
        ("申報地價", "土地所有權人申報、作為地價稅課稅基礎的地價；本頁工具可依行政區、地段、地號查詢每平方公尺申報地價。"),
        (f"累進起點地價（{city}）", f"{city} {city_year(city)} 年累進起點地價為 {num} 元；課稅地價總額未超過此數按 10‰ 課徵，超過部分依超過倍數按 15‰～55‰ 累進。"),
        ("自用住宅用地稅率", "土地所有權人或其配偶、直系親屬在該地設有戶籍、無出租或營業使用且符合面積上限者，地價稅適用 2‰ 優惠稅率，須於 9 月 22 日以前主動申請。"),
        ("一般用地累進稅率", "一般用地地價稅採六級累進：未達累進起點地價課 10‰，超過部分依超過倍數適用 15‰、25‰、35‰、45‰、55‰。"),
        ("地價稅開徵期間", "地價稅每年課徵一次，11 月 1 日開徵、繳納期限至 11 月 30 日止；實際稅額以稅捐稽徵機關核定為準。"),
    ]

def guide_terms(city, num):
    return [
        (f"累進起點地價（{city}）", f"計算地價稅級距的基準，每兩年由各縣市重新公告；{city} {city_year(city)} 年為 {num} 元，課稅地價與此數的倍數決定適用稅率級距。"),
        ("課稅地價", "每平方公尺申報地價乘以課稅面積所得的金額，是地價稅的稅基；申報地價通常為公告地價的 80%。"),
        ("累進差額", "累進稅率速算用的扣除額：稅額＝課稅地價 × 適用稅率 － 累進差額，各級距的累進差額依各縣市累進起點地價計算後公告。"),
        ("自用住宅用地稅率", "符合設籍、無出租或營業使用等條件的自用住宅用地，地價稅適用 2‰ 優惠稅率；須於 9 月 22 日以前提出申請，同年 11 月即可適用。"),
        ("地價稅開徵期間", "地價稅每年課徵一次，11 月 1 日開徵、繳納期限至 11 月 30 日止；實際稅額以稅捐稽徵機關核定為準。"),
    ]

EN_TERMS = ("Taiwan Real-Estate Financing Glossary", "Key Terms", [
    ("Sale-and-Leaseback", "An arrangement with three inseparable elements: the owner transfers title to an investor at an agreed price — typically 70–90% of appraised market value, assessed case-by-case — stays in the property under a tenancy agreement signed at closing, and keeps a contractual right to repurchase on agreed terms."),
    ("Contractual Repurchase Right", "The clause in a sale-and-leaseback that preserves the former owner's right to repurchase the property on agreed terms in the future; one of the three inseparable elements, alongside title transfer and the tenancy agreement."),
    ("Debt Consolidation", "Combining unsecured personal loans, credit-card revolving balances, and private borrowings into a single bank mortgage against Taiwan real estate; in past client cases monthly outgoings fell by 30–50%, depending on the property, income documentation, and the receiving bank's criteria."),
    ("Private-to-Bank Refinancing", "Staged refinancing from private lending, which in Taiwan commonly costs 1–2% per month, into regulated bank facilities at annual rates in the 2–3% range, where the borrower and property qualify — market-practice figures, not a promise of any particular outcome."),
    ("Advisory and Matching", "Cheng Xin Leasing is not a bank, not a financial institution, and does not lend money; its role is analysis, structuring advice, and introduction to suitable institutions. All financing decisions are made solely by the financial institutions concerned."),
])

def block(heading, terms):
    items = "".join(
        f'    <div style="border-left:2px solid #d2d2d7;padding:7px 0 7px 16px;margin-bottom:8px">'
        f'<strong style="color:#1d1d1f;font-size:14.5px">{esc(t)}</strong>'
        f'<span style="color:#6e6e73;font-size:13.5px;line-height:1.85"> — {esc(d)}</span></div>\n' for t, d in terms)
    return (f'<section style="max-width:760px;margin:28px auto 0;padding:0 16px">\n'
            f'  <h2 style="font-size:20px;font-weight:700;color:#1d1d1f;margin:0 0 14px">{esc(heading)}</h2>\n{items}</section>\n')

def apply(fn, tsname, heading, terms, anchor_candidates):
    s = open(fn, encoding="utf-8").read()
    if '"DefinedTerm"' in s:
        print("已有,跳過", fn); return False
    sec = block(heading, terms)
    for a in anchor_candidates:
        if a in s:
            s = s.replace(a, sec + a, 1); break
    else:
        s = s.replace('</body>', sec + '</body>', 1)
    sch = {"@context": "https://schema.org", "@type": "DefinedTermSet", "name": tsname,
           "hasDefinedTerm": [{"@type": "DefinedTerm", "name": t, "description": d} for t, d in terms]}
    k = s.rfind('</head>')
    s = s[:k] + '<script type="application/ld+json">\n' + json.dumps(sch, ensure_ascii=False, indent=1) + '\n</script>\n' + s[k:]
    open(fn, "w", encoding="utf-8").write(s)
    print(f"✅ {fn}: +{len(terms)}名詞(可見+schema同源)")
    return True

ANCHORS = ['<div data-include="line-qr"></div>', '<div data-include="footer"></div>']
n = 0
for pre, city, num in CITIES:
    n += apply(f"{pre}-land-value-tax.html", f"{city}地價稅名詞解釋", "名詞解釋", calc_terms(city, num), ANCHORS)
for pre, city, num in GUIDES:
    n += apply(f"{pre}-land-value-tax-guide.html", f"{city}地價稅名詞解釋", "名詞解釋", guide_terms(city, num), ANCHORS)
tsname, heading, terms = EN_TERMS
n += apply("en/index.html", tsname, heading, terms, ['<footer>'])
print("done", n)
