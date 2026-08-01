"""
解析 output/lvr_*.zip — 北市 + 新北市 + 台中市 + 桃園市 4 縣市買賣主表。

產出：
- clean_df.pkl                          清洗後完整 df (4 城 × 9 季 + mini)
- ranking_w{30,90,180,365}.pkl          4 種時間窗 ranking table
- ranking_w{30,90,180,365}.json         同上，給網頁 JS 用
- 5_focus_kpis_w{...}.json              5 精選區 KPI per window
- shindian_deep.pkl                     新店區 113S1 vs 115S1 深度比較
- {town}_正常住宅_近180天.csv             5 精選明細
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from zipfile import ZipFile
import json

import pandas as pd

OUT_DIR = Path(__file__).resolve().parent / "_cache"
PINGS = 3.305785

FOCUS_TOWNS = ["中和區", "永和區", "板橋區", "新店區", "土城區"]
WINDOWS = [30, 90, 180, 365]
EXCLUDE_NOTE_KEYWORDS = ["親友", "員工", "共有人", "特殊交易", "瑕疵", "急需處分", "公益"]

CITY_FILES = {
    "台北市": "a_lvr_land_a.csv",
    "新北市": "f_lvr_land_a.csv",
    "台中市": "b_lvr_land_a.csv",
    "桃園市": "h_lvr_land_a.csv",
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


def _season_label(zip_path: Path) -> str:
    """由 zip 檔名推季別。

    季檔：lvr_115S1.zip → 115S1
    mini：lvr_mini_20260801.zip → 依日期換算民國季別（如 115S3）。
          不可直接用檔名，否則圖表 X 軸會出現「mini_20260801」這種原始字串
          ——2026-08-01 實際發生過，chart_city_trend 最後一格就是它。
    """
    stem = zip_path.stem.replace("lvr_", "")
    if not stem.startswith("mini_"):
        return stem
    ymd = stem.replace("mini_", "")
    try:
        y, m = int(ymd[:4]), int(ymd[4:6])
        return f"{y - 1911}S{(m - 1) // 3 + 1}"
    except (ValueError, IndexError):
        return stem


def load_main_csv(zip_path: Path, csv_name: str, city: str) -> pd.DataFrame:
    with ZipFile(zip_path) as z:
        with z.open(csv_name) as f:
            df = pd.read_csv(f, encoding="utf-8", dtype=str)
    df = df.iloc[1:].reset_index(drop=True)
    df["__season"] = _season_label(zip_path)
    df["縣市"] = city
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    n0 = len(df)
    df = df.copy()
    if "編號" in df.columns:
        df = df.drop_duplicates(subset=["編號"], keep="first")
    n_dedup = len(df)

    df["交易日期"] = df["交易年月日"].apply(roc_to_date)
    df = df.dropna(subset=["交易日期"])
    df["建築完成日期"] = df["建築完成年月"].apply(roc_to_date)
    df["屋齡"] = ((df["交易日期"] - df["建築完成日期"]).dt.days / 365.25).round(1)

    df = df[df["交易標的"].fillna("").str.contains("房地", regex=False)]
    note = df["備註"].fillna("")
    df = df[~note.apply(lambda x: any(k in x for k in EXCLUDE_NOTE_KEYWORDS))]
    df = df[df["主要用途"].fillna("").str.contains("住", regex=False)]

    for col in ["總價元", "單價元平方公尺", "建物移轉總面積平方公尺"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["總價元", "單價元平方公尺"])

    df["總價_萬"] = df["總價元"] / 10_000
    df["單價_萬每坪"] = df["單價元平方公尺"] * PINGS / 10_000
    df["建坪"] = df["建物移轉總面積平方公尺"] / PINGS

    df = df[df["總價_萬"] >= 100]
    df = df[(df["單價_萬每坪"] >= 5) & (df["單價_萬每坪"] <= 400)]

    print(f"  清洗：{n0:,} → dedupe {n_dedup:,} → 最終 {len(df):,}")
    return df


def town_kpi(df: pd.DataFrame, town: str) -> Optional[dict]:
    sub = df[df["鄉鎮市區"] == town]
    if sub.empty:
        return None
    return {
        "鄉鎮市區": town,
        "縣市": sub["縣市"].iloc[0],
        "n": int(len(sub)),
        "單價中位": round(float(sub["單價_萬每坪"].median()), 1),
        "單價平均": round(float(sub["單價_萬每坪"].mean()), 1),
        "總價中位": round(float(sub["總價_萬"].median()), 0),
        "建坪中位": round(float(sub["建坪"].median()), 1),
        "屋齡中位": (round(float(sub["屋齡"].dropna().median()), 1)
                  if sub["屋齡"].notna().any() else None),
    }


def cross_quarter_change(df: pd.DataFrame, town: str) -> Optional[float]:
    sub = df[df["鄉鎮市區"] == town]
    by_q = sub.groupby("__season")["單價_萬每坪"].median()
    if "113S1" not in by_q.index or "115S1" not in by_q.index:
        return None
    return round((by_q["115S1"] - by_q["113S1"]) / by_q["113S1"] * 100, 1)


def yoy_change(df: pd.DataFrame, town: str) -> Optional[float]:
    sub = df[df["鄉鎮市區"] == town]
    by_q = sub.groupby("__season")["單價_萬每坪"].median()
    if "114S1" not in by_q.index or "115S1" not in by_q.index:
        return None
    return round((by_q["115S1"] - by_q["114S1"]) / by_q["114S1"] * 100, 1)


def build_window(df: pd.DataFrame, days: int) -> tuple:
    """回傳該時間窗的 ranking_df + focus_kpis dict。"""
    cutoff = datetime.now() - timedelta(days=days)
    df_w = df[df["交易日期"] >= cutoff]

    rows = []
    for town in sorted(df_w["鄉鎮市區"].dropna().unique()):
        s = town_kpi(df_w, town)
        if not s:
            continue
        s["2年漲幅"] = cross_quarter_change(df, town)
        s["1年漲幅"] = yoy_change(df, town)
        rows.append(s)
    cols = ["鄉鎮市區", "縣市", "n", "單價中位", "單價平均", "總價中位",
            "建坪中位", "屋齡中位", "2年漲幅", "1年漲幅"]
    if not rows:
        ranking = pd.DataFrame(columns=cols)
    else:
        ranking = pd.DataFrame(rows).sort_values("單價中位", ascending=False)

    focus_kpis = {}
    for town in FOCUS_TOWNS:
        s = town_kpi(df_w, town)
        if s:
            s["2年漲幅"] = cross_quarter_change(df, town)
            s["1年漲幅"] = yoy_change(df, town)
            focus_kpis[town] = s

    return ranking, focus_kpis


def shindian_deep(df: pd.DataFrame) -> dict:
    """新店區 113S1 vs 115S1 深度分布比較。"""
    sd_113 = df[(df["鄉鎮市區"] == "新店區") & (df["__season"] == "113S1")]
    sd_115 = df[(df["鄉鎮市區"] == "新店區") & (df["__season"] == "115S1")]

    def stats(s):
        return {
            "n": int(len(s)),
            "median": round(float(s["單價_萬每坪"].median()), 1) if len(s) else None,
            "mean": round(float(s["單價_萬每坪"].mean()), 1) if len(s) else None,
            "median_total": round(float(s["總價_萬"].median()), 0) if len(s) else None,
            "median_age": (round(float(s["屋齡"].dropna().median()), 1)
                           if s["屋齡"].notna().any() else None),
            "median_ping": round(float(s["建坪"].median()), 1) if len(s) else None,
            "building_type": s["建物型態"].value_counts().to_dict() if len(s) else {},
            "age_buckets": age_bucket_counts(s),
            "price_buckets": price_bucket_counts(s),
        }
    return {
        "113S1": stats(sd_113),
        "115S1": stats(sd_115),
        "delta": {
            "n": int(len(sd_115)) - int(len(sd_113)),
            "median_pct": (
                round((sd_115["單價_萬每坪"].median() - sd_113["單價_萬每坪"].median())
                      / sd_113["單價_萬每坪"].median() * 100, 1)
                if len(sd_115) and len(sd_113) else None
            ),
        }
    }


def age_bucket_counts(s: pd.DataFrame) -> dict:
    buckets = {"0–5 年（新成屋）": 0, "5–15 年": 0, "15–30 年": 0,
               "30–45 年": 0, "45+ 年（老屋）": 0, "未知": 0}
    for v in s["屋齡"]:
        if pd.isna(v):
            buckets["未知"] += 1
        elif v < 5:
            buckets["0–5 年（新成屋）"] += 1
        elif v < 15:
            buckets["5–15 年"] += 1
        elif v < 30:
            buckets["15–30 年"] += 1
        elif v < 45:
            buckets["30–45 年"] += 1
        else:
            buckets["45+ 年（老屋）"] += 1
    return buckets


def price_bucket_counts(s: pd.DataFrame) -> dict:
    buckets = {"<30 萬/坪": 0, "30–45": 0, "45–60": 0, "60–80": 0, "80+": 0}
    for v in s["單價_萬每坪"]:
        if v < 30: buckets["<30 萬/坪"] += 1
        elif v < 45: buckets["30–45"] += 1
        elif v < 60: buckets["45–60"] += 1
        elif v < 80: buckets["60–80"] += 1
        else: buckets["80+"] += 1
    return buckets


def main() -> None:
    zip_files = sorted(OUT_DIR.glob("lvr_*.zip"))
    if not zip_files:
        raise SystemExit("✗ 找不到 output/lvr_*.zip")

    print(f"→ 載入 {len(zip_files)} 個 zip × {len(CITY_FILES)} 縣市")
    frames = []
    for zp in zip_files:
        for city, csv in CITY_FILES.items():
            try:
                frames.append(load_main_csv(zp, csv, city))
            except KeyError:
                print(f"  ⚠ {zp.name} 缺 {csv}（{city}）")
    df_raw = pd.concat(frames, ignore_index=True)
    print(f"→ 合計原始 {len(df_raw):,} 筆\n→ 清洗：")
    df = clean(df_raw)

    # 印一份 180 天 ranking 摘要看看
    print(f"\n{'=' * 76}")
    print(f"  4 縣市 全區 ranking｜TOP 15（近 180 天，按單價中位降序）")
    print(f"{'=' * 76}")
    ranking_180, focus_180 = build_window(df, 180)
    print(ranking_180[["鄉鎮市區", "縣市", "n", "單價中位", "1年漲幅", "2年漲幅"]].head(15).to_string(index=False))
    print(f"  全部 {len(ranking_180)} 區")

    # 產 4 個窗
    print(f"\n→ 產出 4 個時間窗 ranking：")
    for w in WINDOWS:
        ranking, focus = build_window(df, w)
        ranking.to_pickle(OUT_DIR / f"ranking_w{w}.pkl")
        ranking.to_json(OUT_DIR / f"ranking_w{w}.json",
                        orient="records", force_ascii=False)
        with open(OUT_DIR / f"focus_kpis_w{w}.json", "w", encoding="utf-8") as f:
            json.dump(focus, f, ensure_ascii=False, indent=2, default=str)
        print(f"  ✓ w={w}：{len(ranking)} 區")

    # 跨季趨勢序列（給前端互動圖表用；原本只有 PNG，前端沒有逐季資料可畫）
    print(f"\n→ 產出跨季趨勢 JSON（前端互動圖表用）")
    trend_pivot = (
        df.groupby(["__season", "縣市"])["單價_萬每坪"]
          .median().unstack("縣市").sort_index()
    )
    trend = {
        "seasons": [str(s) for s in trend_pivot.index],
        "series": {
            city: [None if pd.isna(v) else round(float(v), 1)
                   for v in trend_pivot[city]]
            for city in ["台北市", "新北市", "台中市", "桃園市"]
            if city in trend_pivot.columns
        },
        "unit": "萬/坪",
        "metric": "單價中位數",
    }
    with open(OUT_DIR / "city_trend.json", "w", encoding="utf-8") as f:
        json.dump(trend, f, ensure_ascii=False, indent=1)
    print(f"  ✓ city_trend.json：{len(trend['seasons'])} 季 × {len(trend['series'])} 縣市")

    # 新店深度解析
    print(f"\n→ 新店區 113S1 vs 115S1 深度解析")
    sd = shindian_deep(df)
    with open(OUT_DIR / "shindian_deep.json", "w", encoding="utf-8") as f:
        json.dump(sd, f, ensure_ascii=False, indent=2, default=str)
    pd.to_pickle(sd, OUT_DIR / "shindian_deep.pkl")
    print(f"  113S1：n={sd['113S1']['n']}、中位 {sd['113S1']['median']}、屋齡中位 {sd['113S1']['median_age']}")
    print(f"  115S1：n={sd['115S1']['n']}、中位 {sd['115S1']['median']}、屋齡中位 {sd['115S1']['median_age']}")
    print(f"  Δ：n {sd['delta']['n']:+d}、中位 {sd['delta']['median_pct']:+.1f}%")

    # clean_df + 5 精選明細
    df.to_pickle(OUT_DIR / "clean_df.pkl")
    cutoff = datetime.now() - timedelta(days=180)
    df_recent = df[df["交易日期"] >= cutoff]
    for town in FOCUS_TOWNS:
        sub = df_recent[df_recent["鄉鎮市區"] == town]
        if sub.empty:
            continue
        out_csv = OUT_DIR / f"{town}_正常住宅_近180天.csv"
        keep = [
            "交易日期", "縣市", "鄉鎮市區", "土地位置建物門牌", "建物型態",
            "建坪", "屋齡", "總價_萬", "單價_萬每坪",
            "建物現況格局-房", "建物現況格局-廳", "建物現況格局-衛",
            "建築完成年月", "移轉層次", "總樓層數",
        ]
        sub[keep].sort_values("交易日期", ascending=False).to_csv(
            out_csv, index=False, encoding="utf-8-sig"
        )
    print(f"\n✓ 已存：clean_df.pkl、5 精選 CSV、4 窗 ranking、shindian_deep")


if __name__ == "__main__":
    main()
