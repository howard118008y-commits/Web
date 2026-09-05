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
from html import escape as html_escape
import json
import os
import re
import aeo_blocks

import pandas as pd

# Production paths (running from CX468/scripts/lvr/)
CX468_DIR = Path(__file__).resolve().parent.parent.parent
OUT_DIR = CX468_DIR / "scripts" / "lvr" / "_cache"
CHART_SRC_DIR = OUT_DIR / "charts"
CARDS_SRC_DIR = OUT_DIR / "social-cards"

CHART_DEST_DIR = CX468_DIR / "lvr-charts"
HTML_DEST = Path(os.environ.get("LVR_HTML_DEST", CX468_DIR / "lvr-observatory.html"))
DATA_DEST_DIR = CX468_DIR / "lvr-data"
CARDS_DEST_DIR = CX468_DIR / "lvr-social-cards"
AI_REPORT_PATH = CX468_DIR / "lvr-data" / "週報_最新.txt"

FOCUS_TOWNS = ["中和區", "永和區", "板橋區", "新店區", "土城區"]
COLORS = {
    "中和區": "#c8102e", "永和區": "#D4AF37", "板橋區": "#1d1d1f",
    "新店區": "#2563EB", "土城區": "#0EA5E9",
}
# 卡片超連結到區域百科頁（slug 須與 scripts/build_area_pages.py 一致）
AREA_SLUG = {
    "中和區": "zhonghe", "永和區": "yonghe", "板橋區": "banqiao",
    "新店區": "xindian", "土城區": "tucheng",
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


def load_ai_report() -> str:
    """讀 AI 週報純文字檔（若存在）。"""
    if AI_REPORT_PATH.exists():
        text = AI_REPORT_PATH.read_text(encoding="utf-8").strip()
        return text
    return ""


def build_html(generated_at: str, season_label: str,
               window_data: dict, deep: dict, ai_report: str = "") -> str:
    # AEO 區塊（schema 與可見同源，見 aeo_blocks.py；改字須重過媽祖）
    aeo_head = aeo_blocks.head_jsonld("observatory", generated_at[:10])
    # Better 版型（2026-09-05）：快速答案／名詞解釋／FAQ 的字仍取自 aeo_blocks.PAGES
    # （與 head JSON-LD 同源，改字要重過媽祖），此處只換外層標記，不用 aeo_blocks 的舊版 html helper
    aeo_page = aeo_blocks.PAGES["observatory"]
    quick_head, quick_text = aeo_page["quick"]
    aeo_quick = (f'<div id="quick-answer" class="bt-card bt-qa">\n'
                 f'  <h4>快速答案｜{quick_head}</h4>\n  <p style="margin:0">{quick_text}</p>\n</div>')
    terms_html = "\n".join(
        f'      <div class="bt-term"><strong>{t}</strong><span>：{d}</span></div>'
        for t, d in aeo_page["terms"])
    faq_html = "\n".join(
        f'    <details{" open" if i == 0 else ""}>\n'
        f'      <summary><h3>{q}</h3></summary>\n'
        f'      <p>{a}</p>\n'
        f'    </details>'
        for i, (q, a) in enumerate(aeo_page["faqs"]))
    aeo_faq_terms = f"""<!-- 3. 名詞解釋（與 DefinedTermSet JSON-LD 同源） -->
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

    # 把 4 窗資料壓進一個 JS 物件
    data_json = json.dumps(window_data, ensure_ascii=False, default=str)
    n_districts_180 = len(window_data[180]["ranking"])

    # AI 摘要 section（若有）
    ai_section_html = ""
    if ai_report:
        # 轉成 HTML 段落（AI 回來的是 markdown，**粗體** 要轉 <strong>，
        # 否則星號會原樣印在頁面上——2026-08-03 目檢實際踩到）
        def _md_inline(p):
            s = html_escape(p, quote=False)
            return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)

        paragraphs = [p.strip() for p in ai_report.split("\n") if p.strip()]
        para_html = "".join(f"<p>{_md_inline(p)}</p>" for p in paragraphs)
        ai_section_html = f"""
  <div class="section-title">本期 AI 摘要</div>
  <div class="ai-card">
    <div class="ai-badge">✨ Claude AI 自動產生</div>
    {para_html}
  </div>"""

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
<link rel="canonical" href="https://cx468.com.tw/lvr-observatory.html">
<meta property="og:type" content="website">
<meta property="og:title" content="實價登錄觀察室 2026｜北中桃四縣市房價追蹤｜鋮馨租賃">
<meta property="og:description" content="台北市+新北市+台中市+桃園市各行政區實價登錄追蹤：YoY 年增率、跨縣市趨勢、新店區深度解析，每月更新。">
<meta property="og:url" content="https://cx468.com.tw/lvr-observatory.html">
<meta property="og:image" content="https://cx468.com.tw/lvr-charts/chart_city_trend.png">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Dataset","name":"實價登錄觀察室 — 台北・新北・台中・桃園 住宅成交追蹤","description":"涵蓋台北市、新北市、台中市、桃園市各行政區的內政部實價登錄正常住宅成交資料，提供單價中位數、YoY 年增率、跨縣市跨季趨勢與行政區排名，每月2/12/22更新。","url":"https://cx468.com.tw/lvr-observatory.html","keywords":["實價登錄","房價","單價中位數","年增率","台北市","新北市","台中市","桃園市"],"creator":{{"@type":"Organization","name":"鋮馨租賃有限公司","url":"https://cx468.com.tw/"}},"isBasedOn":"內政部不動產交易實價查詢服務網","spatialCoverage":{{"@type":"Place","name":"台北市、新北市、台中市、桃園市"}},"license":"https://cx468.com.tw/","inLanguage":"zh-TW"}}
</script>
{aeo_head}
<meta name="description" content="台北市 + 新北市 + 台中市 + 桃園市 各行政區實價登錄追蹤：時間窗 30/90/180/365 切換、YoY 年增率、跨縣市趨勢、新店區深度解析。每月 2/12/22 自動更新。">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">

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
/* === Better 對拷版型（2026-09-04 原型：對標 better.com/mortgage；色票依老闆定案 token） === */
:root{{--forest:#1B2F4A;--forest-deep:#12213A;--action:#2F5B8F;--action-hover:#26497A;--gold:#C8945A;--gold-soft:#E0B685;--gold-deep:#9A6D3A;
  --paper:#F7F5F0;--cream:#F2EFE8;--tint:#EEF2F7;--ink:#1B2F4A;--ink-dim:#5A6878;--line:#E2DED4;
  --shadow:0 4px 6px -1px rgba(0,0,0,.1),0 2px 4px -2px rgba(0,0,0,.1)}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{font-family:'Noto Sans TC',-apple-system,'PingFang TC','Microsoft JhengHei',sans-serif;font-size:16px;line-height:24px;color:var(--ink);background:#fff;padding-top:64px;-webkit-font-smoothing:antialiased}}
a{{color:inherit;text-decoration:none}}
img{{max-width:100%;display:block}}
:focus-visible{{outline:2px solid var(--gold);outline-offset:3px;border-radius:4px}}

/* 版心：外框 1440、內容欄 1200、頁邊距 40／24 */
.bt-in{{max-width:1280px;margin:0 auto;padding:0 40px}}
.bt-narrow{{max-width:880px;margin:0 auto;padding:0 40px}}
.bt-sec{{padding:64px 0}}
.bt-sec-80{{padding:80px 0}}
.bt-sec-96{{padding:96px 0}}

/* 字級 */
.bt-eyebrow{{font-size:18px;line-height:24px;font-weight:500;color:var(--gold-deep);margin-bottom:12px}}
.bt-label{{font-size:14px;line-height:20px;font-weight:700;color:var(--gold-deep);letter-spacing:.08em;margin-bottom:12px}}
.bt-h1{{font-size:48px;line-height:1.2;font-weight:700;color:var(--ink);margin-bottom:24px}}
.bt-h1 em,.bt-h2 em{{font-style:normal;color:var(--action)}}
.bt-h2{{font-size:32px;line-height:1.2;font-weight:700;color:var(--ink);margin-bottom:24px}}
.bt-h4{{font-size:18px;line-height:1.4;font-weight:700;color:var(--ink);margin-bottom:8px}}
.bt-p{{font-size:16px;line-height:24px;color:var(--ink-dim)}}
.bt-p+.bt-p{{margin-top:16px}}
.bt-small{{font-size:14px;line-height:20px;color:var(--ink-dim)}}
.bt-center{{text-align:center}}

/* 按鈕：主 64px／小 48px、8px 圓角、hover 只變深 300ms */
.bt-btn{{display:inline-flex;align-items:center;justify-content:center;height:64px;padding:0 40px;border-radius:8px;background:var(--action);color:#fff;font-size:16px;font-weight:700;white-space:nowrap;border:0;cursor:pointer;font-family:inherit;transition:background-color .3s ease-in-out}}
.bt-btn:hover{{background:var(--action-hover)}}
.bt-btn-sm{{height:48px;padding:0 16px}}
.bt-btn-ghost{{background:var(--cream);color:var(--ink)}}
.bt-btn-ghost:hover{{background:var(--line)}}
.bt-btn-gold{{background:var(--gold);color:var(--forest-deep)}}
.bt-btn-gold:hover{{background:var(--gold-soft)}}
.bt-btn-outline{{background:transparent;color:#fff;border:1px solid rgba(255,255,255,.55)}}
.bt-btn-outline:hover{{background:rgba(255,255,255,.1)}}
.bt-btns{{display:flex;gap:12px;flex-wrap:wrap}}

/* 卡片 */
.bt-card{{background:#fff;border-radius:8px;box-shadow:var(--shadow);padding:32px}}

/* 1. Hero 左文右圖 */
.bt-hero{{background:var(--paper)}}
.bt-hero-grid{{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:64px;align-items:center}}
.bt-hero-text .bt-p{{margin-bottom:32px;max-width:560px}}
.bt-hero-img{{width:100%;height:auto;aspect-ratio:4/5;object-fit:cover;object-position:center 60%;border-radius:8px}}
.bt-hero .aib{{margin:24px 0 0}}
.bt-hero .aib-form{{box-shadow:var(--shadow);border-radius:8px}}
.bt-hero .aib-chips button{{color:var(--ink)}}

/* 快速答案 */
.bt-qa{{border-left:4px solid var(--action)}}
.bt-qa p{{font-size:16px;line-height:24px;color:var(--ink);margin:0 0 16px}}
.bt-qa ul{{margin:0;padding-left:20px;font-size:14px;line-height:22px;color:var(--ink-dim)}}
.bt-qa li+li{{margin-top:4px}}
.bt-qa li strong{{color:var(--ink)}}

/* 2. 深色帶 */
.bt-dark{{background:var(--forest);color:#fff}}
.bt-dark .bt-label{{color:var(--gold)}}
.bt-dark .bt-h2{{color:#fff}}
.bt-dark .bt-p{{color:rgba(255,255,255,.82)}}
.bt-dark-grid{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:64px;align-items:center}}
.bt-dark-img{{width:100%;height:auto;aspect-ratio:5/4;object-fit:cover;border-radius:8px}}
.bt-dark figcaption{{font-size:14px;line-height:20px;color:rgba(255,255,255,.6);margin-top:12px}}
.bt-def{{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:64px}}
.bt-def-item{{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:8px;padding:32px 24px;text-align:center}}
.bt-def-num{{font-size:32px;line-height:1.2;font-weight:700;color:#fff;margin-bottom:12px}}
.bt-def-label{{font-size:16px;line-height:24px;color:rgba(255,255,255,.8)}}

/* 3. 特色格（純文字） */
.bt-steps{{display:grid;grid-template-columns:repeat(4,1fr);gap:40px 32px;margin-top:48px}}
.bt-step-num{{width:40px;height:40px;border-radius:8px;background:var(--forest);color:#fff;font-size:16px;font-weight:700;display:flex;align-items:center;justify-content:center;margin-bottom:16px}}
.bt-step-num.gold{{background:var(--gold);color:var(--forest-deep)}}
.bt-points{{display:grid;grid-template-columns:repeat(3,1fr);gap:40px 32px;margin-top:64px;padding-top:64px;border-top:1px solid var(--line)}}

/* 適合對象卡 */
.bt-who{{background:var(--paper)}}
.bt-who-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:48px}}
.bt-who-card .bt-h4{{margin-bottom:12px}}
.bt-check{{display:flex;flex-direction:column;gap:8px;margin-top:20px;padding-top:20px;border-top:1px solid var(--line)}}
.bt-check span{{font-size:14px;line-height:20px;color:var(--ink);display:flex;gap:8px;align-items:flex-start}}
.bt-check span::before{{content:"✓";color:var(--action);font-weight:700;flex-shrink:0}}

/* 4. CTA 帶 */
.bt-cta{{background:var(--cream);text-align:center}}
.bt-cta .bt-h2{{max-width:640px;margin-left:auto;margin-right:auto}}
.bt-cta .bt-p{{max-width:520px;margin:0 auto 32px}}
.bt-cta .bt-btns{{justify-content:center}}
.bt-promise{{display:flex;gap:12px 28px;justify-content:center;flex-wrap:wrap;margin-top:32px}}
.bt-promise span{{font-size:14px;line-height:20px;color:var(--ink-dim);display:flex;align-items:center;gap:8px}}
.bt-promise span::before{{content:"✓";color:var(--action);font-weight:700}}

/* 5. 相關文章 */
.bt-related{{background:var(--tint)}}
.bt-rel-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:40px}}
.bt-rel-card{{display:flex;flex-direction:column;justify-content:space-between;min-height:180px;transition:box-shadow .3s ease-in-out}}
.bt-rel-card:hover{{box-shadow:0 10px 15px -3px rgba(0,0,0,.1),0 4px 6px -4px rgba(0,0,0,.1)}}
.bt-rel-card h3{{font-size:18px;line-height:1.4;font-weight:700;color:var(--ink)}}
.bt-rel-card::after{{content:"→";font-size:20px;font-weight:700;color:var(--action);margin-top:24px}}

/* 案例 */
.bt-case-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:32px}}
.bt-case-card{{border-left:4px solid var(--action)}}
.bt-case-card .bt-label{{margin-bottom:8px}}
.bt-case-card p{{font-size:16px;line-height:24px;color:var(--ink)}}

/* 比較表 */
.bt-compare{{background:var(--paper)}}
.bt-table-wrap{{overflow-x:auto;-webkit-overflow-scrolling:touch;background:#fff;border-radius:8px;box-shadow:var(--shadow);margin-top:32px}}
.bt-table{{width:100%;border-collapse:collapse;min-width:560px}}
.bt-table th{{padding:16px 20px;font-size:16px;font-weight:700;text-align:center;background:var(--cream);color:var(--ink-dim)}}
.bt-table th:first-child{{text-align:left;width:30%}}
.bt-table th.col-sl{{background:var(--forest);color:#fff}}
.bt-table td{{padding:16px 20px;font-size:16px;line-height:24px;border-top:1px solid var(--line);text-align:center;color:var(--ink-dim)}}
.bt-table td:first-child{{text-align:left;font-weight:700;color:var(--ink)}}
.bt-table td.highlight{{background:var(--tint);color:var(--ink);font-weight:700}}
.bt-table .yes{{color:var(--action);font-weight:700}}
.bt-table .no{{color:var(--ink-dim)}}
.bt-dark-card{{margin-top:48px;background:var(--forest);border-radius:8px;padding:48px 40px;text-align:center;color:#fff}}
.bt-dark-card .bt-h4{{color:#fff;font-size:24px;line-height:1.2;margin-bottom:12px}}
.bt-dark-card .bt-p{{color:rgba(255,255,255,.75);max-width:480px;margin:0 auto 32px}}
.bt-dark-card .bt-btns{{justify-content:center}}

/* 6. FAQ accordion */
.bt-faq details{{border-top:1px solid var(--line);padding:24px 0}}
.bt-faq details:last-of-type{{border-bottom:1px solid var(--line)}}
.bt-faq summary{{font-size:18px;line-height:1.4;font-weight:700;color:var(--ink);cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:16px}}
.bt-faq summary::-webkit-details-marker{{display:none}}
.bt-faq .plus{{font-size:24px;color:var(--ink-dim);font-weight:400;flex-shrink:0;transition:transform .3s ease-in-out}}
.bt-faq details[open] .plus{{transform:rotate(45deg)}}
.bt-faq details p{{font-size:16px;line-height:24px;color:var(--ink-dim);margin-top:16px}}

/* 在地相關方案 */
.bt-local{{margin-top:64px}}
.bt-local .bt-label{{margin-bottom:8px}}
.bt-local p{{margin-bottom:16px}}
.bt-chips{{display:flex;flex-wrap:wrap;gap:8px}}
.bt-chips a{{display:inline-flex;align-items:center;height:40px;padding:0 16px;border-radius:8px;border:1px solid var(--line);background:var(--paper);font-size:14px;font-weight:500;color:var(--ink);transition:background-color .3s ease-in-out}}
.bt-chips a:hover{{background:var(--cream)}}

@media(prefers-reduced-motion:reduce){{*{{transition:none!important}}}}

@media(max-width:900px){{
  body{{padding-top:58px}}
  .bt-hero-grid,.bt-dark-grid{{grid-template-columns:minmax(0,1fr);gap:40px}}
  .bt-hero-img{{aspect-ratio:4/3}}
  .bt-steps{{grid-template-columns:repeat(2,1fr)}}
  .bt-points,.bt-who-grid,.bt-rel-grid,.bt-case-grid,.bt-def{{grid-template-columns:1fr}}
  .bt-rel-card{{min-height:auto}}
}}
@media(max-width:768px){{
  .bt-in,.bt-narrow{{padding:0 24px}}
  .bt-sec-96{{padding:64px 0}}
  .bt-sec-80{{padding:64px 0}}
  .bt-h1{{font-size:32px}}
  .bt-h2{{font-size:32px}}
  .bt-card{{padding:24px}}
  .bt-btns{{flex-direction:column;align-items:stretch}}
  .bt-btn{{width:100%}}
  .bt-dark-card{{padding:32px 24px}}
}}
@media(max-width:520px){{
  .bt-steps{{grid-template-columns:1fr}}
}}
@media(max-width:640px){{
  /* 手機：ai-bar 右側讓出小鋮浮動鈕（chat-widget .cw-launch 固定 right 24px + 58px）的欄位，送出鈕不被蓋住 */
  .bt-hero .aib{{padding-right:70px}}
}}
/* === 本頁補充（lvr 觀察室頁）：資料區選擇器沿用原頁一字不改、只換 token；FAQ「＋」CSS 生成；名詞解釋列 === */
.bt-tool .bt-qa{{margin-bottom:24px}}
.bt-qa h4{{font-size:14px;line-height:20px;font-weight:700;color:var(--gold-deep);letter-spacing:.08em;margin-bottom:12px}}
.bt-hero .bt-label{{margin-bottom:16px}}
.bt-hero .bt-meta{{font-size:14px;line-height:20px;color:var(--ink-dim);margin-top:-16px}}

/* 家族切換（觀察室／預售屋／租金報酬） */
.family-nav{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:24px}}
.family-nav a{{display:inline-flex;align-items:center;height:40px;padding:0 16px;border-radius:8px;border:1px solid var(--line);background:var(--paper);font-size:14px;font-weight:500;color:var(--ink);transition:background-color .3s ease-in-out}}
.family-nav a:hover{{background:var(--cream)}}
.family-nav a.active{{background:var(--forest);border-color:var(--forest);color:#fff}}

/* 區塊小標 */
.section-title{{display:flex;align-items:center;gap:12px;flex-wrap:wrap;font-size:14px;line-height:20px;font-weight:700;color:var(--gold-deep);letter-spacing:.08em;margin:40px 0 14px}}
.section-title::before{{content:'';width:8px;height:8px;background:var(--action);flex:none}}
.section-title:first-child{{margin-top:0}}

/* 時間窗切換 */
.window-toggle{{display:inline-flex;background:var(--cream);border-radius:8px;padding:3px;margin-left:4px;vertical-align:middle}}
.window-toggle button{{font-size:13px;font-weight:600;color:var(--ink-dim);background:transparent;border:none;padding:6px 12px;border-radius:6px;cursor:pointer;font-family:inherit;letter-spacing:0;transition:background-color .3s ease-in-out,color .3s ease-in-out}}
.window-toggle button.active{{background:var(--forest);color:#fff}}

/* KPI 卡 */
.kpi-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px}}
@media(max-width:900px){{.kpi-grid{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:480px){{.kpi-grid{{grid-template-columns:1fr}}}}
.kpi-link{{text-decoration:none;color:inherit;display:block}}
.kpi-link .kpi-card{{transition:box-shadow .3s ease-in-out}}
.kpi-link:hover .kpi-card{{box-shadow:0 10px 15px -3px rgba(0,0,0,.1),0 4px 6px -4px rgba(0,0,0,.1)}}
.kpi-cta{{font-size:12px;font-weight:700;color:var(--action);margin-top:10px;padding-top:10px;border-top:1px solid var(--line)}}
.kpi-card{{background:#fff;border:1px solid var(--line);border-radius:8px;padding:20px 18px;box-shadow:var(--shadow)}}
.kpi-town{{font-size:16px;font-weight:700;color:var(--ink);margin-bottom:10px}}
.kpi-main{{margin-bottom:14px;padding-bottom:12px;border-bottom:1px solid var(--line)}}
.kpi-value{{font-size:28px;font-weight:700;color:var(--ink);letter-spacing:-.02em;line-height:1;font-variant-numeric:tabular-nums}}
.kpi-unit{{font-size:12px;font-weight:500;color:var(--ink-dim);margin-left:4px}}
.kpi-label{{font-size:12px;color:var(--ink-dim);margin-top:4px}}
.kpi-row{{display:flex;justify-content:space-between;font-size:13px;color:var(--ink);margin-bottom:5px;font-variant-numeric:tabular-nums}}
.kpi-row span{{color:var(--ink-dim)}}
.kpi-change{{font-size:12px;color:var(--ink-dim);margin-top:10px;padding-top:10px;border-top:1px solid var(--line)}}
.kpi-empty{{font-size:13px;color:var(--ink-dim);text-align:center;padding:20px 0}}

/* 圖表卡 */
.chart-card{{background:#fff;border:1px solid var(--line);border-radius:8px;padding:24px;margin-bottom:18px;box-shadow:var(--shadow)}}
.chart-card h3{{font-size:18px;line-height:1.4;font-weight:700;color:var(--ink);margin:0 0 6px}}
.chart-card p.chart-note{{font-size:14px;color:var(--ink-dim);margin:0 0 14px;line-height:22px}}
.chart-card img{{width:100%;height:auto;display:block;border-radius:8px}}
.chart-row{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:18px}}
@media(max-width:780px){{.chart-row{{grid-template-columns:1fr}}}}
.chart-row .chart-card{{margin-bottom:0}}

/* spotlight（新店深度） */
.spotlight{{background:#fff;border:1px solid var(--line);border-left:4px solid var(--gold);border-radius:8px;padding:24px;margin-bottom:18px;box-shadow:var(--shadow)}}
.spotlight-header{{font-size:13px;font-weight:700;color:var(--gold-deep);letter-spacing:.08em;margin-bottom:6px}}
.spotlight h3{{font-size:20px;line-height:1.3;font-weight:700;color:var(--ink);margin:0 0 8px}}
.spotlight p.insight{{font-size:15px;color:var(--ink);line-height:1.75;margin:0 0 14px}}
.spotlight p.insight b{{color:var(--gold-deep)}}

/* 排名表（表格外層 overflow-x:auto 必留） */
.rank-card{{background:#fff;border:1px solid var(--line);border-radius:8px;padding:18px 4px;overflow:hidden;box-shadow:var(--shadow)}}
.rank-card-head{{display:flex;justify-content:space-between;align-items:center;padding:0 18px;margin-bottom:6px;flex-wrap:wrap;gap:10px}}
.rank-card h3{{font-size:18px;line-height:1.4;font-weight:700;color:var(--ink);margin:0}}
.rank-card p.rank-note{{font-size:13px;color:var(--ink-dim);margin:0 18px 14px;line-height:1.5}}
.city-chips{{display:flex;gap:6px;flex-wrap:wrap}}
.city-chip{{font-size:13px;font-weight:600;color:var(--ink-dim);background:var(--cream);padding:6px 12px;border-radius:8px;cursor:pointer;border:none;font-family:inherit;transition:background-color .3s ease-in-out,color .3s ease-in-out}}
.city-chip.active{{background:var(--forest);color:#fff}}
.rank-table-wrap{{overflow-x:auto;-webkit-overflow-scrolling:touch}}
table.rank-table{{width:100%;border-collapse:collapse;font-size:14px;color:var(--ink);min-width:760px}}
.rank-table th{{background:var(--cream);color:var(--ink-dim);font-weight:700;text-align:left;padding:10px 12px;cursor:pointer;user-select:none;white-space:nowrap;border-bottom:1.5px solid var(--line);position:sticky;top:0;font-size:12px;letter-spacing:.04em}}
.rank-table th:hover{{background:var(--tint);color:var(--ink)}}
.rank-table th .arrow{{margin-left:4px;opacity:.4;font-size:10px}}
.rank-table th.sorted .arrow{{opacity:1;color:var(--action)}}
.rank-table td{{padding:9px 12px;border-bottom:.5px solid var(--line);white-space:nowrap}}
.rank-table td.num{{text-align:right;font-variant-numeric:tabular-nums;font-size:13px}}
.rank-table tr.low-sample td{{color:var(--ink-dim)}}
.rank-table tr:hover{{background:var(--paper)}}
.badge-low{{display:inline-block;font-size:10px;color:var(--ink-dim);background:var(--cream);padding:1px 6px;border-radius:8px;margin-left:4px;font-weight:500}}
.empty-row td{{text-align:center;color:var(--ink-dim);padding:30px 0;font-style:italic}}

/* 圖卡／原始資料下載 */
.download-card{{background:#fff;border:1px solid var(--line);border-radius:8px;padding:24px;box-shadow:var(--shadow)}}
.download-grid{{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}}
.download-grid a{{display:inline-flex;align-items:center;height:40px;padding:0 16px;border-radius:8px;border:1px solid var(--line);background:var(--paper);font-size:14px;font-weight:500;color:var(--ink);text-decoration:none;transition:background-color .3s ease-in-out}}
.download-grid a:hover{{background:var(--cream)}}

/* 資料說明與免責 */
.notes{{background:#fff;border:1px solid var(--line);border-radius:8px;padding:24px;font-size:14px;color:var(--ink);line-height:1.7;box-shadow:var(--shadow)}}
.notes h4{{font-size:16px;font-weight:700;margin:0 0 10px;color:var(--ink)}}
.notes ul{{margin:0;padding-left:20px;color:var(--ink-dim)}}
.notes li{{margin-bottom:5px}}

/* AI 摘要卡 */
.ai-card{{background:#fff;border:1px solid var(--line);border-left:4px solid var(--gold);border-radius:8px;padding:24px;margin-bottom:18px;box-shadow:var(--shadow)}}
.ai-badge{{display:inline-block;font-size:12px;font-weight:700;color:#fff;background:var(--action);padding:4px 12px;border-radius:8px;margin-bottom:12px;letter-spacing:.06em}}
.ai-card p{{font-size:15px;color:var(--ink);line-height:1.85;margin:0 0 10px}}
.ai-card p:last-child{{margin-bottom:0;font-size:12px;color:var(--ink-dim);font-style:italic}}

/* CTA 帶：次鈕深框 */
.bt-btn-outline-dark{{background:transparent;color:var(--ink);border:1px solid var(--ink)}}
.bt-btn-outline-dark:hover{{background:var(--tint)}}

/* FAQ：h3 進 summary、「＋」用 CSS 生成免新增文字 */
.bt-faq summary h3{{font-size:18px;line-height:1.4;font-weight:700;color:var(--ink);margin:0}}
.bt-faq summary::after{{content:"＋";font-size:24px;color:var(--ink-dim);font-weight:400;flex-shrink:0;transition:transform .3s ease-in-out}}
.bt-faq details[open] summary::after{{transform:rotate(45deg)}}

/* 名詞解釋 */
.bt-terms{{margin-top:8px}}
.bt-term{{border-left:3px solid var(--action);padding:8px 0 8px 20px;margin-bottom:16px}}
.bt-term strong{{color:var(--ink);font-size:16px;font-weight:700}}
.bt-term span{{color:var(--ink-dim);font-size:16px;line-height:24px}}
</style>
<script>window.__cxMotionLoaded=true;/* 本頁不做捲動進場動畫（Better 對拷規格）：跳過 include.js 的 GSAP 載入 */</script>
</head>
<body>
<div id="nav" data-theme="light"></div>
<script src="nav.js"></script>

<!-- 1. Hero 左文右圖 -->
<section class="bt-hero bt-sec">
  <div class="bt-in bt-hero-grid">
    <div class="bt-hero-text">
      <div class="bt-eyebrow">實價登錄觀察</div>
      <h1 class="bt-h1">實價登錄觀察室</h1>
      <p class="bt-label">LVR Observatory · 內政部實價登錄</p>
      <p class="bt-p">台北市 + 新北市 + 台中市 + 桃園市｜正常住宅成交追蹤</p>
      <p class="bt-small bt-meta">資料涵蓋 113Q1 ~ {season_label} · 全 {n_districts_180} 行政區（近 180 天） · 更新於 {generated_at}</p>
    </div>
    <img class="bt-hero-img" src="img/gen-city-taipei.jpg" alt="台北盆地暮色街景" width="1344" height="768" fetchpriority="high" loading="eager">
  </div>
</section>

<!-- 2. 觀察室主體（資料區沿用原頁：id／class／data-* 與資料 JS 一字不改） -->
<section class="bt-sec bt-tool">
  <div class="bt-in">
{aeo_quick}

  <div class="family-nav">
    <a href="lvr-observatory.html" class="active">觀察室（買賣）</a>
    <a href="lvr-presale.html">預售屋</a>
    <a href="lvr-rental.html">租金報酬</a>
  </div>
{ai_section_html}
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

  </div>
</section>

{aeo_faq_terms}
<!-- 5. 資料說明與免責（bt-tool 白底外框） -->
<section class="bt-sec bt-tool">
  <div class="bt-in">
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
  </div>
</section>

<!-- 6. CTA 帶（保留 .cta-strip：GA cta_click 事件靠它） -->
<section class="bt-cta bt-sec-80 cta-strip">
  <div class="bt-in">
    <h2 class="bt-h2">想知道你的房子在當前行情下能借多少？</h2>
    <p class="bt-p">用我們的二胎可貸額度試算，輸入市價與一胎本金即時看結果。</p>
    <div class="bt-btns">
      <a href="second-mortgage-calculator.html" class="bt-btn bt-btn-outline-dark">二胎額度試算 →</a>
      <a href="https://lin.ee/PHIfSoY" class="bt-btn">LINE 線上諮詢</a>
    </div>
  </div>
</section>

<!-- 7. 延伸閱讀 -->
<section class="related-reads bt-sec">
  <div class="bt-narrow">
    <div class="bt-card bt-local">
      <div class="bt-label">延伸閱讀</div>
      <div class="bt-chips"><a href="mortgage-calculator.html">一胎房貸試算 →</a><a href="second-mortgage-calculator.html">二胎可貸額度 →</a><a href="affordability-calculator.html">貸款負擔能力 →</a><a href="tools.html">回工具總覽 →</a></div>
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
const AREA_SLUG = {json.dumps(AREA_SLUG, ensure_ascii=False)};

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
    const href = 'area-' + (AREA_SLUG[t] || '') + '.html';
    if (!k) {{
      return '<a class="kpi-link" href="'+href+'"><div class="kpi-card" style="opacity:.5"><div class="kpi-town">'+t+'</div><div class="kpi-empty">本窗無資料</div></div></a>';
    }}
    const chg = k['2年漲幅'];
    let chgHtml = '—';
    if (chg !== null && chg !== undefined) {{
      const arrow = chg > 0 ? '▲' : (chg < 0 ? '▼' : '—');
      const c = chg > 0 ? '#16A34A' : (chg < 0 ? '#EF4444' : '#6e6e73');
      chgHtml = '<span style="color:'+c+';font-weight:700">'+arrow+' '+Math.abs(chg).toFixed(1)+'%</span>';
    }}
    return `
      <a class="kpi-link" href="${{href}}">
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
        <div class="kpi-cta">看 ${{t}}房市與生活機能 →</div>
      </div>
      </a>`;
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

<script src="include.js" defer></script>
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

    # __season 含 mini_YYYYMMDD 增量標籤，取季別格式的最大值，避免檔名漏進 UI（2026-07-06 老闆抓到）
    seasons = [s for s in df["__season"].unique() if isinstance(s, str) and len(s) == 5 and s[3] == "S"]
    season_label = max(seasons).replace("S", "Q") if seasons else "最新"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    ai_report = load_ai_report()
    html = build_html(generated_at, season_label, window_data, deep, ai_report)

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
