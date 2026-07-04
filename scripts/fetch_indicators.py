#!/usr/bin/env python3
"""
CX468 房貸儀表板 — 18 項指標自動抓取腳本
GitHub Actions 每日 08:30 台灣時間自動執行
"""

import json, requests, csv, io, time, re, sys
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

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

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

# 部分政府站憑證有問題，下面多處用 verify=False；靜音 InsecureRequestWarning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
        r = requests.get(url, timeout=55, headers=HEADERS)
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
    kwargs.setdefault('timeout', 55)
    # 部分政府網站(pip.moi/banking.gov.tw/ws.dgbas)憑證鏈缺中介或缺 SKI，
    # Python/OpenSSL 嚴格驗證會失敗(curl -k 仍 200)。公開統計資料，跳過憑證驗證。
    kwargs.setdefault('verify', False)
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
        r = requests.get(url, headers=HEADERS, timeout=55)
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
    """不動產放款集中度 — CBC 不動產貸款相關資訊.xlsx（每月更新）"""
    if not HAS_OPENPYXL:
        print("  openpyxl not installed, skip A04")
        return None
    try:
        import urllib.parse
        filename = urllib.parse.quote('不動產貸款相關資訊.xlsx')
        url = f'https://www.cbc.gov.tw/public/data/Ebanking/{filename}'
        r = get(url, timeout=55)
        if not r:
            return None
        wb = openpyxl.load_workbook(io.BytesIO(r.content), data_only=True)
        ws = wb.active
        ratio   = None
        updated = None
        prev_row_date = None
        for row in ws.iter_rows(values_only=True):
            for cell in row:
                if cell and isinstance(cell, str):
                    # 日期格式 '115年3月底'
                    dm = re.search(r'(\d{2,3})年(\d{1,2})月', cell)
                    if dm:
                        yr_ad = int(dm.group(1)) + 1911
                        mo    = int(dm.group(2))
                        prev_row_date = f'{yr_ad}-{mo:02d}'
                    # 比率行：包含 '不動產貸款占總放款比率'
                    if '不動產貸款占總放款比率' in cell:
                        for v in row:
                            if isinstance(v, (int, float)) and 0.2 < v < 0.6:
                                ratio   = v
                                updated = prev_row_date
                                break
        if ratio and updated:
            pct = ratio * 100
            if pct > 38:
                status, note = 'red',    f'{pct:.2f}%，集中度過高，監管壓力大'
            elif pct > 36:
                status, note = 'yellow', f'{pct:.2f}%，接近上限，持續下降中'
            else:
                status, note = 'green',  f'跌破36%，{pct:.2f}%，創14年新低'
            return dict(value=f'{pct:.2f}%', status=status, note=note, updated=updated)
    except Exception as e:
        print(f"  A04 CBC XLSX: {e}")
    return None


