"""
從 output/clean_df.pkl 產出 5 張 PNG 圖表到 output/charts/。

執行：.venv/bin/python scripts/make_charts.py

圖表清單：
- chart_quarterly_trend.png   — 5 區跨季單價中位數折線
- chart_district_compare.png  — 5 區近 180 天單價中位數長條
- chart_price_boxplot.png      — 5 區近 180 天單價分布盒鬚
- chart_monthly_volume.png    — 5 區近 12 個月月成交量堆疊長條
- chart_building_types.png    — 5 區建物型態組成百分比堆疊
"""

from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

OUT_DIR = Path(__file__).resolve().parent / "_cache"
CHART_DIR = OUT_DIR / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

TARGET_TOWNS = ["中和區", "永和區", "板橋區", "新店區", "土城區"]
COLORS = {
    "中和區": "#7C3AED",
    "永和區": "#2563EB",
    "板橋區": "#16A34A",
    "新店區": "#F59E0B",
    "土城區": "#EF4444",
}
LOOKBACK_DAYS = 180

# 中文字型 fallback：mac → linux (GitHub Actions)
plt.rcParams["font.sans-serif"] = [
    "PingFang TC", "Heiti TC", "Noto Sans CJK TC", "Noto Sans TC", "DejaVu Sans"
]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 100
plt.rcParams["savefig.dpi"] = 144
plt.rcParams["savefig.bbox"] = "tight"


