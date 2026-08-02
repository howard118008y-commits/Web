"""
產出 5 精選區「區域百科」頁（中和/永和/板橋/新店/土城）。

定位：客觀區域百科 + SEO / AEO（FAQ schema）/ GEO（geo meta + Place JSON-LD）。
即時房市數字由前端 JS 撈 lvr-data/排名_w180.json + rental_ranking_w180.json，
每月隨 LVR 管線自動更新，頁面本身不存死數字。

執行：python3 scripts/build_area_pages.py
輸出：CX468 根目錄 area-<slug>.html（共 5 檔）
觀察室卡片的超連結由 build_observatory.py 產生（AREA_SLUG map）。
"""

import json
from pathlib import Path
from string import Template

CX468_DIR = Path(__file__).resolve().parent.parent
TODAY = "2026-06-03"
# 沿用站上既有的 Google Maps Embed key（與 contact.html 相同）
GMAP_KEY = "AIzaSyAdXf11vCfYR0YYPcyWS40cISihhR87Kjw"
# 簡化版台灣輪廓 viewBox 0 0 210 320（示意定位用，非測繪精度）
TW_PATH = ("M118,16 C138,26 150,52 156,84 C162,112 170,144 166,178 "
           "C162,208 152,242 138,272 C130,290 120,302 109,298 "
           "C100,294 95,282 89,268 C76,238 62,206 54,172 "
           "C47,142 43,108 52,80 C61,52 78,30 100,18 C106,14 112,13 118,16 Z")


def tw_xy(lat: str, lng: str):
    """經緯度→台灣輪廓 SVG 座標（示意）。"""
    x = 50 + (float(lng) - 120.0) / 2.0 * 115
    y = 20 + (25.3 - float(lat)) / 3.4 * 275
    return round(x, 1), round(y, 1)

