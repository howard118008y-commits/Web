#!/usr/bin/env python3
"""
生成新北市房屋稅試算器 HTML
資料來源：新北市官方試算系統 JSON 檔案
"""

import json
import re
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = Path('/tmp/housedata')

DISTRICTS = [
    ('01','新莊區'), ('02','林口區'), ('03','五股區'), ('04','蘆洲區'),
    ('05','三重區'), ('06','泰山區'), ('07','新店區'), ('08','石碇區'),
    ('09','深坑區'), ('10','坪林區'), ('11','烏來區'), ('14','板橋區'),
    ('15','三峽區'), ('16','鶯歌區'), ('17','樹林區'), ('18','中和區'),
    ('19','土城區'), ('21','瑞芳區'), ('22','平溪區'), ('23','雙溪區'),
    ('24','貢寮區'), ('25','金山區'), ('26','萬里區'), ('27','淡水區'),
    ('28','汐止區'), ('30','三芝區'), ('31','石門區'), ('32','八里區'),
    ('33','永和區'),
]
# 偏遠山海區，折舊率額外 +0.0005
EXTRA_DRPY_DISTRICTS = {'21','22','23','24','25','26','27','30','31','32'}


def load_all():
    with open(DATA_DIR / 'struct.json') as f:
        structs = json.load(f)
    with open(DATA_DIR / 'useType.json') as f:
        usetypes = json.load(f)
    with open(DATA_DIR / 'usage.json') as f:
        usages = json.load(f)
    with open(DATA_DIR / 'price.json') as f:
        prices = json.load(f)

    sections = {}
    for code, _ in DISTRICTS:
        fp = DATA_DIR / f'section_{code}.json'
        if fp.exists():
            with open(fp) as f:
                data = json.load(f)
            sections[code] = [
                {'name': s['section'], 'rates': s['rates']}
                for s in data
            ]

    return structs, usetypes, usages, prices, sections


def build_html(structs, usetypes, usages, prices, sections):
    # ── 構造別 dropdown options ──
    struct_order = ['B','C','P','A','S','T','U','J','H','F','G','D','E','K','R','L']
    struct_opts = []
    for s in struct_order:
        if s in structs:
            g = ' (常見)' if structs[s].get('generally') else ''
            struct_opts.append(f'<option value="{s}">{structs[s]["struct"]}{g}</option>')

    # ── 行政區 dropdown options ──
    district_opts = '\n'.join(
        f'        <option value="{code}">{name}</option>'
        for code, name in DISTRICTS
    )

    # ── JS 資料 ──
    # 1. STRUCT: {structNo: {name, depreciation:[{start,end,drpy,residualRatio}]}}
    struct_js = {}
    for k, v in structs.items():
        struct_js[k] = {
            'n': v['struct'],
            'd': [{'s': d['start'], 'e': d['end'], 'r': d['drpy'], 'res': d['residualRatio']}
                  for d in v['depreciation']]
        }

    # 2. USETYPE: {structNo: {useTypeNo: {name, mainUseTypeNo, discount, generally}}}
    usetype_js = {}
    for sk, sv in usetypes.items():
        usetype_js[sk] = {}
        for uk, uv in sv.items():
            usetype_js[sk][uk] = {
                'n': uv['name'],
                'm': uv['mainUseTypeNo'],
                'g': uv.get('generally', False),
                'disc': uv.get('discount')
            }

    # 3. USAGE: {usageNo: {name, rate or 0}}
    usage_js = {}
    for k, v in usages.items():
        usage_js[k] = {
            'n': v['name'],
            'r': v['rates'][0]['rate'] if v['rates'] else 0
        }

    # 4. PRICE: keep as-is (already compact)
    # 5. SECTIONS: {districtNo: [{name, rates:[{start,end,rate}]}]}
    section_js = {}
    for code, sects in sections.items():
        section_js[code] = [
            {'n': s['name'], 'r': [{'s': r['start'], 'e': r['end'], 'v': r['rate']} for r in s['rates']]}
            for s in sects
        ]

    # Serialize all data
    def j(obj): return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))

    return f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8"><!-- ntpc-house-tax v1 -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>新北市房屋稅試算 2026｜鋮馨租賃</title>
