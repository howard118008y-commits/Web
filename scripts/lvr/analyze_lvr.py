"""
解析 output/lvr_*.zip 中的台北市 + 新北市買賣主表，
過濾「正常住宅」+ 計算屋齡，產出 clean df + 5 精選區明細 + 41 區排名表。

清洗規則（排除）：
- 交易標的非「房地」(排除純車位、純土地等)
- 備註含 親友/員工/共有人/特殊交易/瑕疵/急需處分/公益
- 主要用途非住家用
- 總價 < 100 萬 (極可能異常)
- 單價 < 5 萬/坪 或 > 400 萬/坪 (涵蓋台北精華區豪宅)
- 編號重複（mini-package 增量時 dedupe）
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from zipfile import ZipFile

import pandas as pd

OUT_DIR = Path(__file__).resolve().parent / "_cache"
OUT_DIR.mkdir(exist_ok=True)
PINGS = 3.305785

FOCUS_TOWNS = ["中和區", "永和區", "板橋區", "新店區", "土城區"]  # 5 精選保留
LOOKBACK_DAYS = 180
EXCLUDE_NOTE_KEYWORDS = ["親友", "員工", "共有人", "特殊交易", "瑕疵", "急需處分", "公益"]

CITY_FILES = {
    "台北市": "a_lvr_land_a.csv",
    "新北市": "f_lvr_land_a.csv",
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


def load_main_csv(zip_path: Path, csv_name: str, city: str) -> pd.DataFrame:
    with ZipFile(zip_path) as z:
        with z.open(csv_name) as f:
            df = pd.read_csv(f, encoding="utf-8", dtype=str)
    df = df.iloc[1:].reset_index(drop=True)
    df["__season"] = zip_path.stem.replace("lvr_", "")
    df["縣市"] = city
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    n0 = len(df)
    df = df.copy()

    # 編號 dedupe（多份 zip 可能有重複交易）
    if "編號" in df.columns:
        df = df.drop_duplicates(subset=["編號"], keep="first")
    n_dedup = len(df)

    df["交易日期"] = df["交易年月日"].apply(roc_to_date)
    df = df.dropna(subset=["交易日期"])
    n1 = len(df)

    df["建築完成日期"] = df["建築完成年月"].apply(roc_to_date)
    df["屋齡"] = ((df["交易日期"] - df["建築完成日期"]).dt.days / 365.25).round(1)

    df = df[df["交易標的"].fillna("").str.contains("房地", regex=False)]
    n2 = len(df)

    note = df["備註"].fillna("")
    df = df[~note.apply(lambda x: any(k in x for k in EXCLUDE_NOTE_KEYWORDS))]
    n3 = len(df)

    df = df[df["主要用途"].fillna("").str.contains("住", regex=False)]
    n4 = len(df)

    for col in ["總價元", "單價元平方公尺", "建物移轉總面積平方公尺"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["總價元", "單價元平方公尺"])

    df["總價_萬"] = df["總價元"] / 10_000
    df["單價_萬每坪"] = df["單價元平方公尺"] * PINGS / 10_000
    df["建坪"] = df["建物移轉總面積平方公尺"] / PINGS

    df = df[df["總價_萬"] >= 100]
    df = df[(df["單價_萬每坪"] >= 5) & (df["單價_萬每坪"] <= 400)]
    n5 = len(df)

    print(
        f"  清洗：{n0:,} → dedupe {n_dedup:,} → 有效日期 {n1:,} → 限房地 {n2:,} → "
        f"排除特殊 {n3:,} → 限住家用 {n4:,} → 排除極端值 {n5:,}"
    )
    return df


def summarize_town(df: pd.DataFrame, town: str) -> Optional[dict]:
    sub = df[df["鄉鎮市區"] == town]
    if sub.empty:
        return None
    return {
        "鄉鎮市區": town,
        "縣市": sub["縣市"].iloc[0],
        "n": len(sub),
        "單價中位": round(sub["單價_萬每坪"].median(), 1),
        "單價平均": round(sub["單價_萬每坪"].mean(), 1),
        "總價中位": round(sub["總價_萬"].median(), 0),
        "建坪中位": round(sub["建坪"].median(), 1),
        "屋齡中位": round(sub["屋齡"].dropna().median(), 1) if sub["屋齡"].notna().any() else None,
    }


def cross_quarter_change(df: pd.DataFrame, town: str) -> Optional[float]:
    sub = df[df["鄉鎮市區"] == town]
    by_q = sub.groupby("__season")["單價_萬每坪"].median()
    if "113S1" not in by_q.index or "115S1" not in by_q.index:
        return None
    return round((by_q["115S1"] - by_q["113S1"]) / by_q["113S1"] * 100, 1)


def main() -> None:
    zip_files = sorted(OUT_DIR.glob("lvr_*.zip"))
    if not zip_files:
        print("✗ 找不到 output/lvr_*.zip")
        return

    print(f"→ 載入 {len(zip_files)} 個季別檔案 × 2 縣市")
    frames = []
    for zp in zip_files:
        for city, csv in CITY_FILES.items():
            try:
                df = load_main_csv(zp, csv, city)
                frames.append(df)
            except KeyError:
                print(f"  ⚠ {zp.name} 缺 {csv}（{city}）")
    df_raw = pd.concat(frames, ignore_index=True)
    print(f"→ 合計原始 {len(df_raw):,} 筆\n→ 套用清洗規則：")
    df = clean(df_raw)

    cutoff = datetime.now() - timedelta(days=LOOKBACK_DAYS)
    df_recent = df[df["交易日期"] >= cutoff].copy()

    # ===== 5 精選區詳細 =====
    print(f"\n{'=' * 76}")
    print(f"  5 精選區｜正常住宅買賣摘要（近 {LOOKBACK_DAYS} 天）")
    print(f"{'=' * 76}")
    print(f"{'區別':<8}{'筆數':>6}{'單價中位':>10}{'單價平均':>10}{'總價中位':>10}{'建坪中位':>10}{'屋齡中位':>10}")
    print("-" * 76)
    for town in FOCUS_TOWNS:
        s = summarize_town(df_recent, town)
        if not s:
            continue
        print(f"{town:<8}{s['n']:>6}{s['單價中位']:>10.1f}{s['單價平均']:>10.1f}"
              f"{s['總價中位']:>10,.0f}{s['建坪中位']:>10.1f}"
              f"{(s['屋齡中位'] or 0):>10.1f}")

    # ===== 雙北 41 區排名 =====
    print(f"\n{'=' * 76}")
    print(f"  雙北全區排名｜TOP 15（按單價中位數降序）")
    print(f"{'=' * 76}")
    all_towns = sorted(df_recent["鄉鎮市區"].dropna().unique())
    rows = []
    for town in all_towns:
        s = summarize_town(df_recent, town)
        if not s:
            continue
        s["2年漲幅"] = cross_quarter_change(df, town)
        rows.append(s)
    ranking_df = pd.DataFrame(rows).sort_values("單價中位", ascending=False)
    print(ranking_df.head(15).to_string(index=False))
    print(f"\n  全部 {len(ranking_df)} 區，前 15 已列出")

    # ===== 跨季 YoY 變化（5 精選 + 雙北平均）=====
    print(f"\n{'=' * 76}")
    print(f"  跨季單價中位數｜季別 × 5 精選 + 雙北平均")
    print(f"{'=' * 76}")
    by_q_focus = (
        df[df["鄉鎮市區"].isin(FOCUS_TOWNS)]
        .groupby(["__season", "鄉鎮市區"])["單價_萬每坪"]
        .median()
        .unstack("鄉鎮市區")
        .reindex(columns=FOCUS_TOWNS)
        .round(1)
        .sort_index()
    )
    by_q_city = df.groupby(["__season", "縣市"])["單價_萬每坪"].median().unstack("縣市").round(1).sort_index()
    combined = pd.concat([by_q_focus, by_q_city], axis=1)
    print(combined.to_string())

    # 存清洗後 pickle + 排名 + 5 精選 CSV
    pkl = OUT_DIR / "clean_df.pkl"
    df.to_pickle(pkl)
    ranking_df.to_pickle(OUT_DIR / "ranking_recent.pkl")
    print(f"\n✓ 已存：clean_df.pkl（{len(df):,}）、ranking_recent.pkl（{len(ranking_df)} 區）")

    for town in FOCUS_TOWNS:
        sub = df_recent[df_recent["鄉鎮市區"] == town]
        if sub.empty:
            continue
        out_csv = OUT_DIR / f"{town}_正常住宅_近{LOOKBACK_DAYS}天.csv"
        keep = [
            "交易日期", "縣市", "鄉鎮市區", "土地位置建物門牌", "建物型態",
            "建坪", "屋齡", "總價_萬", "單價_萬每坪",
            "建物現況格局-房", "建物現況格局-廳", "建物現況格局-衛",
            "建築完成年月", "移轉層次", "總樓層數",
        ]
        sub[keep].sort_values("交易日期", ascending=False).to_csv(
            out_csv, index=False, encoding="utf-8-sig"
        )
    print(f"✓ 已存 {len(FOCUS_TOWNS)} 個精選區明細 CSV")

    # 全 41 區排名表 CSV
    rank_csv = OUT_DIR / f"雙北全區排名_近{LOOKBACK_DAYS}天.csv"
    ranking_df.to_csv(rank_csv, index=False, encoding="utf-8-sig")
    print(f"✓ 已存：{rank_csv.name}")


if __name__ == "__main__":
    main()
