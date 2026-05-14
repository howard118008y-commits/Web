#!/usr/bin/env python3
"""
地段資料重建腳本
從 NLSC 政府 API 拉取最新地段資料，靜態內嵌至各縣市 HTML 試算器
台北市：改為靜態 SECTIONS（保留 Cloudflare Worker 只用於申報地價查詢）
其他縣市：更新 SECTIONS 名稱清單
"""

import requests
import xml.etree.ElementTree as ET
import re
import json
import time
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
NLSC_BASE = "https://api.nlsc.gov.tw/other/ListLandSection"
TAIPEI_PROXY = "https://taipei-tax-proxy.howard118008y.workers.dev/roadname"

# ── 新北市：dropdown 值 → NLSC town code ──
NEW_TAIPEI_MAP = {
    '01': 'F14',  # 板橋
    '02': 'F05',  # 三重
    '03': 'F18',  # 中和
    '04': 'F33',  # 永和
    '05': 'F01',  # 新莊
    '06': 'F07',  # 新店
    '07': 'F17',  # 樹林
    '08': 'F16',  # 鶯歌
    '09': 'F15',  # 三峽
    '10': 'F27',  # 淡水
    '11': 'F28',  # 汐止
    '12': 'F21',  # 瑞芳
    '13': 'F19',  # 土城
    '14': 'F04',  # 蘆洲
    '15': 'F03',  # 五股
    '16': 'F06',  # 泰山
    '17': 'F02',  # 林口
    '18': 'F09',  # 深坑
    '19': 'F08',  # 石碇
    '20': 'F10',  # 坪林
    '21': 'F30',  # 三芝
    '22': 'F31',  # 石門
    '23': 'F32',  # 八里
    '24': 'F22',  # 平溪
    '25': 'F23',  # 雙溪
    '26': 'F24',  # 貢寮
    '27': 'F25',  # 金山
    '28': 'F26',  # 萬里
    '29': 'F11',  # 烏來
}

# ── 台北市：dropdown 值與 NLSC town code 相同（A01, A02…）──
TAIPEI_DISTRICTS = ['01','02','03','05','09','10','11','13','14','15','16','17']

# ── 其他城市：NLSC county + districts ──
OTHER_CITIES = {
    'taoyuan':       ('H', [f'{i:02d}' for i in range(1, 14)]),
    'keelung':       ('C', [f'{i:02d}' for i in range(1, 8)]),
    'hsinchu_city':  ('O', ['01']),
    'hsinchu_county':('J', ['02','03','04','05','06','08','09','10','11','12','13','14','15']),
}


def fetch_nlsc(county, town):
    url = f"{NLSC_BASE}/{county}/{town}"
    print(f"  fetch {url}")
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    sections = []
    for item in root.findall('.//sectItem'):
        name = item.findtext('sectstr', '').strip()
        if name:
            sections.append(name)
    return sections


def fetch_nlsc_with_code(county, town):
    """同上但回傳 (code, label) tuple"""
    url = f"{NLSC_BASE}/{county}/{town}"
    print(f"  fetch {url}")
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    sections = []
    for item in root.findall('.//sectItem'):
        code = item.findtext('sectcode', '').strip()
        name = item.findtext('sectstr', '').strip()
        if code and name:
            sections.append([code, name])
    return sections


def js_str_array(lst):
    """把 list of str 轉成 JS 陣列字串 ['a','b',...]"""
    escaped = [s.replace("'", "\\'") for s in lst]
    return '[' + ','.join(f"'{s}'" for s in escaped) + ']'


def js_code_label_array(lst):
    """把 [[code, label], ...] 轉成 JS 巢狀陣列 [['0600','西松段一小段'],...]"""
    parts = []
    for code, label in lst:
        lbl = label.replace("'", "\\'")
        parts.append(f"['{code}','{lbl}']")
    return '[' + ','.join(parts) + ']'


def build_sections_obj(sections_dict, use_code_label=False):
    """生成多行 SECTIONS JS 物件字串"""
    lines = ['const SECTIONS = {']
    keys = sorted(sections_dict.keys())
    for i, k in enumerate(keys):
        v = sections_dict[k]
        comma = ',' if i < len(keys) - 1 else ''
        if use_code_label:
            lines.append(f"  '{k}': {js_code_label_array(v)}{comma}")
        else:
            lines.append(f"  '{k}': {js_str_array(v)}{comma}")
    lines.append('};')
    return '\n'.join(lines)


def replace_sections_in_html(filepath, new_sections_js):
    """用新的 SECTIONS JS 物件替換 HTML 中的舊版本"""
    content = filepath.read_text(encoding='utf-8')
    pattern = r'const SECTIONS = \{.*?\};'
    new_content, count = re.subn(pattern, new_sections_js, content, flags=re.DOTALL)
    if count == 0:
        print(f"  ⚠  找不到 SECTIONS 物件 in {filepath.name}")
        return False
    filepath.write_text(new_content, encoding='utf-8')
    print(f"  ✓ {filepath.name} SECTIONS 已更新")
    return True