def chart_quarterly_trend(df: pd.DataFrame) -> Path:
    pivot = (
        df.groupby(["__season", "鄉鎮市區"])["單價_萬每坪"]
          .median()
          .unstack("鄉鎮市區")
          .reindex(columns=TARGET_TOWNS)
          .sort_index()
    )
    fig, ax = plt.subplots(figsize=(12, 5.5))
    for town in TARGET_TOWNS:
        if town not in pivot.columns:
            continue
        ax.plot(pivot.index, pivot[town], marker="o", linewidth=2.2,
                color=COLORS[town], label=town, markersize=7)
    ax.set_title("中和周邊 5 區｜單價中位數跨季趨勢", fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("季別", fontsize=11)
    ax.set_ylabel("單價中位數（萬/坪）", fontsize=11)
    ax.legend(loc="best", frameon=True, framealpha=0.92)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("white")
    path = CHART_DIR / "chart_quarterly_trend.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def chart_district_compare(df_recent: pd.DataFrame) -> Path:
    medians = [df_recent[df_recent["鄉鎮市區"] == t]["單價_萬每坪"].median() for t in TARGET_TOWNS]
    counts = [int((df_recent["鄉鎮市區"] == t).sum()) for t in TARGET_TOWNS]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.bar(TARGET_TOWNS, medians, color=[COLORS[t] for t in TARGET_TOWNS],
                  edgecolor="white", linewidth=2)
    for bar, val, n in zip(bars, medians, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 1.0,
                f"{val:.1f}\n(n={n})", ha="center", fontsize=10, fontweight="bold")
    ax.set_title(f"5 區單價中位數比較（近 {LOOKBACK_DAYS} 天 正常住宅）",
                 fontsize=15, fontweight="bold", pad=14)
    ax.set_ylabel("單價中位數（萬/坪）", fontsize=11)
    ax.set_ylim(0, max(medians) * 1.18)
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("white")
    path = CHART_DIR / "chart_district_compare.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def chart_price_boxplot(df_recent: pd.DataFrame) -> Path:
    data = [df_recent[df_recent["鄉鎮市區"] == t]["單價_萬每坪"].values for t in TARGET_TOWNS]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bp = ax.boxplot(data, tick_labels=TARGET_TOWNS, patch_artist=True,
                    medianprops={"color": "white", "linewidth": 2})
    for patch, town in zip(bp["boxes"], TARGET_TOWNS):
        patch.set_facecolor(COLORS[town])
        patch.set_alpha(0.78)
    ax.set_title(f"5 區單價分布（近 {LOOKBACK_DAYS} 天 正常住宅）",
                 fontsize=15, fontweight="bold", pad=14)
    ax.set_ylabel("單價（萬/坪）", fontsize=11)
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("white")
    path = CHART_DIR / "chart_price_boxplot.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def chart_monthly_volume(df: pd.DataFrame) -> Path:
    cutoff = datetime.now() - timedelta(days=365)
    df_year = df[df["交易日期"] >= cutoff].copy()
    df_year["month"] = df_year["交易日期"].dt.to_period("M").astype(str)
    pivot = (
        df_year.groupby(["month", "鄉鎮市區"]).size()
        .unstack("鄉鎮市區").fillna(0).astype(int)
        .reindex(columns=TARGET_TOWNS, fill_value=0)
        .sort_index()
    )
    fig, ax = plt.subplots(figsize=(13, 5.5))
    bottom = [0] * len(pivot)
    for town in TARGET_TOWNS:
        ax.bar(pivot.index, pivot[town], bottom=bottom,
               label=town, color=COLORS[town], edgecolor="white", linewidth=0.5)
        bottom = [b + v for b, v in zip(bottom, pivot[town])]
    ax.set_title("中和周邊 5 區｜近 12 個月月成交量", fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("月份", fontsize=11)
    ax.set_ylabel("成交筆數", fontsize=11)
    ax.legend(loc="upper right", frameon=True, framealpha=0.92)
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("white")
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
    path = CHART_DIR / "chart_monthly_volume.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def chart_building_types(df_recent: pd.DataFrame) -> Path:
    types_order = [
        "公寓(5樓含以下無電梯)",
        "華廈(10層含以下有電梯)",
        "住宅大樓(11層含以上有電梯)",
        "透天厝",
        "套房(1房1廳1衛)",
        "其他",
    ]
    type_colors = ["#94A3B8", "#60A5FA", "#7C3AED", "#16A34A", "#F59E0B", "#9CA3AF"]

    rows = []
    for town in TARGET_TOWNS:
        sub = df_recent[df_recent["鄉鎮市區"] == town]
        counts = sub["建物型態"].value_counts()
        total = counts.sum() or 1
        row = {}
        used = 0
        for t in types_order[:-1]:
            v = int(counts.get(t, 0))
            row[t] = v / total * 100
            used += v
        row["其他"] = max(0, (total - used) / total * 100)
        rows.append(row)
    pct = pd.DataFrame(rows, index=TARGET_TOWNS)[types_order]

    fig, ax = plt.subplots(figsize=(11, 5.5))
    left = [0] * len(pct)
    for t, c in zip(types_order, type_colors):
        ax.barh(pct.index, pct[t], left=left, label=t, color=c, edgecolor="white", linewidth=1)
        for i, (l, v) in enumerate(zip(left, pct[t])):
            if v >= 6:
                ax.text(l + v / 2, i, f"{v:.0f}%", ha="center", va="center",
                        color="white", fontsize=9, fontweight="bold")
        left = [l + v for l, v in zip(left, pct[t])]

    ax.set_title(f"5 區建物型態組成（近 {LOOKBACK_DAYS} 天 正常住宅）",
                 fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("佔比 (%)", fontsize=11)
    ax.set_xlim(0, 100)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False)
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("white")
    path = CHART_DIR / "chart_building_types.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def main() -> None:
    pkl = OUT_DIR / "clean_df.pkl"
    if not pkl.exists():
        print(f"✗ 找不到 {pkl}，先跑 analyze_lvr.py")
        return

    df = pd.read_pickle(pkl)
    print(f"→ 載入 {len(df):,} 筆 cleaned data")

    cutoff = datetime.now() - timedelta(days=LOOKBACK_DAYS)
    df_recent = df[df["交易日期"] >= cutoff].copy()
    print(f"→ 近 {LOOKBACK_DAYS} 天：{len(df_recent):,} 筆")

    print("\n→ 生成圖表：")
    for fn, args in [
        (chart_quarterly_trend, (df,)),
        (chart_district_compare, (df_recent,)),
        (chart_price_boxplot, (df_recent,)),
        (chart_monthly_volume, (df,)),
        (chart_building_types, (df_recent,)),
    ]:
        path = fn(*args)
        kb = path.stat().st_size / 1024
        print(f"  ✓ {path.name}（{kb:.0f} KB）")

    print(f"\n→ 全部存到 {CHART_DIR.relative_to(Path.cwd())}/")


if __name__ == "__main__":
    main()
