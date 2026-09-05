"""
產出 lvr-presale.html (預售屋) + lvr-rental.html (租屋報酬率)
兩頁使用相同 hero+ranking table 結構（共用 CSS class）。
2026-09-05 套 Better 內頁版型（同 build_observatory.py 手法）；輸出路徑可用
LVR_PRESALE_DEST／LVR_RENTAL_DEST 環境變數覆寫（本機驗證用，預設不變）。
"""

from datetime import datetime
from pathlib import Path
from shutil import copy2
import json
import os
import aeo_blocks

import pandas as pd

# Production paths
CX468_DIR = Path(__file__).resolve().parent.parent.parent
OUT_DIR = CX468_DIR / "scripts" / "lvr" / "_cache"
DATA_DEST_DIR = CX468_DIR / "lvr-data"
PRESALE_DEST = Path(os.environ.get("LVR_PRESALE_DEST", CX468_DIR / "lvr-presale.html"))
RENTAL_DEST = Path(os.environ.get("LVR_RENTAL_DEST", CX468_DIR / "lvr-rental.html"))
LOW_SAMPLE = 30
SHOP_MIN = 5  # 店面樣本低於此值不顯示中位（太少不具參考性）

CITIES = ["台北市", "新北市", "台中市", "桃園市"]
CITY_COLORS = {"台北市": "#1d1d1f", "新北市": "#c8102e",
               "台中市": "#16A34A", "桃園市": "#F59E0B"}


