#!/usr/bin/env python3
"""
CX468 房貸儀表板 — 18 項指標自動抓取腳本
GitHub Actions 每日 08:30 台灣時間自動執行
"""

import json, requests, csv, io, time, re
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

BASE      = Path(__file__).resolve().parent.parent
DATA_FILE = BASE / 'cx_data.json'
TODAY     = date.today()
THIS_MONTH = TODAY.strftime('%Y-%m')
HEADERS   = {'User-Agent': 'CX468-Dashboard/2.0 (cx468.com.tw)'}

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
        r = requests.get(url, timeout=15, headers=HEADERS)
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
    try:
        r = requests.get(url, timeout=15, headers=HEADERS, **kwargs)
        r.raise_for_status()
        return r
    except Exception as e:
        print(f"  GET {url[:60]}... : {e}")
        return None

# ── 個別指標抓取函數 ────────────────────────────────────────────────────────

def fetch_A01():
    """央行重貼現率 — CBC 官網 or FRED INTDSRTW01STQ"""
    # 先試 FRED 台灣重貼現率季報
    val, dt = fred_last('INTDSRTW01STQ')
    if val is None:
        # 備用：CBC 官網 HTML
        r = get('https://www.cbc.gov.tw/tw/lp-640-1-1-20.html')
        if r and HAS_BS4:
            soup = BeautifulSoup(r.text, 'lxml')
            # 找含「重貼現率」那一欄的數字
            tds = soup.find_all('td')
            for i, td in enumerate(tds):
                if '重貼現率' in td.get_text():
                    # 往後找數字
                    for j in range(i+1, min(i+5, len(tds))):
                        m = re.search(r'(\d+\.\d+)', tds[j].get_text())
                        if m:
                            val = float(m.group(1))
                            dt  = THIS_MONTH + '-01'
                            break
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


def fetch_A02():
    """五大銀行平均房貸利率 — CBC 月報 HTML"""
    # 央行統計月報：新承做購屋貸款利率
    r = get('https://www.cbc.gov.tw/tw/cp-725-168266-a4e5a-1.html')
    if r and HAS_BS4:
        soup = BeautifulSoup(r.text, 'lxml')
        # 在表格中找最新利率數字
        for td in soup.find_all('td'):
            m = re.search(r'(\d\.\d{2,3})%?', td.get_text())
            if m:
                v = float(m.group(1))
                if 1.5 < v < 4.0:  # 合理利率範圍過濾
                    if v > 2.5:
                        status, note = 'red',    f'{v:.3f}%，創歷史高點，購屋成本沉重'
                    elif v > 2.0:
                        status, note = 'yellow', f'{v:.3f}%，偏高，借款人壓力增加'
                    else:
                        status, note = 'green',  f'{v:.3f}%，利率合理'
                    return dict(value=f'{v:.3f}%', status=status, note=note,
                                updated=THIS_MONTH)
    return None


def fetch_A03():
    """五大銀行新增房貸金額 — 鉅亨網/央行月報"""
    # 嘗試從央行統計抓月新增房貸
    # 備用：保持現有值，只更新日期標記
    return None  # 月度數據，央行約每月中旬公布，需 scraping 進一步開發


def fetch_A04():
    """不動產放款集中度 — 央行月報"""
    # 央行每月公布銀行不動產放款比率
    r = get('https://www.cbc.gov.tw/tw/cp-725-168266-a4e5a-1.html')
    if r and HAS_BS4:
        soup = BeautifulSoup(r.text, 'lxml')
        for td in soup.find_all('td'):
            m = re.search(r'(\d{2}\.\d{1,2})%?', td.get_text())
            if m:
                v = float(m.group(1))
                if 25 < v < 50:  # 集中度合理範圍
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
    """新青安貸款占比 — 財政部月報"""
    # 財政部每月公布新青安申辦數字
    # 此數據需前往 https://www.mof.gov.tw/ 抓取，後續開發
    return None


def fetch_B01():
    """全國買賣移轉棟數 — 內政部不動產資訊平台"""
    # 內政部統計月報 open data
    try:
        # 使用政府開放資料 API
        url = 'https://data.moi.gov.tw/MoiOD/System/DownloadFile.aspx?DATA=10905'
        # 嘗試 pip.moi.gov.tw JSON API
        url2 = 'https://pip.moi.gov.tw/Api/TransactionCount/GetMonthList'
        r = get(url2)
        if r:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                latest = data[-1]
                # 解析欄位（格式依平台而定）
                val = latest.get('Total') or latest.get('count') or latest.get('棟數')
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
        print(f"  B01 MOI API: {e}")
    return None


