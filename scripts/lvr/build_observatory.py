"""
生成 CX468/lvr-observatory.html v3：
- 5 精選 KPI cards（時間窗 toggle 改變數字）
- YoY 年增率 + 4 縣市趨勢
- 新店深度解析 spotlight (新)
- 區別比較 + 屋齡價值散布
- 4 縣市全區排名表（chip filter 切城市、時間窗 toggle 切窗口、欄位 sortable）
- GA gtag + 4 events
"""

from datetime import datetime, timedelta
from pathlib import Path
from shutil import copy2
import json

import pandas as pd

# Production paths (running from CX468/scripts/lvr/)
CX468_DIR = Path(__file__).resolve().parent.parent.parent
OUT_DIR = CX468_DIR / "scripts" / "lvr" / "_cache"
CHART_SRC_DIR = OUT_DIR / "charts"
CARDS_SRC_DIR = OUT_DIR / "social-cards"

CHART_DEST_DIR = CX468_DIR / "lvr-charts"
HTML_DEST = CX468_DIR / "lvr-observatory.html"
DATA_DEST_DIR = CX468_DIR / "lvr-data"
CARDS_DEST_DIR = CX468_DIR / "lvr-social-cards"

FOCUS_TOWNS = ["中和區", "永和區", "板橋區", "新店區", "土城區"]
COLORS = {
    "中和區": "#7C3AED", "永和區": "#2563EB", "板橋區": "#16A34A",
    "新店區": "#F59E0B", "土城區": "#EF4444",
}
CITIES = ["台北市", "新北市", "台中市", "桃園市"]
WINDOWS = [30, 90, 180, 365]
LOW_SAMPLE_THRESHOLD = 30
DEFAULT_WINDOW = 180


def load_window_data() -> dict:
    """讀回 4 窗 ranking + focus_kpis。"""
    data = {}
    for w in WINDOWS:
        rank_json = OUT_DIR / f"ranking_w{w}.json"
        focus_json = OUT_DIR / f"focus_kpis_w{w}.json"
        ranking = json.loads(rank_json.read_text(encoding="utf-8")) if rank_json.exists() else []
        focus = json.loads(focus_json.read_text(encoding="utf-8")) if focus_json.exists() else {}
        data[w] = {"ranking": ranking, "focus": focus}
    return data