def common_styles() -> str:
    return """
/* === Better 對拷版型（2026-09-04 原型：對標 better.com/mortgage；色票依老闆定案 token） === */
:root{--forest:#1B2F4A;--forest-deep:#12213A;--action:#2F5B8F;--action-hover:#26497A;--gold:#C8945A;--gold-soft:#E0B685;--gold-deep:#9A6D3A;
  --paper:#F7F5F0;--cream:#F2EFE8;--tint:#EEF2F7;--ink:#1B2F4A;--ink-dim:#5A6878;--line:#E2DED4;
  --shadow:0 4px 6px -1px rgba(0,0,0,.1),0 2px 4px -2px rgba(0,0,0,.1)}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:'Noto Sans TC',-apple-system,'PingFang TC','Microsoft JhengHei',sans-serif;font-size:16px;line-height:24px;color:var(--ink);background:#fff;padding-top:64px;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
img{max-width:100%;display:block}
:focus-visible{outline:2px solid var(--gold);outline-offset:3px;border-radius:4px}

/* 版心：外框 1440、內容欄 1200、頁邊距 40／24 */
.bt-in{max-width:1280px;margin:0 auto;padding:0 40px}
.bt-narrow{max-width:880px;margin:0 auto;padding:0 40px}
.bt-sec{padding:64px 0}
.bt-sec-80{padding:80px 0}
.bt-sec-96{padding:96px 0}

/* 字級 */
.bt-eyebrow{font-size:18px;line-height:24px;font-weight:500;color:var(--gold-deep);margin-bottom:12px}
.bt-label{font-size:14px;line-height:20px;font-weight:700;color:var(--gold-deep);letter-spacing:.08em;margin-bottom:12px}
.bt-h1{font-size:48px;line-height:1.2;font-weight:700;color:var(--ink);margin-bottom:24px}
.bt-h1 em,.bt-h2 em{font-style:normal;color:var(--action)}
.bt-h2{font-size:32px;line-height:1.2;font-weight:700;color:var(--ink);margin-bottom:24px}
.bt-h4{font-size:18px;line-height:1.4;font-weight:700;color:var(--ink);margin-bottom:8px}
.bt-p{font-size:16px;line-height:24px;color:var(--ink-dim)}
.bt-p+.bt-p{margin-top:16px}
.bt-small{font-size:14px;line-height:20px;color:var(--ink-dim)}
.bt-center{text-align:center}

/* 按鈕：主 64px／小 48px、8px 圓角、hover 只變深 300ms */
.bt-btn{display:inline-flex;align-items:center;justify-content:center;height:64px;padding:0 40px;border-radius:8px;background:var(--action);color:#fff;font-size:16px;font-weight:700;white-space:nowrap;border:0;cursor:pointer;font-family:inherit;transition:background-color .3s ease-in-out}
.bt-btn:hover{background:var(--action-hover)}
.bt-btn-sm{height:48px;padding:0 16px}
.bt-btn-ghost{background:var(--cream);color:var(--ink)}
.bt-btn-ghost:hover{background:var(--line)}
.bt-btn-gold{background:var(--gold);color:var(--forest-deep)}
.bt-btn-gold:hover{background:var(--gold-soft)}
.bt-btn-outline{background:transparent;color:#fff;border:1px solid rgba(255,255,255,.55)}
.bt-btn-outline:hover{background:rgba(255,255,255,.1)}
.bt-btns{display:flex;gap:12px;flex-wrap:wrap}

/* 卡片 */
.bt-card{background:#fff;border-radius:8px;box-shadow:var(--shadow);padding:32px}

/* 1. Hero 左文右圖 */
.bt-hero{background:var(--paper)}
.bt-hero-grid{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:64px;align-items:center}
.bt-hero-text .bt-p{margin-bottom:32px;max-width:560px}
.bt-hero-img{width:100%;height:auto;aspect-ratio:4/5;object-fit:cover;object-position:center 60%;border-radius:8px}
.bt-hero .aib{margin:24px 0 0}
.bt-hero .aib-form{box-shadow:var(--shadow);border-radius:8px}
.bt-hero .aib-chips button{color:var(--ink)}

/* 快速答案 */
.bt-qa{border-left:4px solid var(--action)}
.bt-qa p{font-size:16px;line-height:24px;color:var(--ink);margin:0 0 16px}
.bt-qa ul{margin:0;padding-left:20px;font-size:14px;line-height:22px;color:var(--ink-dim)}
.bt-qa li+li{margin-top:4px}
.bt-qa li strong{color:var(--ink)}

/* 2. 深色帶 */
.bt-dark{background:var(--forest);color:#fff}
.bt-dark .bt-label{color:var(--gold)}
.bt-dark .bt-h2{color:#fff}
.bt-dark .bt-p{color:rgba(255,255,255,.82)}
.bt-dark-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:64px;align-items:center}
.bt-dark-img{width:100%;height:auto;aspect-ratio:5/4;object-fit:cover;border-radius:8px}
.bt-dark figcaption{font-size:14px;line-height:20px;color:rgba(255,255,255,.6);margin-top:12px}
.bt-def{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:64px}
.bt-def-item{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:8px;padding:32px 24px;text-align:center}
.bt-def-num{font-size:32px;line-height:1.2;font-weight:700;color:#fff;margin-bottom:12px}
.bt-def-label{font-size:16px;line-height:24px;color:rgba(255,255,255,.8)}

/* 3. 特色格（純文字） */
.bt-steps{display:grid;grid-template-columns:repeat(4,1fr);gap:40px 32px;margin-top:48px}
.bt-step-num{width:40px;height:40px;border-radius:8px;background:var(--forest);color:#fff;font-size:16px;font-weight:700;display:flex;align-items:center;justify-content:center;margin-bottom:16px}
.bt-step-num.gold{background:var(--gold);color:var(--forest-deep)}
.bt-points{display:grid;grid-template-columns:repeat(3,1fr);gap:40px 32px;margin-top:64px;padding-top:64px;border-top:1px solid var(--line)}

/* 適合對象卡 */
.bt-who{background:var(--paper)}
.bt-who-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:48px}
.bt-who-card .bt-h4{margin-bottom:12px}
.bt-check{display:flex;flex-direction:column;gap:8px;margin-top:20px;padding-top:20px;border-top:1px solid var(--line)}
.bt-check span{font-size:14px;line-height:20px;color:var(--ink);display:flex;gap:8px;align-items:flex-start}
.bt-check span::before{content:"✓";color:var(--action);font-weight:700;flex-shrink:0}

/* 4. CTA 帶 */
.bt-cta{background:var(--cream);text-align:center}
.bt-cta .bt-h2{max-width:640px;margin-left:auto;margin-right:auto}
.bt-cta .bt-p{max-width:520px;margin:0 auto 32px}
.bt-cta .bt-btns{justify-content:center}
.bt-promise{display:flex;gap:12px 28px;justify-content:center;flex-wrap:wrap;margin-top:32px}
.bt-promise span{font-size:14px;line-height:20px;color:var(--ink-dim);display:flex;align-items:center;gap:8px}
.bt-promise span::before{content:"✓";color:var(--action);font-weight:700}

/* 5. 相關文章 */
.bt-related{background:var(--tint)}
.bt-rel-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:40px}
.bt-rel-card{display:flex;flex-direction:column;justify-content:space-between;min-height:180px;transition:box-shadow .3s ease-in-out}
.bt-rel-card:hover{box-shadow:0 10px 15px -3px rgba(0,0,0,.1),0 4px 6px -4px rgba(0,0,0,.1)}
.bt-rel-card h3{font-size:18px;line-height:1.4;font-weight:700;color:var(--ink)}
.bt-rel-card::after{content:"→";font-size:20px;font-weight:700;color:var(--action);margin-top:24px}

/* 案例 */
.bt-case-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:32px}
.bt-case-card{border-left:4px solid var(--action)}
.bt-case-card .bt-label{margin-bottom:8px}
.bt-case-card p{font-size:16px;line-height:24px;color:var(--ink)}

/* 比較表 */
.bt-compare{background:var(--paper)}
.bt-table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch;background:#fff;border-radius:8px;box-shadow:var(--shadow);margin-top:32px}
.bt-table{width:100%;border-collapse:collapse;min-width:560px}
.bt-table th{padding:16px 20px;font-size:16px;font-weight:700;text-align:center;background:var(--cream);color:var(--ink-dim)}
.bt-table th:first-child{text-align:left;width:30%}
.bt-table th.col-sl{background:var(--forest);color:#fff}
.bt-table td{padding:16px 20px;font-size:16px;line-height:24px;border-top:1px solid var(--line);text-align:center;color:var(--ink-dim)}
.bt-table td:first-child{text-align:left;font-weight:700;color:var(--ink)}
.bt-table td.highlight{background:var(--tint);color:var(--ink);font-weight:700}
.bt-table .yes{color:var(--action);font-weight:700}
.bt-table .no{color:var(--ink-dim)}
.bt-dark-card{margin-top:48px;background:var(--forest);border-radius:8px;padding:48px 40px;text-align:center;color:#fff}
.bt-dark-card .bt-h4{color:#fff;font-size:24px;line-height:1.2;margin-bottom:12px}
.bt-dark-card .bt-p{color:rgba(255,255,255,.75);max-width:480px;margin:0 auto 32px}
.bt-dark-card .bt-btns{justify-content:center}

/* 6. FAQ accordion */
.bt-faq details{border-top:1px solid var(--line);padding:24px 0}
.bt-faq details:last-of-type{border-bottom:1px solid var(--line)}
.bt-faq summary{font-size:18px;line-height:1.4;font-weight:700;color:var(--ink);cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:16px}
.bt-faq summary::-webkit-details-marker{display:none}
.bt-faq .plus{font-size:24px;color:var(--ink-dim);font-weight:400;flex-shrink:0;transition:transform .3s ease-in-out}
.bt-faq details[open] .plus{transform:rotate(45deg)}
.bt-faq details p{font-size:16px;line-height:24px;color:var(--ink-dim);margin-top:16px}

/* 在地相關方案 */
.bt-local{margin-top:64px}
.bt-local .bt-label{margin-bottom:8px}
.bt-local p{margin-bottom:16px}
.bt-chips{display:flex;flex-wrap:wrap;gap:8px}
.bt-chips a{display:inline-flex;align-items:center;height:40px;padding:0 16px;border-radius:8px;border:1px solid var(--line);background:var(--paper);font-size:14px;font-weight:500;color:var(--ink);transition:background-color .3s ease-in-out}
.bt-chips a:hover{background:var(--cream)}

@media(prefers-reduced-motion:reduce){*{transition:none!important}}

@media(max-width:900px){
  body{padding-top:58px}
  .bt-hero-grid,.bt-dark-grid{grid-template-columns:minmax(0,1fr);gap:40px}
  .bt-hero-img{aspect-ratio:4/3}
  .bt-steps{grid-template-columns:repeat(2,1fr)}
  .bt-points,.bt-who-grid,.bt-rel-grid,.bt-case-grid,.bt-def{grid-template-columns:1fr}
  .bt-rel-card{min-height:auto}
}
@media(max-width:768px){
  .bt-in,.bt-narrow{padding:0 24px}
  .bt-sec-96{padding:64px 0}
  .bt-sec-80{padding:64px 0}
  .bt-h1{font-size:32px}
  .bt-h2{font-size:32px}
  .bt-card{padding:24px}
  .bt-btns{flex-direction:column;align-items:stretch}
  .bt-btn{width:100%}
  .bt-dark-card{padding:32px 24px}
}
@media(max-width:520px){
  .bt-steps{grid-template-columns:1fr}
}
@media(max-width:640px){
  /* 手機：ai-bar 右側讓出小鋮浮動鈕（chat-widget .cw-launch 固定 right 24px + 58px）的欄位，送出鈕不被蓋住 */
  .bt-hero .aib{padding-right:70px}
}
/* === 本頁補充（lvr 預售屋／租金報酬頁）：資料區選擇器沿用原頁一字不改、只換 token；FAQ「＋」CSS 生成；名詞解釋列 === */
.bt-tool .bt-qa{margin-bottom:24px}
.bt-qa h4{font-size:14px;line-height:20px;font-weight:700;color:var(--gold-deep);letter-spacing:.08em;margin-bottom:12px}
.bt-hero .bt-label{margin-bottom:16px}
.bt-hero .bt-meta{font-size:14px;line-height:20px;color:var(--ink-dim);margin-top:-16px}

/* 家族切換（觀察室／預售屋／租金報酬） */
.family-nav{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:24px}
.family-nav a{display:inline-flex;align-items:center;height:40px;padding:0 16px;border-radius:8px;border:1px solid var(--line);background:var(--paper);font-size:14px;font-weight:500;color:var(--ink);transition:background-color .3s ease-in-out}
.family-nav a:hover{background:var(--cream)}
.family-nav a.active{background:var(--forest);border-color:var(--forest);color:#fff}

/* 區塊小標 */
.section-title{display:flex;align-items:center;gap:12px;flex-wrap:wrap;font-size:14px;line-height:20px;font-weight:700;color:var(--gold-deep);letter-spacing:.08em;margin:40px 0 14px}
.section-title::before{content:'';width:8px;height:8px;background:var(--action);flex:none}
.section-title:first-child{margin-top:0}

/* KPI 卡（4 縣市） */
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:24px}
@media(max-width:780px){.kpi-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:480px){.kpi-grid{grid-template-columns:1fr}}
.kpi-card{background:#fff;border:1px solid var(--line);border-radius:8px;padding:20px 18px;box-shadow:var(--shadow)}
.kpi-city{font-size:16px;font-weight:700;color:var(--ink);margin-bottom:10px}
.kpi-value{font-size:26px;font-weight:700;color:var(--ink);letter-spacing:-.02em;line-height:1;font-variant-numeric:tabular-nums}
.kpi-unit{font-size:12px;font-weight:500;color:var(--ink-dim);margin-left:4px}
.kpi-label{font-size:12px;color:var(--ink-dim);margin-top:4px}
.kpi-sub{font-size:12px;color:var(--ink-dim);margin-top:10px;padding-top:10px;border-top:1px solid var(--line)}

/* 排名表（表格外層 overflow-x:auto 必留） */
.rank-card{background:#fff;border:1px solid var(--line);border-radius:8px;padding:18px 4px;overflow:hidden;box-shadow:var(--shadow)}
.rank-card-head{display:flex;justify-content:space-between;align-items:center;padding:0 18px;margin-bottom:6px;flex-wrap:wrap;gap:10px}
.rank-card h3{font-size:18px;line-height:1.4;font-weight:700;color:var(--ink);margin:0}
.rank-card p.rank-note{font-size:13px;color:var(--ink-dim);margin:0 18px 14px;line-height:1.5}
.city-chips{display:flex;gap:6px;flex-wrap:wrap}
.city-chip{font-size:13px;font-weight:600;color:var(--ink-dim);background:var(--cream);padding:6px 12px;border-radius:8px;cursor:pointer;border:none;font-family:inherit;transition:background-color .3s ease-in-out,color .3s ease-in-out}
.city-chip.active{background:var(--forest);color:#fff}
.rank-table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
table.rank-table{width:100%;border-collapse:collapse;font-size:14px;color:var(--ink);min-width:680px}
.rank-table th{background:var(--cream);color:var(--ink-dim);font-weight:700;text-align:left;padding:10px 12px;cursor:pointer;user-select:none;white-space:nowrap;border-bottom:1.5px solid var(--line);font-size:12px;letter-spacing:.04em}
.rank-table th:hover{background:var(--tint);color:var(--ink)}
.rank-table th .arrow{margin-left:4px;opacity:.4;font-size:10px}
.rank-table th.sorted .arrow{opacity:1;color:var(--action)}
.rank-table td{padding:9px 12px;border-bottom:.5px solid var(--line);white-space:nowrap}
.rank-table td.num{text-align:right;font-variant-numeric:tabular-nums;font-size:13px}
.rank-table tr.low-sample td{color:var(--ink-dim)}
.rank-table tr:hover{background:var(--paper)}
.badge-low{display:inline-block;font-size:10px;color:var(--ink-dim);background:var(--cream);padding:1px 6px;border-radius:8px;margin-left:4px;font-weight:500}

/* 原始資料下載 */
.download-card{background:#fff;border:1px solid var(--line);border-radius:8px;padding:24px;box-shadow:var(--shadow)}
.download-grid{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.download-grid a{display:inline-flex;align-items:center;height:40px;padding:0 16px;border-radius:8px;border:1px solid var(--line);background:var(--paper);font-size:14px;font-weight:500;color:var(--ink);text-decoration:none;transition:background-color .3s ease-in-out}
.download-grid a:hover{background:var(--cream)}

/* 資料說明與免責 */
.notes{background:#fff;border:1px solid var(--line);border-radius:8px;padding:24px;font-size:14px;color:var(--ink);line-height:1.7;box-shadow:var(--shadow)}
.notes h4{font-size:16px;font-weight:700;margin:0 0 10px;color:var(--ink)}
.notes ul{margin:0;padding-left:20px;color:var(--ink-dim)}
.notes li{margin-bottom:5px}

/* FAQ：h3 進 summary、「＋」用 CSS 生成免新增文字 */
.bt-faq summary h3{font-size:18px;line-height:1.4;font-weight:700;color:var(--ink);margin:0}
.bt-faq summary::after{content:"＋";font-size:24px;color:var(--ink-dim);font-weight:400;flex-shrink:0;transition:transform .3s ease-in-out}
.bt-faq details[open] summary::after{transform:rotate(45deg)}

/* 名詞解釋 */
.bt-terms{margin-top:8px}
.bt-term{border-left:3px solid var(--action);padding:8px 0 8px 20px;margin-bottom:16px}
.bt-term strong{color:var(--ink);font-size:16px;font-weight:700}
.bt-term span{color:var(--ink-dim);font-size:16px;line-height:24px}
"""