# 各區基本資料（slug 與 build_observatory.py 的 AREA_SLUG 必須一致）
AREAS = [
    {
        "town": "中和區", "slug": "zhonghe", "en": "Zhonghe",
        "lat": "24.9930", "lng": "121.5010",
        "desc": "中和區（新北市）區域百科：雙和生活圈、捷運中和新蘆線與環狀線、生活機能與不動產型態，"
                "並附內政部實價登錄近 180 天即時單價、總價與租金行情，每月自動更新。",
        "intro": [
            "中和區位於新北市中部，緊鄰台北市萬華、文山，與永和區合稱「雙和地區」，是新北市人口最稠密的行政區之一，"
            "面積約 20 平方公里、人口約 40 萬。區內商業、住宅與輕工業混合，生活機能成熟、通勤人口眾多。",
            "鋮馨租賃有限公司總部即設於中和區中正路，深耕在地不動產與資金規劃超過 20 年。",
        ],
        "sections": [
            ("生活機能與商圈", [
                "中和擁有四號公園（八二三紀念公園）與國立臺灣圖書館，是雙和重要的綠地與文教核心；"
                "華新街（緬甸街）為知名南洋美食聚落，興南夜市、環球購物中心與多家量販店構成日常採買網絡。",
                "烘爐地南山福德宮是大台北著名的廟宇與夜景據點，假日人潮絡繹不絕。",
            ]),
            ("交通路網", [
                "捷運中和新蘆線（橘線）設有南勢角站、景安站；環狀線（黃線）行經景安、中和、橋和、板新等站，可轉乘多條路線。",
                "主要幹道包含中正路、中山路、員山路、連城路，並透過華中橋、永福橋等橋樑聯絡台北市區。",
            ]),
            ("不動產型態與市場特徵", [
                "中和住宅以中古公寓與華廈為主，屋齡偏高（中位數約 30 年），新建案多來自都市更新與零星重劃。",
                "近年受環狀線通車與都更題材帶動，部分區段價格走升。實際成交行情請見下方即時數字。",
            ]),
        ],
        "schools": "中和學區涵蓋中和國中、漳和國中、自強國中等公立國中，國小有積穗國小、中和國小、員山國小、興南國小等；"
                   "高中職以新北市立中和高中為代表。國立臺灣圖書館坐落區內，是雙和重要的文教資源。",
        "development": [
            ("2020", "環狀線第一階段通車，景安、中和、橋和、板新站啟用，串連板橋、新莊、新店。"),
            ("規劃中", "環狀線南、北環延伸，未來可望進一步擴大軌道路網覆蓋。"),
            ("持續推動", "中和舊市區危老與都市更新案陸續推案，帶動老屋改建。"),
        ],
        "poi": [
            ("醫療", ["衛福部雙和醫院（中正路）", "區域診所與藥局密集"]),
            ("購物賣場", ["家樂福中和店", "Costco 中和店", "環球購物中心中和站"]),
            ("市場夜市", ["興南觀光夜市", "華新街（緬甸街）南洋美食", "中和黃昏市場"]),
            ("公園綠地", ["四號公園（八二三紀念公園）", "錦和運動公園", "員山公園"]),
            ("景點", ["烘爐地南山福德宮（夜景）", "國立臺灣圖書館"]),
        ],
        "faqs": [
            ("中和區屬於哪個生活圈？", "中和與永和合稱「雙和生活圈」，緊鄰台北市，是典型的雙北通勤住宅區。"),
            ("中和區有哪些捷運站？", "捷運中和新蘆線（南勢角、景安）與環狀線（景安、中和、橋和、板新）皆行經中和區。"),
            ("中和區房屋以什麼型態為主？", "以中古公寓與華廈為主，屋齡偏高，新成屋多來自都市更新與重劃案。"),
        ],
    },
    {
        "town": "永和區", "slug": "yonghe", "en": "Yonghe",
        "lat": "25.0078", "lng": "121.5140",
        "desc": "永和區（新北市）區域百科：全臺人口密度最高的行政區、緊鄰台北市、捷運中和新蘆線，"
                "生活機能與不動產特徵，並附實價登錄近 180 天即時單價與租金行情，每月自動更新。",
        "intro": [
            "永和區面積僅約 5.7 平方公里，是臺灣本島面積最小、人口密度最高的行政區之一，與中和合稱雙和。"
            "三面被新店溪環繞，與台北市僅一橋之隔（中正橋、福和橋、永福橋）。",
            "高密度、高度都市化是永和最鮮明的特徵，巷弄密集、生活步調緊湊。",
        ],
        "sections": [
            ("生活機能與商圈", [
                "樂華夜市是永和的代表性商圈，中興街（韓國街）以服飾批發聞名；仁愛公園、永和國父紀念館提供區內少數的開放綠地。",
                "永和亦保留大陳社區等特色聚落，飲食與市集文化豐富。",
            ]),
            ("交通路網", [
                "捷運中和新蘆線設有頂溪站與永安市場站；多座橋樑直通台北公館、古亭一帶，機車與公車通勤普遍。",
            ]),
            ("不動產型態與市場特徵", [
                "永和高密度開發、街廓狹小，住宅以屋齡較高的公寓為主，新建案稀少。",
                "因緊鄰台北蛋黃區、土地供給有限，單價在雙和地區普遍最高。實際成交行情請見下方即時數字。",
            ]),
        ],
        "schools": "永和文教密度高，公立國中有永和國中、福和國中，完全中學永平高中（含國中部）為地方明星；"
                   "國小包括頂溪國小、秀朗國小、永和國小、網溪國小等，其中秀朗國小曾以學生人數眾多聞名。",
        "development": [
            ("2010–2012", "中和新蘆線分段通車，頂溪、永安市場站啟用，往台北古亭、東門更為便捷。"),
            ("持續推動", "因可建土地稀少，發展以危老重建與都市更新為主，新案稀少而搶手。"),
        ],
        "poi": [
            ("醫療", ["天主教耕莘醫院永和分院（中興街）"]),
            ("購物賣場", ["樂華商圈生活採買", "區內超市量販密布"]),
            ("市場夜市", ["樂華觀光夜市", "永和黃昏市場", "中興街韓國街（服飾批發）"]),
            ("公園綠地", ["仁愛公園", "永和公園", "四號公園（跨中永和）"]),
            ("景點", ["世界豆漿大王（永和豆漿意象）", "新店溪河濱自行車道"]),
        ],
        "faqs": [
            ("永和區為什麼房價偏高？", "永和緊鄰台北市、土地稀缺、人口密度全國最高，住宅供給有限，因此單價在雙和地區相對偏高。"),
            ("永和區有捷運嗎？", "有，捷運中和新蘆線設有頂溪站與永安市場站。"),
            ("永和區的房子多是什麼型態？", "多為屋齡較高的公寓，新成屋供給少。"),
        ],
    },
    {
        "town": "板橋區", "slug": "banqiao", "en": "Banqiao",
        "lat": "25.0096", "lng": "121.4590",
        "desc": "板橋區（新北市）區域百科：新北市政經中心、三鐵共構板橋車站、新板特區與江翠重劃區，"
                "生活機能與不動產型態，並附實價登錄近 180 天即時單價與租金行情，每月自動更新。",
        "intro": [
            "板橋區是新北市政府所在地，為全市政治、經濟與交通中心，人口約 55 萬、居各區之冠。",
            "新板特區的崛起讓板橋成為新北最具指標性的商業與居住核心之一。",
        ],
        "sections": [
            ("生活機能與商圈", [
                "新板特區匯聚大遠百、誠品、麗寶百貨與市民廣場，是雙北重要的商業聚落；"
                "林本源園邸（林家花園）、435 藝文特區則保留了板橋的歷史與藝文底蘊。",
                "府中商圈為傳統老城核心，江子翠重劃區則以新興住宅為主。",
            ]),
            ("交通路網", [
                "板橋車站為三鐵共構（高鐵、台鐵、捷運板南線）並結合客運轉運站；環狀線設板橋、板新站，"
                "板南線另有府中、江子翠、新埔站，對外連結四通八達。",
            ]),
            ("不動產型態與市場特徵", [
                "板橋住宅結構多元：新板特區高價豪宅與商辦、江翠重劃區新案、府中老城區中古屋並存。",
                "新板特區單價明顯高於全區平均。實際成交行情請見下方即時數字。",
            ]),
        ],
        "schools": "板橋教育資源充沛，新北市立板橋高中為地方第一志願，另有海山高中、新北高中等；"
                   "公立國中包括江翠國中、中山國中、海山國中、文德國中，國小有板橋國小、莒光國小、新埔國小、後埔國小等，"
                   "江翠與新埔一帶學區尤受家庭青睞。",
        "development": [
            ("2006–2007", "捷運板南線與台鐵、高鐵陸續到位，板橋車站成為三鐵共構交通樞紐。"),
            ("2020", "環狀線通車，板橋、板新站串連新北環狀廊帶。"),
            ("已成形／持續", "新板特區商業豪宅聚落成形；江翠北側重劃區持續開發。"),
        ],
        "poi": [
            ("醫療", ["亞東紀念醫院（醫學中心，南雅南路）"]),
            ("購物百貨", ["板橋大遠百", "誠品生活新板", "麗寶百貨 Mega City", "環球購物中心板橋站"]),
            ("市場", ["黃石市場", "湳興市場", "府中商圈"]),
            ("公園綠地", ["新板市民廣場", "四川公園", "板橋第一運動場", "435 藝文特區"]),
            ("景點", ["林本源園邸（林家花園）", "府中歷史街區"]),
        ],
        "faqs": [
            ("板橋區是新北市的中心嗎？", "是，新北市政府與三鐵共構的板橋車站皆位於板橋區，為全市政經與交通核心。"),
            ("板橋有哪些捷運與車站？", "高鐵／台鐵板橋站、捷運板南線、環狀線皆行經板橋區。"),
            ("新板特區與府中有什麼差別？", "新板特區為新興商業豪宅區，府中則是傳統老城商圈，兩者房屋型態與價位差異明顯。"),
        ],
    },
    {
        "town": "新店區", "slug": "xindian", "en": "Xindian",
        "lat": "24.9678", "lng": "121.5419",
        "desc": "新店區（新北市）區域百科：碧潭風景區、松山新店線與環狀線、央北與十四張重劃區，"
                "生活機能與不動產特徵，並附實價登錄近 180 天即時單價與租金行情，每月自動更新。",
        "intro": [
            "新店區位於新北市南端，面積廣大、多丘陵與水域，新店溪與碧潭是著名地景。",
            "區內涵蓋大坪林、七張、新店、安坑、央北、十四張等次區域，發展型態差異大。",
        ],
        "sections": [
            ("生活機能與商圈", [
                "碧潭風景區與碧潭吊橋是新店代表性景點；大坪林一帶有裕隆城等大型商場，醫療則有慈濟醫院新店院區與耕莘醫院。",
                "央北與十四張為近年的重劃新興住宅區，生活機能持續成形。",
            ]),
            ("交通路網", [
                "捷運松山新店線（綠線）設大坪林、七張、新店區公所、新店等站；環狀線有十四張、秀朗橋站；"
                "安坑輕軌串連安坑地區，並有國道 3 號安坑交流道聯外。",
            ]),
            ("不動產型態與市場特徵", [
                "重劃區（央北、十四張）的新成屋成交，使新店整體屋齡結構與單價中位數波動較大；"
                "大坪林商圈與捷運沿線保值性相對佳。實際成交行情請見下方即時數字。",
            ]),
        ],
        "schools": "新店學區以新店高中、安康高中為代表，公立國中有新店國中、中正國中等；"
                   "國小包括北新國小、大豐國小、復興國小、雙峰國小等，央北與大坪林一帶近年因新住宅湧入、學區需求成長。",
        "development": [
            ("2023", "安坑輕軌通車（K1–K9），改善安坑地區對外交通。"),
            ("2023", "大坪林裕隆城開幕，成為新店新興商業地標。"),
            ("2020", "環狀線十四張、秀朗橋站通車。"),
            ("開發中", "央北重劃區、十四張（中央新村北側）重劃區新案陸續完工。"),
        ],
        "poi": [
            ("醫療", ["台北慈濟醫院（醫學中心，建國路）", "天主教耕莘醫院總院（中正路）"]),
            ("購物賣場", ["裕隆城（大坪林）", "家樂福新店店"]),
            ("市場", ["新店第一公有市場", "大坪林商圈"]),
            ("公園綠地", ["碧潭風景區", "陽光運動公園", "和美山步道"]),
            ("景點", ["碧潭吊橋", "新店渡（人力擺渡）", "銀河洞越嶺步道"]),
        ],
        "faqs": [
            ("新店區有哪些重劃區？", "央北與十四張是新店近年主要的重劃新興住宅區。"),
            ("新店的捷運有哪些？", "松山新店線（綠線）、環狀線，以及串連安坑地區的安坑輕軌。"),
            ("為什麼新店單價中位數變動較大？", "因新成屋與老屋的成交結構變化，會牽動單價中位數，並非單純的漲跌。"),
        ],
    },
    {
        "town": "土城區", "slug": "tucheng", "en": "Tucheng",
        "lat": "24.9722", "lng": "121.4438",
        "desc": "土城區（新北市）區域百科：捷運板南線、土城工業區與頂埔科技園區、承天禪寺桐花季，"
                "生活機能與不動產型態，並附實價登錄近 180 天即時單價與租金行情，每月自動更新。",
        "intro": [
            "土城區位於新北市西南，緊鄰板橋與中和，兼具住宅與產業機能。",
            "承天禪寺與桐花公園是著名景點，每年桐花季吸引大量遊客。",
        ],
        "sections": [
            ("生活機能與商圈", [
                "土城工業區與頂埔科技園區（鴻海集團總部所在地）構成重要的產業基地；"
                "海山捷運商圈、裕民商圈與清水大排綠廊則支撐區內的日常生活與休閒。",
            ]),
            ("交通路網", [
                "捷運板南線設海山、土城、永寧、頂埔站（終點，鄰頂埔科技園區）；"
                "並有國道 3 號土城交流道與台 65 線快速道路聯外。",
            ]),
            ("不動產型態與市場特徵", [
                "土城住宅以住宅大樓與公寓為主，價格相對雙和、板橋親民；",
                "暫緩發展區與工業區轉型題材，為未來的發展想像空間。實際成交行情請見下方即時數字。",
            ]),
        ],
        "schools": "土城以新北市立土城高中、清水高中（完全中學）為主要高中，公立國中有土城國中、清水高中國中部等；"
                   "國小包括土城國小、清水國小、永寧國小、頂埔國小等，頂埔與海山一帶為主要住宅學區。",
        "development": [
            ("2006／2015", "捷運板南線海山、土城、永寧站通車，2015 年延伸頂埔站。"),
            ("已進駐", "頂埔科技園區成形，鴻海集團總部設於土城。"),
            ("規劃中", "暫緩發展區（原彈藥庫一帶）為未來重大開發題材。"),
        ],
        "poi": [
            ("醫療", ["長庚醫療土城醫院（金城路，2019 啟用）"]),
            ("購物賣場", ["家樂福土城店", "裕民商圈"]),
            ("市場", ["土城公有市場", "裕民黃昏市場"]),
            ("公園綠地", ["土城桐花公園", "清水大排綠廊", "媽祖田登山步道"]),
            ("景點", ["承天禪寺", "桐花公園（桐花季）"]),
        ],
        "faqs": [
            ("土城區產業以什麼為主？", "以土城工業區與頂埔科技園區為核心，鴻海集團總部即位於土城。"),
            ("土城有哪些捷運站？", "捷運板南線海山、土城、永寧、頂埔站皆位於土城區。"),
            ("土城房價相對便宜嗎？", "相較雙和與板橋，土城的單價普遍較為親民，實際行情請見頁面即時數字。"),
        ],
    },
]


