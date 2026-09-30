#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""topic-a/b/c/d 快速答案卡＋FAQ（前 3 題）＋名詞解釋 的同源產生器——冪等、數字建置時讀 cx_data.json。

怎麼重跑（repo 根目錄）：
  python3 scripts/_b1_aeo_topics.py                  # 讀 ./cx_data.json，原地更新 topic-a～d
  python3 scripts/_b1_aeo_topics.py --data PATH      # 改讀指定資料檔（測試中止用暫存複本）
  跑完 git diff 檢查；commit 前跑 update_schema_datemod.py＋update_sitemap_lastmod.py。

冪等：只原地替換既有區塊，不插入。區塊定位——
  答案卡＝#quick-answer 內的 <p>＋<ul>；FAQ＝題目符合下方樣板的那一個 <details> 與 FAQPage JSON-LD 同一題
  （數字位置當萬用字元比對，所以舊值、新值都認得）；名詞解釋＝.bt-terms 內容＋DefinedTermSet JSON-LD。
  add_faq_items.py 加的第 4 題以後不歸本檔管、不會被動到。可見文字與 schema 由同一份字串生成。

讀哪些欄位：cx_data.json → indicators[] 以 code 查，取 value／updated／note：
  A01–A05、B01、B04、B05、C01–C04、D01–D04（value 當數字，updated 當日期錨；
  累計型 B01/B04/C03/C04 另驗 note 含「前N月」、B05 驗 note 以「台北市」開頭、C02 以「全國」開頭、
  A05 驗 note 含「五大銀」與「占新承做」；C03/C04 大小決定「使照高於建照」或反向句，相等中止）。
  非數字敘述（B02「量縮價穩」、B03「預售趨緩」）cx_data 無對應欄位，維持原句與原日期。

讀不到會中止：檔案讀不到、指標缺、欄位空、數值格式／單位不符、敘述前提不成立（見 PINS）、
  頁面區塊定位不到或不唯一 → 印原因、exit 1，四頁一律不寫入（不退回寫死值、不留空）。