def ga_block() -> str:
    return """<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-4FX9LNEL7R"></script>
<script>
window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}
gtag('js',new Date());gtag('config','G-4FX9LNEL7R');
document.addEventListener('click',function(e){var a=e.target.closest('a');if(!a||!a.href)return;
if(a.href.indexOf('lin.ee')>-1){gtag('event','line_click',{page_path:location.pathname});}
else if(a.href.indexOf('tel:')===0){gtag('event','phone_click',{page_path:location.pathname});}
else if(a.href.match(/\\.csv$/i)||a.href.match(/\\.json$/i)){gtag('event','data_download',{page_path:location.pathname,file_name:decodeURIComponent(a.href.split('/').pop())});}
});
</script>"""


def family_nav(active: str) -> str:
    items = [
        ("觀察室（買賣）", "lvr-observatory.html", "observatory"),
        ("預售屋", "lvr-presale.html", "presale"),
        ("租金報酬", "lvr-rental.html", "rental"),
    ]
    links = "".join(
        f'<a href="{href}" class="{"active" if k == active else ""}">{label}</a>'
        for label, href, k in items
    )
    return f'<div class="family-nav">{links}</div>'


def render_presale_html(ranking: pd.DataFrame, generated_at: str) -> str:
    aeo_head = aeo_blocks.head_jsonld("presale", generated_at[:10])
    # Better 版型（2026-09-05）：字仍取自 aeo_blocks.PAGES（與 head JSON-LD 同源，改字要重過媽祖），只換外層標記
    aeo_quick = aeo_blocks.quick_answer_bt_html("presale")
    aeo_faq_terms = aeo_blocks.faq_terms_bt_html("presale")
    city_stats = []
    for city in CITIES:
        sub = ranking[ranking["縣市"] == city]
        if sub.empty:
            continue
        city_stats.append({
            "city": city,
            "n": int(sub["n"].sum()),
            "median": round(sub["單價中位"].median(), 1),
            "max_town": sub.iloc[0]["鄉鎮市區"],
            "max_price": sub.iloc[0]["單價中位"],
        })

    kpi_html = "".join(
        f"""<div class="kpi-card" style="border-top:4px solid {CITY_COLORS[c['city']]}">
            <div class="kpi-city">{c['city']}</div>
            <div class="kpi-value">{c['median']:.1f}<span class="kpi-unit">萬/坪</span></div>
            <div class="kpi-label">市中位單價</div>
            <div class="kpi-sub">最高：{c['max_town']} {c['max_price']:.1f} 萬/坪　·　樣本 {c['n']:,}</div>
          </div>""" for c in city_stats
    )

    rows_html = ""
    for i, (_, r) in enumerate(ranking.iterrows(), 1):
        low = r["n"] < LOW_SAMPLE
        cls = ' class="low-sample"' if low else ""
        badge = ' <span class="badge-low">樣本少</span>' if low else ""
        rows_html += (
            f'<tr{cls} data-city="{r["縣市"]}">'
            f'<td class="num">{i}</td>'
            f'<td><b>{r["鄉鎮市區"]}</b>{badge}</td>'
            f'<td>{r["縣市"]}</td>'
            f'<td class="num" data-sort="{r["n"]}">{int(r["n"])}</td>'
            f'<td class="num" data-sort="{r["單價中位"]}">{r["單價中位"]:.1f}</td>'
            f'<td class="num" data-sort="{r["總價中位"]}">{r["總價中位"]:,.0f}</td>'
            f'<td class="num" data-sort="{r["建坪中位"]}">{r["建坪中位"]:.1f}</td>'
            f'</tr>'
        )

    return f"""<!--
  Page: 預售屋觀察 (LVR Presale)
  Status: READY  Generated: {generated_at}
-->
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>預售屋觀察｜雙北・台中・桃園 預售單價追蹤｜鋮馨租賃</title>
<link rel="canonical" href="https://cx468.com.tw/lvr-presale.html">
<meta property="og:type" content="website">
<meta property="og:title" content="預售屋觀察｜雙北・台中・桃園 預售單價追蹤｜鋮馨租賃">
<meta property="og:description" content="台北、新北、台中、桃園四縣市預售屋實價登錄單價追蹤。資料來源：內政部，每月更新。">
<meta property="og:url" content="https://cx468.com.tw/lvr-presale.html">
<meta property="og:image" content="https://cx468.com.tw/img/hero.jpg">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Dataset","name":"預售屋實價登錄觀察 — 雙北・台中・桃園","description":"台北、新北、台中、桃園四縣市預售屋實價登錄單價追蹤，資料來源內政部不動產交易實價查詢服務網，每月2/12/22更新。","url":"https://cx468.com.tw/lvr-presale.html","keywords":["預售屋","實價登錄","預售單價","台北","新北","台中","桃園"],"creator":{{"@type":"Organization","name":"鋮馨租賃有限公司","url":"https://cx468.com.tw/"}},"isBasedOn":"內政部不動產交易實價查詢服務網","spatialCoverage":{{"@type":"Place","name":"台北市、新北市、台中市、桃園市"}},"inLanguage":"zh-TW"}}
</script>
{aeo_head}
<meta name="description" content="台北、新北、台中、桃園四縣市 預售屋實價登錄單價追蹤。資料來源：內政部不動產交易實價查詢服務網。每月 2/12/22 自動更新。">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
{ga_block()}
<style>{common_styles()}</style>
<script>window.__cxMotionLoaded=true;/* 本頁不做捲動進場動畫（Better 對拷規格）：跳過 include.js 的 GSAP 載入 */</script>
</head>
<body>
<div id="nav" data-theme="light"></div>
<script src="nav.js"></script>

<!-- 1. Hero 左文右圖 -->
<section class="bt-hero bt-sec">
  <div class="bt-in bt-hero-grid">
    <div class="bt-hero-text">
      <div class="bt-eyebrow">預售屋行情</div>
      <h1 class="bt-h1">預售屋觀察</h1>
      <p class="bt-label">Presale Observation · 內政部實價登錄</p>
      <p class="bt-p">雙北 + 台中 + 桃園｜預售案件實價單價追蹤</p>
      <p class="bt-small bt-meta">資料涵蓋 113Q1 ~ 115Q1 · {len(ranking)} 行政區 · 更新於 {generated_at}</p>
    </div>
    <img class="bt-hero-img" src="img/gen-city-taoyuan.jpg" alt="新興重劃區住宅大樓與施工吊車" width="1344" height="768" fetchpriority="high" loading="eager">
  </div>
</section>

<!-- 2. 預售屋主體（資料區沿用原頁：id／class／data-* 與資料 JS 一字不改） -->
<section class="bt-sec bt-tool">
  <div class="bt-in">
{aeo_quick}

{family_nav("presale")}

  <div class="section-title">4 縣市預售屋市中位數</div>
  <div class="kpi-grid">{kpi_html}</div>

  <div class="section-title">全區排名（近 180 天）</div>
  <div class="rank-card">
    <div class="rank-card-head">
      <h3>{len(ranking)} 區預售單價</h3>
      <div class="city-chips" id="presaleChips">
        <button class="city-chip active" data-city="all">全部</button>
        <button class="city-chip" data-city="台北市">台北市</button>
        <button class="city-chip" data-city="新北市">新北市</button>
        <button class="city-chip" data-city="台中市">台中市</button>
        <button class="city-chip" data-city="桃園市">桃園市</button>
      </div>
    </div>
    <p class="rank-note">已排除「解除契約」案件。樣本 &lt; {LOW_SAMPLE} 標「樣本少」。</p>
    <div class="rank-table-wrap">
      <table class="rank-table" id="presaleTable">
        <thead><tr>
          <th data-type="num">排名<span class="arrow">▲▼</span></th>
          <th data-type="str">區別<span class="arrow">▲▼</span></th>
          <th data-type="str">縣市<span class="arrow">▲▼</span></th>
          <th data-type="num">樣本<span class="arrow">▲▼</span></th>
          <th data-type="num" class="sorted">單價中位<span class="arrow">▼</span></th>
          <th data-type="num">總價中位<span class="arrow">▲▼</span></th>
          <th data-type="num">建坪中位<span class="arrow">▲▼</span></th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
  </div>

  <div class="section-title">原始資料下載</div>
  <div class="download-card">
    <div style="font-size:14px;color:#1d1d1f">4 縣市預售屋全區排名（含解約篩除）：</div>
    <div class="download-grid">
      <a href="lvr-data/presale_ranking_w180.json">預售排名 JSON（近 180 天）</a>
    </div>
  </div>

  </div>
</section>

{aeo_faq_terms}
<!-- 5. 資料說明與免責（bt-tool 白底外框） -->
<section class="bt-sec bt-tool">
  <div class="bt-in">
  <div class="section-title">資料說明</div>
  <div class="notes">
    <h4>資料來源</h4>
    <ul>
      <li>內政部「不動產成交案件實際資訊」開放資料 _b.csv（預售屋備查）。</li>
      <li>已排除「解除契約」案件（建商解約者不計入有效成交）。</li>
      <li>每月 2/12/22 自動同步。</li>
    </ul>
    <h4 style="margin-top:14px">免責聲明</h4>
    <ul>
      <li>本頁為市場觀察，非投資建議。預售屋價格反映建商定價，與成屋成交價可能有結構性差距。</li>
      <li>本公司為融資租賃業者，非金融機構，最終核貸由金融機構決定。</li>
    </ul>
  </div>
  </div>
</section>

<div data-include="line-qr"></div>
<div data-include="footer"></div>
<div data-include="anti-fraud-modal"></div>

<script>
// chip filter + sortable table for presale
(function() {{
  const tbody = document.querySelector('#presaleTable tbody');
  const all = Array.from(tbody.querySelectorAll('tr'));
  let active = 'all';
  function apply() {{
    all.forEach(tr => tr.style.display = (active === 'all' || tr.dataset.city === active) ? '' : 'none');
  }}
  document.querySelectorAll('#presaleChips .city-chip').forEach(c => c.addEventListener('click', () => {{
    document.querySelectorAll('#presaleChips .city-chip').forEach(x => x.classList.remove('active'));
    c.classList.add('active'); active = c.dataset.city; apply();
  }}));
  document.querySelectorAll('#presaleTable th').forEach((th, idx) => {{
    let dir = 'desc';
    th.addEventListener('click', () => {{
      const type = th.dataset.type;
      const rows = Array.from(tbody.querySelectorAll('tr'));
      rows.sort((a, b) => {{
        let va = a.children[idx].dataset.sort ?? a.children[idx].innerText.trim();
        let vb = b.children[idx].dataset.sort ?? b.children[idx].innerText.trim();
        if (type === 'num') {{ va = parseFloat(va.replace(/,/g, '')) || 0; vb = parseFloat(vb.replace(/,/g, '')) || 0; }}
        return dir === 'asc' ? (va < vb ? -1 : va > vb ? 1 : 0) : (va > vb ? -1 : va < vb ? 1 : 0);
      }});
      rows.forEach(r => tbody.appendChild(r));
      document.querySelectorAll('#presaleTable th').forEach(t => t.classList.remove('sorted'));
      th.classList.add('sorted');
      dir = dir === 'asc' ? 'desc' : 'asc';
    }});
  }});
}})();
</script>
<script src="include.js" defer></script>
</body>
</html>"""


