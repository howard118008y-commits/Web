"""
產出 lvr-presale.html (預售屋) + lvr-rental.html (租屋報酬率)
兩頁使用相同 hero+ranking table 結構（共用 CSS class）。
"""

from datetime import datetime
from pathlib import Path
from shutil import copy2
import json

import pandas as pd

# Production paths
CX468_DIR = Path(__file__).resolve().parent.parent.parent
OUT_DIR = CX468_DIR / "scripts" / "lvr" / "_cache"
DATA_DEST_DIR = CX468_DIR / "lvr-data"
LOW_SAMPLE = 30
SHOP_MIN = 5  # 店面樣本低於此值不顯示中位（太少不具參考性）

CITIES = ["台北市", "新北市", "台中市", "桃園市"]
CITY_COLORS = {"台北市": "#0F172A", "新北市": "#7C3AED",
               "台中市": "#16A34A", "桃園市": "#F59E0B"}


def common_styles() -> str:
    return """
nav{background:rgba(255,255,255,.92);backdrop-filter:blur(20px);border-bottom:.5px solid rgba(0,0,0,.08);padding:0 24px;height:60px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100}
img.nav-logo{height:44px;width:44px;object-fit:cover;border-radius:8px;border:1px solid rgba(0,0,0,.06)}
.nav-back{font-size:14px;color:#7C3AED;text-decoration:none;font-weight:500}

.hero{padding:60px 24px 44px;text-align:center;color:#fff}
.eyebrow{font-size:12px;font-weight:600;color:rgba(255,255,255,.75);letter-spacing:.1em;text-transform:uppercase;margin-bottom:12px}
.hero h1{font-size:44px;font-weight:700;letter-spacing:-.03em;line-height:1.1;margin-bottom:14px;color:#fff}
.hero p{font-size:17px;color:rgba(255,255,255,.85);max-width:600px;margin:0 auto 6px}
.hero .meta{font-size:13px;color:rgba(255,255,255,.7);margin-top:14px}
@media(max-width:768px){.hero h1{font-size:32px}}

.obs-wrap{max-width:1120px;margin:40px auto;padding:0 20px 80px}
.section-title{font-size:13px;font-weight:700;color:#6e6e73;letter-spacing:.08em;text-transform:uppercase;margin:36px 0 14px 4px}
.section-title:first-child{margin-top:0}

/* family nav */
.family-nav{display:flex;gap:8px;padding:14px 18px;background:#f5f5f7;border-radius:12px;margin-bottom:14px;flex-wrap:wrap}
.family-nav a{font-size:13px;font-weight:600;color:#6e6e73;text-decoration:none;padding:8px 14px;border-radius:980px;background:transparent;transition:all .2s}
.family-nav a:hover{background:#fff;color:#1d1d1f}
.family-nav a.active{background:#7C3AED;color:#fff}

/* top KPIs (city) */
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:24px}
@media(max-width:780px){.kpi-grid{grid-template-columns:repeat(2,1fr)}}
.kpi-card{background:#fff;border-radius:18px;padding:20px 18px;box-shadow:0 2px 12px rgba(0,0,0,.05)}
.kpi-city{font-size:12px;font-weight:700;color:#1d1d1f;margin-bottom:10px;letter-spacing:.04em}
.kpi-value{font-size:28px;font-weight:700;color:#1d1d1f;letter-spacing:-.02em;line-height:1}
.kpi-unit{font-size:12px;font-weight:500;color:#6e6e73;margin-left:4px}
.kpi-label{font-size:11px;color:#6e6e73;margin-top:4px}
.kpi-sub{font-size:11px;color:#6e6e73;margin-top:10px;padding-top:10px;border-top:1px solid #f0f0f3}

/* Ranking */
.rank-card{background:#fff;border-radius:18px;padding:18px 4px;box-shadow:0 2px 12px rgba(0,0,0,.05);overflow:hidden}
.rank-card-head{display:flex;justify-content:space-between;align-items:center;padding:0 18px;margin-bottom:6px;flex-wrap:wrap;gap:10px}
.rank-card h3{font-size:16px;font-weight:600;color:#1d1d1f;margin:0}
.rank-card p.rank-note{font-size:12px;color:#6e6e73;margin:0 18px 14px;line-height:1.5}
.city-chips{display:flex;gap:6px;flex-wrap:wrap}
.city-chip{font-size:12px;font-weight:600;color:#6e6e73;background:#f5f5f7;padding:6px 12px;border-radius:980px;cursor:pointer;border:none;transition:all .2s}
.city-chip.active{background:#7C3AED;color:#fff}
.rank-table-wrap{overflow-x:auto}
table.rank-table{width:100%;border-collapse:collapse;font-size:13px;color:#1d1d1f;min-width:680px}
.rank-table th{background:#f5f5f7;color:#6e6e73;font-weight:600;text-align:left;padding:10px 12px;cursor:pointer;user-select:none;white-space:nowrap;border-bottom:1.5px solid #e8e8ed}
.rank-table th:hover{background:#ebebef;color:#1d1d1f}
.rank-table th .arrow{margin-left:4px;opacity:.4;font-size:10px}
.rank-table th.sorted .arrow{opacity:1;color:#7C3AED}
.rank-table td{padding:9px 12px;border-bottom:.5px solid #f0f0f3;white-space:nowrap}
.rank-table td.num{text-align:right;font-variant-numeric:tabular-nums}
.rank-table tr.low-sample td{color:#86868b}
.rank-table tr:hover{background:#fafafc}
.badge-low{display:inline-block;font-size:10px;color:#86868b;background:#f0f0f3;padding:1px 6px;border-radius:8px;margin-left:4px;font-weight:500}

.download-card{background:#f5f5f7;border-radius:16px;padding:24px}
.download-grid{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}
.download-grid a{font-size:13px;color:#1d1d1f;background:#fff;border:.5px solid #d2d2d7;padding:10px 16px;border-radius:980px;text-decoration:none;font-weight:500}
.download-grid a:hover{border-color:#7C3AED;color:#7C3AED}

.notes{background:#f5f5f7;border-radius:16px;padding:22px;font-size:13px;color:#1d1d1f;line-height:1.7}
.notes h4{font-size:14px;font-weight:700;margin:0 0 10px;color:#1d1d1f}
.notes ul{margin:0;padding-left:20px;color:#3a3a3c}
.notes li{margin-bottom:5px}
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
<meta name="description" content="台北、新北、台中、桃園四縣市 預售屋實價登錄單價追蹤。資料來源：內政部不動產交易實價查詢服務網。每月 2/12/22 自動更新。">
<link rel="preload" href="style.css" as="style" onload="this.onload=null;this.rel='stylesheet'"><noscript><link rel="stylesheet" href="style.css"></noscript>
{ga_block()}
<style>{common_styles()}
.hero{{background:linear-gradient(135deg,#0EA5E9 0%,#7C3AED 60%,#EC4899 100%)}}
</style>
</head>
<body>
<div data-include="nav-tool"></div>
<div class="hero">
  <p class="eyebrow">Presale Observation</p>
  <h1>預售屋觀察</h1>
  <p>雙北 + 台中 + 桃園｜預售案件實價單價追蹤</p>
  <p class="meta">資料涵蓋 113Q1 ~ 115Q1　·　{len(ranking)} 行政區　·　更新於 {generated_at}</p>
</div>

<div class="obs-wrap">
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
</body>
</html>"""