def fetch_A05():
    """新青安貸款占比 — 財政部「安心貸款{民國YYMM}.pdf」×央行 5newloan

    官方口徑（媒體引用「央行公布」的占比）＝五大銀行新承做購屋貸款中新青安部分：
      分子：財政部青安月統計 PDF 內「五大銀行（臺銀/土銀/合庫/一銀/華銀）本月撥貸金額」加總
            （PDF 涵蓋 8 家公股銀行，兆豐/彰銀/臺企銀不在央行五大之列，須排除）
      分母：央行 5newloan 五大銀行新承做購屋貸款金額（同月）
    PDF 網址規律：service.mof.gov.tw/public/Data/statistic/Other_Statistics/安心貸款11505.pdf
    每列格式：銀行 受理本月(戶,億) 受理累計(戶,億) 撥貸本月(戶,億) 撥貸累計(戶,億) 比率×2
    """
    if not HAS_PYPDF:
        print("  pypdf not installed, skip A05")
        return None
    try:
        import urllib.parse
        base = 'https://service.mof.gov.tw/public/Data/statistic/Other_Statistics/'
        # 從本月往回找最新一期 PDF（次月下旬公布，最多回看 3 期）
        pdf_text = pdf_roc = None
        y, m = TODAY.year, TODAY.month
        for _ in range(4):
            roc = f'{y - 1911}{m:02d}'
            url = base + urllib.parse.quote(f'安心貸款{roc}.pdf')
            r = get(url, timeout=40)
            if r and r.content[:4] == b'%PDF':
                pdf_text = "\n".join(p.extract_text() for p in PdfReader(io.BytesIO(r.content)).pages)
                pdf_roc = roc
                break
            m -= 1
            if m == 0:
                y, m = y - 1, 12
        if not pdf_text:
            return None

        # 月份以 PDF 內文「截至115年5月底」為準（比檔名可靠）
        dm = re.search(r'截至(\d{2,3})年(\d{1,2})月底', pdf_text)
        if dm:
            pdf_month = f'{int(dm.group(1)) + 1911}-{int(dm.group(2)):02d}'
        else:
            pdf_month = f'{int(pdf_roc[:3]) + 1911}-{int(pdf_roc[3:]):02d}'

        # 五大銀行「撥貸本月」戶數/金額（每列第 5、6 個數字，0-indexed 4、5）
        FIVE = ['臺銀', '土銀', '合庫', '一銀', '華銀']
        disb_amt = disb_cnt = 0.0
        found = []
        for bank in FIVE:
            bm = re.search(bank + r'\s+((?:[\d,]+(?:\.\d+)?[\s]+){9,}[\d,.]+)', pdf_text)
            if not bm:
                continue
            nums = [float(x.replace(',', '')) for x in re.findall(r'[\d,]+(?:\.\d+)?', bm.group(1))]
            if len(nums) < 8:
                continue
            disb_cnt += nums[4]
            disb_amt += nums[5]
            found.append(bank)
        if len(found) != 5:
            print(f"  A05 PDF 只解析到 {found}，放棄")
            return None

        # 分母：央行五大銀行新承做購屋貸款（同月對齊）
        five = _fetch_5newloan_data()
        if not five:
            return None
        cbc_month, _, amount_mln, prev_amount_mln = five
        if cbc_month == pdf_month:
            denom_yi = amount_mln / 100
        else:
            # 財政部比央行慢一個月時，用央行前月值對齊
            prev_y, prev_m = int(cbc_month[:4]), int(cbc_month[5:7]) - 1
            if prev_m == 0:
                prev_y, prev_m = prev_y - 1, 12
            if f'{prev_y}-{prev_m:02d}' == pdf_month and prev_amount_mln:
                denom_yi = prev_amount_mln / 100
            else:
                print(f"  A05 月份對不上：PDF={pdf_month} CBC={cbc_month}，放棄")
                return None
        if denom_yi <= 0:
            return None

        share = disb_amt / denom_yi * 100
        if not (5 < share < 90):   # 合理性防呆
            print(f"  A05 占比 {share:.1f}% 超出合理範圍，放棄")
            return None
        mo_label = f'{int(pdf_month[5:7])}月'
        if share >= 45:
            status = 'red'
            note = f'{mo_label}占比{share:.1f}%，政策貸款依賴度高'
        elif share >= 35:
            status = 'yellow'
            note = f'{mo_label}五大銀撥貸{disb_amt:.0f}億、占新承做{share:.1f}%'
        else:
            status = 'green'
            note = f'{mo_label}占比{share:.1f}%，回落至三成五以下'
        return dict(value=f'{share:.1f}%', status=status, note=note, updated=pdf_month)
    except Exception as e:
        print(f"  A05 MOF/CBC: {e}")
    return None


_MOI_B0X_CACHE = None   # 快取同一次執行中的 ODS 解析結果

