"""
生成 CX468/lvr-observatory.html v2：
- 5 精選 KPI cards
- YoY 年增率長條 + 雙北平均趨勢
- 區別比較 + 屋齡價值散布
- 雙北全區排名表（sortable）
- CSV 下載 + 免責
- GA gtag + csv_download/cta_click events
"""

from datetime import datetime, timedelta
from pathlib import Path
from shutil import copy2

import pandas as pd

# Production paths (running from CX468/scripts/lvr/)
CX468_DIR = Path(__file__).resolve().parent.parent.parent
OUT_DIR = CX468_DIR / "scripts" / "lvr" / "_cache"
CHART_SRC_DIR = OUT_DIR / "charts"

CHART_DEST_DIR = CX468_DIR / "lvr-charts"
HTML_DEST = CX468_DIR / "lvr-observatory.html"
DATA_DEST_DIR = CX468_DIR / "lvr-data"

FOCUS_TOWNS = ["中和區", "永和區", "板橋區", "新店區", "土城區"]
COLORS = {
    "中和區": "#7C3AED", "永和區": "#2563EB", "板橋區": "#16A34A",
    "新店區": "#F59E0B", "土城區": "#EF4444",
}
LOOKBACK_DAYS = 180
LOW_SAMPLE_THRESHOLD = 30


def town_kpi(df_recent: pd.DataFrame, town: str) -> dict:
    sub = df_recent[df_recent["鄉鎮市區"] == town]
    if sub.empty:
        return {"n": 0}
    return {
        "n": len(sub),
        "unit_median": sub["單價_萬每坪"].median(),
        "total_median": sub["總價_萬"].median(),
        "ping_median": sub["建坪"].median(),
    }


def cross_quarter_change(df: pd.DataFrame, town: str):
    sub = df[df["鄉鎮市區"] == town]
    by_q = sub.groupby("__season")["單價_萬每坪"].median()
    if "113S1" not in by_q.index or "115S1" not in by_q.index:
        return None
    return round((by_q["115S1"] - by_q["113S1"]) / by_q["113S1"] * 100, 1)


def render_kpi_card(town: str, kpi: dict, change) -> str:
    color = COLORS[town]
    if kpi["n"] == 0:
        return (f'<div class="kpi-card" style="opacity:.5">'
                f'<div class="kpi-town">{town}</div>'
                f'<div class="kpi-empty">無近期資料</div></div>')
    if change is None:
        change_text = "—"
    else:
        arrow = "▲" if change > 0 else ("▼" if change < 0 else "—")
        c = "#16A34A" if change > 0 else ("#EF4444" if change < 0 else "#6e6e73")
        change_text = f'<span style="color:{c};font-weight:700">{arrow} {abs(change):.1f}%</span>'
    return f"""
    <div class="kpi-card" style="border-top:4px solid {color}">
      <div class="kpi-town">{town}</div>
      <div class="kpi-main">
        <div class="kpi-value">{kpi['unit_median']:.1f}<span class="kpi-unit">萬/坪</span></div>
        <div class="kpi-label">單價中位數</div>
      </div>
      <div class="kpi-row"><span>總價中位</span><b>{kpi['total_median']:,.0f} 萬</b></div>
      <div class="kpi-row"><span>建坪中位</span><b>{kpi['ping_median']:.1f} 坪</b></div>
      <div class="kpi-row"><span>近 6 月成交</span><b>{kpi['n']} 筆</b></div>
      <div class="kpi-change">2 年變化 {change_text}</div>
    </div>"""


def render_ranking_rows(ranking_df: pd.DataFrame) -> str:
    rows = []
    for rank, (_, r) in enumerate(ranking_df.iterrows(), 1):
        low = r["n"] < LOW_SAMPLE_THRESHOLD
        row_class = ' class="low-sample"' if low else ""
        # 漲幅顯示
        chg = r.get("2年漲幅")
        if pd.isna(chg) or chg is None:
            chg_html = '<td class="num">—</td>'
        else:
            arrow = "▲" if chg > 0 else ("▼" if chg < 0 else "—")
            c = "#16A34A" if chg > 0 else ("#EF4444" if chg < 0 else "#6e6e73")
            chg_html = f'<td class="num" data-sort="{chg}" style="color:{c};font-weight:600">{arrow} {abs(chg):.1f}%</td>'
        # 屋齡
        age = r.get("屋齡中位")
        age_html = "—" if (age is None or pd.isna(age)) else f"{age:.1f}"
        # 樣本少標註
        n_badge = ' <span class="badge-low">樣本少</span>' if low else ""
        rows.append(
            f'<tr{row_class}>'
            f'<td class="num">{rank}</td>'
            f'<td><b>{r["鄉鎮市區"]}</b>{n_badge}</td>'
            f'<td>{r["縣市"]}</td>'
            f'<td class="num" data-sort="{r["n"]}">{r["n"]}</td>'
            f'<td class="num" data-sort="{r["單價中位"]}">{r["單價中位"]:.1f}</td>'
            f'<td class="num" data-sort="{r["單價平均"]}">{r["單價平均"]:.1f}</td>'
            f'<td class="num" data-sort="{r["總價中位"]}">{r["總價中位"]:,.0f}</td>'
            f'<td class="num" data-sort="{age if age and not pd.isna(age) else -1}">{age_html}</td>'
            f'{chg_html}'
            f'</tr>'
        )
    return "\n      ".join(rows)