def render_rental_html(ranking: pd.DataFrame, generated_at: str) -> str:
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
<meta name="description" content="台北、新北、台中、桃園四縣市租金實價登錄追蹤，含年化報酬率（年租 / 售價）估算。資料來源：內政部不動產交易實價查詢服務網。">
<link rel="preload" href="style.css" as="style" onload="this.onload=null;this.rel='stylesheet'"><noscript><link rel="stylesheet" href="style.css"></noscript>
{ga_block()}
<style>{common_styles()}
.hero{{background:linear-gradient(135deg,#16A34A 0%,#0EA5E9 60%,#7C3AED 100%)}}
</style>
</head>
<body>
<div data-include="nav-tool"></div>
<div class="hero">
  <p class="eyebrow">Rental Yield Observation</p>
  <h1>租金報酬觀察</h1>
  <p>雙北 + 台中 + 桃園｜月租 + 年化報酬率</p>
  <p class="meta">資料涵蓋 113Q1 ~ 115Q1　·　{len(ranking)} 行政區　·　更新於 {generated_at}</p>
</div>

<div class="obs-wrap">
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
        dest = CX468_DIR / "lvr-presale.html"
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
        dest = CX468_DIR / "lvr-rental.html"
        dest.write_text(html, encoding="utf-8")
        copy2(OUT_DIR / "rental_ranking_w180.json", DATA_DEST_DIR / "rental_ranking_w180.json")
        print(f"✓ {dest.name}（{dest.stat().st_size // 1024} KB、{len(rental)} 區）")
    else:
        print("✗ 找不到 rental_ranking_w180.pkl，跑 analyze_extras.py")


if __name__ == "__main__":
    main()
