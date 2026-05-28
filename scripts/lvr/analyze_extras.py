"""
解析預售屋 (_b.csv) + 租屋 (_c.csv) 資料，產出 ranking + 租金報酬率。

產出：
- presale_clean.pkl / presale_ranking_w180.{pkl,json}
- rental_clean.pkl / rental_ranking_w180.{pkl,json}（含 yield_pct，以 buy ranking 對齊計算）

執行：.venv/bin/python scripts/analyze_extras.py
需要先跑：scripts/analyze_lvr.py（產 ranking_w180.pkl 給 yield 計算用）
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from zipfile import ZipFile
import json

import pandas as pd

OUT_DIR = Path(__file__).resolve().parent / "_cache"
PINGS = 3.305785
LOOKBACK_DAYS = 180

CITY_FILES_B = {  # 預售屋
    "台北市": "a_lvr_land_b.csv",
    "新北市": "f_lvr_land_b.csv",
    "台中市": "b_lvr_land_b.csv",
    "桃園市": "h_lvr_land_b.csv",
}
CITY_FILES_C = {  # 租屋
    "台北市": "a_lvr_land_c.csv",
    "新北市": "f_lvr_land_c.csv",
    "台中市": "b_lvr_land_c.csv",
    "桃園市": "h_lvr_land_c.csv",
}


def roc_to_date(s):
    try:
        s = str(s).strip()
        if len(s) not in (6, 7) or not s.isdigit():
            return pd.NaT
        if len(s) == 6:
            yyy, mm, dd = int(s[:2]), int(s[2:4]), int(s[4:6])
        else:
            yyy, mm, dd = int(s[:3]), int(s[3:5]), int(s[5:7])
        return datetime(yyy + 1911, mm, dd)
    except (ValueError, TypeError):
        return pd.NaT


def load_csvs(zip_files, city_files: dict, date_col: str) -> pd.DataFrame:
    frames = []
    for zp in zip_files:
        for city, csv in city_files.items():
            try:
                with ZipFile(zp) as z:
                    with z.open(csv) as f:
                        df = pd.read_csv(f, encoding="utf-8", dtype=str,
                                         on_bad_lines="skip", engine="c")
                df = df.iloc[1:].reset_index(drop=True)
                df["__season"] = zp.stem.replace("lvr_", "")
                df["縣市"] = city
                frames.append(df)
            except KeyError:
                pass  # 該 zip 沒此 csv，skip
            except Exception as e:
                print(f"  ⚠ {zp.name}:{csv}（{city}）解析失敗：{e}")
                continue
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    if "編號" in df.columns:
        df = df.drop_duplicates(subset=["編號"], keep="first")
    df["交易日期"] = df[date_col].apply(roc_to_date)
    df = df.dropna(subset=["交易日期"])
    return df


def clean_presale(df: pd.DataFrame) -> pd.DataFrame:
    """預售屋清洗：排除解約、住家用、價格極端值。"""
    df = df.copy()
    n0 = len(df)
    if "解約情形" in df.columns:
        cancelled = df["解約情形"].fillna("").str.contains("解除契約", regex=False)
        df = df[~cancelled]
    df = df[df["主要用途"].fillna("").str.contains("住", regex=False)]

    for col in ["總價元", "單價元平方公尺", "建物移轉總面積平方公尺"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["總價元", "單價元平方公尺"])

    df["總價_萬"] = df["總價元"] / 10_000
    df["單價_萬每坪"] = df["單價元平方公尺"] * PINGS / 10_000
    df["建坪"] = df["建物移轉總面積平方公尺"] / PINGS

    df = df[df["總價_萬"] >= 100]
    df = df[(df["單價_萬每坪"] >= 5) & (df["單價_萬每坪"] <= 400)]

    print(f"  預售清洗：{n0:,} → {len(df):,}")
    return df


def clean_rental(df: pd.DataFrame) -> pd.DataFrame:
    """租屋清洗：住家用、月租合理範圍。"""
    df = df.copy()
    n0 = len(df)
    df = df[df["主要用途"].fillna("").str.contains("住", regex=False)].copy()

    # 租屋的「總額元」= 月租金、「單價元平方公尺」= 月租/平方公尺
    for col in ["總額元", "單價元平方公尺", "建物總面積平方公尺"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["總額元", "單價元平方公尺"])

    df["月租_元"] = df["總額元"]
    df["月租_元每坪"] = df["單價元平方公尺"] * PINGS  # 元/坪/月
    df["建坪"] = df["建物總面積平方公尺"] / PINGS

    # 排除月租 < 3000 (異常)、月租 > 200000 (豪宅另論)
    df = df[(df["月租_元"] >= 3000) & (df["月租_元"] <= 200000)]
    # 排除每坪月租 < 200 元 (異常低) 或 > 5000 (豪宅異常)
    df = df[(df["月租_元每坪"] >= 200) & (df["月租_元每坪"] <= 5000)]

    print(f"  租屋清洗：{n0:,} → {len(df):,}")
    return df


def town_summary(df: pd.DataFrame, town: str, kind: str) -> Optional[dict]:
    sub = df[df["鄉鎮市區"] == town]
    if sub.empty:
        return None
    base = {
        "鄉鎮市區": town,
        "縣市": sub["縣市"].iloc[0],
        "n": int(len(sub)),
    }
    if kind == "presale":
        base.update({
            "單價中位": round(float(sub["單價_萬每坪"].median()), 1),
            "總價中位": round(float(sub["總價_萬"].median()), 0),
            "建坪中位": round(float(sub["建坪"].median()), 1),
        })
    else:  # rental
        base.update({
            "月租中位": round(float(sub["月租_元"].median()), 0),
            "月租每坪中位": round(float(sub["月租_元每坪"].median()), 0),
            "建坪中位": round(float(sub["建坪"].median()), 1),
        })
    return base


def build_ranking(df: pd.DataFrame, kind: str, days: int = LOOKBACK_DAYS) -> pd.DataFrame:
    cutoff = datetime.now() - timedelta(days=days)
    df_w = df[df["交易日期"] >= cutoff]
    rows = []
    for town in sorted(df_w["鄉鎮市區"].dropna().unique()):
        s = town_summary(df_w, town, kind)
        if s:
            rows.append(s)
    if not rows:
        return pd.DataFrame()
    sort_col = "單價中位" if kind == "presale" else "月租每坪中位"
    return pd.DataFrame(rows).sort_values(sort_col, ascending=False)


def add_yield(rental_rank: pd.DataFrame) -> pd.DataFrame:
    """以買賣 ranking 對齊計算租金報酬率：年租 / 售價 × 100%。"""
    buy_pkl = OUT_DIR / "ranking_w180.pkl"
    if not buy_pkl.exists():
        print("  ⚠ 找不到 ranking_w180.pkl，跳過 yield 計算")
        rental_rank["年化報酬率"] = None
        return rental_rank
    buy = pd.read_pickle(buy_pkl)  # 含 單價中位 萬/坪
    buy_lookup = {r["鄉鎮市區"]: r["單價中位"] for _, r in buy.iterrows()}

    def calc_yield(row):
        buy_price = buy_lookup.get(row["鄉鎮市區"])  # 萬/坪 = 10000 元/坪
        if buy_price is None or buy_price <= 0:
            return None
        annual_rent_per_ping = row["月租每坪中位"] * 12  # 元/坪/年
        buy_price_per_ping = buy_price * 10_000  # 元/坪
        return round(annual_rent_per_ping / buy_price_per_ping * 100, 2)

    rental_rank["年化報酬率"] = rental_rank.apply(calc_yield, axis=1)
    return rental_rank


def main() -> None:
    zip_files = sorted(OUT_DIR.glob("lvr_*.zip"))
    if not zip_files:
        raise SystemExit("✗ 找不到 output/lvr_*.zip")

    print(f"→ 載入 {len(zip_files)} 個 zip")

    # 預售屋
    print("\n→ 預售屋 (_b.csv)")
    presale_raw = load_csvs(zip_files, CITY_FILES_B, "交易年月日")
    print(f"  原始 {len(presale_raw):,} 筆")
    presale = clean_presale(presale_raw)
    presale.to_pickle(OUT_DIR / "presale_clean.pkl")
    presale_rank = build_ranking(presale, "presale")
    presale_rank.to_pickle(OUT_DIR / "presale_ranking_w180.pkl")
    presale_rank.to_json(OUT_DIR / "presale_ranking_w180.json",
                          orient="records", force_ascii=False)
    print(f"  ranking：{len(presale_rank)} 區")
    if len(presale_rank) >= 5:
        print(presale_rank.head(10).to_string(index=False))

    # 租屋
    print("\n→ 租屋 (_c.csv)")
    rental_raw = load_csvs(zip_files, CITY_FILES_C, "租賃年月日")
    print(f"  原始 {len(rental_raw):,} 筆")
    rental = clean_rental(rental_raw)
    rental.to_pickle(OUT_DIR / "rental_clean.pkl")
    rental_rank = build_ranking(rental, "rental")
    rental_rank = add_yield(rental_rank)
    rental_rank.to_pickle(OUT_DIR / "rental_ranking_w180.pkl")
    rental_rank.to_json(OUT_DIR / "rental_ranking_w180.json",
                         orient="records", force_ascii=False)
    print(f"  ranking：{len(rental_rank)} 區（含年化報酬率）")
    if len(rental_rank) >= 5:
        print(rental_rank.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