def replace_taipei_ondistrictchange(filepath):
    """把台北的 async onDistrictChange（proxy 版）改成同步靜態版"""
    content = filepath.read_text(encoding='utf-8')

    old_func = r'async function onDistrictChange\(\) \{.*?checkQueryBtn\(\);\s*\}'
    new_func = """function onDistrictChange() {
  const dv = document.getElementById('district').value;
  const sel = document.getElementById('section');
  sel.innerHTML = '<option value="">請先選擇行政區</option>';
  resetPrice();
  if (!dv) { checkQueryBtn(); return; }
  sel.innerHTML = '<option value="">請選擇地段</option>';
  if (SECTIONS[dv]) {
    SECTIONS[dv].forEach(function(item) {
      const code = item[0], label = item[1];
      const o = document.createElement('option');
      o.value = code; o.textContent = label;
      sel.appendChild(o);
    });
  }
  checkQueryBtn();
}"""

    new_content, count = re.subn(old_func, new_func, content, flags=re.DOTALL)
    if count == 0:
        print(f"  ⚠  找不到 async onDistrictChange in {filepath.name}")
        return False
    filepath.write_text(new_content, encoding='utf-8')
    print(f"  ✓ {filepath.name} onDistrictChange 已改為靜態版")
    return True


def process_taipei():
    print("\n== 台北市 ==")
    sections = {}
    for dv in TAIPEI_DISTRICTS:
        town = f"A{dv}"
        items = fetch_nlsc_with_code('A', town)
        sections[dv] = items
        print(f"    {dv} ({town}): {len(items)} 地段")
        time.sleep(0.3)

    filepath = ROOT_DIR / 'taipei-land-value-tax.html'
    sections_js = build_sections_obj(sections, use_code_label=True)

    content = filepath.read_text(encoding='utf-8')
    # Insert SECTIONS before TIERS or const T
    if 'const SECTIONS' in content:
        replace_sections_in_html(filepath, sections_js)
    else:
        # insert before TIERS
        new_content = content.replace(
            'const TIERS = [',
            sections_js + '\n\nconst TIERS = ['
        )
        filepath.write_text(new_content, encoding='utf-8')
        print(f"  ✓ {filepath.name} SECTIONS 已插入")

    replace_taipei_ondistrictchange(filepath)


def process_new_taipei():
    print("\n== 新北市 ==")
    sections = {}
    for dv, town in sorted(NEW_TAIPEI_MAP.items()):
        items = fetch_nlsc('F', town)
        sections[dv] = items
        print(f"    {dv} ({town}): {len(items)} 地段")
        time.sleep(0.3)

    filepath = ROOT_DIR / 'new-taipei-land-value-tax.html'
    replace_sections_in_html(filepath, build_sections_obj(sections))


def process_other(city_key, county, districts):
    from scripts_tax_config import CITY_FILES
    city_files = {
        'taoyuan': 'taoyuan-land-value-tax.html',
        'keelung': 'keelung-land-value-tax.html',
        'hsinchu_city': 'hsinchu-city-land-value-tax.html',
        'hsinchu_county': 'hsinchu-county-land-value-tax.html',
    }
    filename = city_files[city_key]
    print(f"\n== {filename} ({county}) ==")
    sections = {}
    for dv in districts:
        town = f"{county}{dv}"
        items = fetch_nlsc(county, town)
        sections[dv] = items
        print(f"    {dv} ({town}): {len(items)} 地段")
        time.sleep(0.3)

    filepath = ROOT_DIR / filename
    replace_sections_in_html(filepath, build_sections_obj(sections))


def main():
    process_taipei()
    process_new_taipei()

    city_files = {
        'taoyuan': 'taoyuan-land-value-tax.html',
        'keelung': 'keelung-land-value-tax.html',
        'hsinchu_city': 'hsinchu-city-land-value-tax.html',
        'hsinchu_county': 'hsinchu-county-land-value-tax.html',
    }
    for city_key, (county, districts) in OTHER_CITIES.items():
        print(f"\n== {city_files[city_key]} ({county}) ==")
        sections = {}
        for dv in districts:
            town = f"{county}{dv}"
            items = fetch_nlsc(county, town)
            sections[dv] = items
            print(f"    {dv} ({town}): {len(items)} 地段")
            time.sleep(0.3)
        filepath = ROOT_DIR / city_files[city_key]
        replace_sections_in_html(filepath, build_sections_obj(sections))

    print("\n✓ 全部完成")


if __name__ == '__main__':
    main()
