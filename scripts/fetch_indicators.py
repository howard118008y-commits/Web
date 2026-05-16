#!/usr/bin/env python3
"""
CX468 房貸儀表板 — 18 項指標自動抓取腳本
GitHub Actions 每日 08:30 台灣時間自動執行
"""

import json, requests, csv, io, time, re
import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path

try:
    import yfinance as yf
    HAS_YF = True
except ImportError:
    HAS_YF = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    import xlrd
    HAS_XLRD = True
except ImportError:
    HAS_XLRD = False

BASE      = Path(__file__).resolve().parent.parent
DATA_FILE = BASE / 'cx_data.json'
TODAY     = date.today()
THIS_MONTH = TODAY.strftime('%Y-%m')

# 使用 Mozilla UA — 許多政府 API 會封鎖自訂 UA
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept': 'application/json, text/html, */*',
}

# 主計總處 CPI XML（每月更新一次，約月初發布上月數據）
# 若 GitHub Actions 回報 404，請更新此 URL（從 ws.dgbas.gov.tw 取最新路徑）
DGBAS_CPI_XML = 'https://ws.dgbas.gov.tw/001/Upload/461/relfile/11525/230555/pr0101a1m.xml'

# ── 工具函數 ────────────────────────────────────────────────────────────────

def load_data():
    with open(DATA_FILE, encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def yf_get(ticker, period='5d'):
    """Yahoo Finance 最新收盤價"""
    if not HAS_YF:
        return None, None
    try:
        hist = yf.Ticker(ticker).history(period=period)
        if hist.empty:
            return None, None
        return float(hist['Close'].iloc[-1]), hist.index[-1].strftime('%Y-%m-%d')
    except Exception as e:
        print(f"  yfinance {ticker}: {e}")
        return None, None

def fred_last(series):
    """FRED CSV 最新值（無需 API key）— 只解析 YYYY-MM-DD,number 格式行"""
    try:
        url = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}'
        r = requests.get(url, timeout=20, headers=HEADERS)
        valid = []
        for line in r.text.strip().splitlines():
            parts = line.split(',')
            if len(parts) >= 2:
                dt_part  = parts[0].strip()
                val_part = parts[1].strip()
                if re.match(r'\d{4}-\d{2}-\d{2}', dt_part) and val_part and val_part != '.':
                    try:
                        valid.append((float(val_part), dt_part))
                    except ValueError:
                        pass
        return valid[-1] if valid else (None, None)
    except Exception as e:
        print(f"  FRED {series}: {e}")
        return None, None

def quarter_str(date_str):
    """'2026-01-01' → '2026-Q1'"""
    try:
        d = datetime.strptime(date_str, '%Y-%m-%d')
        q = (d.month - 1) // 3 + 1
        return f'{d.year}-Q{q}'
    except:
        return date_str[:7]

def get(url, **kwargs):
    kwargs.setdefault('timeout', 15)
    try:
        r = requests.get(url, headers=HEADERS, **kwargs)
        r.raise_for_status()
        return r
    except Exception as e:
        print(f"  GET {url[:60]}... : {e}")
        return None

# ── 個別指標抓取函數 ────────────────────────────────────────────────────────

def fetch_A01():
    """央行重貼現率 — CBC Open Data API set_id=6022"""
    try:
        url = 'https://cpx.cbc.gov.tw/api/OpenData/DataSet?set_id=6022'
        r = requests.get(url, headers=HEADERS, timeout=15)
        data = r.json()
        if isinstance(data, list) and data:
            latest = data[0]  # 最新一筆在最前面
            val = float(latest.get('重貼現率', 0))
            raw_dt = latest.get('調整日期', '')  # '2024/3/22'
            try:
                d = datetime.strptime(raw_dt, '%Y/%m/%d')
                updated = d.strftime('%Y-%m')
            except Exception:
                updated = THIS_MONTH

            if val > 2.5:
                status, note = 'red',    f'重貼現率 {val:.2f}%，升息週期，信貸趨緊'
            elif val >= 1.5:
                status, note = 'yellow', f'{val:.2f}%，中性偏緊，連續凍漲'
            else:
                status, note = 'green',  f'{val:.2f}%，寬鬆週期，有利購屋'
            return dict(value=f'{val:.2f}%', status=status, note=note, updated=updated)
    except Exception as e:
        print(f"  A01 CBC API: {e}")

    # 備用：FRED 台灣重貼現率季報（可能落後 1~2 季）
    val, dt = fred_last('INTDSRTW01STQ')
    if val is None:
        return None
    if val > 2.5:
        status, note = 'red',    f'重貼現率 {val:.2f}%，升息週期，信貸趨緊'
    elif val >= 1.5:
        status, note = 'yellow', f'{val:.2f}%，中性偏緊，連續凍漲'
    else:
        status, note = 'green',  f'{val:.2f}%，寬鬆週期'
    return dict(value=f'{val:.2f}%', status=status, note=note,
                updated=dt[:7] if dt else THIS_MONTH)


def _fetch_5newloan_data():
    """CBC 五大銀行新承做放款金額與利率 XLS
    抓取流程：lp-528-1 → 最新 cp-528 → dl-XXXXX(5newloan.xls) → xlrd 解析
    回傳 (updated, mtg_rate_pct, mtg_amount_mln) 或 None
    """
    if not HAS_XLRD:
        print("  xlrd not installed, skip 5newloan")
        return None
    try:
        # Step 1: 取得最新一期新聞稿 URL
        r1 = get('https://www.cbc.gov.tw/tw/lp-528-1.html')
        if not r1:
            return None
        m1 = re.search(r'href="(/tw/cp-528-\d+-\w+-\d+\.html)"', r1.text)
        if not m1:
            return None
        article_url = 'https://www.cbc.gov.tw' + m1.group(1)

        # Step 2: 取得新聞稿頁面，找 5newloan.xls 下載連結
        r2 = get(article_url)
        if not r2:
            return None
        # 配對 title="5newloan.xls" 的 <a href="..."> 或 class="xls" 緊接在 5newloan span 後
        xls_m = re.search(
            r'href="(https://www\.cbc\.gov\.tw/tw/dl-\d+[^"]+)"[^>]*title="5newloan\.xls"',
            r2.text)
        if not xls_m:
            xls_m = re.search(
                r'title="5newloan\.xls"[^>]*href="(https://www\.cbc\.gov\.tw/tw/dl-\d+[^"]+)"',
                r2.text)
        if not xls_m:
            # 備用：找 5newloan span 附近的 class="xls" 連結
            xls_m = re.search(
                r'5newloan.*?<a\s+href="(https://www\.cbc\.gov\.tw/tw/dl-\d+[^"]+)"[^>]*class="xls"',
                r2.text, re.DOTALL)
        if not xls_m:
            print("  5newloan: XLS link not found")
            return None

        # Step 3: 下載並解析 XLS
        r3 = get(xls_m.group(1))
        if not r3:
            return None
        wb = xlrd.open_workbook(file_contents=r3.content)
        ws = wb.sheet_by_index(0)

        for i in range(ws.nrows - 2, 2, -1):
            row = ws.row_values(i)
            date_str = str(row[0]).strip() if row[0] else ''
            if '/' not in date_str:
                continue
            try:
                rate   = float(row[2]) if row[2] else 0.0
                amount = float(row[1]) if row[1] else 0.0
                if rate > 0 and amount > 0:
                    yr_roc_str, mo_str = date_str.split('/')
                    year_ad  = int(yr_roc_str) + 1911
                    updated  = f'{year_ad}-{int(mo_str):02d}'
                    # 也傳回同月去年資料（row[2] 同欄、i-12）
                    prev_amount = None
                    if i >= 12:
                        prev_row = ws.row_values(i - 12)
                        try:
                            prev_amount = float(prev_row[1])
                        except Exception:
                            pass
                    return (updated, rate, amount, prev_amount)
            except Exception:
                continue
    except Exception as e:
        print(f"  5newloan: {e}")
    return None


def fetch_A02():
    """五大銀行新承做購屋貸款利率 — CBC 5newloan.xls"""
    result = _fetch_5newloan_data()
    if result:
        updated, rate, _, _ = result
        if rate > 2.5:
            status, note = 'red',    f'{rate:.3f}%，創歷史高點，購屋成本沉重'
        elif rate > 2.0:
            status, note = 'yellow', f'{rate:.3f}%，創17年新高，成本壓力大'
        else:
            status, note = 'green',  f'{rate:.3f}%，利率合理'
        return dict(value=f'{rate:.3f}%', status=status, note=note, updated=updated)
    return None


def fetch_A03():
    """五大銀行新增購屋貸款金額 — CBC 5newloan.xls（同 A02 數據源）"""
    result = _fetch_5newloan_data()
    if result:
        updated, _, amount_mln, prev_amount_mln = result
        amount_yi = amount_mln / 100   # 百萬 → 億
        yoy_note = ''
        if prev_amount_mln and prev_amount_mln > 0:
            chg = (amount_mln - prev_amount_mln) / prev_amount_mln * 100
            yoy_note = f'，年{"增" if chg > 0 else "減"}{abs(chg):.1f}%'
        if amount_yi < 450:
            status, note = 'red',    f'Q1年減，{amount_yi:.0f}億/月{yoy_note}，創3年新低'
        elif amount_yi < 650:
            status, note = 'red',    f'{amount_yi:.0f}億/月{yoy_note}，量縮明顯'
        elif amount_yi < 850:
            status, note = 'yellow', f'{amount_yi:.0f}億/月{yoy_note}'
        else:
            status, note = 'green',  f'{amount_yi:.0f}億/月{yoy_note}'
        return dict(value=f'{amount_yi:.0f}億/月', status=status, note=note, updated=updated)
    return None


def fetch_A04():
    """不動產放款集中度 — CBC 央行月報（HTML 解析）"""
    r = get('https://www.cbc.gov.tw/tw/lp-640-1-1-20.html')
    if r and HAS_BS4:
        soup = BeautifulSoup(r.text, 'lxml')
        text = soup.get_text()
        # 不動產放款集中度通常是 30~45% 之間的兩位數百分比
        for m in re.finditer(r'(\d{2}\.\d{1,2})%?', text):
            v = float(m.group(1))
            if 28 < v < 45:
                if v > 38:
                    status, note = 'red',    f'{v:.2f}%，集中度過高，監管壓力大'
                elif v > 36:
                    status, note = 'yellow', f'{v:.2f}%，接近上限，持續下降中'
                else:
                    status, note = 'green',  f'{v:.2f}%，跌破36%，創多年新低'
                return dict(value=f'{v:.2f}%', status=status, note=note,
                            updated=THIS_MONTH)
    return None


def fetch_A05():
    """新青安貸款占比 — 財政部月報（待開發）"""
    return None


def fetch_B01():
    """全國買賣移轉棟數 — 內政部不動產平台"""
    # 嘗試 pip.moi.gov.tw 統計 API
    endpoints = [
        'https://pip.moi.gov.tw/Api/TransactionCount/GetMonthList',
        'https://pip.moi.gov.tw/Api/E3010/GetData',
    ]
    for url in endpoints:
        r = get(url)
        if r:
            try:
                data = r.json()
                if isinstance(data, list) and data:
                    latest = data[-1]
                    val = (latest.get('Total') or latest.get('棟數')
                           or latest.get('count') or latest.get('transferCount'))
                    if val:
                        val = int(str(val).replace(',', ''))
                        ann = val * 12
                        if ann < 250000:
                            status, note = 'red',    f'月均{val:,}棟，年化低於25萬，量縮嚴重'
                        elif ann < 300000:
                            status, note = 'yellow', f'月均{val:,}棟，交易量偏低'
                        else:
                            status, note = 'green',  f'月均{val:,}棟，交易量正常'
                        return dict(value=f'{val:,}棟', status=status, note=note,
                                    updated=THIS_MONTH)
            except Exception as e:
                print(f"  B01 API parse {url}: {e}")
    return None


def fetch_B02():
    """信義房價指數 — 信義房屋（季報）"""
    # 每季發布，需 HTML 解析，尚不穩定
    return None


def fetch_B03():
    """國泰房價指數 — 國立政治大學（季報）"""
    # 每季發布，需 HTML 解析，尚不穩定
    return None


def fetch_B04():
    """六都移轉棟數 — 內政部（待開發）"""
    return None


def fetch_B05():
    """六都房價所得比 — 內政部（季報）"""
    try:
        r = get('https://pip.moi.gov.tw/Publicize/Info/E1050')
        if r and HAS_BS4:
            soup = BeautifulSoup(r.text, 'lxml')
            # 找「XX 倍」形式，合理範圍 8~30 倍
            for m in re.finditer(r'(\d{1,2}\.\d{1,2})\s*倍', r.text):
                v = float(m.group(1))
                if 8 < v < 30:
                    if v > 20:
                        status, note = 'red',    f'全台 {v} 倍，遠超國際合理值(5倍)'
                    elif v > 12:
                        status, note = 'yellow', f'全台 {v} 倍，購屋負擔沉重'
                    else:
                        status, note = 'green',  f'全台 {v} 倍'
                    return dict(value=f'{v}倍', status=status, note=note,
                                updated=quarter_str(TODAY.strftime('%Y-%m-%d')))
    except Exception as e:
        print(f"  B05 MOI: {e}")
    return None


def fetch_C01():
    """房貸逾放比 — 金管會月報（HTML 解析）"""
    try:
        r = get('https://www.banking.gov.tw/ch/home.jsp?id=296&parentpath=0,4,132')
        if r and HAS_BS4:
            soup = BeautifulSoup(r.text, 'lxml')
            # 逾放比通常是 0.XX% 形式
            for m in re.finditer(r'(\d+\.\d{2})%', r.text):
                v = float(m.group(1))
                if 0.01 < v < 5.0:
                    if v > 0.5:
                        status, note = 'red',    f'逾放比 {v:.2f}%，不良貸款擴散'
                    elif v > 0.2:
                        status, note = 'yellow', f'逾放比 {v:.2f}%，件數快速攀升'
                    else:
                        status, note = 'yellow', f'逾放比 {v:.2f}%，隱性風險擴散'
                    return dict(value=f'{v:.2f}%', status=status, note=note,
                                updated=THIS_MONTH)
    except Exception as e:
        print(f"  C01 FSC: {e}")
    return None


def fetch_C02():
    """房價所得比 — 內政部（季報）"""
    # 正確值約 15~30 倍，MOI 網站動態載入不易 scraping，手動維護
    return None


def fetch_C03():
    """建照核發 — 內政部統計月報"""
    try:
        r = get('https://data.moi.gov.tw/MoiOD/System/DownloadFile.aspx?DATA=11086',
                timeout=20)
        if r and r.status_code == 200 and r.text.strip():
            rows = list(csv.reader(io.StringIO(r.text.lstrip('﻿'))))
            if len(rows) > 1:
                # 找最後一筆有效數字列
                for row in reversed(rows[1:]):
                    cols = [c.strip().replace(',', '') for c in row]
                    nums = [c for c in cols if c.isdigit() and int(c) > 0]
                    if nums:
                        val = int(nums[-1])
                        ann = val * 12
                        if ann < 130000:
                            status, note = 'red',    f'月均{val:,}棟，年化13萬以下，創7年低'
                        elif ann < 160000:
                            status, note = 'yellow', f'月均{val:,}棟，建商保守減量'
                        else:
                            status, note = 'green',  f'月均{val:,}棟，供給正常'
                        return dict(value=f'{val:,}棟', status=status, note=note,
                                    updated=THIS_MONTH)
    except Exception as e:
        print(f"  C03 MOI: {e}")
    return None


def fetch_C04():
    """使照核發 — 內政部統計月報"""
    try:
        r = get('https://data.moi.gov.tw/MoiOD/System/DownloadFile.aspx?DATA=11087',
                timeout=20)
        if r and r.status_code == 200 and r.text.strip():
            rows = list(csv.reader(io.StringIO(r.text.lstrip('﻿'))))
            if len(rows) > 1:
                for row in reversed(rows[1:]):
                    cols = [c.strip().replace(',', '') for c in row]
                    nums = [c for c in cols if c.isdigit() and int(c) > 0]
                    if nums:
                        val = int(nums[-1])
                        status = 'yellow'
                        note = f'月均{val:,}棟，使照>建照，交屋潮持續'
                        return dict(value=f'{val:,}棟', status=status, note=note,
                                    updated=THIS_MONTH)
    except Exception as e:
        print(f"  C04 MOI: {e}")
    return None


def fetch_D01():
    """美十年期公債殖利率 — FRED DGS10 + Yahoo Finance"""
    val, dt = fred_last('DGS10')
    if val is None:
        val, dt = yf_get('^TNX')
    if val is None:
        return None

    if val > 4.5:
        status, note = 'red',    f'{val:.3f}%，高位持續，全球資金成本居高不下'
    elif val > 3.5:
        status, note = 'yellow', f'{val:.3f}%，利率偏高，需持續觀察'
    else:
        status, note = 'green',  f'{val:.3f}%，利率回落，資金環境趨寬'

    return dict(value=f'{val:.3f}%', status=status, note=note,
                updated=dt[:7] if dt else THIS_MONTH)


def fetch_D02():
    """美元台幣匯率 — ExchangeRate API + Yahoo Finance"""
    val = None
    try:
        r = requests.get('https://open.er-api.com/v6/latest/USD',
                         timeout=10, headers=HEADERS)
        val = r.json()['rates'].get('TWD')
    except Exception:
        pass
    if val is None:
        val, _ = yf_get('TWD=X')
    if val is None:
        return None

    if val > 33.0:
        status, note = 'red',    f'{val:.2f}，台幣明顯弱勢，資金外流壓力大'
    elif val > 31.5:
        status, note = 'yellow', f'{val:.2f}，台幣承壓，近期趨穩'
    else:
        status, note = 'green',  f'{val:.2f}，台幣相對強勢'

    return dict(value=f'{val:.2f}', status=status, note=note,
                updated=THIS_MONTH)


def fetch_D03():
    """台股加權指數 — TWSE 官方 API + Yahoo Finance"""
    val = None
    dt  = None
    try:
        ds  = TODAY.strftime('%Y%m%d')
        url = (f'https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST'
               f'?date={ds}&response=json')
        r   = requests.get(url, timeout=10, headers=HEADERS)
        d   = r.json()
        rows = d.get('data', [])
        if rows:
            raw = str(rows[-1][4]).replace(',', '')
            val = float(raw)
            dt  = THIS_MONTH
    except Exception as e:
        print(f"  D03 TWSE: {e}")
    if val is None:
        val, dt = yf_get('^TWII')
    if val is None:
        return None

    if val > 30000:
        status, note = 'green',  f'{val:,.0f}點，台股高位，市場信心穩定'
    elif val > 20000:
        status, note = 'yellow', f'{val:,.0f}點，中位區間，觀察方向'
    else:
        status, note = 'red',    f'{val:,.0f}點，台股修正，市場信心不足'

    return dict(value=f'{val:,.0f}點', status=status, note=note,
                updated=dt[:7] if dt else THIS_MONTH)


def fetch_D04():
    """台灣CPI — 主計總處 XML 月報（pr0101a1m.xml）"""
    # 主計總處每月初發布上月 CPI，XML 檔路徑每月更新
    # DGBAS_CPI_XML 常數定義在本檔案頂部，每月新資料發布後需更新路徑
    try:
        r = requests.get(DGBAS_CPI_XML, headers=HEADERS, timeout=20)
        if r.status_code == 200 and r.content:
            root = ET.fromstring(r.content)
            obs_list = []
            for obs in root.findall('Obs'):
                item  = obs.findtext('Item', '')
                tstr  = obs.findtext('TIME_PERIOD', '')
                otype = obs.findtext('TYPE', '')
                vstr  = obs.findtext('Item_VALUE', '').strip()
                if '總指數' in item and '年增率' in otype and vstr:
                    try:
                        obs_list.append((tstr, float(vstr)))
                    except ValueError:
                        pass
            if obs_list:
                obs_list.sort()
                latest_time, val = obs_list[-1]
                # '2026M04' → '2026-04'
                try:
                    yr, mn = latest_time.split('M')
                    updated = f'{yr}-{mn.zfill(2)}'
                except Exception:
                    updated = THIS_MONTH

                if val > 3.0:
                    status, note = 'red',    f'CPI 年增 {val:.2f}%，通膨明顯'
                elif val > 2.0:
                    status, note = 'yellow', f'CPI 年增 {val:.2f}%，通膨升溫'
                elif val > 1.0:
                    status, note = 'yellow', f'{val:.2f}%，通膨回升，需持續觀察'
                else:
                    status, note = 'green',  f'CPI 年增 {val:.2f}%，通膨溫和'
                return dict(value=f'{val:.2f}%', status=status, note=note,
                            updated=updated)
    except Exception as e:
        print(f"  D04 DGBAS XML: {e}")

    # 備用：嘗試主計總處統計資料庫 HTML 頁
    try:
        url = ('https://nstatdb.dgbas.gov.tw/dgbasAll/webMain.aspx'
               '?sys=100&funid=qryout&funid2=A040101010'
               '&cycle=41&outkind=11&outmode=8&fldlst=111111111111')
        r = requests.get(url, timeout=20, headers=HEADERS)
        if HAS_BS4 and r.status_code == 200:
            soup = BeautifulSoup(r.text, 'lxml')
            tds  = soup.find_all('td')
            nums = []
            for td in tds:
                m = re.search(r'^-?\d+\.\d{2}$', td.get_text().strip())
                if m:
                    nums.append(float(m.group()))
            if nums:
                val = nums[-1]
                if val > 3.0:
                    status, note = 'red',    f'CPI 年增 {val:.2f}%，通膨明顯'
                elif val > 2.0:
                    status, note = 'yellow', f'CPI 年增 {val:.2f}%，通膨升溫'
                else:
                    status, note = 'yellow', f'CPI 年增 {val:.2f}%，通膨溫和'
                return dict(value=f'{val:.2f}%', status=status, note=note,
                            updated=THIS_MONTH)
    except Exception as e:
        print(f"  D04 DGBAS HTML: {e}")
    return None


# ── 指標 → 抓取函數對應表 ──────────────────────────────────────────────────

FETCHERS = {
    'A01': fetch_A01,
    'A02': fetch_A02,
    'A03': fetch_A03,
    'A04': fetch_A04,
    'A05': fetch_A05,
    'B01': fetch_B01,
    'B02': fetch_B02,
    'B03': fetch_B03,
    'B04': fetch_B04,
    'B05': fetch_B05,
    'C01': fetch_C01,
    'C02': fetch_C02,
    'C03': fetch_C03,
    'C04': fetch_C04,
    'D01': fetch_D01,
    'D02': fetch_D02,
    'D03': fetch_D03,
    'D04': fetch_D04,
}

# ── 主程式 ─────────────────────────────────────────────────────────────────

def main():
    print(f"=== CX468 指標更新 {TODAY} ===\n")
    data = load_data()
    ok = fail = skip = 0

    for ind in data['indicators']:
        code    = ind['code']
        fetcher = FETCHERS.get(code)
        if fetcher is None:
            print(f"  · {code}: 無抓取函數")
            skip += 1
            continue

        print(f"  [{code}] 抓取中...")
        result = fetcher()
        if result:
            ind.update(result)
            ok += 1
            print(f"    ✓ {result.get('value')} [{result.get('status')}]"
                  f" — {result.get('note','')[:40]}")
        else:
            fail += 1
            print(f"    – 抓取失敗，保留上次數值: {ind.get('value','?')}")
        time.sleep(0.8)  # 避免連續請求過快

    data['generated'] = TODAY.strftime('%Y-%m-%d')
    save_data(data)
    print(f"\n=== 完成 | 成功 {ok} | 失敗 {fail} | 跳過 {skip} | "
          f"生成日期 {data['generated']} ===")

if __name__ == '__main__':
    main()
