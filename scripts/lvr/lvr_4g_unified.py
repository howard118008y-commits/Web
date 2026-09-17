#!/usr/bin/env python3
# 口徑：4G（115S1+115S2 房地買賣、扣車位、住家用、排特殊備註、依編號去重、交易日 114/9/1–115/5/31）——三重／永和／板橋售後回租頁行情表唯一口徑，定義見 行銷產出/技術記錄/2026-09-14-行情口徑統一-4G.md §①
# 資料檔：本檔同層 115S1/f_lvr_land_a.csv、115S2/f_lvr_land_a.csv（內政部 plvr DownloadSeason?season=115S1|115S2&type=zip&fileName=lvr_landcsv.zip 解出）；本機 _cache/ 無季 zip，重跑前先下載
# 115S3 季檔 10/1 發布後，所有引用本口徑的頁（sanchong/yonghe/banqiao-sale-leaseback、第三批服務軸 6 頁、yonghe/tucheng-second-mortgage）要一起重跑、一起改，不可只改一頁；2026-09-17 加土城區（四區數字不變，僅新增土城四型態）
"""4G 口徑統一重跑（純標準庫，python3 即可）
資料：lvr_115S1.zip / lvr_115S2.zip（內政部 plvr DownloadSeason 全國 csv 包）解出的 f_lvr_land_a.csv（新北市）
口徑：①兩季合併、依「編號」去重（保留先出現者）②交易標的以「房地」開頭 ③主要用途＝住家用
     ④備註含 親友/員工/共有人/特殊交易/瑕疵/急需處分/公益 任一者排除 ⑤交易日 114/9/1–115/5/31
     ⑥扣車位：單價＝(總價元−車位總價元)/(建物移轉總面積−車位移轉總面積)×3.305785/1e4（萬/坪）；總價亦扣車位總價
     ⑦屋齡＝(交易日−建築完成年月)/365.25；建築完成年月缺者不入屋齡統計（n_age 另列）
     ⑧型態依「建物型態」原始標籤：公寓(5樓含以下無電梯)／華廈(10層含以下有電梯)／住宅大樓(11層含以上有電梯)／透天厝
用法：python3 lvr_4g_unified.py            → 五區×型態主表（三重／永和／板橋／中和／土城）
      python3 lvr_4g_unified.py --banqiao  → 板橋頁額外欄（40年+／0–5年／20年+／浮洲）
"""
import csv, sys, re, statistics as st
from datetime import date
from pathlib import Path
HERE = Path(__file__).resolve().parent
PING = 3.305785
TOWNS = ["三重區", "永和區", "板橋區", "中和區", "土城區"]
TYPES = {"公寓": "公寓(5樓含以下無電梯)", "華廈": "華廈(10層含以下有電梯)",
         "住宅大樓": "住宅大樓(11層含以上有電梯)", "透天": "透天厝"}
EXCL = ["親友", "員工", "共有人", "特殊交易", "瑕疵", "急需處分", "公益"]
D0, D1 = date(2025, 9, 1), date(2026, 5, 31)
FUZHOU_ROADS = ["大觀路", "僑中一街", "僑中二街", "僑中三街", "溪崑一街", "溪崑二街", "溪城路"]

def roc(s):
    s = (s or "").strip()
    if not s.isdigit() or len(s) < 6: return None
    s = s.zfill(7); y, m, d = int(s[:-4]) + 1911, int(s[-4:-2]), int(s[-2:])
    for dd in (d, 1):
        try: return date(y, m, dd)
        except ValueError: pass
    return None

def f(x):
    try: return float(x)
    except (TypeError, ValueError): return 0.0

def load():
    seen, out = set(), []
    for season in ("115S1", "115S2"):
        with open(HERE / season / "f_lvr_land_a.csv", encoding="utf-8-sig", newline="") as fh:
            for i, r in enumerate(csv.DictReader(fh)):
                if i == 0 and r["鄉鎮市區"].startswith("The"): continue
                k = r["編號"]
                if k in seen: continue
                seen.add(k)
                if r["鄉鎮市區"] not in TOWNS or not r["交易標的"].startswith("房地"): continue
                if r["主要用途"].strip() != "住家用": continue
                if any(kw in (r["備註"] or "") for kw in EXCL): continue
                td = roc(r["交易年月日"])
                if td is None or not (D0 <= td <= D1): continue
                tot, area = f(r["總價元"]), f(r["建物移轉總面積平方公尺"])
                pt, pa = f(r["車位總價元"]), f(r["車位移轉總面積平方公尺"])
                if area - pa <= 0 or tot - pt <= 0: continue
                bd = roc(r["建築完成年月"])
                out.append(dict(town=r["鄉鎮市區"], typ=r["建物型態"], addr=r["土地位置建物門牌"], season=season,
                                up=(tot - pt) / (area - pa) * PING / 1e4, tot=(tot - pt) / 1e4,
                                age=((td - bd).days / 365.25) if bd else None))
    return out

def stats(g):
    ages = [o["age"] for o in g if o["age"] is not None]
    return dict(n=len(g), 每坪中位=round(st.median(o["up"] for o in g), 1), 總價中位=round(st.median(o["tot"] for o in g)),
                屋齡平均=round(st.mean(ages), 1) if ages else None, 屋齡中位=round(st.median(ages), 1) if ages else None,
                逾30年pct=round(100 * sum(a >= 30 for a in ages) / len(ages)) if ages else None, n_age=len(ages))

if __name__ == "__main__":
    data = load()
    if "--banqiao" in sys.argv:
        b = [o for o in data if o["town"] == "板橋區"]
        ap = [o for o in b if o["typ"] == TYPES["公寓"]]; bl = [o for o in b if o["typ"] == TYPES["住宅大樓"]]
        print("板橋 全體住宅(四型態+其他)", len(b), round(st.median(o["up"] for o in b), 1))
        print("板橋 公寓40年+", stats([o for o in ap if o["age"] is not None and o["age"] >= 40]))
        print("板橋 大樓0-5年", stats([o for o in bl if o["age"] is not None and 0 <= o["age"] <= 5]))
        print("板橋 大樓20年+", stats([o for o in bl if o["age"] is not None and o["age"] >= 20]))
        fz = [o for o in b if any(rd in o["addr"] for rd in FUZHOU_ROADS)]
        print("板橋 浮洲(路名清單) 公寓", stats([o for o in fz if o["typ"] == TYPES["公寓"]]) if any(o["typ"] == TYPES["公寓"] for o in fz) else None)
        print("板橋 浮洲(路名清單) 大樓", stats([o for o in fz if o["typ"] == TYPES["住宅大樓"]]) if any(o["typ"] == TYPES["住宅大樓"] for o in fz) else None)
        aged = [o for o in b if o["age"] is not None]
        print("板橋 全體屋齡30+占比", len(aged), round(100 * sum(o["age"] >= 30 for o in aged) / len(aged), 1))
        sys.exit()
    for town in TOWNS:
        for name, label in TYPES.items():
            g = [o for o in data if o["town"] == town and o["typ"] == label]
            print(town, name, stats(g) if g else "n=0")