<meta name="description" content="新北市房屋稅線上試算，依建造年月、構造別、用途、路段率與房屋使用情形計算預估稅額，資料來自官方標準單價。">
<link rel="preload" href="style.css" as="style" onload="this.onload=null;this.rel=\'stylesheet\'"><noscript><link rel="stylesheet" href="style.css"></noscript>
<style>
*{{box-sizing:border-box}}
body{{background:#fdf8f0;margin:0;font-family:-apple-system,BlinkMacSystemFont,\'Helvetica Neue\',Arial,sans-serif}}
nav{{background:rgba(255,255,255,.92);backdrop-filter:blur(20px);border-bottom:.5px solid rgba(0,0,0,.08);padding:0 24px;height:60px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100}}
img.nav-logo{{height:44px;width:44px;object-fit:cover;border-radius:8px;border:1px solid rgba(0,0,0,.06)}}
.nav-back{{font-size:14px;color:#b45309;text-decoration:none;font-weight:500}}
.hero{{background:#1e3a5f;padding:28px 24px 22px;text-align:center}}
.hero h1{{font-size:26px;font-weight:700;color:#fff;margin:0 0 4px}}
.hero p{{font-size:13px;color:rgba(255,255,255,.8);margin:0}}
.wrap{{max-width:720px;margin:0 auto;padding:20px 16px 80px}}
.notice{{background:#fefce8;border:1px solid #d97706;border-radius:10px;padding:14px 16px;margin-bottom:16px;font-size:13px;color:#713f12;line-height:1.75}}
.step-card{{background:#fff;border-radius:14px;padding:22px;margin-bottom:14px;box-shadow:0 1px 6px rgba(0,0,0,.06)}}
.step-label{{font-size:13px;font-weight:700;color:#1e3a5f;margin-bottom:16px;padding-bottom:8px;border-bottom:2px solid #bfdbfe}}
.g2{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.g3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}}
.g4{{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px}}
@media(max-width:580px){{.g3{{grid-template-columns:1fr 1fr}}.g4{{grid-template-columns:1fr 1fr}}.g2{{grid-template-columns:1fr}}}}
.field{{display:flex;flex-direction:column;gap:5px}}
.field label{{font-size:12px;font-weight:600;color:#6e6e73}}
.field input,.field select{{height:42px;border:1.5px solid #d2d2d7;border-radius:8px;padding:0 10px;font-size:14px;color:#1d1d1f;outline:none;background:#fff;transition:border-color .2s}}
.field input:focus,.field select:focus{{border-color:#1e3a5f}}
.field input::placeholder{{color:#b0b0b0}}
.hint{{font-size:11px;color:#9ca3af;margin-top:2px}}
.usage-block{{background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;padding:14px;margin-bottom:10px}}
.usage-row{{display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap}}
.usage-row .field{{flex:1;min-width:140px}}
.add-btn{{background:#e0f2fe;color:#0369a1;border:1.5px solid #bae6fd;border-radius:8px;height:42px;padding:0 16px;font-size:13px;font-weight:700;cursor:pointer;white-space:nowrap;font-family:inherit}}
.remove-btn{{background:#fef2f2;color:#dc2626;border:1.5px solid #fecaca;border-radius:8px;height:36px;padding:0 12px;font-size:12px;font-weight:600;cursor:pointer;font-family:inherit}}
.result-card{{background:#1e3a5f;border-radius:14px;padding:22px;margin-top:16px;color:#fff}}
.result-title{{font-size:13px;color:rgba(255,255,255,.7);margin-bottom:8px}}
.result-total{{font-size:36px;font-weight:700;color:#fbbf24;margin-bottom:4px}}
.result-unit{{font-size:13px;color:rgba(255,255,255,.7)}}
.result-breakdown{{margin-top:16px;border-top:1px solid rgba(255,255,255,.2);padding-top:14px}}
.breakdown-row{{display:flex;justify-content:space-between;font-size:12px;color:rgba(255,255,255,.8);padding:4px 0}}
.breakdown-label{{color:rgba(255,255,255,.6)}}
.breakdown-val{{font-weight:600;color:#fff}}
.btn-row{{display:flex;gap:12px;justify-content:center;margin-top:20px}}
.btn-calc{{background:#1e3a5f;color:#fff;border:none;border-radius:24px;height:48px;padding:0 40px;font-size:15px;font-weight:700;cursor:pointer;font-family:inherit}}
.btn-calc:hover{{background:#152d4a}}
.btn-outline{{background:#fff;color:#6e6e73;border:1.5px solid #d2d2d7;border-radius:24px;height:48px;padding:0 28px;font-size:14px;font-weight:600;cursor:pointer;font-family:inherit}}
.btn-home{{background:#fff;color:#6e6e73;border:1.5px solid #d2d2d7;border-radius:24px;height:48px;padding:0 28px;font-size:14px;font-weight:600;cursor:pointer;font-family:inherit;text-decoration:none;display:inline-flex;align-items:center}}
.era-grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:4px}}
.era-label{{display:flex;align-items:center;gap:6px;background:#f9fafb;border:1.5px solid #d2d2d7;border-radius:8px;padding:8px 10px;cursor:pointer;font-size:13px;transition:border-color .2s}}
.era-label:has(input:checked){{border-color:#1e3a5f;background:#eff6ff}}
.era-label input{{accent-color:#1e3a5f}}
.sub-select{{margin-top:8px;display:none}}
.disclaimer{{font-size:11px;color:#6e6e73;line-height:1.7;margin-top:14px;padding:10px 14px;background:#f9f9f9;border-radius:8px;border:.5px solid #e5e5e5}}
</style>
<script src="include.js" defer></script>
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta property="og:image" content="https://cx468.com.tw/img/og-image.jpg">
<meta property="og:site_name" content="鋮馨租賃有限公司">
<meta property="og:type" content="website">
<link rel="canonical" href="https://cx468.com.tw/new-taipei-house-tax.html">
<meta property="og:title" content="新北市房屋稅試算 2026｜鋮馨租賃">
<meta property="og:description" content="新北市房屋稅試算，依建造年月、構造別、用途、路段率計算預估稅額。">
<meta property="og:url" content="https://cx468.com.tw/new-taipei-house-tax.html">
<link rel="preconnect" href="https://www.googletagmanager.com">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-4FX9LNEL7R"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag(\'js\',new Date());gtag(\'config\',\'G-4FX9LNEL7R\');</script>
</head>
<body>
<div data-include="nav-tool"></div>

<div class="hero">
  <h1>房屋稅稅額試算</h1>
  <p>新北市・依官方標準單價計算・鋮馨租賃</p>
</div>

<div class="wrap">

<div class="notice">
  <strong>⚠ 試算說明</strong><br>
  本試算依「房屋標準價格及房屋現值計算方式」官方公式計算，<strong>僅供單一房屋簡易參考</strong>。
  實際稅額依新北市稅務局核定為準。不含電梯附加、巷弄減級、個別加減項等調整。
</div>

<!-- STEP 1 房屋基本資料 -->
<div class="step-card">
  <div class="step-label">步驟一：房屋基本資料</div>

  <!-- 建造年月 -->
  <div style="margin-bottom:16px">
    <div style="font-size:12px;font-weight:600;color:#6e6e73;margin-bottom:8px">房屋建造完成年月（民國年月）</div>
    <div class="era-grid">
      <label class="era-label">
        <input type="radio" name="taxType" value="00000" onchange="onEraChange()" checked>
        103年6月以前
      </label>
      <label class="era-label">
        <input type="radio" name="taxType" value="10307" onchange="onEraChange()">
        103年7月～109年6月
      </label>
      <label class="era-label">
        <input type="radio" name="taxType" value="10907" onchange="onEraChange()">
        109年7月～112年6月
      </label>
      <label class="era-label">
        <input type="radio" name="taxType" value="11207" onchange="onEraChange()">
        112年7月以後
      </label>
    </div>
    <div class="g2" style="margin-top:10px">
      <div class="field">
        <label>民國年（3位）</label>
        <input type="number" id="rocYear" placeholder="例：090" min="1" max="200" oninput="onDateChange()">
        <div class="hint">例：090 代表 90年，103以前選第一選項</div>
      </div>
      <div class="field">
        <label>月份</label>
        <select id="rocMonth" onchange="onDateChange()">
          <option value="">選月份</option>
          <option value="1">1月</option><option value="2">2月</option><option value="3">3月</option>
          <option value="4">4月</option><option value="5">5月</option><option value="6">6月</option>
          <option value="7">7月</option><option value="8">8月</option><option value="9">9月</option>
          <option value="10">10月</option><option value="11">11月</option><option value="12">12月</option>
        </select>
      </div>
    </div>
    <div id="taxYmDisplay" style="font-size:11px;color:#0369a1;margin-top:4px"></div>
  </div>

  <!-- 構造別 + 總層數 + 樓層高度 -->
  <div class="g3">
    <div class="field">
      <label>構造別</label>
      <select id="structNo" onchange="onStructChange()">
        <option value="">請選擇</option>
        {''.join(struct_opts)}
      </select>
    </div>
    <div class="field">
      <label>總層數</label>
      <input type="number" id="floors" placeholder="例：12" min="-6" max="99" oninput="calcAll()">
      <div class="hint">地下層輸入負數（-1, -2...）</div>
    </div>
    <div class="field">
      <label>樓層淨高（公尺）</label>
      <input type="number" id="floorHeight" placeholder="例：3.5" min="0" max="30" step="0.1" value="3.5" oninput="calcAll()">
      <div class="hint">超過 4m 加價，低於 2m 減價</div>
    </div>
  </div>

  <!-- 用途類別 -->
  <div class="field" style="margin-top:12px">
    <label>用途類別</label>
    <select id="useTypeNo" onchange="calcAll()">
      <option value="">請先選擇構造別</option>
    </select>
  </div>
</div>

<!-- STEP 2 地段資料 -->
<div class="step-card">
  <div class="step-label">步驟二：房屋所在地段</div>
  <div class="g2">
    <div class="field">
      <label>行政區</label>
      <select id="district" onchange="onDistrictChange()">
        <option value="">請選擇</option>
{district_opts}
      </select>
    </div>
    <div class="field">
      <label>路段範圍</label>
      <select id="section" onchange="calcAll()">
        <option value="">請先選擇行政區</option>
      </select>
    </div>
  </div>
  <div id="sectionRateDisplay" style="font-size:12px;color:#1e3a5f;margin-top:8px;display:none">
    📍 路段率：<strong id="sectionRateVal">—</strong>
  </div>
</div>

<!-- STEP 3 使用情形 + 面積 -->
<div class="step-card">
  <div class="step-label">步驟三：房屋使用情形與面積</div>

  <div id="usageBlocks">
    <!-- 第一個使用情形 -->
    <div class="usage-block" id="usageBlock0">
      <div style="font-size:12px;font-weight:700;color:#374151;margin-bottom:10px">使用情形 ①</div>
      <div class="usage-row">
        <div class="field" style="flex:2">
          <label>房屋使用情形</label>
          <select id="usageNo0" onchange="onUsageChange(0)">
            <option value="">請選擇</option>
            <option value="1">全國單一自住（1%）</option>
            <option value="2">自住或公益出租（1.2%）</option>
            <option value="3">出租達標或繼承共有（1.5%～2.4%）</option>
            <option value="4">起造人待銷售（2%～4.8%）</option>
            <option value="5">其它非自住（3.2%～4.8%）</option>
            <option value="6">非住家非營業用（2%）</option>
            <option value="7">營業用（3%）</option>
            <option value="8">私人醫院・診所・自由職業事務所（3%）</option>
          </select>
        </div>
        <div class="field">
          <label>課稅面積（㎡）</label>
          <input type="number" id="area0" placeholder="例：80" min="0" step="0.01" oninput="calcAll()">
        </div>
      </div>
      <div class="sub-select" id="sub0">
        <div class="field">
          <label id="subLabel0">細項</label>
          <select id="subNo0" onchange="calcAll()">
          </select>
        </div>
      </div>
    </div>

    <!-- 第二個使用情形（可選） -->
    <div class="usage-block" id="usageBlock1" style="display:none">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
        <div style="font-size:12px;font-weight:700;color:#374151">使用情形 ②</div>
        <button class="remove-btn" onclick="removeUsage()">移除</button>
      </div>
      <div class="usage-row">
        <div class="field" style="flex:2">
          <label>房屋使用情形</label>
          <select id="usageNo1" onchange="onUsageChange(1)">
            <option value="">請選擇</option>
            <option value="1">全國單一自住（1%）</option>
            <option value="2">自住或公益出租（1.2%）</option>
            <option value="3">出租達標或繼承共有（1.5%～2.4%）</option>
            <option value="4">起造人待銷售（2%～4.8%）</option>
            <option value="5">其它非自住（3.2%～4.8%）</option>
            <option value="6">非住家非營業用（2%）</option>
            <option value="7">營業用（3%）</option>
            <option value="8">私人醫院・診所・自由職業事務所（3%）</option>
          </select>
        </div>
        <div class="field">
          <label>課稅面積（㎡）</label>
          <input type="number" id="area1" placeholder="例：20" min="0" step="0.01" oninput="calcAll()">
        </div>
      </div>
      <div class="sub-select" id="sub1">
        <div class="field">
          <label id="subLabel1">細項</label>
          <select id="subNo1" onchange="calcAll()">
          </select>
        </div>
      </div>
    </div>
  </div>

  <button class="add-btn" id="addUsageBtn" onclick="addUsage()" style="margin-top:8px">+ 新增第二種使用情形</button>

  <div class="btn-row">
    <button class="btn-calc" onclick="calcAll()">計算稅額</button>
    <button class="btn-outline" onclick="clearAll()">清除</button>
    <a href="tools.html" class="btn-home">回工具首頁</a>
  </div>
</div>

<!-- 試算結果 -->
<div class="result-card" id="resultCard" style="display:none">
  <div class="result-title">預估全年房屋稅</div>
  <div class="result-total" id="resultTotal">—</div>
  <div class="result-unit">元（每年 5 月徵收）</div>
  <div class="result-breakdown" id="resultBreakdown"></div>
  <div style="font-size:11px;color:rgba(255,255,255,.5);margin-top:12px">
    ⚠️ 本試算為估算，不含個別加減項。實際稅額依新北市稅務局核定為準。
  </div>
</div>

<a href="https://einvdonate.tax.ntpc.gov.tw/Calculation/HouseTax" target="_blank" rel="noopener"
   style="display:flex;align-items:center;gap:8px;background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:10px 14px;margin-top:12px;font-size:12px;color:#1d4ed8;text-decoration:none">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" stroke="#1d4ed8" stroke-width="2" stroke-linecap="round"/><polyline points="15 3 21 3 21 9" stroke="#1d4ed8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><line x1="10" y1="14" x2="21" y2="3" stroke="#1d4ed8" stroke-width="2" stroke-linecap="round"/></svg>
  前往新北市稅務局官方房屋稅試算系統
</a>

<div class="disclaimer">
  資料來源：新北市政府稅務局官方標準單價表。本試算依標準計算公式估算，實際稅額依各年度房屋標準單價、地段率等公告數字核定，可能與本試算有差異。
  本公司非金融機構，最終核定由稅務主管機關決定。
</div>

</div><!-- /wrap -->

<script>
// ── 靜態資料 ──
const STRUCT = {j(struct_js)};
const USETYPE = {j(usetype_js)};
const USAGE_DATA = {j(usage_js)};
const PRICE = {j(prices)};
const SECTIONS = {j(section_js)};
const EXTRA_DRPY = new Set({j(list(EXTRA_DRPY_DISTRICTS))});

// sub-options for usage 3/4/5
const SUB_OPTIONS = {{
  '3': [
    {{v:'0.015', l:'4戶以內（1.5%）'}},
    {{v:'0.020', l:'5～6戶（2.0%）'}},
    {{v:'0.024', l:'7戶以上（2.4%）'}},
  ],
  '4': [
    {{v:'0.020', l:'1年以內（2.0%）'}},
    {{v:'0.024', l:'超過1年、2年以內（2.4%）'}},
    {{v:'0.036', l:'超過2年、4年以內（3.6%）'}},
    {{v:'0.042', l:'超過4年、5年以內（4.2%）'}},
    {{v:'0.048', l:'超過5年（4.8%）'}},
  ],
  '5': [
    {{v:'0.032', l:'2戶以內（3.2%）'}},
    {{v:'0.038', l:'3～4戶（3.8%）'}},
    {{v:'0.042', l:'5～6戶（4.2%）'}},
    {{v:'0.048', l:'7戶以上（4.8%）'}},
  ]
}};

// ── 工具函數 ──
function fmt(n) {{
  if (!n && n !== 0) return '—';
  return Math.round(n).toLocaleString('zh-TW');
}}

function getTaxYm() {{
  const year = parseInt(document.getElementById('rocYear').value) || 0;
  const month = parseInt(document.getElementById('rocMonth').value) || 0;
  if (!year || !month) return null;
  return String(year).padStart(3,'0') + String(month).padStart(2,'0');
}}

function getTaxType() {{
  const r = document.querySelector('input[name="taxType"]:checked');
  return r ? r.value : '00000';
}}

function cmpYm(a, b) {{
  return a.localeCompare(b);
}}

function getDeprInfo(structNo, taxYm) {{
  const s = STRUCT[structNo];
  if (!s) return null;
  for (const d of s.d) {{
    if (cmpYm(taxYm, d.s) >= 0 && cmpYm(taxYm, d.e) <= 0) return d;
  }}
  return s.d[s.d.length - 1];
}}

function getPrice(structNo, floors, mainUseTypeNo, taxType) {{
  const ps = PRICE[structNo];
  if (!ps) return 0;
  const floorStr = String(floors);
  if (!ps[floorStr]) return 0;
  const u = ps[floorStr][String(mainUseTypeNo)];
  if (!u) return 0;
  return u[taxType] || 0;
}}

function getSectionRate(districtNo, sectionIdx, taxYm) {{
  const sects = SECTIONS[districtNo];
  if (!sects || sectionIdx < 0 || sectionIdx >= sects.length) return 1;
  const sect = sects[sectionIdx];
  for (const r of sect.r) {{
    if (cmpYm(taxYm || '00000', r.s) >= 0 && cmpYm(taxYm || '00000', r.e) <= 0) return r.v / 100;
  }}
  return sect.r[sect.r.length - 1].v / 100;
}}

function calcTaxYears(taxYm) {{
  // 計算到下一個課稅年度的經歷年數
  const rocYear = parseInt(taxYm.slice(0, 3));
  const rocMonth = parseInt(taxYm.slice(3, 5));
  const adYear = rocYear + 1911;
  const completionDate = new Date(adYear, rocMonth - 1, 1);
  // 課稅年度：當年超過10月則為下年度
  const now = new Date();
  const taxYear = (now.getMonth() >= 10) ? now.getFullYear() + 1 : now.getFullYear();
  const houseYear = completionDate.getFullYear();
  return Math.max(0, taxYear - houseYear);
}}

function calcOnePart(structNo, floors, floorHeight, useTypeNo, taxYm, taxType, districtNo, sectionIdx, usageRate) {{
  if (!structNo || floors === '' || !useTypeNo || !taxYm || !districtNo || sectionIdx < 0 || !usageRate) return null;

  // 取 mainUseTypeNo 和 discount
  const ut = USETYPE[structNo] && USETYPE[structNo][useTypeNo];
  if (!ut) return null;
  const mainUseTypeNo = ut.m;
  const discount = ut.disc;

  // 標準單價
  let price = getPrice(structNo, parseInt(floors), mainUseTypeNo, taxType);
  if (!price) return null;

  // 樓層高度調整
  const h = parseFloat(floorHeight);
  if (!isNaN(h)) {{
    if (h > 4) price = price + price * (h - 4) * 10 * 0.0125;
    else if (h < 2) price = price - price * (3 - h) / 3 * 0.5;
  }}

  // 用途折扣
  if (discount) price = price * discount;
  price = Math.floor(price);

  // 折舊
  const dep = getDeprInfo(structNo, taxYm);
  if (!dep) return null;
  let drpy = dep.r;
  if (EXTRA_DRPY.has(districtNo)) drpy += 0.0005;
  const years = calcTaxYears(taxYm);
  const deprecFactor = Math.max(dep.res, 1 - drpy * years);

  // 地段率
  const sectionRate = getSectionRate(districtNo, sectionIdx, taxYm);

  // 現值 & 稅額
  const currentValue = price * deprecFactor * sectionRate;
  return {{
    price,
    drpy,
    years,
    deprecFactor,
    sectionRate,
    currentValue,
    usageRate,
    tax: Math.floor(currentValue * usageRate)
  }};
}}

// ── UI 事件 ──
function onEraChange() {{
  calcAll();
}}

function onDateChange() {{
  const taxYm = getTaxYm();
  const disp = document.getElementById('taxYmDisplay');
  if (taxYm) {{
    disp.textContent = '▶ 地價稅年月代碼：' + taxYm;
  }} else {{
    disp.textContent = '';
  }}
  calcAll();
}}

function onStructChange() {{
  const structNo = document.getElementById('structNo').value;
  const sel = document.getElementById('useTypeNo');
  sel.innerHTML = '<option value="">請選擇</option>';
  if (!structNo || !USETYPE[structNo]) {{ calcAll(); return; }}
  const types = USETYPE[structNo];
  // 常見的放前面
  const common = [], others = [];
  for (const [k, v] of Object.entries(types)) {{
    (v.g ? common : others).push({{k, ...v}});
  }}
  if (common.length) {{
    const og = document.createElement('optgroup');
    og.label = '常見用途';
    common.forEach(t => {{
      const o = document.createElement('option');
      o.value = t.k; o.textContent = t.n;
      og.appendChild(o);
    }});
    sel.appendChild(og);
  }}
  if (others.length) {{
    const og = document.createElement('optgroup');
    og.label = '其他用途';
    others.forEach(t => {{
      const o = document.createElement('option');
      o.value = t.k; o.textContent = t.n;
      og.appendChild(o);
    }});
    sel.appendChild(og);
  }}
  calcAll();
}}

function onDistrictChange() {{
  const dv = document.getElementById('district').value;
  const sel = document.getElementById('section');
  sel.innerHTML = '<option value="">請選擇路段</option>';
  document.getElementById('sectionRateDisplay').style.display = 'none';
  if (!dv || !SECTIONS[dv]) {{ calcAll(); return; }}
  SECTIONS[dv].forEach((s, i) => {{
    const o = document.createElement('option');
    o.value = i; o.textContent = s.n;
    sel.appendChild(o);
  }});
  calcAll();
}}

function onUsageChange(idx) {{
  const usageNo = document.getElementById('usageNo' + idx).value;
  const sub = document.getElementById('sub' + idx);
  const subSel = document.getElementById('subNo' + idx);
  const subLabel = document.getElementById('subLabel' + idx);
  if (['3','4','5'].includes(usageNo)) {{
    sub.style.display = 'block';
    subSel.innerHTML = '';
    SUB_OPTIONS[usageNo].forEach(opt => {{
      const o = document.createElement('option');
      o.value = opt.v; o.textContent = opt.l;
      subSel.appendChild(o);
    }});
    subLabel.textContent = usageNo === '3' ? '持有戶數' : usageNo === '4' ? '持有年數' : '持有戶數';
  }} else {{
    sub.style.display = 'none';
  }}
  calcAll();
}}

function addUsage() {{
  document.getElementById('usageBlock1').style.display = 'block';
  document.getElementById('addUsageBtn').style.display = 'none';
}}

function removeUsage() {{
  document.getElementById('usageBlock1').style.display = 'none';
  document.getElementById('addUsageBtn').style.display = '';
  document.getElementById('usageNo1').value = '';
  document.getElementById('area1').value = '';
  document.getElementById('sub1').style.display = 'none';
  calcAll();
}}

function getUsageRate(idx) {{
  const usageNo = document.getElementById('usageNo' + idx).value;
  if (!usageNo) return null;
  if (['3','4','5'].includes(usageNo)) {{
    const subVal = document.getElementById('subNo' + idx).value;
    return subVal ? parseFloat(subVal) : null;
  }}
  const ud = USAGE_DATA[usageNo];
  return ud ? ud.r : null;
}}

function calcAll() {{
  const structNo = document.getElementById('structNo').value;
  const floors = document.getElementById('floors').value;
  const floorHeight = document.getElementById('floorHeight').value || '3.5';
  const useTypeNo = document.getElementById('useTypeNo').value;
  const taxType = getTaxType();
  const taxYm = getTaxYm();
  const districtNo = document.getElementById('district').value;
  const sectionIdx = parseInt(document.getElementById('section').value);

  // Update section rate display
  const srDisp = document.getElementById('sectionRateDisplay');
  if (districtNo && !isNaN(sectionIdx) && sectionIdx >= 0 && taxYm) {{
    const rate = getSectionRate(districtNo, sectionIdx, taxYm);
    document.getElementById('sectionRateVal').textContent = (rate * 100).toFixed(0) + '%';
    srDisp.style.display = 'block';
  }} else {{
    srDisp.style.display = 'none';
  }}

  const rc = document.getElementById('resultCard');
  const breakdownEl = document.getElementById('resultBreakdown');

  let totalTax = 0;
  let allValid = false;
  let breakdownHtml = '';
  let hasAnyArea = false;

  for (let idx = 0; idx < 2; idx++) {{
    if (idx === 1 && document.getElementById('usageBlock1').style.display === 'none') continue;
    const area = parseFloat(document.getElementById('area' + idx).value) || 0;
    const usageRate = getUsageRate(idx);
    if (!area || !usageRate) continue;
    hasAnyArea = true;

    const result = calcOnePart(structNo, floors, floorHeight, useTypeNo, taxYm, taxType, districtNo, sectionIdx, usageRate);
    if (!result) continue;

    const partTax = Math.floor(result.tax * area / (result.currentValue / result.currentValue));
    // Actually recalc with area
    const tax = Math.floor(result.price * result.deprecFactor * result.sectionRate * area * usageRate);
    totalTax += tax;
    allValid = true;

    const usageName = document.getElementById('usageNo' + idx).options[document.getElementById('usageNo' + idx).selectedIndex]?.text || '';
    breakdownHtml += `
      <div style="border-top:.5px solid rgba(255,255,255,.15);padding-top:10px;margin-top:8px">
        <div class="breakdown-row"><span class="breakdown-label">使用情形 ${{idx+1}}</span><span class="breakdown-val">${{usageName.split('（')[0]}}</span></div>
        <div class="breakdown-row"><span class="breakdown-label">課稅面積</span><span class="breakdown-val">${{area.toLocaleString()}} ㎡</span></div>
        <div class="breakdown-row"><span class="breakdown-label">核定單價</span><span class="breakdown-val">${{fmt(result.price)}} 元/㎡</span></div>
        <div class="breakdown-row"><span class="breakdown-label">折舊後現值比例</span><span class="breakdown-val">${{(result.deprecFactor * 100).toFixed(2)}}%（折舊 ${{(result.drpy*100).toFixed(2)}}%×${{result.years}}年）</span></div>
        <div class="breakdown-row"><span class="breakdown-label">路段率</span><span class="breakdown-val">${{(result.sectionRate * 100).toFixed(0)}}%</span></div>
        <div class="breakdown-row"><span class="breakdown-label">適用稅率</span><span class="breakdown-val">${{(usageRate * 100).toFixed(1)}}%</span></div>
        <div class="breakdown-row" style="font-size:13px;font-weight:700"><span style="color:#fbbf24">本部分稅額</span><span style="color:#fbbf24">${{fmt(tax)}} 元</span></div>
      </div>`;
  }}

  if (allValid && hasAnyArea) {{
    rc.style.display = 'block';
    document.getElementById('resultTotal').textContent = fmt(totalTax);
    breakdownEl.innerHTML = breakdownHtml;
  }} else {{
    rc.style.display = 'none';
  }}
}}

function clearAll() {{
  ['rocYear','floors','floorHeight','area0','area1'].forEach(id => {{
    const el = document.getElementById(id);
    if (el) el.value = id === 'floorHeight' ? '3.5' : '';
  }});
  ['rocMonth','structNo','useTypeNo','district','usageNo0','usageNo1'].forEach(id => {{
    const el = document.getElementById(id);
    if (el) el.value = '';
  }});
  document.getElementById('section').innerHTML = '<option value="">請先選擇行政區</option>';
  document.getElementById('sub0').style.display = 'none';
  document.getElementById('sub1').style.display = 'none';
  document.getElementById('usageBlock1').style.display = 'none';
  document.getElementById('addUsageBtn').style.display = '';
  document.getElementById('resultCard').style.display = 'none';
  document.getElementById('sectionRateDisplay').style.display = 'none';
  document.getElementById('taxYmDisplay').textContent = '';
  document.querySelector('input[name="taxType"][value="00000"]').checked = true;
  document.getElementById('useTypeNo').innerHTML = '<option value="">請先選擇構造別</option>';
}}
</script>

<section style="max-width:720px;margin:0 auto 40px;padding:0 16px">
  <div style="background:#f5f5f7;border-radius:14px;padding:20px">
    <div style="font-size:11px;font-weight:700;color:#86868b;letter-spacing:.1em;text-transform:uppercase;margin-bottom:14px;text-align:center">延伸閱讀</div>
    <div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center">
      <a href="new-taipei-land-value-tax.html" style="font-size:13px;color:#1d1d1f;background:#fff;border:.5px solid #d2d2d7;padding:9px 16px;border-radius:980px;text-decoration:none;font-weight:500">新北市地價稅試算 →</a>
      <a href="land-value-tax-calculator.html" style="font-size:13px;color:#1d1d1f;background:#fff;border:.5px solid #d2d2d7;padding:9px 16px;border-radius:980px;text-decoration:none;font-weight:500">全台地價稅試算 →</a>
      <a href="land-tax-calculator.html" style="font-size:13px;color:#1d1d1f;background:#fff;border:.5px solid #d2d2d7;padding:9px 16px;border-radius:980px;text-decoration:none;font-weight:500">土地增值稅試算 →</a>
    </div>
  </div>
</section>
<div data-include="line-qr"></div>
<div data-include="footer"></div>
<div data-include="anti-fraud-modal"></div>'''


def main():
    import progress
    progress.start("generate_house_tax.py", 3, task="生成新北市房屋稅試算器")

    print("Loading data...")
    progress.update(1, message="載入資料中（建物構造、使用類別、單價、地段）…")
    structs, usetypes, usages, prices, sections = load_all()
    print(f"  structs: {len(structs)}")
    print(f"  usetypes: {sum(len(v) for v in usetypes.values())} entries")
    print(f"  prices: {len(prices)} structs")
    print(f"  sections: {len(sections)} districts")

    print("Generating HTML...")
    progress.update(2, message="生成 HTML 中…")
    html = build_html(structs, usetypes, usages, prices, sections)

    out = ROOT_DIR / 'new-taipei-house-tax.html'
    out.write_text(html, encoding='utf-8')
    size = len(html)
    print(f"✓ {out.name} written ({size:,} bytes / {size//1024} KB)")
    progress.done(f"✓ {out.name} 已寫入（{size//1024} KB）")


if __name__ == '__main__':
    main()
