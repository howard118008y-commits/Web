"""
解析 output/lvr_*.zip 中的新北市買賣主表 (f_lvr_land_a.csv)，
過濾「中和及周邊 5 區 × 正常住宅 × 近 N 個月」，產 summary + 明細 CSV + clean df pickle。

清洗規則（排除）：
- 交易標的非「房地」(排除純車位、純土地等)
- 備註含 親友/員工/共有人/特殊交易/瑕疵/急需處分/公益
- 主要用途非住家用
- 總價 < 100 萬 (極可能異常)
- 單價 < 5 萬/坪 或 > 200 萬/坪 (中和周邊極端值)
"""

from datetime import datetime, timedelta
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

OUT_DIR = Path(__file__).resolve().parent / "_cache"
PINGS = 3.305785
TARGET_TOWNS = ["中和區", "永和區", "板橋區", "新店區", "土城區"]
LOOKBACK_DAYS = 180

EXCLUDE_NOTE_KEYWORDS = ["親友", "員工", "共有人", "特殊交易", "瑕疵", "急需處分", "公益"]


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


def load_main_csv(zip_path: Path) -> pd.DataFrame:
    with ZipFile(zip_path) as z:
        with z.open("f_lvr_land_a.csv") as f:
            df = pd.read_csv(f, encoding="utf-8", dtype=str)
    df = df.iloc[1:].reset_index(drop=True)
    df["__season"] = zip_path.stem.replace("lvr_", "")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    n0 = len(df)
    df = df.copy()
    df["交易日期"] = df["交易年月日"].apply(roc_to_date)
    df = df.dropna(subset=["交易日期"])
    n1 = len(df)

    # 必須是房地或房地+車位交易（含「房地」字樣）
    df = df[df["交易標的"].fillna("").str.contains("房地", regex=False)]
    n2 = len(df)

    note = df["備註"].fillna("")
    mask_special = note.apply(lambda x: any(k in x for k in EXCLUDE_NOTE_KEYWORDS))
    df = df[~mask_special]
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
    df = df[(df["單價_萬每坪"] >= 5) & (df["單價_萬每坪"] <= 200)]
    n5 = len(df)

    print(
        f"  清洗：{n0:,} → 有效日期 {n1:,} → 限房地 {n2:,} → "
        f"排除特殊交易 {n3:,} → 限住家用 {n4:,} → 排除極端值 {n5:,}"
    )
    return df


def summarize_town(df: pd.DataFrame, town: str) -> dict:
    sub = df[df["鄉鎮市區"] == town]
    if sub.empty:
        return {"town": town, "n": 0}
    return {
        "town": town,
        "n": len(sub),
        "unit_median": round(sub["單價_萬每坪"].median(), 1),
        "unit_mean": round(sub["單價_萬每坪"].mean(), 1),
        "total_median": round(sub["總價_萬"].median(), 0),
        "ping_median": round(sub["建坪"].median(), 1),
    }


def main() -> None:
    zip_files = sorted(OUT_DIR.glob("lvr_*.zip"))
    if not zip_files:
        print("✗ 找不到 output/lvr_*.zip，請先跑 download_lvr.py")
        return

    print(f"→ 載入 {len(zip_files)} 個季別檔案")
    frames = []
    for zp in zip_files:
        df = load_main_csv(zp)
        print(f"  {zp.name}：{len(df):,} 筆原始")
        frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    print(f"→ 合計原始 {len(df):,} 筆\n→ 套用清洗規則：")
    df = clean(df)

    df_5 = df[df["鄉鎮市區"].isin(TARGET_TOWNS)].copy()
    print(f"\n→ 限定中和周邊 5 區：{len(df_5):,} 筆")

    cutoff = datetime.now() - timedelta(days=LOOKBACK_DAYS)
    df_recent = df_5[df_5["交易日期"] >= cutoff].copy()

    print(f"\n{'=' * 72}")
    print(f"  中和周邊 5 區｜正常住宅買賣摘要（近 {LOOKBACK_DAYS} 天）")
    print(f"{'=' * 72}")
    print(f"{'區別':<8}{'筆數':>8}{'單價中位':>12}{'單價平均':>12}{'總價中位':>12}{'建坪中位':>10}")
    print("-" * 72)
    for town in TARGET_TOWNS:
        s = summarize_town(df_recent, town)
        if s["n"] == 0:
            print(f"{town:<8}{'0':>8}  ── 無資料 ──")
            continue
        print(
            f"{town:<8}{s['n']:>8}"
            f"{s['unit_median']:>12.1f}{s['unit_mean']:>12.1f}"
            f"{s['total_median']:>12,.0f}{s['ping_median']:>10.1f}"
        )

    if len(df_5["__season"].unique()) > 1:
        print(f"\n{'=' * 72}")
        print(f"  跨季趨勢｜單價中位數（萬/坪）")
        print(f"{'=' * 72}")
        pivot = (
            df_5.groupby(["__season", "鄉鎮市區"])["單價_萬每坪"]
                .median()
                .unstack("鄉鎮市區")
                .round(1)
                .reindex(columns=TARGET_TOWNS)
                .sort_index()
        )
        print(pivot.to_string())

    pickle_path = OUT_DIR / "clean_df.pkl"
    df_5.to_pickle(pickle_path)
    print(f"\n✓ 已存清洗 df（5 區 × 全期間）：{pickle_path.relative_to(Path.cwd())}")

    for town in TARGET_TOWNS:
        sub = df_recent[df_recent["鄉鎮市區"] == town]
        if sub.empty:
            continue
        out_csv = OUT_DIR / f"{town}_正常住宅_近{LOOKBACK_DAYS}天.csv"
        keep = [
            "交易日期", "鄉鎮市區", "土地位置建物門牌", "建物型態",
            "建坪", "總價_萬", "單價_萬每坪",
            "建物現況格局-房", "建物現況格局-廳", "建物現況格局-衛",
            "建築完成年月", "移轉層次", "總樓層數",
        ]
        sub[keep].sort_values("交易日期", ascending=False).to_csv(
            out_csv, index=False, encoding="utf-8-sig"
        )
    print(f"✓ 已存 5 區明細 CSV")


if __name__ == "__main__":
    main()