def render_rental_html(ranking: pd.DataFrame, generated_at: str) -> str:
    aeo_head = aeo_blocks.head_jsonld("rental", generated_at[:10])
    # Better 版型（2026-09-05）：字仍取自 aeo_blocks.PAGES（與 head JSON-LD 同源，改字要重過媽祖），只換外層標記
    aeo_quick = aeo_blocks.quick_answer_bt_html("rental")
    aeo_faq_terms = aeo_blocks.faq_terms_bt_html("rental")
    # 4 城市 KPI（月租每坪中位 + 平均報酬率）
    city_stats = []
    for city in CITIES:
        sub = ranking[ranking["縣市"] == city]
        sub_with_yield = sub.dropna(subset=["年化報酬率"])
        if sub.empty:
            continue
        city_stats.append({
            "city": city,
            "n": int(sub["n"].sum()),
            "rent_median": round(sub["月租每坪中位"].median(), 0),
            "yield_median": round(sub_with_yield["年化報酬率"].median(), 2) if not sub_with_yield.empty else None,
        })

    kpi_html = ""
    for c in city_stats:
        yield_text = f"{c['yield_median']:.2f}%" if c['yield_median'] is not None else "—"
        kpi_html += f"""<div class="kpi-card" style="border-top:4px solid {CITY_COLORS[c['city']]}">
            <div class="kpi-city">{c['city']}</div>
            <div class="kpi-value">{c['rent_median']:,.0f}<span class="kpi-unit">元/坪/月</span></div>
            <div class="kpi-label">月租每坪中位</div>
            <div class="kpi-sub">年化報酬率中位 <b>{yield_text}</b>　·　樣本 {c['n']:,}</div>
          </div>"""

    rows_html = ""
    for i, (_, r) in enumerate(ranking.iterrows(), 1):
        low = r["n"] < LOW_SAMPLE
        cls = ' class="low-sample"' if low else ""
        badge = ' <span class="badge-low">樣本少</span>' if low else ""
        y = r.get("年化報酬率")
        y_html = ('<td class="num">—</td>' if pd.isna(y)
                  else f'<td class="num" data-sort="{y}"><b>{y:.2f}%</b></td>')
        shop = r.get("店面月租中位")
        shop_n = r.get("店面n") or 0
        if pd.isna(shop) or shop_n < SHOP_MIN:
            shop_html = '<td class="num">—</td>'
        else:
            shop_badge = ' <span class="badge-low">樣本少</span>' if shop_n < LOW_SAMPLE else ''
            shop_html = f'<td class="num" data-sort="{shop}">{shop:,.0f}{shop_badge}</td>'
        rows_html += (
            f'<tr{cls} data-city="{r["縣市"]}">'
            f'<td class="num">{i}</td>'
            f'<td><b>{r["鄉鎮市區"]}</b>{badge}</td>'
            f'<td>{r["縣市"]}</td>'
            f'<td class="num" data-sort="{r["n"]}">{int(r["n"])}</td>'
            f'<td class="num" data-sort="{r["月租中位"]}">{r["月租中位"]:,.0f}</td>'
            f'{shop_html}'
            f'<td class="num" data-sort="{r["月租每坪中位"]}">{r["月租每坪中位"]:,.0f}</td>'
            f'<td class="num" data-sort="{r["建坪中位"]}">{r["建坪中位"]:.1f}</td>'
            f'{y_html}'
            f'</tr>'
        )

    return f"""<!--
  Page: 租金報酬 (LVR Rental Yield)
  Status: READY  Generated: {generated_at}
-->
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>租金報酬觀察｜雙北・台中・桃園 月租 + 年化報酬率｜鋮馨租賃</title>
<link rel="canonical" href="https://cx468.com.tw/lvr-rental.html">
<meta property="og:type" content="website">
<meta property="og:title" content="租金報酬觀察｜雙北・台中・桃園 月租 + 年化報酬率｜鋮馨租賃">
<meta property="og:description" content="台北、新北、台中、桃園四縣市租金實價登錄追蹤，含年化報酬率（年租/售價）估算。資料來源：內政部。">
<meta property="og:url" content="https://cx468.com.tw/lvr-rental.html">
<meta property="og:image" content="https://cx468.com.tw/img/hero.jpg">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Dataset","name":"租金報酬實價登錄觀察 — 雙北・台中・桃園","description":"台北、新北、台中、桃園四縣市租金實價登錄追蹤，含年化報酬率（年租/售價）估算，資料來源內政部不動產交易實價查詢服務網。","url":"https://cx468.com.tw/lvr-rental.html","keywords":["租金","實價登錄","年化報酬率","包租","台北","新北","台中","桃園"],"creator":{{"@type":"Organization","name":"鋮馨租賃有限公司","url":"https://cx468.com.tw/"}},"isBasedOn":"內政部不動產交易實價查詢服務網","spatialCoverage":{{"@type":"Place","name":"台北市、新北市、台中市、桃園市"}},"inLanguage":"zh-TW"}}
</script>
{aeo_head}
<meta name="description" content="台北、新北、台中、桃園四縣市租金實價登錄追蹤，含年化報酬率（年租 / 售價）估算。資料來源：內政部不動產交易實價查詢服務網。">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
{ga_block()}
<style>{common_styles()}</style>
<script>window.__cxMotionLoaded=true;/* 本頁不做捲動進場動畫（Better 對拷規格）：跳過 include.js 的 GSAP 載入 */</script>
</head>
<body>
<div id="nav" data-theme="light"></div>
<script src="nav.js"></script>

<!-- 1. Hero 左文右圖 -->
<section class="bt-hero bt-sec">
  <div class="bt-in bt-hero-grid">
    <div class="bt-hero-text">
      <div class="bt-eyebrow">租金報酬率</div>
      <h1 class="bt-h1">租金報酬觀察</h1>
      <p class="bt-label">Rental Yield Observation · 內政部實價登錄</p>
      <p class="bt-p">雙北 + 台中 + 桃園｜月租 + 年化報酬率</p>
      <p class="bt-small bt-meta">資料涵蓋 113Q1 ~ 115Q1 · {len(ranking)} 行政區 · 更新於 {generated_at}</p>
    </div>
    <img class="bt-hero-img" src="img/gen-zhonghe-slb.jpg" alt="社區公寓黃昏亮起的窗燈" width="1344" height="768" fetchpriority="high" loading="eager">
  </div>
</section>

<!-- 2. 租金報酬主體（資料區沿用原頁：id／class／data-* 與資料 JS 一字不改） -->
<section class="bt-sec bt-tool">
  <div class="bt-in">
{aeo_quick}

{family_nav("rental")}

  <div class="section-title">4 縣市租金與報酬率</div>
  <div class="kpi-grid">{kpi_html}</div>

  <div class="section-title">全區排名（近 180 天）</div>
  <div class="rank-card">
    <div class="rank-card-head">
      <h3>{len(ranking)} 區月租與報酬率</h3>
      <div class="city-chips" id="rentalChips">
        <button class="city-chip active" data-city="all">全部</button>
        <button class="city-chip" data-city="台北市">台北市</button>
        <button class="city-chip" data-city="新北市">新北市</button>
        <button class="city-chip" data-city="台中市">台中市</button>
        <button class="city-chip" data-city="桃園市">桃園市</button>
      </div>
    </div>
    <p class="rank-note">年化報酬率 = 月租每坪 × 12 ÷ 同區買賣中位售價（元/坪）× 100%。供參考估算，非保證投報。樣本 &lt; {LOW_SAMPLE} 標「樣本少」。「住家月租中位」為住家用整租月租；「店面月租中位」為建物型態店面／商業用整間月租（樣本 &lt; {SHOP_MIN} 以「—」表示）。</p>
    <div class="rank-table-wrap">
      <table class="rank-table" id="rentalTable">
        <thead><tr>
          <th data-type="num">排名<span class="arrow">▲▼</span></th>
          <th data-type="str">區別<span class="arrow">▲▼</span></th>
          <th data-type="str">縣市<span class="arrow">▲▼</span></th>
          <th data-type="num">樣本<span class="arrow">▲▼</span></th>
          <th data-type="num">住家月租中位<span class="arrow">▲▼</span></th>
          <th data-type="num">店面月租中位<span class="arrow">▲▼</span></th>
          <th data-type="num" class="sorted">月租每坪<span class="arrow">▼</span></th>
          <th data-type="num">建坪中位<span class="arrow">▲▼</span></th>
          <th data-type="num">年化報酬率<span class="arrow">▲▼</span></th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
  </div>

  <div class="section-title">原始資料下載</div>
  <div class="download-card">
    <div style="font-size:14px;color:#1d1d1f">4 縣市租屋全區排名（含年化報酬率）：</div>
    <div class="download-grid">
      <a href="lvr-data/rental_ranking_w180.json">租金排名 JSON（近 180 天）</a>
    </div>
  </div>

  </div>
</section>

{aeo_faq_terms}
<!-- 5. 資料說明與免責（bt-tool 白底外框） -->
<section class="bt-sec bt-tool">
  <div class="bt-in">
  <div class="section-title">資料說明</div>
  <div class="notes">
    <h4>資料來源</h4>
    <ul>
      <li>內政部「不動產租賃實際資訊」開放資料 _c.csv。</li>
      <li>住家月租為「總額元」欄位（已排除月租 &lt; 3,000 或 &gt; 200,000 異常值）。</li>
      <li>店面月租中位取建物型態含「店面」或主要用途含「商」之案件「總額元」（範圍 5,000 ~ 1,000,000），各區店面成交量普遍偏少，僅供概略參考。</li>
      <li>年化報酬率為估算，以住家月租計算，未計入房屋稅、地價稅、管理費、空置率等實質成本。</li>
    </ul>
    <h4 style="margin-top:14px">免責聲明</h4>
    <ul>
      <li>本頁為市場觀察，非投資建議。實際投報率依個案運營狀況、稅務與市場波動而定。</li>
      <li>本公司為融資租賃業者，非金融機構，最終核貸由金融機構決定。</li>
    </ul>
  </div>
  </div>
</section>

<div data-include="line-qr"></div>
<div data-include="footer"></div>
<div data-include="anti-fraud-modal"></div>

<script>
(function() {{
  const tbody = document.querySelector('#rentalTable tbody');
  const all = Array.from(tbody.querySelectorAll('tr'));
  let active = 'all';
  function apply() {{
    all.forEach(tr => tr.style.display = (active === 'all' || tr.dataset.city === active) ? '' : 'none');
  }}
  document.querySelectorAll('#rentalChips .city-chip').forEach(c => c.addEventListener('click', () => {{
    document.querySelectorAll('#rentalChips .city-chip').forEach(x => x.classList.remove('active'));
    c.classList.add('active'); active = c.dataset.city; apply();
  }}));
  document.querySelectorAll('#rentalTable th').forEach((th, idx) => {{
    let dir = 'desc';
    th.addEventListener('click', () => {{
      const type = th.dataset.type;
      const rows = Array.from(tbody.querySelectorAll('tr'));
      rows.sort((a, b) => {{
        let va = a.children[idx].dataset.sort ?? a.children[idx].innerText.trim();
        let vb = b.children[idx].dataset.sort ?? b.children[idx].innerText.trim();
        if (type === 'num') {{ va = parseFloat(va.replace(/,|%/g, '')) || 0; vb = parseFloat(vb.replace(/,|%/g, '')) || 0; }}
        return dir === 'asc' ? (va < vb ? -1 : va > vb ? 1 : 0) : (va > vb ? -1 : va < vb ? 1 : 0);
      }});
      rows.forEach(r => tbody.appendChild(r));
      document.querySelectorAll('#rentalTable th').forEach(t => t.classList.remove('sorted'));
      th.classList.add('sorted');
      dir = dir === 'asc' ? 'desc' : 'asc';
    }});
  }});
}})();
</script>
<script src="include.js" defer></script>
</body>
</html>"""


