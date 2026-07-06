#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cx_history.json 歷史序列管線 — 房貸儀表板 v4 完整版的走勢資料

兩層架構：
1. 深歷史（來源本身給全序列）：A01 央行API、A02/A03 央行5newloan(1994起)、
   D01 FRED DGS10、D02/D03 yfinance、D04 FRED 台灣CPI年增
2. 累積制（來源只給當期值）：其餘指標每次執行把 cx_data.json 的現值記到當期月份，
   歷史隨每日 CI 自然長出來（誠實累積，不偽造回溯）

輸出格式：{code: {"unit": str, "points": [["YYYY-MM", float], ...]}}
merge 規則：新值覆蓋同月舊值；舊月份永不刪除。
"""
import json, re, io, sys
from datetime import date
from pathlib import Path

import requests
import urllib3
urllib3.disable_warnings()

BASE = Path(__file__).resolve().parent.parent
HIST_FILE = BASE / 'cx_history.json'
DATA_FILE = BASE / 'cx_data.json'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
SINCE = '2015-01'   # 深歷史起點（頁面畫 10 年）


def get(url, **kw):
    kw.setdefault('timeout', 60)
    kw.setdefault('verify', False)
    kw.setdefault('headers', HEADERS)
    try:
        r = requests.get(url, **kw)
        r.raise_for_status()
        return r
    except Exception as e:
        print(f'  GET {url[:70]}: {e}')
        return None


def load_hist():
    if HIST_FILE.exists():
        return json.load(open(HIST_FILE, encoding='utf-8'))
    return {}


def merge(hist, code, unit, points):
    """points: dict {ym: value}"""
    ent = hist.setdefault(code, {'unit': unit, 'points': []})
    ent['unit'] = unit
    cur = dict(ent['points'])
    for ym, v in points.items():
        if ym >= SINCE and v is not None:
            cur[ym] = round(float(v), 4)
    ent['points'] = sorted(cur.items())
    return len(points)


# ── 深歷史抓取 ──────────────────────────────────────────────

def hist_A01():
    """央行重貼現率：調整點 → 前向填充成月序列"""
    r = get('https://cpx.cbc.gov.tw/api/OpenData/DataSet?set_id=6022')
    if not r:
        return {}
    changes = []
    for row in r.json():
        try:
            d = row.get('調整日期', '')
            m = re.match(r'(\d{4})/(\d{1,2})', d)
            if m:
                changes.append((f'{m.group(1)}-{int(m.group(2)):02d}', float(row['重貼現率'])))
        except Exception:
            continue
    changes.sort()
    if not changes:
        return {}
    out, val = {}, None
    y0, m0 = int(SINCE[:4]), int(SINCE[5:7])
    today = date.today()
    # 起點值 = SINCE 之前最後一次調整
    for ym, v in changes:
        if ym <= SINCE:
            val = v
    y, m = y0, m0
    ci = 0
    while (y, m) <= (today.year, today.month):
        ym = f'{y}-{m:02d}'
        while ci < len(changes) and changes[ci][0] <= ym:
            val = changes[ci][1]
            ci += 1
        if val is not None:
            out[ym] = val
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def _dl_5newloan():
    """lp-528 → cp-528 → 附件（實為 ODS）"""
    r1 = get('https://www.cbc.gov.tw/tw/lp-528-1.html')
    if not r1:
        return None
    m1 = re.search(r'href="(/tw/cp-528-\d+-\w+-\d+\.html)"', r1.text)
    if not m1:
        return None
    r2 = get('https://www.cbc.gov.tw' + m1.group(1))
    if not r2:
        return None
    # 附件連結是絕對網址，且同稿常掛 xls/ods/pdf 三種——逐一試到 zip(PK) 為止
    for m2 in re.finditer(r'href="(?:https://www\.cbc\.gov\.tw)?(/tw/dl-\d+-[0-9a-f]+\.html)"', r2.text):
        r3 = get('https://www.cbc.gov.tw' + m2.group(1))
        if r3 and r3.content[:2] == b'PK':
            return r3.content
    return None


def hist_A02_A03():
    """五大銀行新承做：83/07 起月列（金額百萬、利率%）"""
    import zipfile
    blob = _dl_5newloan()
    if not blob or blob[:2] != b'PK':
        print('  5newloan 非 ODS，跳過')
        return {}, {}
    xml = zipfile.ZipFile(io.BytesIO(blob)).read('content.xml').decode('utf-8', 'ignore')
    t = re.sub(r'<[^>]+>', '|', xml)
    t = re.sub(r'\|+', '|', t)
    rate, amt = {}, {}
    # 列樣式：|115/05|56,204|2.322|...（購屋貸款=第1組 金額,利率）
    for m in re.finditer(r'\|(\d{2,3})/(\d{2})\|([\d,]+)\|([\d.]+)\|', t):
        y = int(m.group(1)) + 1911
        ym = f'{y}-{int(m.group(2)):02d}'
        try:
            amt[ym] = float(m.group(3).replace(',', '')) / 100.0   # 百萬 → 億
            rate[ym] = float(m.group(4))
        except ValueError:
            continue
    return rate, amt


def _fred_series(series_id):
    r = get(f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}')
    if not r:
        return {}
    out = {}
    for line in r.text.splitlines()[1:]:
        parts = line.split(',')
        if len(parts) != 2 or parts[1] in ('', '.'):
            continue
        ym = parts[0][:7]
        try:
            out[ym] = float(parts[1])   # 同月多筆取最後（月末值）
        except ValueError:
            continue
    return out


def hist_D01():
    return _fred_series('DGS10')


def hist_D04():
    """台灣 CPI 年增率 — 主計總處 XML（沿用 fetch_indicators 的 DGBAS_CPI_XML，整串月序列）"""
    import xml.etree.ElementTree as ET
    from fetch_indicators import DGBAS_CPI_XML
    r = get(DGBAS_CPI_XML, timeout=55)
    if not r:
        return {}
    out = {}
    for obs in ET.fromstring(r.content).findall('Obs'):
        if '總指數' in obs.findtext('Item', '') and '年增率' in obs.findtext('TYPE', ''):
            tstr = obs.findtext('TIME_PERIOD', '')
            v = obs.findtext('Item_VALUE', '').strip()
            m = re.match(r'(\d{4})M(\d{2})', tstr)
            if m and v:
                try:
                    out[f"{m.group(1)}-{m.group(2)}"] = float(v)
                except ValueError:
                    pass
    return out


def _yf_monthly(ticker):
    try:
        import yfinance as yf
        h = yf.Ticker(ticker).history(period='11y', interval='1mo')
        return {idx.strftime('%Y-%m'): float(v) for idx, v in h['Close'].items() if v == v}
    except Exception as e:
        print(f'  yfinance {ticker}: {e}')
        return {}


def hist_D02():
    return _yf_monthly('TWD=X')


def hist_D03():
    return _yf_monthly('^TWII')


# ── 累積制 ──────────────────────────────────────────────────

NUM_RE = re.compile(r'-?\d[\d,]*\.?\d*')

def _q_to_ym(u):
    m = re.match(r'(\d{4})-Q([1-4])', u)
    if m:
        return f"{m.group(1)}-{int(m.group(2)) * 3:02d}"
    m = re.match(r'\d{4}-\d{2}$', u or '')
    return u if m else None


def accumulate(hist):
    data = json.load(open(DATA_FILE, encoding='utf-8'))
    n = 0
    for ind in data['indicators']:
        code = ind['code']
        ym = _q_to_ym(ind.get('updated', ''))
        if not ym:
            continue
        m = NUM_RE.search(ind.get('value', ''))
        if not m:
            continue   # 質性值（下滑中等）不入序列
        val = float(m.group(0).replace(',', ''))
        unit = re.sub(NUM_RE, '', ind.get('value', '')).strip() or ''
        merge(hist, code, unit, {ym: val})
        n += 1
    return n


def main():
    hist = load_hist()
    print('=== 深歷史 ===')
    for code, unit, fn in [('A01', '%', hist_A01), ('D01', '%', hist_D01),
                           ('D02', '', hist_D02), ('D03', '點', hist_D03),
                           ('D04', '%', hist_D04)]:
        try:
            pts = fn()
            print(f'  {code}: {merge(hist, code, unit, pts)} 點')
        except Exception as e:
            print(f'  {code}: 失敗（{type(e).__name__}: {str(e)[:60]}），保留既有序列')
    try:
        rate, amt = hist_A02_A03()
        print(f'  A02: {merge(hist, "A02", "%", rate)} 點（利率）')
        print(f'  A03: {merge(hist, "A03", "億", amt)} 點（金額）')
    except Exception as e:
        print(f'  A02/A03: 失敗（{str(e)[:60]}），保留既有序列')
    print('=== 累積制（cx_data 現值入帳）===')
    print(f'  記入 {accumulate(hist)} 項')
    json.dump(hist, open(HIST_FILE, 'w', encoding='utf-8'), ensure_ascii=False)
    total = sum(len(v['points']) for v in hist.values())
    print(f'=== 完成：{len(hist)} 指標、共 {total} 點 → {HIST_FILE.name} ===')


if __name__ == '__main__':
    main()