def render_sections(secs) -> str:
    out = []
    for title, paras in secs:
        out.append(f'  <h2>{title}</h2>')
        for p in paras:
            out.append(f'  <p>{p}</p>')
    return "\n".join(out)


def render_faq_html(faqs) -> str:
    out = ['  <h2>常見問題</h2>']
    for q, a in faqs:
        out.append('  <div class="faq-item">')
        out.append(f'    <h3>{q}</h3>')
        out.append(f'    <p>{a}</p>')
        out.append('  </div>')
    return "\n".join(out)


def render_faq_ld(faqs) -> str:
    import json
    items = [{
        "@type": "Question",
        "name": q,
        "acceptedAnswer": {"@type": "Answer", "text": a},
    } for q, a in faqs]
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": items}
    return json.dumps(ld, ensure_ascii=False)


def render_extras(a) -> str:
    """學區、重大建設時程、生活機能 POI 三個加深區塊。"""
    out = []
    out.append('  <h2>學區與教育資源</h2>')
    out.append(f'  <p>{a["schools"]}</p>')

    out.append('  <h2>重大建設與發展時程</h2>')
    out.append('  <ul class="timeline">')
    for period, desc in a["development"]:
        out.append(f'    <li><span class="tl-year">{period}</span><span class="tl-desc">{desc}</span></li>')
    out.append('  </ul>')

    out.append('  <h2>生活機能一覽</h2>')
    out.append('  <div class="poi-grid">')
    for cat, items in a["poi"]:
        lis = "".join(f"<li>{x}</li>" for x in items)
        out.append(f'    <div class="poi-card"><h4>{cat}</h4><ul>{lis}</ul></div>')
    out.append('  </div>')
    return "\n".join(out)