"""
import argparse, html, json, re, string, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class Abort(Exception):
    pass


# ── 資料讀取：缺一律中止 ────────────────────────────────────────────────
def load_values(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        inds = {i["code"]: i for i in data["indicators"]}
    except Exception as e:
        raise Abort(f"讀不到 {path}：{e!r}")

    def ind(code):
        i = inds.get(code)
        if not i:
            raise Abort(f"cx_data 缺指標 {code}")
        for k in ("value", "updated", "note"):
            if not str(i.get(k) or "").strip():
                raise Abort(f"cx_data {code}.{k} 缺值")
        return i

    def num(code, pat):  # value 必須完全符合格式（含單位），回傳數字部分
        m = re.fullmatch(pat, ind(code)["value"])
        if not m:
            raise Abort(f"cx_data {code}.value={ind(code)['value']!r} 不符格式 {pat}")
        return m.group(1)

    def per(code):  # 期別原樣：2026-08 / 2026-Q2
        u = ind(code)["updated"]
        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2]|Q[1-4])", u):
            raise Abort(f"cx_data {code}.updated={u!r} 不是 YYYY-MM 或 YYYY-Qn")
        return u

    def ym(code):  # 2026 年 8 月
        u = per(code)
        if "Q" in u:
            raise Abort(f"cx_data {code}.updated={u!r} 預期為月資料")
        return f"{u[:4]} 年 {int(u[5:])} 月"

    def ytd(code):  # 累計值：2026 年前 8 月（note 必須寫明前N月）
        u = per(code)
        if "Q" in u or f"前{int(u[5:])}月" not in ind(code)["note"]:
            raise Abort(f"cx_data {code} 不是前{u[5:]}月累計（note={ind(code)['note']!r}）")
        return f"{u[:4]} 年前 {int(u[5:])} 月"

    PCT, CNT = r"(\d+\.\d+%)", r"(\d{1,3}(?:,\d{3})+|\d+)"
    v = dict(
        a01=num("A01", PCT), a01_ym=ym("A01"),
        a02=num("A02", PCT), a02_p=per("A02"),
        a03=num("A03", CNT + r"億/月"), a03_p=per("A03"),
        a04=num("A04", PCT), a04_p=per("A04"), a04_ym=ym("A04"),
        a05=num("A05", r"(\d+\.\d+)%"), a05_p=per("A05"),
        b01=num("B01", CNT + "棟"), b01_ytd=ytd("B01"),
        b04=num("B04", CNT + "棟"), b04_ytd=ytd("B04"),
        b05=num("B05", r"(\d+\.\d+)倍"), b05_p=per("B05"),
        c01=num("C01", PCT), c01_p=per("C01"),
        c02=num("C02", r"(\d+\.\d+)倍"), c02_p=per("C02"),
        c03=num("C03", CNT + "戶"), c03_ytd=ytd("C03"),
        c04=num("C04", CNT + "戶"), c04_ytd=ytd("C04"),
        d01=num("D01", PCT), d01_p=per("D01"), d01_ym=ym("D01"),
        d02=num("D02", r"(\d+\.\d+)"), d02_p=per("D02"),
        d03=num("D03", CNT + "點"), d03_p=per("D03"),
        d04=num("D04", PCT), d04_p=per("D04"), d04_ym=ym("D04"),
    )
    # 敘述前提（PINS）：句子裡寫死的判斷只在核定當時的資料狀態下成立，資料一變就中止、請人改句，不自動編
    pins = [
        (per("A01") == "2024-03", "A01 答案卡「2024-03 升到此後凍漲」：央行已再調整，句子要人工改寫"),
        (float(v["a02"][:-1]) >= 2, "A02 答案卡「已站上 2%」：房貸利率已跌破 2%"),
        (float(v["c01"][:-1]) <= 0.08, "C01「目前極低／偏低」係 0.08% 時核定：逾放比升破 0.08% 要媽祖重審"),
        (ind("B05")["note"].startswith(f"台北市{v['b05']}倍"), "B05 value 已不是台北市數字（note 開頭不符）"),
        (ind("C02")["note"].startswith(f"全國{v['c02']}倍"), "C02 value 已不是全國數字（note 開頭不符）"),
        ("Q" not in v["a05_p"] and all(k in ind("A05")["note"] for k in ("五大銀", "占新承做")),
         "A05 已不是「五大銀新承做占比」月資料（note／updated 不符），答案卡定義句要重寫"),
        (v["c03_ytd"] == v["c04_ytd"], "C03／C04 累計期別不同，不能並列「建照 vs 使照」"),
        (v["c03"] != v["c04"], "C03 與 C04 相等，無核定句可用"),
    ]
    for ok, why in pins:
        if not ok:
            raise Abort(f"敘述前提不成立——{why}")
    # C 答案卡第 4 項：大小關係決定用哪一句（兩句皆媽祖 2026-09-30 核定）
    v["c34_rel"] = ("使照高於建照，完工交屋量超過新核發建照量，"
                    if int(v["c04"].replace(",", "")) > int(v["c03"].replace(",", ""))
                    else "建照高於使照，新核發建照量超過完工交屋量，")
    return v


# ── 內容樣板：{欄位} 由 load_values() 填入；其餘字句為已核定原句 ──────────────────
CONTENT = {
"topic-a.html": {
  "termset_name": "房貸金融指標名詞解釋",
  "qa_lead": "想知道「銀行願不願意放款、利率往哪走」，先看這 5 個房貸金融面指標。",
  "qa_body": "A 系列追蹤央行政策利率、實際房貸利率、新增房貸量、不動產放款集中度與新青安占比，是研判台灣房貸授信環境鬆緊的第一道訊號。",
  "qa_bullets": [
    ("央行重貼現率 {a01}", "政策基準利率，2024-03 升到此後凍漲，定錨整體利率走向。"),
    ("房貸利率 {a02}（{a02_p}）", "銀行實際核貸的加權平均，已站上 2%，直接影響每月月付。"),
    ("新增房貸 {a03} 億/月（{a03_p}）", "反映市場購屋需求與信用擴張的強度。"),
    ("不動產放款集中度 {a04}（{a04_p}）", "銀行對房市的曝險程度，金管會設有警戒上限。"),
    ("新青安占比 {a05}%（{a05_p}）", "五大銀行新承做房貸中新青安撥貸的占比，屬政策補貼房貸的背景指標，隨新舊方案交接而變動。舊方案（青安 2.0）申辦期間已於 2026-07-31 屆期，青安 3.0 自 2026-08-01 起受理申貸、至 2029-07-31 止，新增年齡、借款人本人年所得與購屋總價三項資格條件（財政部國庫署民國 115 年 7 月公告）。"),
  ],
  "faqs": [
    ("央行重貼現率跟我的房貸利率有什麼關係？",
     "央行重貼現率是政策基準利率（{a01_ym}起為 {a01}），決定銀行資金成本，房貸利率通常隨它連動。央行升降息會牽動未來月付，但實際房貸利率仍由各銀行依個案核定。"),
    ("「不動產放款集中度」過高代表什麼？",
     "它是銀行總放款中不動產貸款的占比（{a04_ym}約 {a04}）。比率過高代表銀行體系對房市曝險偏高，金管會設有警戒上限，可能促使銀行收緊房貸條件或降低成數。"),
    ("新青安占比變動，對首購族有什麼影響？",
     "新青安（青安 2.0）申辦期間已於 2026 年 7 月 31 日屆期，占比隨新舊方案交接而變動；青安 3.0 自 2026 年 8 月 1 日起受理申貸，申辦期間至 2029 年 7 月 31 日止（民國 115 年 8 月 1 日至 118 年 7 月 31 日），撥款日至遲不得逾 2029 年 10 月 31 日（民國 118 年 10 月 31 日）。依財政部國庫署民國 115 年 7 月公告之貸款原則，新制新增三項申貸資格條件：申貸時未滿 50 歲（以向銀行申請日為準）、借款人本人年所得總額不逾 200 萬元（以借款人本人所得計）、購屋鑑價或買賣總價取高者不逾臺北市 3,500 萬元／新北市及新竹縣（市）2,500 萬元／其他縣（市）2,000 萬元；利息補貼自撥貸日起 3 年內最高，滿 3 年後逐年遞減，補貼期滿後第 4 年（撥貸滿 6 年後）起回復原貸款利率。以上為當年度（民國 115 年）公告內容，日後容有修正，實際資格與條件以財政部國庫署當期公告及承辦公股銀行審核為準。對首購族而言，能否申請、額度與補貼幅度都與舊制不同，建議依自身年齡、所得與購屋總價重新試算負擔，並比較其他可行方案。本公司非金融機構、非本項政策貸款之承辦單位，實際貸款條件依個案與銀行而定，最終核貸由金融機構決定。"),
  ],
  "terms": [
    ("央行重貼現率", "中央銀行對銀行融通資金的基準利率，是房貸利率的政策定錨。"),
    ("不動產放款集中度", "銀行總放款中不動產相關貸款的占比，金管會設有警戒上限。"),
    ("新青安貸款", "政府「青年安心成家購屋優惠貸款」政策性房貸方案，由公股行庫受理；2026 年 8 月起適用青安 3.0，申貸資格新增年齡、借款人本人年所得與購屋總價上限。"),
    ("選擇性信用管制", "央行針對特定對象或區域調整貸款成數與條件的工具，俗稱限貸令。"),
  ],
},
"topic-b.html": {
  "termset_name": "房市量價指標名詞解釋",
  "qa_lead": "想知道「現在房市是熱還是冷、價格撐不撐得住」，看這組量價指標。",
  "qa_body": "B 系列追蹤買賣移轉棟數、信義與國泰房價指數、六都移轉與房價所得比，量（成交）與價（房價）一起看，才不會被單一數字誤導。",
  "qa_bullets": [
    ("買賣移轉 {b01} 棟（{b01_ytd}）", "全國成交量，量縮通常領先價格鬆動。"),
    ("六都移轉 {b04} 棟（{b04_ytd}）", "六大都會成交量，占全國多數。"),
    ("信義房價指數 量縮價穩（2026-Q1）", "以純住中古屋為主，目前量縮但價格緩穩。"),
    ("國泰房價指數 預售趨緩（2026-Q1）", "含預售與新成屋，預售市場轉趨保守。"),
    ("台北市房價所得比 {b05} 倍（{b05_p}）", "房價約等於 {b05} 年家庭可支配所得，負擔概略指標。"),
  ],
  "faqs": [
    ("買賣移轉棟數下降，代表房價要跌嗎？",
     "不必然。移轉棟數（{b01_ytd}共 {b01} 棟）是成交量，量縮通常領先價格鬆動，但價格還受利率、供給與政策影響。量與價要一起看，不宜用單一數字判斷。"),
    ("信義和國泰房價指數有什麼不同？",
     "信義指數以純住宅中古屋為主（2026 年第 1 季量縮價穩）；國泰指數涵蓋預售與新成屋（2026 年第 1 季預售趨緩）。兩者編製口徑不同，分別反映成屋與預售市場。"),
    ("房價所得比 {b05} 倍是什麼意思？",
     "指房價約等於家庭 {b05} 年的可支配所得（台北市，{b05_p}）。數字越高代表購屋負擔越重，是衡量房市可負擔性的常用指標之一。"),
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
    ("房貸逾放比 {c01}（{c01_p}）", "房貸違約比率，目前極低，銀行資產品質良好。"),
    ("房價所得比 {c02} 倍（{c02_p}）", "全國買房負擔倍數，偏高代表可負擔性吃緊。"),
    ("建照核發 {c03} 戶（{c03_ytd}）", "未來新增供給的領先指標。"),
    ("建照 vs 使照 {c03} vs {c04} 戶（{c04_ytd}）", "{c34_rel}兩者落差反映建商推案與交屋節奏。"),
  ],
  "faqs": [
    ("房貸逾放比 {c01} 算高還是低？",
     "偏低。逾放比是房貸逾期放款金額占房貸餘額的比率，{c01}（{c01_p}）代表整體房貸違約極少、銀行資產品質良好。這個數字往上走，才是風險升高的訊號。"),
    ("房價所得比 {c02} 倍代表什麼？",
     "全國房價約等於 {c02} 年的家庭可支配所得（{c02_p}）。比率偏高代表購屋負擔吃緊，是觀察房市可負擔性與泡沫風險的指標之一。"),
    ("建照核發數量能預測房市嗎？",
     "建照是未來房屋供給的領先指標（{c03_ytd}核發 {c03} 戶）。核發大增預示未來推案量上升，可能影響供需與價格，但從核發到完工有時間落差，需搭配其他指標一起看。"),
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
    ("美十年期公債殖利率 {d01}（{d01_p}）", "全球利率定錨，牽動台灣資金成本與長天期利率。"),
    ("美元台幣匯率 {d02}（{d02_p}）", "影響資金流向與輸入性通膨。"),
    ("台股加權指數 {d03} 點（{d03_p}）", "資產與財富效果，間接影響購屋力。"),
    ("台灣 CPI {d04}（{d04_p}）", "通膨水準，是央行升降息的關鍵依據。"),
  ],
  "faqs": [
    ("美國公債殖利率，關台灣房貸什麼事？",
     "美十年期公債殖利率（{d01_ym}約 {d01}）被視為全球利率定錨，會牽動台灣的資金成本與長天期利率，間接影響房貸利率走向與央行的政策空間。"),
    ("CPI（消費者物價指數）和房貸利率有關係嗎？",
     "有。CPI 反映通膨（{d04_ym}為 {d04}），是央行決定升降息的關鍵依據；通膨升溫常使央行傾向升息，進而牽動房貸利率與每月月付。"),
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

# 改過題目的 FAQ：新題目 → 舊題目（頁面還是舊題時也定位得到）
FORMER_Q = {"新青安占比變動，對首購族有什麼影響？": "新青安占比下滑，對首購族有什麼影響？"}

def esc(s): return html.escape(s, quote=True)

def pattern(tpl):
    """樣板 → 比對用 regex：{欄位} 當萬用字元，舊值新值都認得（冪等定位的關鍵）。"""
    p = "".join(re.escape(lit) + (".+?" if f else "") for lit, f, _, _ in string.Formatter().parse(tpl))
    return f"(?:{p}|{re.escape(FORMER_Q[tpl])})" if tpl in FORMER_Q else p

def one(regex, s, what):
    ms = list(re.finditer(regex, s, re.S))
    if len(ms) != 1:
        raise Abort(f"{what} 命中 {len(ms)} 次（預期 1）")
    return ms[0]

JSONLD = r'(<script type="application/ld\+json">\n)(.*?)(\n</script>)'
DETAILS = r'(<details(?: open)?>\n      <summary><h3>)(.*?)(</h3></summary>\n      <p>)(.*?)(</p>\n    </details>)'

def jsonld_block(s, typ, fn):
    hits = [m for m in re.finditer(JSONLD, s, re.S) if f'"@type": "{typ}"' in m.group(2)]
    if len(hits) != 1:
        raise Abort(f"{fn} {typ} JSON-LD 命中 {len(hits)} 次（預期 1）")
    m = hits[0]
    data = json.loads(m.group(2))
    if json.dumps(data, ensure_ascii=False, indent=1) != m.group(2):
        raise Abort(f"{fn} {typ} JSON-LD 重新序列化會變動格式，拒絕改寫")
    return m, data

def render(fn, c, v, log):
    s = (ROOT / fn).read_text(encoding="utf-8")
    fill = lambda t: t.format(**v)

    # 1) 答案卡：#quick-answer 內 <p> 與 <ul>
    bullets = [(fill(t), fill(d)) for t, d in c["qa_bullets"]]
    m = one(r'(<div id="quick-answer" class="bt-card bt-qa">\n      <div class="bt-label">快速答案 · QUICK ANSWER</div>\n      )'
            r'<p>.*?</p>\n      <ul>(.*?)</ul>', s, f"{fn} #quick-answer")
    old = re.findall(r"<li><strong>(.*?)</strong>：(.*?)</li>", m.group(2))
    if len(old) != len(bullets):
        raise Abort(f"{fn} 答案卡條目 {len(old)} ≠ 樣板 {len(bullets)}")
    for (ot, od), (nt, nd) in zip(old, bullets):
        if (html.unescape(ot), html.unescape(od)) != (nt, nd):
            log.append((fn, f"{html.unescape(ot)}：{html.unescape(od)}", f"{nt}：{nd}"))
    new = (f'<p><strong>{esc(c["qa_lead"])}</strong>{esc(c["qa_body"])}</p>\n      <ul>'
           + "".join(f"<li><strong>{esc(t)}</strong>：{esc(d)}</li>" for t, d in bullets) + "</ul>")
    s = s[:m.start()] + m.group(1) + new + s[m.end():]

    # 2) FAQ：可見 <details> 與 FAQPage schema 同一題、同一份字串
    sm, faq = jsonld_block(s, "FAQPage", fn)
    for qt, at in c["faqs"]:
        q, a, pat = fill(qt), fill(at), pattern(qt)
        vis = [d for d in re.finditer(DETAILS, s, re.S) if re.fullmatch(pat, html.unescape(d.group(2)))]
        sch = [e for e in faq["mainEntity"] if re.fullmatch(pat, e["name"])]
        if len(vis) != 1 or len(sch) != 1:
            raise Abort(f"{fn} FAQ「{q}」可見 {len(vis)}／schema {len(sch)} 題（預期各 1）")
        d, e = vis[0], sch[0]
        if (html.unescape(d.group(2)), html.unescape(d.group(4))) != (e["name"], e["acceptedAnswer"]["text"]):
            raise Abort(f"{fn} FAQ「{q}」改寫前可見與 schema 已不同源，先人工對齊")
        if (e["name"], e["acceptedAnswer"]["text"]) != (q, a):
            log.append((fn, f"Q {e['name']}｜A {e['acceptedAnswer']['text']}", f"Q {q}｜A {a}"))
        e["name"], e["acceptedAnswer"]["text"] = q, a
        s = s[:d.start()] + d.group(1) + esc(q) + d.group(3) + esc(a) + d.group(5) + s[d.end():]
    sm, _ = jsonld_block(s, "FAQPage", fn)  # 位置可能因可見區改動而位移，重抓
    s = s[:sm.start(2)] + json.dumps(faq, ensure_ascii=False, indent=1) + s[sm.end(2):]

    # 3) 名詞解釋：.bt-terms 與 DefinedTermSet schema
    m = one(r'(<div class="bt-terms">\n)(.*?)(    </div>)', s, f"{fn} .bt-terms")
    items = "".join(f'      <div class="bt-term"><strong>{esc(t)}</strong><span> — {esc(d)}</span></div>\n' for t, d in c["terms"])
    s = s[:m.start(2)] + items + s[m.end(2):]
    tm, ts = jsonld_block(s, "DefinedTermSet", fn)
    ts["name"] = c["termset_name"]
    ts["hasDefinedTerm"] = [{"@type": "DefinedTerm", "name": t, "description": d} for t, d in c["terms"]]
    s = s[:tm.start(2)] + json.dumps(ts, ensure_ascii=False, indent=1) + s[tm.end(2):]
    return s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "cx_data.json"))
    args = ap.parse_args()
    log, out = [], {}
    try:
        v = load_values(args.data)
        for fn, c in CONTENT.items():
            out[fn] = render(fn, c, v, log)
    except Abort as e:
        sys.exit(f"❌ 中止：{e}（四頁皆未寫入）")
    for fn, s in out.items():  # 全部算完才寫，任何一頁失敗都不會半套落地
        p = ROOT / fn
        changed = p.read_text(encoding="utf-8") != s
        if changed:
            p.write_text(s, encoding="utf-8")
        print(f"{'✏️ ' if changed else '＝ '}{fn}")
    for fn, o, n in log:
        print(f"  {fn}｜{o}\n    → {n}")
    print(f"done：{len(log)} 處更動")

if __name__ == "__main__":
    main()
