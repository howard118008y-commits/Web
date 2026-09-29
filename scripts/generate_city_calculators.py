#!/usr/bin/env python3
"""
重建 14 個縣市地價稅試算頁的「行政區／地段」資料（NLSC API）

產物即模板（2026-09-29 改）：頁面上線後已逐頁手改（Better 版型、米米配色、fluid.css、
analytics-config.js、各縣市差異化 AEO 答案卡與 FAQ、手機試算卡片的 data-label），舊版
f-string 模板重跑會把這些全部洗回舊版。所以本腳本改成以「現行頁面」為底，只重寫 NLSC
衍生的兩段：
  1. <select id="district"> 的行政區選項
  2. const SECTIONS = {...}; 地段資料
其餘位元組原樣保留。版型／樣式改頁面本身或 fluid.css（§23 稅務試算表），不改這裡。
T 值與年度由 scripts/update_calculators.py + tax-config.json 管，不歸本腳本。

用法：
  python scripts/generate_city_calculators.py                 # 拉 NLSC 最新資料，覆寫 14 頁
  python scripts/generate_city_calculators.py --city hualien  # 只做一個縣市
  python scripts/generate_city_calculators.py --stub          # 不連網，資料取自現行頁面（驗 diff 0 用）
  CITY_CALC_DEST=/tmp/out python scripts/generate_city_calculators.py --stub   # 輸出到別處再 diff
"""

import argparse
import os
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
DEST_DIR = Path(os.environ.get('CITY_CALC_DEST') or ROOT_DIR)
NLSC_BASE = "https://api.nlsc.gov.tw/other"

CITIES = {
    'taichung': {'name': '台中市', 'county': 'B', 'file': 'taichung-land-value-tax.html'},
    'tainan': {'name': '台南市', 'county': 'D', 'file': 'tainan-land-value-tax.html'},
    'kaohsiung': {'name': '高雄市', 'county': 'E', 'file': 'kaohsiung-land-value-tax.html'},
    'yilan': {'name': '宜蘭縣', 'county': 'G', 'file': 'yilan-land-value-tax.html'},
    'chiayi_city': {'name': '嘉義市', 'county': 'I', 'file': 'chiayi-city-land-value-tax.html'},
    'miaoli': {'name': '苗栗縣', 'county': 'K', 'file': 'miaoli-land-value-tax.html'},
    'nantou': {'name': '南投縣', 'county': 'M', 'file': 'nantou-land-value-tax.html'},
    'changhua': {'name': '彰化縣', 'county': 'N', 'file': 'changhua-land-value-tax.html'},
    'yunlin': {'name': '雲林縣', 'county': 'P', 'file': 'yunlin-land-value-tax.html'},
    'chiayi_county': {'name': '嘉義縣', 'county': 'Q', 'file': 'chiayi-county-land-value-tax.html'},
    'pingtung': {'name': '屏東縣', 'county': 'T', 'file': 'pingtung-land-value-tax.html'},
    'hualien': {'name': '花蓮縣', 'county': 'U', 'file': 'hualien-land-value-tax.html'},
    'taitung': {'name': '台東縣', 'county': 'V', 'file': 'taitung-land-value-tax.html'},
    'penghu': {'name': '澎湖縣', 'county': 'X', 'file': 'penghu-land-value-tax.html'},
}

DISTRICT_RE = re.compile(r'(<select id="district"[^>]*>\n\s*<option value="">請選擇</option>\n)(.*?)(\n\s*</select>)', re.S)
SECTIONS_RE = re.compile(r'const SECTIONS = \{\n.*?\n\};', re.S)


def fetch_towns(county):
    import requests
    url = f"{NLSC_BASE}/ListTown/{county}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    towns = {}
    for item in root.findall('.//townItem'):
        code = item.findtext('towncode', '').strip()
        name = item.findtext('townname', '').strip()
        if code and name:
            towns[code] = name
    return towns


def fetch_sections(county, town_code):
    import requests
    url = f"{NLSC_BASE}/ListLandSection/{county}/{town_code}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    sections = []
    for item in root.findall('.//sectItem'):
        code = item.findtext('sectcode', '').strip()
        name = item.findtext('sectstr', '').strip()
        if code and name:
            sections.append([code, name])
    return sections


