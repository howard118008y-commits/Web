#!/usr/bin/env python3
"""
重建新北市房屋稅試算頁 new-taipei-house-tax.html 的資料段

產物即模板（2026-10-01 改）：頁面上線後已手改（米米配色、fluid.css 等），舊版 f-string
全頁模板重跑會洗回舊版。本腳本改以「現行頁面」為底，只重寫資料衍生的段落：
  1. <select id="structNo"> 構造別選項
  2. <select id="district"> 行政區選項
  3. const STRUCT / USETYPE / USAGE_DATA / PRICE / SECTIONS 五行
其餘位元組原樣保留。版型／樣式改頁面本身，不改這裡。

用法：
  /usr/bin/python3 scripts/generate_house_tax.py          # 讀 /tmp/housedata/*.json（新北市官方試算 JSON）重寫資料段
  /usr/bin/python3 scripts/generate_house_tax.py --stub   # 不需資料目錄，資料取自現行頁面（驗 diff 0 用）
  HOUSE_TAX_DEST=/tmp/out ... --stub                      # 輸出到別處再 diff
"""

import json
import argparse
import os
import re
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = Path('/tmp/housedata')
DEST_DIR = Path(os.environ.get('HOUSE_TAX_DEST') or ROOT_DIR)
PAGE = 'new-taipei-house-tax.html'

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


def build_parts(structs, usetypes, usages, prices, sections):
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

    def j(obj): return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))

    return {
        'struct_opts': ''.join(struct_opts),
        'district_opts': district_opts,
        'consts': {
            'STRUCT': j(struct_js), 'USETYPE': j(usetype_js), 'USAGE_DATA': j(usage_js),
            'PRICE': j(prices), 'SECTIONS': j(section_js),
        },
    }


STRUCT_SEL_RE = re.compile(r'(<select id="structNo"[^>]*>\n\s*<option value="">請選擇</option>\n\s*)(.*?)(\n\s*</select>)', re.S)
DISTRICT_SEL_RE = re.compile(r'(<select id="district"[^>]*>\n\s*<option value="">請選擇</option>\n)(.*?)(\n\s*</select>)', re.S)


def const_re(name):
    return re.compile(r'^const ' + name + r' = .*;$', re.M)


def apply_to_page(base_html, parts):
    """以現行頁面為底，只換資料衍生段落；找不到錨點就停止，不回退舊模板"""
    html = base_html
    for rx, key in ((STRUCT_SEL_RE, 'struct_opts'), (DISTRICT_SEL_RE, 'district_opts')):
        if not rx.search(html):
            raise SystemExit(f'✗ 頁面找不到 {key} 對應的 <select>，停止')
        html = rx.sub(lambda m: m.group(1) + parts[key] + m.group(3), html, count=1)
    for name, val in parts['consts'].items():
        rx = const_re(name)
        if not rx.search(html):
            raise SystemExit(f'✗ 頁面找不到 const {name}，停止')
        html = rx.sub(lambda m: f'const {name} = {val};', html, count=1)
    return html


def parts_from_page(base_html):
    """--stub：原樣讀回現行頁面的資料段（驗證重跑 diff 0）"""
    parts = {'consts': {}}
    for rx, key in ((STRUCT_SEL_RE, 'struct_opts'), (DISTRICT_SEL_RE, 'district_opts')):
        parts[key] = rx.search(base_html).group(2)
    for name in ('STRUCT', 'USETYPE', 'USAGE_DATA', 'PRICE', 'SECTIONS'):
        parts['consts'][name] = const_re(name).search(base_html).group(0)[len(f'const {name} = '):-1]
    return parts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stub', action='store_true', help='不連資料目錄，資料取自現行頁面')
    args = ap.parse_args()

    base_path = ROOT_DIR / PAGE
    if not base_path.exists():
        raise SystemExit(f'✗ {PAGE} 不存在：本腳本只重建既有頁面的資料段')
    base_html = base_path.read_text(encoding='utf-8')

    if args.stub:
        parts = parts_from_page(base_html)
    else:
        print("Loading data...")
        parts = build_parts(*load_all())
    html = apply_to_page(base_html, parts)

    out = DEST_DIR / PAGE
    out.write_text(html, encoding='utf-8')
    print(f"✓ {out} {'（無變更）' if html == base_html else '（資料已更新）'}")


if __name__ == '__main__':
    main()