def build_html(kpi_html: str, ranking_rows: str, generated_at: str,
               season_label: str, total_recent: int, n_districts: int) -> str:
    return f"""<!--
  Page: 實價登錄觀察室 v2 (LVR Observatory)
  Status: READY
  Generated: {generated_at}
  Data source: 內政部不動產交易實價查詢服務網
-->
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>實價登錄觀察室 2026｜雙北 36 區房價追蹤｜鋮馨租賃</title>
<meta name="description" content="台北市 + 新北市 36 區實價登錄追蹤：單價中位數、年增率 YoY、跨季趨勢、屋齡價值散布。資料來源：內政部不動產交易實價查詢服務網。每月 2/12/22 自動更新。">
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

/* Ranking table */
.rank-card{{background:#fff;border-radius:18px;padding:18px 4px;box-shadow:0 2px 12px rgba(0,0,0,.05);overflow:hidden}}
.rank-card h3{{font-size:16px;font-weight:600;color:#1d1d1f;margin:0 18px 6px}}
.rank-card p.rank-note{{font-size:12px;color:#6e6e73;margin:0 18px 14px;line-height:1.5}}
.rank-table-wrap{{overflow-x:auto}}
table.rank-table{{width:100%;border-collapse:collapse;font-size:13px;color:#1d1d1f;min-width:680px}}
.rank-table th{{background:#f5f5f7;color:#6e6e73;font-weight:600;text-align:left;padding:10px 12px;cursor:pointer;user-select:none;white-space:nowrap;border-bottom:1.5px solid #e8e8ed;position:sticky;top:0}}
.rank-table th:hover{{background:#ebebef;color:#1d1d1f}}
.rank-table th .arrow{{margin-left:4px;opacity:.4;font-size:10px}}
.rank-table th.sorted .arrow{{opacity:1;color:#7C3AED}}
.rank-table td{{padding:9px 12px;border-bottom:.5px solid #f0f0f3;white-space:nowrap}}
.rank-table td.num{{text-align:right;font-variant-numeric:tabular-nums}}
.rank-table tr.low-sample td{{color:#86868b}}
.rank-table tr:hover{{background:#fafafc}}
.badge-low{{display:inline-block;font-size:10px;color:#86868b;background:#f0f0f3;padding:1px 6px;border-radius:8px;margin-left:4px;font-weight:500}}

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
  <p class="eyebrow">LVR Observatory · v2</p>
  <h1>實價登錄觀察室</h1>
  <p>台北市 + 新北市 36 區｜正常住宅成交資料追蹤</p>
  <p class="meta">資料涵蓋 113Q1 ~ {season_label}　·　近 6 月有效樣本 {total_recent:,} 筆　·　涵蓋 {n_districts} 個行政區　·　更新於 {generated_at}</p>
</div>

<div class="obs-wrap">

  <div class="section-title">5 精選區當前快照（近 180 天 正常住宅）</div>
  <div class="kpi-grid">
{kpi_html}
  </div>

  <div class="section-title">近 1 年單價變化（年增率 YoY）</div>
  <div class="chart-card">
    <h3>115Q1 vs 114Q1 單價中位數年增率</h3>
    <p class="chart-note">綠 = 上漲、紅 = 下跌。比較同季別（去年同期 vs 今年）避開季節性偏差，比跨季更能反映真實趨勢。</p>
    <img src="lvr-charts/chart_yoy_change.png" alt="5 精選區與雙北平均年增率 YoY">
  </div>

  <div class="section-title">雙北全市平均跨季趨勢</div>
  <div class="chart-card">
    <h3>台北市 vs 新北市 9 季均價</h3>
    <p class="chart-note">每點為該季全市正常住宅單價中位數，已排除特殊交易與極端值。</p>
    <img src="lvr-charts/chart_city_trend.png" alt="雙北全市平均跨季趨勢">
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
      <p class="chart-note">盒子=中間 50% 區間；線=中位數；點=極端值。盒子愈高代表單價差異愈大。</p>
      <img src="lvr-charts/chart_price_boxplot.png" alt="5 區單價分布箱形圖">
    </div>
  </div>

  <div class="section-title">屋齡價值散布（雙北全區）</div>
  <div class="chart-card">
    <h3>屋齡 vs 單價（每點為一筆成交）</h3>
    <p class="chart-note">屋齡 0 年附近為新成屋／預售移轉；30 年以上多為老公寓。台北市（深色）整體價位高於新北市（紫色），但新北市新成屋與台北市老公寓部分價位帶有重疊。</p>
    <img src="lvr-charts/chart_age_price_scatter.png" alt="屋齡與單價散布圖">
  </div>

  <div class="section-title">交易量與結構（5 精選區）</div>
  <div class="chart-card">
    <h3>近 12 個月月成交量（5 區堆疊）</h3>
    <p class="chart-note">堆疊長條反映整體市場活躍度。內政部 open data 發布有 30–50 天延遲，最近 1~2 個月筆數會偏低。</p>
    <img src="lvr-charts/chart_monthly_volume.png" alt="近 12 個月月成交量堆疊長條">
  </div>
  <div class="chart-card">
    <h3>5 區建物型態組成（近 180 天）</h3>
    <p class="chart-note">公寓比例高 = 老舊社區為主；大樓比例高 = 重劃區為主。對應地段與屋齡偏好。</p>
    <img src="lvr-charts/chart_building_types.png" alt="5 區建物型態組成堆疊長條">
  </div>

  <div class="section-title">雙北全區排名表（近 180 天）</div>
  <div class="rank-card">
    <h3>{n_districts} 個行政區排名</h3>
    <p class="rank-note">點欄位標題排序。樣本 &lt; {LOW_SAMPLE_THRESHOLD} 筆者標「樣本少」、僅供參考；2 年漲幅 = 115Q1 vs 113Q1 單價中位數變化。</p>
    <div class="rank-table-wrap">
      <table class="rank-table" id="rankTable">
        <thead>
          <tr>
            <th data-sort-type="num" data-sort-default="asc">排名<span class="arrow">▲▼</span></th>
            <th data-sort-type="str">區別<span class="arrow">▲▼</span></th>
            <th data-sort-type="str">縣市<span class="arrow">▲▼</span></th>
            <th data-sort-type="num">樣本<span class="arrow">▲▼</span></th>
            <th data-sort-type="num" class="sorted" data-sort-default="desc">單價中位<span class="arrow">▼</span></th>
            <th data-sort-type="num">單價平均<span class="arrow">▲▼</span></th>
            <th data-sort-type="num">總價中位<span class="arrow">▲▼</span></th>
            <th data-sort-type="num">屋齡中位<span class="arrow">▲▼</span></th>
            <th data-sort-type="num">2 年漲幅<span class="arrow">▲▼</span></th>
          </tr>
        </thead>
        <tbody>
      {ranking_rows}
        </tbody>
      </table>
    </div>
  </div>

  <div class="section-title">原始資料下載</div>
  <div class="download-card">
    <div style="font-size:14px;color:#1d1d1f;margin-bottom:4px"><b>5 精選區明細</b>（近 180 天，含地址、建物型態、坪數、總價、單價、屋齡、格局、樓層）：</div>
    <div class="download-grid">
      <a href="lvr-data/中和區_正常住宅_近180天.csv">中和區 CSV</a>
      <a href="lvr-data/永和區_正常住宅_近180天.csv">永和區 CSV</a>
      <a href="lvr-data/板橋區_正常住宅_近180天.csv">板橋區 CSV</a>
      <a href="lvr-data/新店區_正常住宅_近180天.csv">新店區 CSV</a>
      <a href="lvr-data/土城區_正常住宅_近180天.csv">土城區 CSV</a>
    </div>
    <div style="font-size:14px;color:#1d1d1f;margin:18px 0 4px"><b>雙北全區排名</b>：</div>
    <div class="download-grid">
      <a href="lvr-data/雙北全區排名_近180天.csv">36 區排名 CSV</a>
    </div>
  </div>

  <div class="section-title">資料說明與免責</div>
  <div class="notes">
    <h4>資料來源</h4>
    <ul>
      <li>內政部不動產交易實價查詢服務網（plvr.land.moi.gov.tw）開放資料。</li>
      <li>每月 1、11、21 日由內政部公告，本站於 2/12/22 自動同步（每月 3 次）。</li>
      <li>因登錄與公告流程，最新資料較實際交易日延遲約 30–50 天。</li>
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
// Sortable ranking table
(function() {{
  var table = document.getElementById('rankTable');
  if (!table) return;
  var tbody = table.querySelector('tbody');
  var headers = table.querySelectorAll('th');
  var currentSort = {{col: 4, dir: 'desc'}};  // 預設按單價中位 desc

  function sortBy(col, type, dir) {{
    var rows = Array.from(tbody.querySelectorAll('tr'));
    rows.sort(function(a, b) {{
      var ca = a.children[col];
      var cb = b.children[col];
      var va = ca.getAttribute('data-sort') !== null ? ca.getAttribute('data-sort') : ca.innerText.trim();
      var vb = cb.getAttribute('data-sort') !== null ? cb.getAttribute('data-sort') : cb.innerText.trim();
      if (type === 'num') {{
        va = parseFloat(va.replace(/,/g,'')) || 0;
        vb = parseFloat(vb.replace(/,/g,'')) || 0;
      }}
      if (va < vb) return dir === 'asc' ? -1 : 1;
      if (va > vb) return dir === 'asc' ? 1 : -1;
      return 0;
    }});
    rows.forEach(function(r) {{ tbody.appendChild(r); }});
    headers.forEach(function(h, i) {{
      h.classList.toggle('sorted', i === col);
      var arrow = h.querySelector('.arrow');
      if (arrow) arrow.textContent = (i === col) ? (dir === 'asc' ? '▲' : '▼') : '▲▼';
    }});
    currentSort = {{col: col, dir: dir}};
  }}

  headers.forEach(function(h, i) {{
    h.addEventListener('click', function() {{
      var type = h.getAttribute('data-sort-type') || 'str';
      var defaultDir = h.getAttribute('data-sort-default') || (type === 'num' ? 'desc' : 'asc');
      var dir = (currentSort.col === i)
        ? (currentSort.dir === 'asc' ? 'desc' : 'asc')
        : defaultDir;
      sortBy(i, type, dir);
    }});
  }});
}})();
</script>

</body>
</html>
"""