def build_html(generated_at: str, season_label: str,
               window_data: dict, deep: dict) -> str:
    # 把 4 窗資料壓進一個 JS 物件
    data_json = json.dumps(window_data, ensure_ascii=False, default=str)
    n_districts_180 = len(window_data[180]["ranking"])

    return f"""<!--
  Page: 實價登錄觀察室 v3 (LVR Observatory)
  Status: READY
  Generated: {generated_at}
  Data source: 內政部不動產交易實價查詢服務網
-->
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>實價登錄觀察室 2026｜北中桃四縣市房價追蹤｜鋮馨租賃</title>
<meta name="description" content="台北市 + 新北市 + 台中市 + 桃園市 共 75 行政區實價登錄追蹤：時間窗 30/90/180/365 切換、YoY 年增率、跨縣市趨勢、新店區深度解析。每月 2/12/22 自動更新。">
<link rel="preload" href="style.css" as="style" onload="this.onload=null;this.rel='stylesheet'"><noscript><link rel="stylesheet" href="style.css"></noscript>

<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-4FX9LNEL7R"></script>
<script>
window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}
gtag('js',new Date());gtag('config','G-4FX9LNEL7R');
document.addEventListener('click',function(e){{var a=e.target.closest('a');if(!a||!a.href)return;
if(a.href.indexOf('lin.ee')>-1){{gtag('event','line_click',{{page_path:location.pathname,link_text:(a.innerText||'').trim().substring(0,50)}});}}
else if(a.href.indexOf('tel:')===0){{gtag('event','phone_click',{{page_path:location.pathname,phone_number:a.href.replace('tel:','')}});}}
else if(a.href.match(/\\.csv$/i)){{gtag('event','csv_download',{{page_path:location.pathname,file_name:decodeURIComponent(a.href.split('/').pop())}});}}
else if(a.closest('.cta-strip')){{gtag('event','cta_click',{{page_path:location.pathname,cta_text:(a.innerText||'').trim().substring(0,50),cta_url:a.href}});}}
}});
</script>

<style>
nav{{background:rgba(255,255,255,.92);backdrop-filter:blur(20px);border-bottom:.5px solid rgba(0,0,0,.08);padding:0 24px;height:60px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100}}
img.nav-logo{{height:44px;width:44px;object-fit:cover;border-radius:8px;border:1px solid rgba(0,0,0,.06)}}
.nav-back{{font-size:14px;color:#7C3AED;text-decoration:none;font-weight:500}}

.hero{{background:linear-gradient(135deg,#7C3AED 0%,#2563EB 60%,#16A34A 100%);padding:60px 24px 44px;text-align:center}}
.eyebrow{{font-size:12px;font-weight:600;color:rgba(255,255,255,.75);letter-spacing:.1em;text-transform:uppercase;margin-bottom:12px}}
.hero h1{{font-size:44px;font-weight:700;letter-spacing:-.03em;line-height:1.1;margin-bottom:14px;color:#fff}}
.hero p{{font-size:17px;color:rgba(255,255,255,.85);max-width:600px;margin:0 auto 6px}}
.hero .meta{{font-size:13px;color:rgba(255,255,255,.7);margin-top:14px}}
@media(max-width:768px){{.hero h1{{font-size:32px}}}}

.obs-wrap{{max-width:1120px;margin:40px auto;padding:0 20px 80px}}
.section-title{{font-size:13px;font-weight:700;color:#6e6e73;letter-spacing:.08em;text-transform:uppercase;margin:36px 0 14px 4px}}
.section-title:first-child{{margin-top:0}}

/* time toggle */
.window-toggle{{display:inline-flex;background:#f5f5f7;border-radius:10px;padding:3px;margin-left:12px;vertical-align:middle}}
.window-toggle button{{font-size:12px;font-weight:600;color:#6e6e73;background:transparent;border:none;padding:6px 12px;border-radius:8px;cursor:pointer;transition:all .2s}}
.window-toggle button.active{{background:#fff;color:#7C3AED;box-shadow:0 1px 3px rgba(0,0,0,.08)}}

.kpi-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px}}
@media(max-width:900px){{.kpi-grid{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:480px){{.kpi-grid{{grid-template-columns:1fr}}}}
.kpi-card{{background:#fff;border-radius:18px;padding:20px 18px;box-shadow:0 2px 12px rgba(0,0,0,.05)}}
.kpi-town{{font-size:14px;font-weight:700;color:#1d1d1f;margin-bottom:10px}}
.kpi-main{{margin-bottom:14px;padding-bottom:12px;border-bottom:1px solid #f0f0f3}}
.kpi-value{{font-size:30px;font-weight:700;color:#1d1d1f;letter-spacing:-.02em;line-height:1}}
.kpi-unit{{font-size:13px;font-weight:500;color:#6e6e73;margin-left:4px}}
.kpi-label{{font-size:11px;color:#6e6e73;margin-top:4px}}
.kpi-row{{display:flex;justify-content:space-between;font-size:12px;color:#1d1d1f;margin-bottom:5px}}
.kpi-row span{{color:#6e6e73}}
.kpi-change{{font-size:11px;color:#6e6e73;margin-top:10px;padding-top:10px;border-top:1px solid #f0f0f3}}
.kpi-empty{{font-size:13px;color:#6e6e73;text-align:center;padding:20px 0}}

.chart-card{{background:#fff;border-radius:18px;padding:24px;box-shadow:0 2px 12px rgba(0,0,0,.05);margin-bottom:18px}}
.chart-card h3{{font-size:16px;font-weight:600;color:#1d1d1f;margin:0 0 6px}}
.chart-card p.chart-note{{font-size:12px;color:#6e6e73;margin:0 0 14px;line-height:1.5}}
.chart-card img{{width:100%;height:auto;display:block;border-radius:10px}}
.chart-row{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:18px}}
@media(max-width:780px){{.chart-row{{grid-template-columns:1fr}}}}
.chart-row .chart-card{{margin-bottom:0}}

/* spotlight card */
.spotlight{{background:linear-gradient(135deg,#FEF3C7,#FECACA);border-radius:18px;padding:24px;margin-bottom:18px;border-left:6px solid #F59E0B}}
.spotlight-header{{font-size:11px;font-weight:700;color:#92400E;letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px}}
.spotlight h3{{font-size:18px;font-weight:700;color:#1d1d1f;margin:0 0 8px}}
.spotlight p.insight{{font-size:14px;color:#1d1d1f;line-height:1.7;margin:0 0 14px}}
.spotlight p.insight b{{color:#92400E}}

/* Ranking */
.rank-card{{background:#fff;border-radius:18px;padding:18px 4px;box-shadow:0 2px 12px rgba(0,0,0,.05);overflow:hidden}}
.rank-card-head{{display:flex;justify-content:space-between;align-items:center;padding:0 18px;margin-bottom:6px;flex-wrap:wrap;gap:10px}}
.rank-card h3{{font-size:16px;font-weight:600;color:#1d1d1f;margin:0}}
.rank-card p.rank-note{{font-size:12px;color:#6e6e73;margin:0 18px 14px;line-height:1.5}}
.city-chips{{display:flex;gap:6px;flex-wrap:wrap}}
.city-chip{{font-size:12px;font-weight:600;color:#6e6e73;background:#f5f5f7;padding:6px 12px;border-radius:980px;cursor:pointer;border:none;transition:all .2s}}
.city-chip.active{{background:#7C3AED;color:#fff}}
.rank-table-wrap{{overflow-x:auto}}
table.rank-table{{width:100%;border-collapse:collapse;font-size:13px;color:#1d1d1f;min-width:760px}}
.rank-table th{{background:#f5f5f7;color:#6e6e73;font-weight:600;text-align:left;padding:10px 12px;cursor:pointer;user-select:none;white-space:nowrap;border-bottom:1.5px solid #e8e8ed;position:sticky;top:0}}
.rank-table th:hover{{background:#ebebef;color:#1d1d1f}}
.rank-table th .arrow{{margin-left:4px;opacity:.4;font-size:10px}}
.rank-table th.sorted .arrow{{opacity:1;color:#7C3AED}}
.rank-table td{{padding:9px 12px;border-bottom:.5px solid #f0f0f3;white-space:nowrap}}
.rank-table td.num{{text-align:right;font-variant-numeric:tabular-nums}}
.rank-table tr.low-sample td{{color:#86868b}}
.rank-table tr:hover{{background:#fafafc}}
.badge-low{{display:inline-block;font-size:10px;color:#86868b;background:#f0f0f3;padding:1px 6px;border-radius:8px;margin-left:4px;font-weight:500}}
.empty-row td{{text-align:center;color:#86868b;padding:30px 0;font-style:italic}}

.download-card{{background:#f5f5f7;border-radius:16px;padding:24px}}
.download-grid{{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}}
.download-grid a{{font-size:13px;color:#1d1d1f;background:#fff;border:.5px solid #d2d2d7;padding:10px 16px;border-radius:980px;text-decoration:none;font-weight:500}}
.download-grid a:hover{{border-color:#7C3AED;color:#7C3AED}}

.notes{{background:#f5f5f7;border-radius:16px;padding:22px;font-size:13px;color:#1d1d1f;line-height:1.7}}
.notes h4{{font-size:14px;font-weight:700;margin:0 0 10px;color:#1d1d1f}}
.notes ul{{margin:0;padding-left:20px;color:#3a3a3c}}
.notes li{{margin-bottom:5px}}

.cta-strip{{background:linear-gradient(135deg,#7C3AED,#2563EB);color:#fff;padding:30px 24px;border-radius:18px;text-align:center;margin-top:28px}}
.cta-strip h2{{font-size:20px;font-weight:700;margin:0 0 8px;color:#fff}}
.cta-strip p{{font-size:14px;color:rgba(255,255,255,.85);margin:0 0 18px}}
.cta-strip a.btn-on-gradient{{display:inline-block;background:#fff;color:#7C3AED;font-weight:600;padding:10px 22px;border-radius:980px;text-decoration:none;font-size:14px;margin:0 6px}}
</style>
</head>
<body>

<div data-include="nav-tool"></div>

<div class="hero">
  <p class="eyebrow">LVR Observatory · v3</p>
  <h1>實價登錄觀察室</h1>
  <p>台北市 + 新北市 + 台中市 + 桃園市｜正常住宅成交追蹤</p>
  <p class="meta">資料涵蓋 113Q1 ~ {season_label}　·　全 {n_districts_180} 行政區（近 180 天）　·　更新於 {generated_at}</p>
</div>

<div class="obs-wrap">

  <div class="section-title">
    5 精選區當前快照
    <div class="window-toggle" data-target="kpi">
      <button data-w="30">30 天</button>
      <button data-w="90">90 天</button>
      <button data-w="180" class="active">180 天</button>
      <button data-w="365">365 天</button>
    </div>
  </div>
  <div class="kpi-grid" id="kpiGrid"></div>

  <div class="section-title">本期 Spotlight｜新店區深度解析</div>
  <div class="spotlight">
    <div class="spotlight-header">為何新店單價中位數下降？</div>
    <h3>不是房市衰退，是成交品結構改變</h3>
    <p class="insight">
      113Q1 → 115Q1 新店區成交筆數從 <b>{deep['113S1']['n']}</b> 降到 <b>{deep['115S1']['n']}</b>（{deep['delta']['n']:+d} 筆，成交量縮 {abs(deep['delta']['n'])*100//deep['113S1']['n']}%），
      單價中位數從 <b>{deep['113S1']['median']}</b> 降到 <b>{deep['115S1']['median']}</b> 萬/坪（{deep['delta']['median_pct']:+.1f}%）。
      但更關鍵的是 <b>屋齡中位數從 {deep['113S1']['median_age']} 年 → {deep['115S1']['median_age']} 年（+{deep['115S1']['median_age']-deep['113S1']['median_age']:.1f} 年）</b>——
      113 期由新成屋（重劃區開案）帶量，115 期新成屋移轉停止，老屋佔比上升，中位數自然回歸老屋常態值。
    </p>
  </div>
  <div class="chart-card">
    <h3>113Q1 vs 115Q1 結構對比</h3>
    <p class="chart-note">屋齡分布（左上）：新成屋（0–5 年）佔比從 36% 降到 23%、老屋（45+ 年）從 5% 升到 9%。建物型態（左下）：大樓佔比下降、公寓佔比上升。</p>
    <img src="lvr-charts/chart_shindian_deep.png" alt="新店區 113Q1 vs 115Q1 深度解析">
  </div>

  <div class="section-title">近 1 年單價變化（年增率 YoY）</div>
  <div class="chart-card">
    <h3>115Q1 vs 114Q1 單價中位數年增率</h3>
    <p class="chart-note">綠 = 上漲、紅 = 下跌。新店 -14.9% 看數字大但需結合上方深度解析看（屋齡結構變化所致）。</p>
    <img src="lvr-charts/chart_yoy_change.png" alt="5 精選區與雙北平均年增率 YoY">
  </div>

  <div class="section-title">4 縣市平均跨季趨勢</div>
  <div class="chart-card">
    <h3>台北 / 新北 / 台中 / 桃園 9 季均價</h3>
    <p class="chart-note">每點為該季全市正常住宅單價中位數，已排除特殊交易與極端值。</p>
    <img src="lvr-charts/chart_city_trend.png" alt="4 縣市全市平均跨季趨勢">
  </div>

  <div class="section-title">5 精選區比較（近 180 天）</div>
  <div class="chart-row">
    <div class="chart-card">
      <h3>單價中位數</h3>
      <p class="chart-note">中位數抗極端值，比平均數更能代表「典型成交」。</p>
      <img src="lvr-charts/chart_district_compare.png" alt="5 區單價中位數比較">
    </div>
    <div class="chart-card">
      <h3>單價分布（箱形圖）</h3>
      <p class="chart-note">盒子=中間 50% 區間；線=中位數；點=極端值。</p>
      <img src="lvr-charts/chart_price_boxplot.png" alt="5 區單價分布箱形圖">
    </div>
  </div>

  <div class="section-title">屋齡價值散布（雙北全區）</div>
  <div class="chart-card">
    <h3>屋齡 vs 單價（每點為一筆成交）</h3>
    <p class="chart-note">屋齡 0 年附近為新成屋／預售移轉。台北市（深色）整體價位高於新北市（紫色），但新北市新成屋與台北市老公寓部分價位帶有重疊。</p>
    <img src="lvr-charts/chart_age_price_scatter.png" alt="屋齡與單價散布圖">
  </div>

  <div class="section-title">交易量與結構（5 精選區）</div>
  <div class="chart-card">
    <h3>近 12 個月月成交量（5 區堆疊）</h3>
    <p class="chart-note">堆疊長條反映整體市場活躍度。最近 1~2 個月筆數會因資料延遲偏低。</p>
    <img src="lvr-charts/chart_monthly_volume.png" alt="近 12 個月月成交量">
  </div>
  <div class="chart-card">
    <h3>5 區建物型態組成（近 180 天）</h3>
    <p class="chart-note">公寓比例高 = 老舊社區為主；大樓比例高 = 重劃區為主。</p>
    <img src="lvr-charts/chart_building_types.png" alt="5 區建物型態組成">
  </div>

  <div class="section-title">
    全區排名表
    <div class="window-toggle" data-target="rank">
      <button data-w="30">30 天</button>
      <button data-w="90">90 天</button>
      <button data-w="180" class="active">180 天</button>
      <button data-w="365">365 天</button>
    </div>
  </div>
  <div class="rank-card">
    <div class="rank-card-head">
      <h3 id="rankHeading">行政區排名</h3>
      <div class="city-chips" id="cityChips">
        <button class="city-chip active" data-city="all">全部</button>
        <button class="city-chip" data-city="台北市">台北市</button>
        <button class="city-chip" data-city="新北市">新北市</button>
        <button class="city-chip" data-city="台中市">台中市</button>
        <button class="city-chip" data-city="桃園市">桃園市</button>
      </div>
    </div>
    <p class="rank-note">樣本 &lt; {LOW_SAMPLE_THRESHOLD} 筆者標「樣本少」；2 年漲幅 = 115Q1 vs 113Q1；1 年漲幅 = 115Q1 vs 114Q1（YoY）。</p>
    <div class="rank-table-wrap">
      <table class="rank-table" id="rankTable">
        <thead>
          <tr>
            <th data-key="__rank" data-type="num">排名<span class="arrow">▲▼</span></th>
            <th data-key="鄉鎮市區" data-type="str">區別<span class="arrow">▲▼</span></th>
            <th data-key="縣市" data-type="str">縣市<span class="arrow">▲▼</span></th>
            <th data-key="n" data-type="num">樣本<span class="arrow">▲▼</span></th>
            <th data-key="單價中位" data-type="num" class="sorted">單價中位<span class="arrow">▼</span></th>
            <th data-key="總價中位" data-type="num">總價中位<span class="arrow">▲▼</span></th>
            <th data-key="屋齡中位" data-type="num">屋齡中位<span class="arrow">▲▼</span></th>
            <th data-key="1年漲幅" data-type="num">1 年漲幅<span class="arrow">▲▼</span></th>
            <th data-key="2年漲幅" data-type="num">2 年漲幅<span class="arrow">▲▼</span></th>
          </tr>
        </thead>
        <tbody id="rankBody"></tbody>
      </table>
    </div>
  </div>

  <div class="section-title">本期社群圖卡（FB / IG / LINE 文章可用）</div>
  <div class="download-card">
    <div style="font-size:14px;color:#1d1d1f;margin-bottom:12px">6 張 1080×1350 圖卡，IG 輪播或 FB 相簿直接上傳：</div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">
      <a href="lvr-social-cards/card_1_hero.png" target="_blank" style="display:block;text-decoration:none"><img src="lvr-social-cards/card_1_hero.png" style="width:100%;border-radius:8px;display:block" alt="Card 1: Hero"><div style="font-size:11px;color:#6e6e73;text-align:center;margin-top:4px">1. 標題</div></a>
      <a href="lvr-social-cards/card_2_yoy.png" target="_blank" style="display:block;text-decoration:none"><img src="lvr-social-cards/card_2_yoy.png" style="width:100%;border-radius:8px;display:block" alt="Card 2: YoY"><div style="font-size:11px;color:#6e6e73;text-align:center;margin-top:4px">2. YoY 年增率</div></a>
      <a href="lvr-social-cards/card_3_city_trend.png" target="_blank" style="display:block;text-decoration:none"><img src="lvr-social-cards/card_3_city_trend.png" style="width:100%;border-radius:8px;display:block" alt="Card 3: trend"><div style="font-size:11px;color:#6e6e73;text-align:center;margin-top:4px">3. 縣市趨勢</div></a>
      <a href="lvr-social-cards/card_4_top_gain.png" target="_blank" style="display:block;text-decoration:none"><img src="lvr-social-cards/card_4_top_gain.png" style="width:100%;border-radius:8px;display:block" alt="Card 4: top"><div style="font-size:11px;color:#6e6e73;text-align:center;margin-top:4px">4. TOP 5 漲幅</div></a>
      <a href="lvr-social-cards/card_5_shindian.png" target="_blank" style="display:block;text-decoration:none"><img src="lvr-social-cards/card_5_shindian.png" style="width:100%;border-radius:8px;display:block" alt="Card 5: spotlight"><div style="font-size:11px;color:#6e6e73;text-align:center;margin-top:4px">5. 新店 Spotlight</div></a>
      <a href="lvr-social-cards/card_6_cta.png" target="_blank" style="display:block;text-decoration:none"><img src="lvr-social-cards/card_6_cta.png" style="width:100%;border-radius:8px;display:block" alt="Card 6: CTA"><div style="font-size:11px;color:#6e6e73;text-align:center;margin-top:4px">6. CTA</div></a>
    </div>
  </div>

  <div class="section-title">原始資料下載</div>
  <div class="download-card">
    <div style="font-size:14px;color:#1d1d1f;margin-bottom:4px"><b>5 精選區明細</b>（近 180 天，含地址、建物型態、坪數、屋齡、總價、單價）：</div>
    <div class="download-grid">
      <a href="lvr-data/中和區_正常住宅_近180天.csv">中和區 CSV</a>
      <a href="lvr-data/永和區_正常住宅_近180天.csv">永和區 CSV</a>
      <a href="lvr-data/板橋區_正常住宅_近180天.csv">板橋區 CSV</a>
      <a href="lvr-data/新店區_正常住宅_近180天.csv">新店區 CSV</a>
      <a href="lvr-data/土城區_正常住宅_近180天.csv">土城區 CSV</a>
    </div>
    <div style="font-size:14px;color:#1d1d1f;margin:18px 0 4px"><b>各時間窗全區排名</b>（4 縣市合計 {n_districts_180} 區）：</div>
    <div class="download-grid">
      <a href="lvr-data/排名_w30.json">30 天 JSON</a>
      <a href="lvr-data/排名_w90.json">90 天 JSON</a>
      <a href="lvr-data/排名_w180.json">180 天 JSON</a>
      <a href="lvr-data/排名_w365.json">365 天 JSON</a>
    </div>
  </div>

  <div class="section-title">資料說明與免責</div>
  <div class="notes">
    <h4>資料來源</h4>
    <ul>
      <li>內政部不動產交易實價查詢服務網（plvr.land.moi.gov.tw）開放資料。</li>
      <li>每月 1、11、21 日由內政部公告，本站於 2/12/22 自動同步（每月 3 次）。</li>
      <li>因登錄與公告流程，最新資料較實際交易日延遲約 30–50 天；30 天窗常顯示「無資料」屬正常。</li>
    </ul>
    <h4 style="margin-top:14px">「正常住宅」清洗規則</h4>
    <ul>
      <li>限 交易標的 = 房地（排除純車位、純土地）</li>
      <li>限 主要用途含「住」字（排除商業用、工業用、其他用途）</li>
      <li>排除備註含「親友、員工、共有人、特殊交易、瑕疵、急需處分、公益」之關係人交易</li>
      <li>排除總價 &lt; 100 萬、單價 &lt; 5 萬/坪、單價 &gt; 400 萬/坪 之極端值</li>
      <li>編號重複者保留首筆（mini-package 增量更新時 dedupe）</li>
    </ul>
    <h4 style="margin-top:14px">免責聲明</h4>
    <ul>
      <li>本頁資料整理自政府公開資料，僅作為市場觀察參考，<b>非投資建議</b>。</li>
      <li>實價登錄數字反映歷史成交，不代表未來市場走勢。</li>
      <li>實際房屋估值、可貸金額、利率等，依個案不動產條件、財務狀況與市場情況而定；本公司為融資租賃業者，非金融機構，最終核貸由金融機構決定。</li>
    </ul>
  </div>

  <div class="cta-strip">
    <h2>想知道你的房子在當前行情下能借多少？</h2>
    <p>用我們的二胎可貸額度試算，輸入市價與一胎本金即時看結果。</p>
    <a href="second-mortgage-calculator.html" class="btn-on-gradient">二胎額度試算 →</a>
    <a href="https://lin.ee/PHIfSoY" class="btn-on-gradient">LINE 線上諮詢</a>
  </div>

</div>

<section class="related-reads" style="max-width:1120px;margin:0 auto 40px;padding:0 24px">
  <div style="background:#f5f5f7;border-radius:16px;padding:28px 24px">
    <div style="font-size:12px;font-weight:600;color:#86868b;letter-spacing:.12em;text-transform:uppercase;margin-bottom:18px;text-align:center">延伸閱讀</div>
    <div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center">
      <a href="mortgage-calculator.html" style="font-size:14px;color:#1d1d1f;background:#fff;border:.5px solid #d2d2d7;padding:10px 18px;border-radius:980px;text-decoration:none;font-weight:500">一胎房貸試算 →</a>
      <a href="second-mortgage-calculator.html" style="font-size:14px;color:#1d1d1f;background:#fff;border:.5px solid #d2d2d7;padding:10px 18px;border-radius:980px;text-decoration:none;font-weight:500">二胎可貸額度 →</a>
      <a href="affordability-calculator.html" style="font-size:14px;color:#1d1d1f;background:#fff;border:.5px solid #d2d2d7;padding:10px 18px;border-radius:980px;text-decoration:none;font-weight:500">貸款負擔能力 →</a>
      <a href="tools.html" style="font-size:14px;color:#1d1d1f;background:#fff;border:.5px solid #d2d2d7;padding:10px 18px;border-radius:980px;text-decoration:none;font-weight:500">回工具總覽 →</a>
    </div>
  </div>
</section>

<div data-include="line-qr"></div>
<div data-include="footer"></div>
<div data-include="anti-fraud-modal"></div>

<script>
// 4 時間窗資料（embedded JSON）
const WINDOW_DATA = {data_json};
const FOCUS_TOWNS = {json.dumps(FOCUS_TOWNS, ensure_ascii=False)};
const COLORS = {json.dumps(COLORS, ensure_ascii=False)};

let state = {{
  kpiWindow: {DEFAULT_WINDOW},
  rankWindow: {DEFAULT_WINDOW},
  city: 'all',
  sort: {{key: '單價中位', dir: 'desc', type: 'num'}}
}};

function renderKPI() {{
  const focus = WINDOW_DATA[state.kpiWindow].focus;
  const grid = document.getElementById('kpiGrid');
  grid.innerHTML = FOCUS_TOWNS.map(t => {{
    const k = focus[t];
    const color = COLORS[t];
    if (!k) {{
      return '<div class="kpi-card" style="opacity:.5"><div class="kpi-town">'+t+'</div><div class="kpi-empty">本窗無資料</div></div>';
    }}
    const chg = k['2年漲幅'];
    let chgHtml = '—';
    if (chg !== null && chg !== undefined) {{
      const arrow = chg > 0 ? '▲' : (chg < 0 ? '▼' : '—');
      const c = chg > 0 ? '#16A34A' : (chg < 0 ? '#EF4444' : '#6e6e73');
      chgHtml = '<span style="color:'+c+';font-weight:700">'+arrow+' '+Math.abs(chg).toFixed(1)+'%</span>';
    }}
    return `
      <div class="kpi-card" style="border-top:4px solid ${{color}}">
        <div class="kpi-town">${{t}}</div>
        <div class="kpi-main">
          <div class="kpi-value">${{k['單價中位'].toFixed(1)}}<span class="kpi-unit">萬/坪</span></div>
          <div class="kpi-label">單價中位數</div>
        </div>
        <div class="kpi-row"><span>總價中位</span><b>${{k['總價中位'].toLocaleString('zh-TW')}} 萬</b></div>
        <div class="kpi-row"><span>建坪中位</span><b>${{k['建坪中位'].toFixed(1)}} 坪</b></div>
        <div class="kpi-row"><span>樣本</span><b>${{k['n']}} 筆</b></div>
        <div class="kpi-change">2 年變化 ${{chgHtml}}</div>
      </div>`;
  }}).join('');
}}

function renderRank() {{
  let rows = WINDOW_DATA[state.rankWindow].ranking;
  if (state.city !== 'all') {{
    rows = rows.filter(r => r['縣市'] === state.city);
  }}
  // sort
  const {{key, dir, type}} = state.sort;
  if (key !== '__rank') {{
    rows = [...rows].sort((a, b) => {{
      let va = a[key], vb = b[key];
      if (va === null || va === undefined) va = type === 'num' ? -Infinity : '';
      if (vb === null || vb === undefined) vb = type === 'num' ? -Infinity : '';
      if (va < vb) return dir === 'asc' ? -1 : 1;
      if (va > vb) return dir === 'asc' ? 1 : -1;
      return 0;
    }});
  }}
  const tbody = document.getElementById('rankBody');
  if (rows.length === 0) {{
    tbody.innerHTML = '<tr class="empty-row"><td colspan="9">本時間窗 / 縣市無資料（30 天窗常因資料延遲為空）</td></tr>';
    return;
  }}
  tbody.innerHTML = rows.map((r, i) => {{
    const low = r.n < {LOW_SAMPLE_THRESHOLD};
    const rowCls = low ? ' class="low-sample"' : '';
    const badge = low ? ' <span class="badge-low">樣本少</span>' : '';
    function pctCell(v) {{
      if (v === null || v === undefined) return '<td class="num">—</td>';
      const arrow = v > 0 ? '▲' : (v < 0 ? '▼' : '—');
      const c = v > 0 ? '#16A34A' : (v < 0 ? '#EF4444' : '#6e6e73');
      return `<td class="num" style="color:${{c}};font-weight:600">${{arrow}} ${{Math.abs(v).toFixed(1)}}%</td>`;
    }}
    const age = (r['屋齡中位'] === null || r['屋齡中位'] === undefined) ? '—' : r['屋齡中位'].toFixed(1);
    return `<tr${{rowCls}}>
      <td class="num">${{i+1}}</td>
      <td><b>${{r['鄉鎮市區']}}</b>${{badge}}</td>
      <td>${{r['縣市']}}</td>
      <td class="num">${{r.n}}</td>
      <td class="num">${{r['單價中位'].toFixed(1)}}</td>
      <td class="num">${{r['總價中位'].toLocaleString('zh-TW')}}</td>
      <td class="num">${{age}}</td>
      ${{pctCell(r['1年漲幅'])}}
      ${{pctCell(r['2年漲幅'])}}
    </tr>`;
  }}).join('');
  // update header sort indicators
  document.querySelectorAll('#rankTable th').forEach(th => {{
    const k = th.getAttribute('data-key');
    const arrow = th.querySelector('.arrow');
    if (k === state.sort.key) {{
      th.classList.add('sorted');
      if (arrow) arrow.textContent = state.sort.dir === 'asc' ? '▲' : '▼';
    }} else {{
      th.classList.remove('sorted');
      if (arrow) arrow.textContent = '▲▼';
    }}
  }});
  // update heading
  const cityLabel = state.city === 'all' ? '4 縣市' : state.city;
  document.getElementById('rankHeading').textContent = `${{cityLabel}}｜${{state.rankWindow}} 天｜${{rows.length}} 區`;
}}

// 綁定 toggle 按鈕
document.querySelectorAll('.window-toggle').forEach(group => {{
  const target = group.getAttribute('data-target');
  group.querySelectorAll('button').forEach(btn => {{
    btn.addEventListener('click', () => {{
      group.querySelectorAll('button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const w = parseInt(btn.getAttribute('data-w'));
      if (target === 'kpi') {{ state.kpiWindow = w; renderKPI(); }}
      else if (target === 'rank') {{ state.rankWindow = w; renderRank(); }}
    }});
  }});
}});

// 綁定 city chip
document.querySelectorAll('.city-chip').forEach(chip => {{
  chip.addEventListener('click', () => {{
    document.querySelectorAll('.city-chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    state.city = chip.getAttribute('data-city');
    renderRank();
  }});
}});

// 綁定 table 排序
document.querySelectorAll('#rankTable th').forEach(th => {{
  th.addEventListener('click', () => {{
    const key = th.getAttribute('data-key');
    const type = th.getAttribute('data-type') || 'str';
    let dir;
    if (state.sort.key === key) {{
      dir = state.sort.dir === 'asc' ? 'desc' : 'asc';
    }} else {{
      dir = type === 'num' ? 'desc' : 'asc';
    }}
    state.sort = {{key, dir, type}};
    renderRank();
  }});
}});

// 初始 render
renderKPI();
renderRank();
</script>

</body>
</html>
"""