def main() -> None:
    DATA_DEST_DIR.mkdir(exist_ok=True)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 預售
    presale_pkl = OUT_DIR / "presale_ranking_w180.pkl"
    if presale_pkl.exists():
        presale = pd.read_pickle(presale_pkl)
        html = render_presale_html(presale, generated_at)
        dest = PRESALE_DEST
        dest.write_text(html, encoding="utf-8")
        copy2(OUT_DIR / "presale_ranking_w180.json", DATA_DEST_DIR / "presale_ranking_w180.json")
        print(f"✓ {dest.name}（{dest.stat().st_size // 1024} KB、{len(presale)} 區）")
    else:
        print("✗ 找不到 presale_ranking_w180.pkl，跑 analyze_extras.py")

    # 租屋
    rental_pkl = OUT_DIR / "rental_ranking_w180.pkl"
    if rental_pkl.exists():
        rental = pd.read_pickle(rental_pkl)
        html = render_rental_html(rental, generated_at)
        dest = RENTAL_DEST
        dest.write_text(html, encoding="utf-8")
        copy2(OUT_DIR / "rental_ranking_w180.json", DATA_DEST_DIR / "rental_ranking_w180.json")
        print(f"✓ {dest.name}（{dest.stat().st_size // 1024} KB、{len(rental)} 區）")
    else:
        print("✗ 找不到 rental_ranking_w180.pkl，跑 analyze_extras.py")


if __name__ == "__main__":
    main()