def _fetch_moi_b0x():
    """下載並解析 statis.moi.gov.tw 內政統計月報 4.5-辦理建物所有權登記 ODS
    回傳 dict: {
      'b01': {'ytd':int, 'n_months':int, 'prev_ytd':int},
      'b04': {'curr':{city:int}, 'prev':{city:int}, 'period':'Q1'/...}
    }
    """
    global _MOI_B0X_CACHE
    if _MOI_B0X_CACHE is not None:
        return _MOI_B0X_CACHE

    import zipfile
    url = 'https://statis.moi.gov.tw/micst/report/324050.ods'
    r = get(url, timeout=55)
    if not r:
        return None
    try:
        with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
            xml_content = zf.read('content.xml')
    except Exception as e:
        print(f"  B0x ODS zip: {e}")
        return None

    root = ET.fromstring(xml_content)
    ns = {
        'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
        'text':  'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
    }

    def ctext(cell):
        return ' '.join(t.text or '' for t in cell.findall('.//text:p', ns)).strip()

    def cint(cells, idx):
        if idx < len(cells):
            v = ctext(cells[idx]).replace(',', '').replace('－', '').strip()
            return int(v) if v.isdigit() else None
        return None

    rows = root.findall('.//table:table-row', ns)

    # ── B01: 國家月別合計 (Sheet 1 前半段) ──────────────────────────────────
    year_data = {}
    current_yr = None
    for row in rows:
        cells = row.findall('table:table-cell', ns)
        if not cells:
            continue
        v0 = ctext(cells[0])
        yr_m = re.search(r'(\d{4})', v0)
        if yr_m and '年' in v0 and '月' not in v0:
            yr = int(yr_m.group(1))
            if 2010 <= yr <= TODAY.year + 1:
                current_yr = yr
                ytd = cint(cells, 5)
                year_data[yr] = {'ytd': ytd, 'months': []}
                continue
        if current_yr and re.match(r'[一二三四五六七八九十]+[　\s]*月', v0):
            val = cint(cells, 5)
            if val is not None:
                year_data[current_yr]['months'].append(val)

    b01 = None
    years = sorted(year_data.keys())
    if years:
        ly = years[-1]
        latest = year_data[ly]
        n = len(latest['months'])
        ytd = latest['ytd'] or sum(latest['months'])
        prev_ytd = None
        if ly - 1 in year_data:
            pm = year_data[ly - 1]['months'][:n]
            if pm:
                prev_ytd = sum(pm)
        b01 = {'ytd': ytd, 'n_months': n, 'prev_ytd': prev_ytd, 'year': ly}

    # ── B04: 六都累積 (區域別部分) ──────────────────────────────────────────
    SIX = ['新 北 市', '臺 北 市', '桃 園 市', '臺 中 市', '臺 南 市', '高 雄 市']
    SIX_LABELS = ['新北市', '台北市', '桃園市', '台中市', '台南市', '高雄市']

    cur_yr_roc  = TODAY.year - 1911
    prev_yr_roc = cur_yr_roc - 1

    curr_ytd_start    = None
    prev_annual_start = None
    prev_mo_starts    = {}

    for i, row in enumerate(rows):
        cells = row.findall('table:table-cell', ns)
        if not cells:
            continue
        v0 = ctext(cells[0])
        if re.search(rf'{cur_yr_roc}年\s*\d+\s*-\s*\d+月', v0) and curr_ytd_start is None:
            curr_ytd_start = i
        elif re.search(rf'{prev_yr_roc}年\s*1\s*-\s*12月', v0) and prev_annual_start is None:
            prev_annual_start = i
        elif prev_annual_start and re.match(r'^\d+月$', v0):
            mo = int(v0.replace('月', ''))
            if mo not in prev_mo_starts:
                prev_mo_starts[mo] = i

    curr_cities = {}
    if curr_ytd_start:
        for i in range(curr_ytd_start + 1, curr_ytd_start + 35):
            if i >= len(rows):
                break
            cells = rows[i].findall('table:table-cell', ns)
            v0 = ctext(cells[0]) if cells else ''
            if re.match(r'^\d+月$', v0):
                break
            v1 = ctext(cells[1]) if len(cells) > 1 else ''
            for j, city in enumerate(SIX):
                if city in v1:
                    val = cint(cells, 6)
                    if val is not None:
                        curr_cities[SIX_LABELS[j]] = val

    prev_q1_cities = {c: 0 for c in SIX_LABELS}
    n_months_region = len(curr_cities) and b01['n_months'] if b01 else 3
    for mo in range(1, n_months_region + 1):
        mo_start = prev_mo_starts.get(mo)
        if not mo_start:
            continue
        for i in range(mo_start + 1, mo_start + 35):
            if i >= len(rows):
                break
            cells = rows[i].findall('table:table-cell', ns)
            v0 = ctext(cells[0]) if cells else ''
            if re.match(r'^\d+月$', v0) and i > mo_start + 1:
                break
            v1 = ctext(cells[1]) if len(cells) > 1 else ''
            for j, city in enumerate(SIX):
                if city in v1:
                    val = cint(cells, 6)
                    if val is not None:
                        prev_q1_cities[SIX_LABELS[j]] += val

    # Determine period string for B04
    nm = b01['n_months'] if b01 else 3
    if nm == 3:
        period = 'Q1'
    elif nm == 6:
        period = 'Q2'
    elif nm == 9:
        period = '前3季'
    else:
        period = f'前{nm}月'

    b04 = {'curr': curr_cities, 'prev': prev_q1_cities, 'period': period}

    _MOI_B0X_CACHE = {'b01': b01, 'b04': b04}
    return _MOI_B0X_CACHE