def main() -> None:
    pkl = OUT_DIR / "clean_df.pkl"
    rank_pkl = OUT_DIR / "ranking_recent.pkl"
    if not pkl.exists() or not rank_pkl.exists():
        raise SystemExit("✗ 先跑 analyze_lvr.py")

    df = pd.read_pickle(pkl)
    ranking = pd.read_pickle(rank_pkl)

    cutoff = datetime.now() - timedelta(days=LOOKBACK_DAYS)
    df_recent = df[df["交易日期"] >= cutoff].copy()

    kpi_html = ""
    for town in FOCUS_TOWNS:
        kpi = town_kpi(df_recent, town)
        change = cross_quarter_change(df, town)
        kpi_html += render_kpi_card(town, kpi, change) + "\n"

    ranking_rows = render_ranking_rows(ranking)

    season_label = df["__season"].max().replace("S", "Q") if not df.empty else "?"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    n_districts = len(ranking)
    html = build_html(kpi_html, ranking_rows, generated_at, season_label, len(df_recent), n_districts)

    CHART_DEST_DIR.mkdir(exist_ok=True)
    DATA_DEST_DIR.mkdir(exist_ok=True)

    # 清掉舊圖（防止舊 chart_quarterly_trend.png 殘留）
    old = CHART_DEST_DIR / "chart_quarterly_trend.png"
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
    for csv in OUT_DIR.glob("雙北全區排名_*.csv"):
        copy2(csv, DATA_DEST_DIR / csv.name)
        n_csv += 1

    HTML_DEST.write_text(html, encoding="utf-8")

    print(f"✓ 寫入 {HTML_DEST.name}（{HTML_DEST.stat().st_size // 1024} KB）")
    print(f"✓ 複製 {n_charts} 張圖表 → {CHART_DEST_DIR.name}/")
    print(f"✓ 複製 {n_csv} 個 CSV → {DATA_DEST_DIR.name}/")
    print(f"✓ 涵蓋 {n_districts} 行政區、{len(df_recent):,} 筆近 180 天樣本")


if __name__ == "__main__":
    main()