def main() -> None:
    pkl = OUT_DIR / "clean_df.pkl"
    if not pkl.exists():
        raise SystemExit("✗ 先跑 analyze_lvr.py")

    df = pd.read_pickle(pkl)
    window_data = load_window_data()
    deep_pkl = OUT_DIR / "shindian_deep.pkl"
    deep = pd.read_pickle(deep_pkl)

    season_label = df["__season"].max().replace("S", "Q") if not df.empty else "?"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    html = build_html(generated_at, season_label, window_data, deep)

    CHART_DEST_DIR.mkdir(exist_ok=True)
    DATA_DEST_DIR.mkdir(exist_ok=True)
    CARDS_DEST_DIR.mkdir(exist_ok=True)

    # 清掉舊圖
    for old_name in ["chart_quarterly_trend.png"]:
        old = CHART_DEST_DIR / old_name
        if old.exists():
            old.unlink()

    n_charts = 0
    for png in CHART_SRC_DIR.glob("*.png"):
        copy2(png, CHART_DEST_DIR / png.name)
        n_charts += 1

    n_csv = 0
    for csv in OUT_DIR.glob("*_正常住宅_近180天.csv"):
        copy2(csv, DATA_DEST_DIR / csv.name)
        n_csv += 1
    # JSON 排名（4 窗）
    for w in WINDOWS:
        src = OUT_DIR / f"ranking_w{w}.json"
        if src.exists():
            copy2(src, DATA_DEST_DIR / f"排名_w{w}.json")
            n_csv += 1

    # 複製社群圖卡（若存在）
    n_cards = 0
    if CARDS_SRC_DIR.exists():
        for card in CARDS_SRC_DIR.glob("*.png"):
            copy2(card, CARDS_DEST_DIR / card.name)
            n_cards += 1

    HTML_DEST.write_text(html, encoding="utf-8")

    print(f"✓ 寫入 {HTML_DEST.name}（{HTML_DEST.stat().st_size // 1024} KB）")
    print(f"✓ 複製 {n_charts} 張圖表 → {CHART_DEST_DIR.name}/")
    print(f"✓ 複製 {n_csv} 個資料檔 → {DATA_DEST_DIR.name}/")
    print(f"✓ 複製 {n_cards} 張社群圖卡 → {CARDS_DEST_DIR.name}/")
    n180 = len(window_data[180]["ranking"])
    print(f"✓ 涵蓋 {n180} 行政區（180 天窗）、4 縣市、4 時間窗")


if __name__ == "__main__":
    main()