def fetch_B01():
    """全國買賣移轉棟數 — 內政部統計月報 (statis.moi.gov.tw 4.5-辦理建物所有權登記)"""
    try:
        d = _fetch_moi_b0x()
        if not d or not d.get('b01'):
            return None
        b = d['b01']
        ytd, n, prev_ytd, yr = b['ytd'], b['n_months'], b['prev_ytd'], b['year']
        if not ytd or not n:
            return None

        ann = ytd / n * 12
        yoy_str = ''
        if prev_ytd and prev_ytd > 0:
            yoy = (ytd - prev_ytd) / prev_ytd * 100
            yoy_str = f'，年{"增" if yoy >= 0 else "減"}{abs(yoy):.1f}%'

        if n == 3:
            period, updated = 'Q1', f'{yr}-Q1'
        elif n == 6:
            period, updated = 'Q2', f'{yr}-Q2'
        elif n == 9:
            period, updated = '前3季', f'{yr}-Q3'
        elif n == 12:
            period, updated = '全年', str(yr)
        else:
            period, updated = f'前{n}月', f'{yr}-{n:02d}'

        if ann < 250000:
            status, note = 'red',    f'{period}共{ytd:,}棟{yoy_str}，年化不足25萬'
        elif ann < 320000:
            status, note = 'yellow', f'{period}共{ytd:,}棟{yoy_str}'
        else:
            status, note = 'green',  f'{period}共{ytd:,}棟{yoy_str}'

        return dict(value=f'{ytd:,}棟', status=status, note=note, updated=updated)
    except Exception as e:
        print(f"  B01 statis.moi: {e}")
    return None