def fetch_B02():
    """信義房價指數 — 信義房屋月報"""
    try:
        r = get('https://www.sinyinews.com.tw/monthly')
        if r and HAS_BS4:
            soup = BeautifulSoup(r.text, 'lxml')
            # 找最新指數數字（大台北月指數）
            # 格式依頁面結構而定，需定期維護
            nums = re.findall(r'指數[：:]\s*(\d{3,4}\.?\d*)', r.text)
            if nums:
                v = float(nums[0])
                if v > 200:
                    status, note = 'red',    f'大台北指數 {v:.1f}，房價仍高'
                elif v > 150:
                    status, note = 'yellow', f'大台北指數 {v:.1f}，量縮價撐'
                else:
                    status, note = 'green',  f'大台北指數 {v:.1f}'
                return dict(value=str(v), status=status, note=note,
                            updated=THIS_MONTH)
    except Exception as e:
        print(f"  B02 Sinyi: {e}")
    return None


def fetch_B03():
    """國泰房價指數 — 國立政治大學不動產研究中心"""
    # 季報，每季末發布
    try:
        r = get('https://rer.nccu.edu.tw/article/detail/2210058784414')
        if r and HAS_BS4:
            soup = BeautifulSoup(r.text, 'lxml')
            # 找最新季報數字
            text = soup.get_text()
            m = re.search(r'國泰[^0-9]*(\d{3,4}\.?\d*)', text)
            if m:
                v = float(m.group(1))
                status = 'yellow'
                note = f'Q{(TODAY.month-1)//3+1}指數 {v:.1f}，預售市場趨緩'
                return dict(value=str(v), status=status, note=note,
                            updated=quarter_str(TODAY.strftime('%Y-%m-%d')))
    except Exception as e:
        print(f"  B03 NCCU: {e}")
    return None


def fetch_B04():
    """六都移轉棟數 — 內政部統計"""
    # 與 B01 同源，從 MOI 月報
    return None  # 待進一步開發，與 B01 共用數據源


def fetch_B05():
    """六都房價（房價所得比）— 內政部房價負擔能力統計"""
    try:
        r = get('https://pip.moi.gov.tw/Publicize/Info/E1050')
        if r and HAS_BS4:
            soup = BeautifulSoup(r.text, 'lxml')
            # 找全國平均房價所得比
            m = re.search(r'(\d{1,2}\.\d{1,2})\s*倍', r.text)
            if m:
                v = float(m.group(1))
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
    """房貸逾放比 — 金管會月報"""
    try:
        # 金管會銀行局統計資料
        r = get('https://www.banking.gov.tw/ch/home.jsp?id=296&parentpath=0,4,132')
        if r and HAS_BS4:
            soup = BeautifulSoup(r.text, 'lxml')
            m = re.search(r'(\d+\.\d{2})%', r.text)
            if m:
                v = float(m.group(1))
                if v > 0.5:
                    status, note = 'red',    f'逾放比 {v:.2f}%，不良貸款擴散'
                elif v > 0.2:
                    status, note = 'yellow', f'逾放比 {v:.2f}%，件數快速攀升'
                else:
                    status, note = 'yellow', f'逾放比 {v:.2f}%（低）但逾放件數年增60%'
                return dict(value=f'{v:.2f}%', status=status, note=note,
                            updated=THIS_MONTH)
    except Exception as e:
        print(f"  C01 FSC: {e}")
    return None


def fetch_C02():
    """房價所得比 — 內政部房價負擔能力統計（季報）"""
    # 正確數值應在 15~30 倍之間（全國平均）
    # 內政部頁面用 JS 動態載入，HTML scraping 易取到錯誤數值，先保持手動更新
    return None