def load_credits() -> dict:
    p = CX468_DIR / "img" / "area" / "credits.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def render_credit(slug, credits) -> str:
    c = credits.get(slug)
    if not c:
        return ""
    url = c.get("descurl", "")
    name = f'{c.get("landmark", "")}'
    src = f'攝影：{c.get("author", "")}／{c.get("license", "")}'
    if url:
        src = f'<a href="{url}" target="_blank" rel="noopener">{src}（Wikimedia Commons）</a>'
    return f'{name}　·　{src}'


def render_neighbors(cur_slug) -> str:
    links = []
    for a in AREAS:
        if a["slug"] == cur_slug:
            continue
        links.append(f'    <li><a href="area-{a["slug"]}.html">{a["town"]}房市與生活機能 →</a></li>')
    return "\n".join(links)


PAGE = Template("""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>$town房市與生活機能總覽｜實價登錄即時行情｜鋮馨租賃</title>
<meta name="description" content="$desc">
<link rel="canonical" href="https://cx468.com.tw/area-$slug.html">
<meta name="keywords" content="$town,新北市$town,$town房價,$town實價登錄,$town租金,$town捷運,鋮馨租賃">
<meta property="og:title" content="$town房市與生活機能總覽｜實價登錄即時行情">
<meta property="og:description" content="$desc">
<meta property="og:type" content="article">
<meta property="og:url" content="https://cx468.com.tw/area-$slug.html">
<meta property="og:locale" content="zh_TW">
<meta property="og:site_name" content="鋮馨租賃有限公司">
<meta property="og:image" content="https://cx468.com.tw/img/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="$town房市與生活機能總覽">
<meta name="twitter:description" content="$desc">
<meta name="twitter:image" content="https://cx468.com.tw/img/og-image.jpg">
<meta name="author" content="鋮馨租賃有限公司">
<meta name="geo.region" content="TW-NWT">
<meta name="geo.placename" content="新北市$town">
<meta name="geo.position" content="$lat;$lng">
<meta name="ICBM" content="$lat, $lng">
<link rel="preload" href="style.css" as="style" onload="this.onload=null;this.rel='stylesheet'"><noscript><link rel="stylesheet" href="style.css"></noscript>
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="favicon-16.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="192x192" href="favicon-192.png">
<style>
.art-hero{background:linear-gradient(135deg,#16A34A 0%,#0EA5E9 60%,#7C3AED 100%);padding:100px 2rem 56px;text-align:center}
.art-tag{display:inline-block;font-size:11px;font-weight:600;padding:4px 12px;border-radius:10px;background:rgba(255,255,255,.22);color:#fff;margin-bottom:1rem;letter-spacing:.08em}
.art-hero h1{font-size:40px;font-weight:700;color:#fff;letter-spacing:-.025em;line-height:1.14;max-width:720px;margin:0 auto .75rem}
.art-hero-meta{font-size:13px;color:rgba(255,255,255,.7)}
.art-body{max-width:720px;margin:0 auto;padding:3rem 2rem 5rem}
.art-body h2{font-size:26px;font-weight:700;letter-spacing:-.02em;margin:2.5rem 0 1rem;padding-top:.6rem;border-top:1px solid #f0f0f0}
.art-body h3{font-size:18px;font-weight:600;margin:1.4rem 0 .5rem}
.art-body p{font-size:16px;line-height:1.85;color:#3d3d3f;margin-bottom:1.1rem}
.art-body ul{margin:.5rem 0 1.25rem 1.4rem}
.art-body li{font-size:16px;line-height:1.8;color:#3d3d3f;margin-bottom:.4rem}
.back-link{display:inline-flex;align-items:center;gap:6px;font-size:13px;color:#86868b;margin-bottom:1.5rem}
.faq-item{border-bottom:1px solid #f0f0f0;padding-bottom:.5rem;margin-bottom:1rem}
.live-stats{margin:1.5rem 0 .5rem}
.live-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.live-card{background:#f7f9fb;border:1px solid #eef1f4;border-radius:14px;padding:18px 18px 16px}
.live-card h4{font-size:13px;color:#6e6e73;font-weight:600;margin:0 0 10px}
.live-big{font-size:30px;font-weight:700;color:#0F172A;letter-spacing:-.02em}
.live-big .u{font-size:14px;font-weight:600;color:#86868b;margin-left:4px}
.live-row{display:flex;justify-content:space-between;font-size:13px;color:#3d3d3f;padding:5px 0;border-top:1px dashed #e6e9ec}
.live-row b{color:#1d1d1f}
.live-note{font-size:12px;color:#86868b;margin-top:10px;line-height:1.6}
.live-note a{color:#0071e3;text-decoration:none}
.cta-box{background:#0a2a1a;border-radius:20px;padding:2.25rem;text-align:center;margin:3rem 0 1rem}
.cta-box h3{font-size:22px;font-weight:700;color:#fff;margin-bottom:.6rem}
.cta-box p{font-size:14px;color:rgba(255,255,255,.65);margin-bottom:1.3rem}
.cta-box a{display:inline-block;background:#fff;color:#1d1d1f;padding:11px 30px;border-radius:980px;font-size:15px;font-weight:600;text-decoration:none}
.disclaimer{font-size:12px;color:#9b9b9f;line-height:1.7;margin-top:1.5rem}
.loc-grid{display:grid;grid-template-columns:0.8fr 1.2fr;gap:14px;align-items:stretch;margin:1.25rem 0 .5rem}
.loc-card{background:#f7f9fb;border:1px solid #eef1f4;border-radius:14px;padding:16px;display:flex;flex-direction:column}
.loc-card h4{font-size:13px;color:#6e6e73;font-weight:600;margin:0 0 10px}
.tw-wrap{flex:1;display:flex;align-items:center;justify-content:center}
.tw-wrap svg{width:auto;height:200px;max-width:100%}
.tw-island{fill:#e3e9ef;stroke:#cfd8e1;stroke-width:1.5}
.tw-pin{fill:#EF4444}
.tw-pin-ring{fill:none;stroke:#EF4444;stroke-width:2;opacity:.55;transform-origin:center}
@keyframes pin-pulse{0%{r:5;opacity:.6}70%{r:16;opacity:0}100%{r:16;opacity:0}}
.tw-label{font-size:12px;fill:#1d1d1f;font-weight:700}
.map-embed{flex:1;min-height:240px;border:0;width:100%;border-radius:10px}
.area-photo{margin:1.25rem 0 .5rem}
.area-photo img{width:100%;border-radius:14px;display:block}
.area-photo figcaption{font-size:12px;color:#86868b;text-align:center;margin-top:8px}
.chart-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:1.25rem 0 .5rem}
.chart-card{background:#fff;border:1px solid #eef1f4;border-radius:14px;padding:16px}
.chart-card h4{font-size:13px;color:#1d1d1f;font-weight:700;margin:0 0 4px}
.chart-card .sub{font-size:11px;color:#86868b;margin:0 0 10px}
.bar-row{display:flex;align-items:center;gap:8px;margin-bottom:9px;font-size:12px}
.bar-name{width:84px;color:#3d3d3f;flex:none;white-space:nowrap}
.bar-track{flex:1;background:#f0f2f5;border-radius:6px;height:18px;overflow:hidden}
.bar-fill{height:100%;border-radius:6px;transition:width .5s ease}
.bar-val{width:74px;text-align:right;color:#1d1d1f;font-weight:600;flex:none}
.chart-empty{font-size:12px;color:#86868b;padding:14px 0;text-align:center}
.bar-dot{width:9px;height:9px;border-radius:50%;flex:none;margin-right:2px}
.bar-tag{font-size:10px;font-weight:700;color:#fff;background:#1d1d1f;border-radius:6px;padding:1px 5px;margin-left:6px}
.live-card:nth-child(1){border-top:3px solid #2563EB}
.live-card:nth-child(2){border-top:3px solid #16A34A}
.timeline{list-style:none;margin:1rem 0 1.25rem;padding:0;border-left:2px solid #e6e9ec}
.timeline li{position:relative;padding:0 0 1rem 1.1rem}
.timeline li::before{content:"";position:absolute;left:-7px;top:4px;width:12px;height:12px;border-radius:50%;background:#16A34A;border:2px solid #fff;box-shadow:0 0 0 1px #cfe8d6}
.tl-year{display:inline-block;font-size:12px;font-weight:700;color:#16A34A;background:#eafff1;border-radius:6px;padding:2px 8px;margin-right:8px}
.tl-desc{font-size:15px;color:#3d3d3f;line-height:1.7}
.poi-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin:1rem 0 1.25rem}
.poi-card{background:#f7f9fb;border:1px solid #eef1f4;border-radius:12px;padding:14px 16px}
.poi-card h4{font-size:13px;font-weight:700;color:#0F172A;margin:0 0 8px;padding-bottom:6px;border-bottom:1px solid #e6e9ec}
.poi-card ul{margin:0;padding-left:1.1rem}
.poi-card li{font-size:13.5px;color:#3d3d3f;line-height:1.7;margin-bottom:2px}
@media(max-width:768px){.art-hero h1{font-size:27px}.live-grid{grid-template-columns:1fr}.loc-grid{grid-template-columns:1fr}.chart-grid{grid-template-columns:1fr}.tw-wrap svg{height:170px}.poi-grid{grid-template-columns:1fr}}
</style>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":["Place","AdministrativeArea"],"name":"$town","alternateName":"新北市$town","description":"$desc","geo":{"@type":"GeoCoordinates","latitude":$lat,"longitude":$lng},"containedInPlace":{"@type":"AdministrativeArea","name":"新北市","containedInPlace":{"@type":"Country","name":"臺灣"}},"url":"https://cx468.com.tw/area-$slug.html"}
</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"首頁","item":"https://cx468.com.tw/"},{"@type":"ListItem","position":2,"name":"實價登錄觀察室","item":"https://cx468.com.tw/lvr-observatory.html"},{"@type":"ListItem","position":3,"name":"$town","item":"https://cx468.com.tw/area-$slug.html"}]}
</script>
<script type="application/ld+json">
$faq_ld
</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":["LocalBusiness","ProfessionalService"],"@id":"https://cx468.com.tw/#organization","name":"鋮馨租賃有限公司","alternateName":"Cheng Xin Leasing","url":"https://cx468.com.tw","telephone":"+886-2-2249-0517","email":"cx468468@gmail.com","address":{"@type":"PostalAddress","streetAddress":"中正路468號","addressLocality":"中和區","addressRegion":"新北市","postalCode":"23552","addressCountry":"TW"},"geo":{"@type":"GeoCoordinates","latitude":25.0070,"longitude":121.4912},"areaServed":[{"@type":"AdministrativeArea","name":"新北市中和區"},{"@type":"AdministrativeArea","name":"新北市永和區"},{"@type":"AdministrativeArea","name":"新北市板橋區"},{"@type":"AdministrativeArea","name":"新北市新店區"},{"@type":"AdministrativeArea","name":"新北市土城區"}],"sameAs":["https://lin.ee/PHIfSoY"]}
</script>
<script src="include.js" defer></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-4FX9LNEL7R"></script>
<script>
window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}
gtag('js',new Date());gtag('config','G-4FX9LNEL7R');
document.addEventListener('click',function(e){var a=e.target.closest('a');if(!a||!a.href)return;
if(a.href.indexOf('lin.ee')>-1){gtag('event','line_click',{page_path:location.pathname,link_text:(a.innerText||'').trim().substring(0,50)});}
else if(a.href.indexOf('tel:')===0){gtag('event','phone_click',{page_path:location.pathname,phone_number:a.href.replace('tel:','')});}
});
</script>
</head>
<body>
<div data-include="nav"></div>

<section class="art-hero">
  <div class="art-tag">新北市・區域百科</div>
  <h1>$town 房市與生活機能總覽</h1>
  <div class="art-hero-meta">鋮馨租賃有限公司 · 實價登錄行情每月 2/12/22 自動同步</div>
</section>

<div class="art-body">
  <a href="lvr-observatory.html" class="back-link">← 返回實價登錄觀察室</a>

$intro

  <h2>$town 在哪裡？</h2>
  <div class="loc-grid">
    <div class="loc-card">
      <h4>台灣位置</h4>
      <div class="tw-wrap">
        <svg viewBox="0 0 210 320" role="img" aria-label="$town 在台灣的位置">
          <path class="tw-island" d="$tw_path"/>
          <circle class="tw-pin-ring" cx="$mx" cy="$my" r="6"><animate attributeName="r" values="5;16" dur="1.8s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.6;0" dur="1.8s" repeatCount="indefinite"/></circle>
          <circle class="tw-pin" cx="$mx" cy="$my" r="5"/>
          <text class="tw-label" x="$mx" y="$my" dx="-8" dy="-10" text-anchor="end">新北市$town</text>
        </svg>
      </div>
    </div>
    <div class="loc-card" style="padding:8px">
      <iframe class="map-embed" loading="lazy" allowfullscreen referrerpolicy="no-referrer-when-downgrade"
        src="https://www.google.com/maps/embed/v1/place?key=$gmap_key&q=新北市$town&zoom=13&language=zh-TW"
        title="$town 地圖"></iframe>
    </div>
  </div>

  <figure class="area-photo">
    <img src="img/area/$slug.jpg" alt="新北市$town 地標：$credit_alt" loading="lazy"
      onerror="this.closest('.area-photo').remove()">
    <figcaption>$credit</figcaption>
  </figure>

  <h2>$town 實價登錄即時行情</h2>
  <div class="live-stats" id="liveStats" data-town="$town">
    <div class="live-grid">
      <div class="live-card"><h4>買賣行情（近 180 天）</h4><div class="live-big" id="buyMain">載入中…</div></div>
      <div class="live-card"><h4>租金行情（近 180 天）</h4><div class="live-big" id="rentMain">載入中…</div></div>
    </div>
    <div class="live-note">資料來源：內政部不動產實價登錄，近 180 天成交中位數，每月自動更新。完整 75 區比較見
      <a href="lvr-observatory.html">買賣觀察室</a>與<a href="lvr-rental.html">租金報酬頁</a>。數字僅供參考，非投資建議。</div>
  </div>

  <h2>$town 與鄰近精選區租金比較</h2>
  <div class="chart-grid">
    <div class="chart-card">
      <h4>住宅月租每坪中位</h4><p class="sub">元／坪／月 · 近 180 天</p>
      <div id="chartRent"><div class="chart-empty">載入中…</div></div>
    </div>
    <div class="chart-card">
      <h4>店面月租中位</h4><p class="sub">整間月租金 · 元／月 · 近 180 天</p>
      <div id="chartShop"><div class="chart-empty">載入中…</div></div>
    </div>
  </div>

$sections

$extras

$faq_html

  <div class="cta-box">
    <h3>在地深耕 20 年，懂$town的房子</h3>
    <p>不動產售後回租、貸款整合、民間轉銀行——免費評估你的狀況，不申請不收費。</p>
    <a href="evaluate.html">免費諮詢與評估</a>
  </div>

  <p class="disclaimer">本頁區域資訊與實價登錄數字僅供參考，實際成交與市場狀況可能變動。鋮馨租賃有限公司為融資租賃業者，
  非金融機構，相關貸款或核貸結果最終由金融機構依個案決定。</p>

  <h2>其他精選區</h2>
  <ul>
$neighbors
    <li><a href="lvr-observatory.html">實價登錄觀察室（75 區比較）→</a></li>
  </ul>
</div>

<div data-include="line-qr"></div>
<div data-include="footer"></div>
<div data-include="anti-fraud-modal"></div>

<script>
(function(){
  var box=document.getElementById('liveStats');if(!box)return;
  var town=box.dataset.town;
  var FOCUS=['中和區','永和區','板橋區','新店區','土城區'];
  var COLORS={'中和區':'#7C3AED','永和區':'#2563EB','板橋區':'#16A34A','新店區':'#F59E0B','土城區':'#EF4444'};
  function num(n){return (n===null||n===undefined||isNaN(n))?null:Number(n);}
  function fmt(n){return n===null?'—':n.toLocaleString('zh-TW');}
  function chg(v){v=num(v);if(v===null)return '—';
    var up=v>0,c=up?'#16A34A':(v<0?'#EF4444':'#6e6e73'),a=up?'▲':(v<0?'▼':'—');
    return '<span style="color:'+c+';font-weight:700">'+a+' '+Math.abs(v).toFixed(1)+'%</span>';}
  function pick(arr){for(var i=0;i<arr.length;i++){if(arr[i]&&arr[i]['鄉鎮市區']===town)return arr[i];}return null;}
  function getJSON(u){return fetch(u).then(function(r){return r.ok?r.json():[];}).catch(function(){return [];});}
  Promise.all([getJSON('lvr-data/排名_w180.json'),getJSON('lvr-data/rental_ranking_w180.json')]).then(function(res){
    var buy=pick(res[0]||[]),rent=pick(res[1]||[]);
    var bc=document.getElementById('buyMain').parentNode,rc=document.getElementById('rentMain').parentNode;
    if(buy){
      var up=num(buy['單價中位']);
      bc.innerHTML='<h4>買賣行情（近 180 天）</h4>'+
        '<div class="live-big">'+(up===null?'—':up.toFixed(1))+'<span class="u">萬/坪</span></div>'+
        '<div class="live-row"><span>總價中位</span><b>'+fmt(num(buy['總價中位']))+' 萬</b></div>'+
        '<div class="live-row"><span>建坪中位</span><b>'+(num(buy['建坪中位'])===null?'—':num(buy['建坪中位']).toFixed(1))+' 坪</b></div>'+
        '<div class="live-row"><span>屋齡中位</span><b>'+(num(buy['屋齡中位'])===null?'—':num(buy['屋齡中位']).toFixed(1))+' 年</b></div>'+
        '<div class="live-row"><span>樣本</span><b>'+fmt(num(buy['n']))+' 筆</b></div>'+
        '<div class="live-row"><span>2 年漲幅</span><b>'+chg(buy['2年漲幅'])+'</b></div>';
    }else{bc.innerHTML='<h4>買賣行情（近 180 天）</h4><div class="live-big" style="font-size:18px;color:#86868b">本區暫無資料</div>';}
    if(rent){
      var rp=num(rent['月租每坪中位']);
      rc.innerHTML='<h4>租金行情（近 180 天）</h4>'+
        '<div class="live-big">'+(rp===null?'—':rp.toLocaleString('zh-TW'))+'<span class="u">元/坪/月</span></div>'+
        '<div class="live-row"><span>住家月租中位</span><b>'+fmt(num(rent['月租中位']))+' 元</b></div>'+
        '<div class="live-row"><span>店面月租中位</span><b>'+(num(rent['店面月租中位'])===null?'—':fmt(num(rent['店面月租中位']))+' 元')+'</b></div>'+
        '<div class="live-row"><span>年化報酬率</span><b>'+(num(rent['年化報酬率'])===null?'—':num(rent['年化報酬率']).toFixed(2)+'%')+'</b></div>'+
        '<div class="live-row"><span>樣本</span><b>'+fmt(num(rent['n']))+' 筆</b></div>';
    }else{rc.innerHTML='<h4>租金行情（近 180 天）</h4><div class="live-big" style="font-size:18px;color:#86868b">本區暫無資料</div>';}

    // ---- 鄰近精選區租金比較長條圖 ----
    var rentArr=res[1]||[];
    function lookup(t){for(var i=0;i<rentArr.length;i++){if(rentArr[i]['鄉鎮市區']===t)return rentArr[i];}return null;}
    function drawBars(elId,field,fmtVal){
      var el=document.getElementById(elId);if(!el)return;
      var items=FOCUS.map(function(t){var r=lookup(t);return {name:t,val:r?num(r[field]):null};});
      var vals=items.map(function(x){return x.val;}).filter(function(v){return v!==null;});
      if(vals.length===0){el.innerHTML='<div class="chart-empty">店面資料更新中，下次每月更新後顯示</div>';return;}
      var max=Math.max.apply(null,vals);
      el.innerHTML=items.map(function(x){
        var w=(x.val===null||max===0)?6:Math.max(6,Math.round(x.val/max*100));
        var c=COLORS[x.name]||'#8a8a8e';var hi=x.name===town;
        var nm=x.name.replace('區','');
        var grad='linear-gradient(90deg,'+c+'cc 0%,'+c+' 100%)';
        return '<div class="bar-row">'+
          '<span class="bar-dot" style="background:'+c+'"></span>'+
          '<span class="bar-name" style="'+(hi?'font-weight:700;color:'+c:'')+'">'+nm+(hi?'<span class="bar-tag" style="background:'+c+'">本區</span>':'')+'</span>'+
          '<span class="bar-track"><span class="bar-fill" style="width:'+w+'%;background:'+grad+';opacity:'+(hi?1:0.78)+(hi?';box-shadow:0 0 0 2px '+c+'55':'')+'"></span></span>'+
          '<span class="bar-val" style="'+(hi?'color:'+c:'')+'">'+(x.val===null?'—':fmtVal(x.val))+'</span></div>';
      }).join('');
    }
    drawBars('chartRent','月租每坪中位',function(v){return v.toLocaleString('zh-TW');});
    drawBars('chartShop','店面月租中位',function(v){return v.toLocaleString('zh-TW');});
  });
})();
</script>
</body>
</html>
""")


def main() -> None:
    credits = load_credits()
    for a in AREAS:
        mx, my = tw_xy(a["lat"], a["lng"])
        c = credits.get(a["slug"], {})
        credit_alt = f'{c.get("landmark", a["town"])}'
        html = PAGE.substitute(
            town=a["town"], slug=a["slug"], desc=a["desc"],
            lat=a["lat"], lng=a["lng"], today=TODAY,
            gmap_key=GMAP_KEY, tw_path=TW_PATH, mx=mx, my=my,
            intro="\n".join(f"  <p>{p}</p>" for p in a["intro"]),
            sections=render_sections(a["sections"]),
            extras=render_extras(a),
            faq_html=render_faq_html(a["faqs"]),
            faq_ld=render_faq_ld(a["faqs"]),
            neighbors=render_neighbors(a["slug"]),
            credit=render_credit(a["slug"], credits) or f'{a["town"]} 生活圈一隅',
            credit_alt=credit_alt,
        )
        dest = CX468_DIR / f'area-{a["slug"]}.html'
        dest.write_text(html, encoding="utf-8")
        print(f"✓ {dest.name}（{dest.stat().st_size // 1024} KB）")


if __name__ == "__main__":
    main()