def fetch_B02():
    """信義房價指數（全台）— sinyinews.com.tw/quarterly

    頁面為 JS 渲染，需 playwright（CI 未裝則跳過、保留上次值，由本機排程器負責）。
    表格含「台灣」全國列：指數 / 上季指數 / QoQ% / 去年同季 / YoY%。
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  playwright not installed, skip B02（本機排程器負責）")
        return None
    try:
        qm = None
        for attempt in range(2):        # 頁面 JS 偶發未渲染完，重試一次
            with sync_playwright() as p:
                b = p.chromium.launch(headless=True)
                pg = b.new_page()
                pg.goto('https://www.sinyinews.com.tw/quarterly',
                        wait_until='networkidle', timeout=60_000)
                pg.wait_for_timeout(1500 + attempt * 3000)
                txt = pg.evaluate("() => document.body.innerText")
                b.close()
            qm = re.search(r'(20\d\d)年第([一二三四])季（信義房價指數）', txt) \
                 or re.search(r'(20\d\d)年第([一二三四])季都會區季指數', txt)
            if qm:
                break
            print(f"  B02 第 {attempt + 1} 次渲染未取得表格，重試")
        if not qm:
            return None
        q = {'一': 1, '二': 2, '三': 3, '四': 4}[qm.group(2)]
        updated = f'{qm.group(1)}-Q{q}'

        rm = re.search(r'台灣\s+([\d.]+)\s+[\d.]+\s+(-?[\d.]+)%\s+[\d.]+\s+(-?[\d.]+)%', txt)
        if not rm:
            print("  B02 找不到「台灣」全國列")
            return None
        idx, qoq, yoy = float(rm.group(1)), float(rm.group(2)), float(rm.group(3))
        if not (50 < idx < 500):
            return None
        if yoy <= -5:
            status = 'red'
        elif yoy < 0:
            status = 'yellow'
        else:
            status = 'green'
        note = f'{updated.replace("-", "")}全台{idx:.2f}，季{qoq:+.2f}%、年{yoy:+.2f}%'
        return dict(value=f'{idx:.2f}', status=status, note=note, updated=updated)
    except Exception as e:
        print(f"  B02 sinyi: {e}")
    return None


def fetch_B03():
    """國泰房地產指數（全國可能成交價）— cathay-red 季報 PDF

    網址規律：/Content/Upload/files/about/about-house/report/{西元年}/{民國年}report_Q{季}.pdf
    解析「綜合評估－全國」頁：可能成交價格 <指數> <萬元/坪> QoQ% YoY%。
    季報約於季後 1 個月發布，從當前季往回試 4 季。
    """
    if not HAS_PYPDF:
        print("  pypdf not installed, skip B03")
        return None
    try:
        y, q = TODAY.year, (TODAY.month - 1) // 3 + 1
        content = updated = None
        for _ in range(4):
            url = (f'https://www.cathay-red.com.tw/Content/Upload/files/about/'
                   f'about-house/report/{y}/{y - 1911}report_Q{q}.pdf')
            r = get(url, timeout=60)
            if r and r.content[:4] == b'%PDF':
                content = r.content
                updated = f'{y}-Q{q}'
                break
            q -= 1
            if q == 0:
                y, q = y - 1, 4
        if not content:
            return None

        rd = PdfReader(io.BytesIO(content))
        page_text = None
        for pg in rd.pages[60:]:            # 綜合評估在報告後段，跳過前段省時間
            t = pg.extract_text() or ''
            if '綜合評估－全國' in t or ('綜合評估' in t and '可能成交價格' in t):
                page_text = t
                break
        if not page_text:
            for pg in rd.pages:             # 保險：全掃一次
                t = pg.extract_text() or ''
                if '可能成交價格' in t and '全國' in t:
                    page_text = t
                    break
        if not page_text:
            print("  B03 PDF 找不到綜合評估頁")
            return None

        pm = re.search(r'可能成交價格\s+([\d.]+)\s+[\d.]+\s*萬元/坪\s*(-?[\d.]+)%[^-\d]*(-?[\d.]+)%', page_text)
        if not pm:
            print("  B03 可能成交價格列解析失敗")
            return None
        idx, qoq, yoy = float(pm.group(1)), float(pm.group(2)), float(pm.group(3))
        if not (50 < idx < 500):
            return None
        sm = re.search(r'全國綜合表現分數為\s*(-?\d+)\s*分', "".join((p.extract_text() or '') for p in rd.pages[70:90]))
        score_note = f'、綜合分數{sm.group(1)}' if sm else ''
        if yoy <= -3 or qoq <= -2:
            status = 'red'
        elif (sm and int(sm.group(1)) < 0) or yoy < 1:
            status = 'yellow'
        else:
            status = 'green'
        note = f'{updated.replace("-", "")}全國{idx:.2f}，季{qoq:+.2f}%、年{yoy:+.2f}%{score_note}'
        return dict(value=f'{idx:.2f}', status=status, note=note, updated=updated)
    except Exception as e:
        print(f"  B03 cathay: {e}")
    return None


def fetch_B04():
    """六都移轉棟數 — 內政部統計月報 (statis.moi.gov.tw 4.5-辦理建物所有權登記)"""
    try:
        d = _fetch_moi_b0x()
        if not d or not d.get('b04'):
            return None
        b = d['b04']
        curr, prev, period = b['curr'], b['prev'], b['period']
        if not curr:
            return None

        total_curr = sum(curr.values())
        total_prev = sum(prev.values())

        yoy_str = ''
        worst_city, worst_yoy = '', 0.0
        if total_prev > 0:
            total_yoy = (total_curr - total_prev) / total_prev * 100
            yoy_str = f'年{"增" if total_yoy >= 0 else "減"}{abs(total_yoy):.1f}%'
            # Find city with largest drop
            for city in curr:
                p = prev.get(city, 0)
                if p > 0:
                    cy = (curr[city] - p) / p * 100
                    if cy < worst_yoy:
                        worst_yoy = cy
                        worst_city = city

        note_parts = [f'{period}六都{yoy_str}']
        if worst_city:
            note_parts.append(f'{worst_city}年減{abs(worst_yoy):.1f}%最多')
        note = '，'.join(note_parts)

        b01 = d.get('b01', {})
        yr = b01.get('year', TODAY.year) if b01 else TODAY.year
        nm = b01.get('n_months', 3) if b01 else 3
        if nm == 3:
            updated = f'{yr}-Q1'
        elif nm == 6:
            updated = f'{yr}-Q2'
        else:
            updated = f'{yr}-{nm:02d}'

        if total_prev > 0:
            total_yoy_val = (total_curr - total_prev) / total_prev * 100
            if total_yoy_val < -10:
                status = 'red'
            elif total_yoy_val < 0:
                status = 'yellow'
            else:
                status = 'green'
        else:
            status = 'yellow'

        return dict(value=f'{total_curr:,}棟', status=status, note=note, updated=updated)
    except Exception as e:
        print(f"  B04 statis.moi: {e}")
    return None


_PIP_HOUSING_CACHE = None   # pip.moi.gov.tw E1050 解析結果快取
_STATIS_BUILDING_CACHE = {}  # statis.moi.gov.tw 建照/使照 ODS 快取 {rptid: dict}


def _fetch_pip_housing():
    """抓取 pip.moi.gov.tw/Publicize/Info/E1050 房價負擔能力指標 HTML 表格
    回傳 {'period':'2025-Q3', 'national':9.71, 'cities':{'台北市':14.98, ...}}
    """
    global _PIP_HOUSING_CACHE
    if _PIP_HOUSING_CACHE is not None:
        return _PIP_HOUSING_CACHE
    if not HAS_BS4:
        return None
    from bs4 import BeautifulSoup
    r = get('https://pip.moi.gov.tw/Publicize/Info/E1050', timeout=55)
    if not r:
        return None
    soup = BeautifulSoup(r.text, 'lxml')
    tbl = soup.find('table', id='t1')
    if not tbl:
        return None

    period = THIS_MONTH
    caption = tbl.find('caption')
    if caption:
        m = re.search(r'(\d{2,3})年第([1-4])季', caption.get_text())
        if m:
            yr_ad = int(m.group(1)) + 1911
            period = f'{yr_ad}-Q{m.group(2)}'

    CITY_MAP = {
        '新北市': '新北市', '臺北市': '台北市', '桃園市': '桃園市',
        '臺中市': '台中市', '臺南市': '台南市', '高雄市': '高雄市',
    }
    national = None
    cities   = {}
    for row in tbl.find_all('tr'):
        tds = row.find_all('td')
        if len(tds) < 5:
            continue
        city_raw = tds[0].get_text(strip=True)
        try:
            ratio = float(tds[4].get_text(strip=True))
        except ValueError:
            continue
        if city_raw == '全國':
            national = ratio
        elif city_raw in CITY_MAP:
            cities[CITY_MAP[city_raw]] = ratio

    if national is None:
        return None
    _PIP_HOUSING_CACHE = {'period': period, 'national': national, 'cities': cities}
    return _PIP_HOUSING_CACHE


def fetch_B05():
    """六都房價所得比 — pip.moi.gov.tw E1050 (內政部房價負擔能力指標)"""
    try:
        d = _fetch_pip_housing()
        if not d or not d.get('cities'):
            return None
        cities = d['cities']
        period = d['period']
        worst_city = max(cities, key=cities.get)
        worst_val  = cities[worst_city]
        avg_6 = sum(cities.values()) / len(cities)
        note  = f'{worst_city}{worst_val:.2f}倍，六都均值{avg_6:.2f}倍'
        if worst_val > 12:
            status = 'red'
        elif worst_val > 8:
            status = 'yellow'
        else:
            status = 'green'
        return dict(value=f'{worst_val:.2f}倍', status=status, note=note, updated=period)
    except Exception as e:
        print(f"  B05 pip: {e}")
    return None


def fetch_C01():
    """房貸逾放比 — 金管會月報（HTML 解析）"""
    try:
        r = get('https://www.banking.gov.tw/ch/home.jsp?id=296&parentpath=0,4,132')
        if r and HAS_BS4:
            from bs4 import BeautifulSoup
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
    """房價所得比（全國）— pip.moi.gov.tw E1050 (內政部房價負擔能力指標)"""
    try:
        d = _fetch_pip_housing()
        if not d or d.get('national') is None:
            return None
        v = d['national']
        period = d['period']
        if v > 12:
            status, note = 'red',    f'全國{v:.2f}倍，嚴重超出負擔能力'
        elif v > 8:
            status, note = 'yellow', f'全國{v:.2f}倍，購屋負擔沉重'
        else:
            status, note = 'green',  f'全國{v:.2f}倍'
        return dict(value=f'{v:.2f}倍', status=status, note=note, updated=period)
    except Exception as e:
        print(f"  C02 pip: {e}")
    return None


def _parse_statis_building(rptid):
    """解析 statis.moi.gov.tw 建照/使照 ODS，回傳 {ytd, n_months, prev_ytd, year}
    328010 = 建造執照, 328050 = 使用執照；column 3 = 宅數
    """
    global _STATIS_BUILDING_CACHE
    if rptid in _STATIS_BUILDING_CACHE:
        return _STATIS_BUILDING_CACHE[rptid]

    import zipfile
    url = f'https://statis.moi.gov.tw/micst/report/{rptid}.ods'
    r = get(url, timeout=55)
    if not r:
        return None
    try:
        with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
            xml_content = zf.read('content.xml')
    except Exception as e:
        print(f"  {rptid} ODS zip: {e}")
        return None

    root = ET.fromstring(xml_content)
    ns = {
        'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
        'text':  'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
    }

    def ctext(cell):
        return ' '.join(t.text or '' for t in cell.findall('.//text:p', ns)).strip()

    def cint(cells, idx):
        if idx < len(cells):
            v = ctext(cells[idx]).replace(',', '').replace('－', '').strip()
            return int(v) if v.isdigit() else None
        return None

    rows = root.findall('.//table:table-row', ns)
    year_data = {}
    current_yr = None

    for row in rows:
        cells = row.findall('table:table-cell', ns)
        if not cells:
            continue
        v0 = ctext(cells[0])
        yr_m = re.search(r'\b(20\d{2})\b', v0)
        if yr_m and '年' in v0 and '月' not in v0:
            yr = int(yr_m.group(1))
            if 2015 <= yr <= TODAY.year + 1:
                current_yr = yr
                year_data[yr] = {'ytd': cint(cells, 3), 'months': []}
                continue
        if current_yr and re.match(r'[一二三四五六七八九十]+[　\s]*月', v0):
            val = cint(cells, 3)
            if val is not None:
                year_data[current_yr]['months'].append(val)

    if not year_data:
        return None

    years = sorted(year_data.keys())
    ly     = years[-1]
    latest = year_data[ly]
    n      = len(latest['months'])
    ytd    = latest['ytd'] or (sum(latest['months']) if latest['months'] else None)
    prev_ytd = None
    if ly - 1 in year_data:
        pm = year_data[ly - 1]['months'][:n]
        if pm:
            prev_ytd = sum(pm)
        elif n == 12 and year_data[ly - 1].get('ytd'):
            prev_ytd = year_data[ly - 1]['ytd']

    result = {'ytd': ytd, 'n_months': n, 'prev_ytd': prev_ytd, 'year': ly}
    _STATIS_BUILDING_CACHE[rptid] = result
    return result


def fetch_C03():
    """建照核發 — statis.moi.gov.tw 328010，備用 data.moi.gov.tw"""
    try:
        d = _parse_statis_building('328010')
        if d and d.get('ytd') and d.get('n_months'):
            n, ytd, prev_ytd, yr = d['n_months'], d['ytd'], d['prev_ytd'], d['year']
            ann = ytd / n * 12
            yoy_str = ''
            if prev_ytd and prev_ytd > 0:
                yoy = (ytd - prev_ytd) / prev_ytd * 100
                yoy_str = f'，年{"增" if yoy >= 0 else "減"}{abs(yoy):.1f}%'
            period_map = {3: 'Q1', 6: 'Q2', 9: '前3季', 12: '全年'}
            period  = period_map.get(n, f'前{n}月')
            updated = (f'{yr}-Q{n//3}' if n in (3,6,9) else
                       str(yr) if n == 12 else f'{yr}-{n:02d}')
            if ann < 100000:
                status, note = 'red',    f'{period}核發{ytd:,}戶{yoy_str}，年化不足10萬'
            elif ann < 140000:
                status, note = 'yellow', f'{period}核發{ytd:,}戶{yoy_str}，建照減少'
            else:
                status, note = 'green',  f'{period}核發{ytd:,}戶{yoy_str}'
            return dict(value=f'{ytd:,}戶', status=status, note=note, updated=updated)
    except Exception as e:
        print(f"  C03 statis: {e}")

    try:
        r = get('https://data.moi.gov.tw/MoiOD/System/DownloadFile.aspx?DATA=11086',
                timeout=55)
        if r and r.text.strip():
            rows = list(csv.reader(io.StringIO(r.text.lstrip('﻿'))))
            for row in reversed(rows[1:]):
                nums = [c.strip().replace(',','') for c in row
                        if c.strip().replace(',','').isdigit() and int(c.strip().replace(',','')) > 0]
                if nums:
                    val = int(nums[-1])
                    ann = val * 12
                    if ann < 130000:
                        status, note = 'red',    f'月均{val:,}戶，年化13萬以下'
                    elif ann < 160000:
                        status, note = 'yellow', f'月均{val:,}戶，建商保守減量'
                    else:
                        status, note = 'green',  f'月均{val:,}戶，供給正常'
                    return dict(value=f'{val:,}戶', status=status, note=note,
                                updated=THIS_MONTH)
    except Exception as e:
        print(f"  C03 MOI fallback: {e}")
    return None


def fetch_C04():
    """使照核發 — statis.moi.gov.tw 328050，備用 data.moi.gov.tw"""
    try:
        d_c4 = _parse_statis_building('328050')
        if d_c4 and d_c4.get('ytd') and d_c4.get('n_months'):
            n, ytd, prev_ytd, yr = d_c4['n_months'], d_c4['ytd'], d_c4['prev_ytd'], d_c4['year']
            yoy_str = ''
            if prev_ytd and prev_ytd > 0:
                yoy = (ytd - prev_ytd) / prev_ytd * 100
                yoy_str = f'，年{"增" if yoy >= 0 else "減"}{abs(yoy):.1f}%'
            period_map = {3: 'Q1', 6: 'Q2', 9: '前3季', 12: '全年'}
            period  = period_map.get(n, f'前{n}月')
            updated = (f'{yr}-Q{n//3}' if n in (3,6,9) else
                       str(yr) if n == 12 else f'{yr}-{n:02d}')
            # 建照數量（比較用）
            d_c3 = _parse_statis_building('328010')
            c3_ytd = d_c3['ytd'] if d_c3 and d_c3.get('ytd') else 0
            compare = '使照>建照，交屋潮持續' if ytd > c3_ytd else '使照<建照，供給將增'
            note = f'{period}核發{ytd:,}戶{yoy_str}，{compare}'
            status = 'yellow'
            return dict(value=f'{ytd:,}戶', status=status, note=note, updated=updated)
    except Exception as e:
        print(f"  C04 statis: {e}")

    try:
        r = get('https://data.moi.gov.tw/MoiOD/System/DownloadFile.aspx?DATA=11087',
                timeout=55)
        if r and r.text.strip():
            rows = list(csv.reader(io.StringIO(r.text.lstrip('﻿'))))
            for row in reversed(rows[1:]):
                nums = [c.strip().replace(',','') for c in row
                        if c.strip().replace(',','').isdigit() and int(c.strip().replace(',','')) > 0]
                if nums:
                    val = int(nums[-1])
                    return dict(value=f'{val:,}戶', status='yellow',
                                note=f'月均{val:,}戶，使照>建照，交屋潮持續',
                                updated=THIS_MONTH)
    except Exception as e:
        print(f"  C04 MOI fallback: {e}")
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
                         timeout=55, headers=HEADERS)
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
        r   = requests.get(url, timeout=55, headers=HEADERS)
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
        r = requests.get(DGBAS_CPI_XML, headers=HEADERS, timeout=55, verify=False)
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
        r = requests.get(url, timeout=55, headers=HEADERS, verify=False)
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
    # --only A05,B02 → 只跑指定代碼（本機排程器用來補 CI 抓不到的指標）
    only = None
    for i, a in enumerate(sys.argv):
        if a == '--only' and i + 1 < len(sys.argv):
            only = {c.strip().upper() for c in sys.argv[i + 1].split(',') if c.strip()}
    print(f"=== CX468 指標更新 {TODAY}{'（only=' + ','.join(sorted(only)) + '）' if only else ''} ===\n")
    data = load_data()
    ok = fail = skip = 0

    for ind in data['indicators']:
        code    = ind['code']
        if only and code not in only:
            skip += 1
            continue
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