def fetch_C03():
    """建照核發 — 內政部統計月報"""
    try:
        # 內政部統計查詢系統
        r = get('https://data.moi.gov.tw/MoiOD/System/DownloadFile.aspx?DATA=11086')
        if r:
            # CSV 格式，解析最新月份
            rows = list(csv.reader(io.StringIO(r.text.lstrip('﻿'))))
            if len(rows) > 1:
                last = rows[-1]
                # 欄位格式待確認，通常是 年月, 棟數
                val = int(str(last[-1]).replace(',', ''))
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
        r = get('https://data.moi.gov.tw/MoiOD/System/DownloadFile.aspx?DATA=11087')
        if r:
            rows = list(csv.reader(io.StringIO(r.text.lstrip('﻿'))))
            if len(rows) > 1:
                last = rows[-1]
                val = int(str(last[-1]).replace(',', ''))
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
    # 第一優先：ExchangeRate.host（免費無需 key）
    try:
        r = requests.get('https://open.er-api.com/v6/latest/USD', timeout=10)
        val = r.json()['rates'].get('TWD')
    except:
        pass
    # 備用：Yahoo Finance
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
    # 第一優先：TWSE 官方 JSON API
    try:
        ds = TODAY.strftime('%Y%m%d')
        url = f'https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST?date={ds}&response=json'
        r   = requests.get(url, timeout=10, headers=HEADERS)
        d   = r.json()
        rows = d.get('data', [])
        if rows:
            # 最後一筆的收盤（第5欄）
            last_row = rows[-1]
            raw = str(last_row[4]).replace(',', '')
            val = float(raw)
            dt  = THIS_MONTH
    except Exception as e:
        print(f"  D03 TWSE: {e}")
    # 備用：Yahoo Finance
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
    """台灣 CPI — 主計總處 JSON API"""
    # 主計總處統計資料庫開放 API
    try:
        url = ('https://nstatdb.dgbas.gov.tw/dgbasAll/webMain.aspx?'
               'sys=100&funid=qryout&funid2=A040101010&cycle=41'
               '&outkind=11&outmode=8&fldlst=111111111111')
        r = requests.get(url, timeout=15, headers=HEADERS)
        # 嘗試解析 HTML 表格
        if HAS_BS4:
            soup = BeautifulSoup(r.text, 'lxml')
            tds  = soup.find_all('td')
            nums = []
            for td in tds:
                m = re.search(r'^-?\d+\.\d{2}$', td.get_text().strip())
                if m:
                    nums.append(float(m.group()))
            if nums:
                val = nums[-1]  # 最新月份年增率
                if val > 3.0:
                    status, note = 'red',    f'CPI 年增 {val:.2f}%，通膨明顯'
                elif val > 2.0:
                    status, note = 'yellow', f'CPI 年增 {val:.2f}%，通膨升溫'
                else:
                    status, note = 'green',  f'CPI 年增 {val:.2f}%，通膨溫和'
                return dict(value=f'{val:.2f}%', status=status, note=note,
                            updated=THIS_MONTH)
    except Exception as e:
        print(f"  D04 DGBAS: {e}")

    # 備用：World Bank 年度 CPI
    try:
        url = 'https://api.worldbank.org/v2/country/TW/indicator/FP.CPI.TOTL.ZG?format=json&mrv=3'
        r   = requests.get(url, timeout=10)
        payload = r.json()
        if isinstance(payload, list) and len(payload) > 1:
            entries = payload[1] or []
            valid   = [e for e in entries if e.get('value') is not None]
            if valid:
                val  = float(valid[0]['value'])
                year = valid[0]['date']
                if val > 3.0:
                    status, note = 'red',    f'CPI {val:.2f}%，通膨明顯'
                elif val > 2.0:
                    status, note = 'yellow', f'CPI {val:.2f}%，回升中，持續觀察'
                else:
                    status, note = 'green',  f'CPI {val:.2f}%，通膨溫和'
                return dict(value=f'{val:.2f}%', status=status, note=note,
                            updated=year)
    except Exception as e:
        print(f"  D04 WorldBank: {e}")
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
            print(f"    ✓ {result.get('value')} [{result.get('status')}] — {result.get('note','')[:40]}")
        else:
            fail += 1
            print(f"    – 抓取失敗，保留上次數值: {ind.get('value','?')}")
        time.sleep(0.5)  # 避免連續請求過快

    data['generated'] = TODAY.strftime('%Y-%m-%d')
    save_data(data)
    print(f"\n=== 完成 | 成功 {ok} | 失敗 {fail} | 跳過 {skip} | 生成日期 {data['generated']} ===")

if __name__ == '__main__':
    main()