def js_sections(sections_dict):
    lines = ['const SECTIONS = {']
    keys = sorted(sections_dict.keys())
    for i, k in enumerate(keys):
        pairs = sections_dict[k]
        comma = ',' if i < len(keys) - 1 else ''
        inner = ','.join(f"['{c}','{n.replace(chr(39), chr(92)+chr(39))}']" for c, n in pairs)
        lines.append(f"  '{k}': [{inner}]{comma}")
    lines.append('};')
    return '\n'.join(lines)


def district_options(towns):
    """Generate <option> elements for district dropdown"""
    lines = []
    for code in sorted(towns.keys()):
        dv = code[-2:]  # strip county prefix, use last 2 digits
        lines.append(f'        <option value="{dv}">{towns[code]}</option>')
    return '\n'.join(lines)


def data_from_page(base_html):
    """--stub：從現行頁面讀回行政區與地段（不連網），用來驗證重跑 diff 0"""
    m = DISTRICT_RE.search(base_html)
    towns = dict(re.findall(r'<option value="(\d+)">([^<]+)</option>', m.group(2)))
    sections = {}
    for line in SECTIONS_RE.search(base_html).group(0).split('\n')[1:-1]:
        k, body = re.match(r"\s*'(\d+)': \[(.*)\],?$", line).groups()
        sections[k] = [[c, n.replace("\\'", "'")] for c, n in re.findall(r"\['([^']*)','((?:[^'\\]|\\.)*)'\]", body)]
    return towns, sections


def generate_html(base_html, towns, sections_dict):
    """以現行頁面為底，只換掉行政區選項與 SECTIONS 兩段"""
    if not DISTRICT_RE.search(base_html) or not SECTIONS_RE.search(base_html):
        raise ValueError('頁面找不到 <select id="district"> 或 const SECTIONS 區塊，停止（不回退舊模板）')
    html = DISTRICT_RE.sub(lambda m: m.group(1) + district_options(towns) + m.group(3), base_html, count=1)
    return SECTIONS_RE.sub(lambda m: js_sections(sections_dict), html, count=1)


def main():
    ap = argparse.ArgumentParser(description='重建縣市地價稅試算頁的行政區／地段資料')
    ap.add_argument('--city', help='只處理指定城市 key（如 hualien）')
    ap.add_argument('--stub', action='store_true', help='不連網，資料取自現行頁面')
    args = ap.parse_args()

    cities = [(k, c) for k, c in CITIES.items() if not args.city or k == args.city]
    if not cities:
        raise SystemExit(f'未知城市 key：{args.city}')
    progress = None
    if not args.stub:
        import progress
        progress.start("generate_city_calculators.py", len(cities), task="重建縣市地價稅行政區／地段")
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    for i, (city_key, cfg) in enumerate(cities):
        base_path = ROOT_DIR / cfg['file']
        if not base_path.exists():
            raise SystemExit(f"✗ {cfg['file']} 不存在：本腳本只重建既有頁面的資料段，新頁請先手工建好")
        base_html = base_path.read_text(encoding='utf-8')
        print(f"\n== {cfg['name']} ({cfg['county']}) ==")

        if args.stub:
            towns, sections_dict = data_from_page(base_html)
        else:
            county = cfg['county']
            progress.update(i, task=f"處理 {cfg['name']}", message=f"拉取 {cfg['name']} 行政區資料…")
            towns_raw = fetch_towns(county)
            towns = {code[-2:]: name for code, name in towns_raw.items()}
            print(f"  {len(towns)} districts")
            time.sleep(0.3)
            sections_dict = {}
            for j, full_code in enumerate(sorted(towns_raw.keys())):
                dv = full_code[-2:]
                progress.update(i, task=f"處理 {cfg['name']}", message=f"  地段 {j+1}/{len(towns_raw)}：{towns[dv]}")
                sects = fetch_sections(county, full_code)
                if sects:
                    sections_dict[dv] = sects
                time.sleep(0.25)

        html = generate_html(base_html, towns, sections_dict)
        out = DEST_DIR / cfg['file']
        out.write_text(html, encoding='utf-8')
        print(f"  ✓ {out} {'（無變更）' if html == base_html else '（資料已更新）'}")
        if progress:
            progress.update(i + 1, task=f"完成 {cfg['name']}", message=f"✓ {cfg['file']} 已寫入")

    if progress:
        progress.done("✓ 全部縣市完成！")
    print("\n✓ 全部完成")


if __name__ == '__main__':
    main()
