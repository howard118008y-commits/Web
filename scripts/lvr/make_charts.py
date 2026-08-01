"""
從 output/clean_df.pkl 產出 6 張 PNG 圖表到 output/charts/。

執行：.venv/bin/python scripts/make_charts.py

圖表清單：
- chart_yoy_change.png        — 5 精選 + 雙北平均 近 1 年 YoY 變化
- chart_city_trend.png        — 4 縣市 9 季均價趨勢 (台北/新北/台中/桃園)
- chart_district_compare.png  — 5 精選區單價中位數比較
- chart_price_boxplot.png      — 5 精選區單價分布盒鬚
- chart_monthly_volume.png    — 5 精選區近 12 月成交量堆疊
- chart_building_types.png    — 5 精選區建物型態組成
- chart_age_price_scatter.png — 雙北全區屋齡 vs 單價散布圖
- chart_shindian_deep.png     — 新店區 113S1 vs 115S1 深度比較 (4 面板)
"""

from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from cjk_font import setup_cjk

OUT_DIR = Path(__file__).resolve().parent / "_cache"
CHART_DIR = OUT_DIR / "charts"
CHART_DIR.mkdir(exist_ok=True)

FOCUS_TOWNS = ["中和區", "永和區", "板橋區", "新店區", "土城區"]
COLORS = {
    "中和區": "#7C3AED", "永和區": "#2563EB", "板橋區": "#16A34A",
    "新店區": "#F59E0B", "土城區": "#EF4444",
    "台北市": "#0F172A", "新北市": "#7C3AED",
    "台中市": "#16A34A", "桃園市": "#F59E0B",
}
LOOKBACK_DAYS = 180

setup_cjk()  # 設定中文字型（含 CI/Ubuntu 的 Noto 路徑註冊）— 避免圖表中文變 □□□
plt.rcParams["figure.dpi"] = 100
plt.rcParams["savefig.dpi"] = 144
plt.rcParams["savefig.bbox"] = "tight"


def _save(fig, name: str) -> Path:
    path = CHART_DIR / name
    fig.savefig(path)
    plt.close(fig)
    return path


def chart_yoy_change(df: pd.DataFrame) -> Path:
    """5 精選 + 雙北平均，115S1 vs 114S1 單價中位數 YoY % 變化。"""
    rows = []
    # 5 精選區
    for town in FOCUS_TOWNS:
        sub = df[df["鄉鎮市區"] == town]
        by_q = sub.groupby("__season")["單價_萬每坪"].median()
        if "114S1" not in by_q.index or "115S1" not in by_q.index:
            continue
        yoy = (by_q["115S1"] - by_q["114S1"]) / by_q["114S1"] * 100
        rows.append((town, yoy, COLORS[town]))
    # 雙北平均
    for city in ["台北市", "新北市"]:
        sub = df[df["縣市"] == city]
        by_q = sub.groupby("__season")["單價_萬每坪"].median()
        if "114S1" not in by_q.index or "115S1" not in by_q.index:
            continue
        yoy = (by_q["115S1"] - by_q["114S1"]) / by_q["114S1"] * 100
        rows.append((f"{city}\n（全市平均）", yoy, COLORS[city]))

    rows.sort(key=lambda x: x[1])
    labels = [r[0] for r in rows]
    values = [r[1] for r in rows]
    colors = [r[2] for r in rows]

    fig, ax = plt.subplots(figsize=(12, 5.5))
    bars = ax.bar(labels, values, color=colors, edgecolor="white", linewidth=2)
    for bar, val in zip(bars, values):
        y = val + 0.4 if val >= 0 else val - 0.8
        ax.text(bar.get_x() + bar.get_width() / 2, y, f"{val:+.1f}%",
                ha="center", fontsize=10, fontweight="bold",
                color="#1B5E20" if val >= 0 else "#B71C1C")
    ax.axhline(0, color="#3a3a3c", linewidth=1)
    ax.set_title("單價中位數年增率 YoY（115Q1 vs 114Q1）",
                 fontsize=15, fontweight="bold", pad=14)
    ax.set_ylabel("年增率 (%)", fontsize=11)
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("white")
    return _save(fig, "chart_yoy_change.png")


def chart_city_trend(df: pd.DataFrame) -> Path:
    """4 縣市跨季均價趨勢線。"""
    pivot = (
        df.groupby(["__season", "縣市"])["單價_萬每坪"]
          .median()
          .unstack("縣市")
          .sort_index()
    )
    fig, ax = plt.subplots(figsize=(12, 5.5))
    for city in ["台北市", "新北市", "台中市", "桃園市"]:
        if city not in pivot.columns:
            continue
        ax.plot(pivot.index, pivot[city], marker="o", linewidth=2.5,
                color=COLORS[city], label=city, markersize=8)
        for x, y in zip(pivot.index, pivot[city]):
            ax.annotate(f"{y:.1f}", xy=(x, y), xytext=(0, 8),
                        textcoords="offset points", ha="center", fontsize=8,
                        color=COLORS[city], fontweight="bold")
    # 標題季別由資料實算，不可寫死——舊版固定寫「113Q1 → 115Q1」，
    # 資料往前走後標題與 X 軸對不上（2026-08-01 已到 115S3 仍寫 115Q1）。
    seasons = list(pivot.index)
    span = f"（{seasons[0]} → {seasons[-1]}）" if seasons else ""
    ax.set_title(f"4 縣市全市平均｜單價中位數跨季趨勢{span}",
                 fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("季別", fontsize=11)
    ax.set_ylabel("單價中位數（萬/坪）", fontsize=11)
    ax.legend(loc="best", frameon=True, framealpha=0.92, fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("white")
    return _save(fig, "chart_city_trend.png")


def chart_district_compare(df_recent: pd.DataFrame) -> Path:
    sub = df_recent[df_recent["鄉鎮市區"].isin(FOCUS_TOWNS)]
    medians = [sub[sub["鄉鎮市區"] == t]["單價_萬每坪"].median() for t in FOCUS_TOWNS]
    counts = [int((sub["鄉鎮市區"] == t).sum()) for t in FOCUS_TOWNS]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.bar(FOCUS_TOWNS, medians, color=[COLORS[t] for t in FOCUS_TOWNS],
                  edgecolor="white", linewidth=2)
    for bar, val, n in zip(bars, medians, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 1.0,
                f"{val:.1f}\n(n={n})", ha="center", fontsize=10, fontweight="bold")
    ax.set_title(f"5 精選區單價中位數比較（近 {LOOKBACK_DAYS} 天 正常住宅）",
                 fontsize=15, fontweight="bold", pad=14)
    ax.set_ylabel("單價中位數（萬/坪）", fontsize=11)
    ax.set_ylim(0, max(medians) * 1.18)
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("white")
    return _save(fig, "chart_district_compare.png")


def chart_price_boxplot(df_recent: pd.DataFrame) -> Path:
    data = [df_recent[df_recent["鄉鎮市區"] == t]["單價_萬每坪"].values for t in FOCUS_TOWNS]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bp = ax.boxplot(data, tick_labels=FOCUS_TOWNS, patch_artist=True,
                    medianprops={"color": "white", "linewidth": 2})
    for patch, town in zip(bp["boxes"], FOCUS_TOWNS):
        patch.set_facecolor(COLORS[town])
        patch.set_alpha(0.78)
    ax.set_title(f"5 精選區單價分布（近 {LOOKBACK_DAYS} 天 正常住宅）",
                 fontsize=15, fontweight="bold", pad=14)
    ax.set_ylabel("單價（萬/坪）", fontsize=11)
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("white")
    return _save(fig, "chart_price_boxplot.png")


def chart_monthly_volume(df: pd.DataFrame) -> Path:
    cutoff = datetime.now() - timedelta(days=365)
    sub = df[(df["交易日期"] >= cutoff) & (df["鄉鎮市區"].isin(FOCUS_TOWNS))].copy()
    sub["month"] = sub["交易日期"].dt.to_period("M").astype(str)
    pivot = (
        sub.groupby(["month", "鄉鎮市區"]).size()
        .unstack("鄉鎮市區").fillna(0).astype(int)
        .reindex(columns=FOCUS_TOWNS, fill_value=0)
        .sort_index()
    )
    fig, ax = plt.subplots(figsize=(13, 5.5))
    bottom = [0] * len(pivot)
    for town in FOCUS_TOWNS:
        ax.bar(pivot.index, pivot[town], bottom=bottom,
               label=town, color=COLORS[town], edgecolor="white", linewidth=0.5)
        bottom = [b + v for b, v in zip(bottom, pivot[town])]
    ax.set_title("5 精選區｜近 12 個月月成交量", fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("月份", fontsize=11)
    ax.set_ylabel("成交筆數", fontsize=11)
    ax.legend(loc="upper right", frameon=True, framealpha=0.92)
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("white")
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
    return _save(fig, "chart_monthly_volume.png")


def chart_building_types(df_recent: pd.DataFrame) -> Path:
    types_order = [
        "公寓(5樓含以下無電梯)",
        "華廈(10層含以下有電梯)",
        "住宅大樓(11層含以上有電梯)",
        "透天厝", "套房(1房1廳1衛)", "其他",
    ]
    type_colors = ["#94A3B8", "#60A5FA", "#7C3AED", "#16A34A", "#F59E0B", "#9CA3AF"]
    rows = []
    sub = df_recent[df_recent["鄉鎮市區"].isin(FOCUS_TOWNS)]
    for town in FOCUS_TOWNS:
        ss = sub[sub["鄉鎮市區"] == town]
        counts = ss["建物型態"].value_counts()
        total = counts.sum() or 1
        row, used = {}, 0
        for t in types_order[:-1]:
            v = int(counts.get(t, 0))
            row[t] = v / total * 100
            used += v
        row["其他"] = max(0, (total - used) / total * 100)
        rows.append(row)
    pct = pd.DataFrame(rows, index=FOCUS_TOWNS)[types_order]

    fig, ax = plt.subplots(figsize=(11, 5.5))
    left = [0] * len(pct)
    for t, c in zip(types_order, type_colors):
        ax.barh(pct.index, pct[t], left=left, label=t, color=c, edgecolor="white", linewidth=1)
        for i, (l, v) in enumerate(zip(left, pct[t])):
            if v >= 6:
                ax.text(l + v / 2, i, f"{v:.0f}%", ha="center", va="center",
                        color="white", fontsize=9, fontweight="bold")
        left = [l + v for l, v in zip(left, pct[t])]
    ax.set_title(f"5 精選區建物型態組成（近 {LOOKBACK_DAYS} 天 正常住宅）",
                 fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("佔比 (%)", fontsize=11)
    ax.set_xlim(0, 100)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False)
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("white")
    return _save(fig, "chart_building_types.png")


def chart_age_price_scatter(df_recent: pd.DataFrame) -> Path:
    """雙北全區 屋齡 vs 單價 散布圖（用顏色區分台北/新北）。"""
    sub = df_recent.dropna(subset=["屋齡"]).copy()
    sub = sub[(sub["屋齡"] >= 0) & (sub["屋齡"] <= 60)]
    fig, ax = plt.subplots(figsize=(12, 6))
    for city, color in [("新北市", "#7C3AED"), ("台北市", "#0F172A")]:
        ss = sub[sub["縣市"] == city]
        ax.scatter(ss["屋齡"], ss["單價_萬每坪"], s=6, alpha=0.25,
                   c=color, label=f"{city}（n={len(ss):,}）", edgecolors="none")
    ax.set_title(f"屋齡 vs 單價散布圖（雙北全區 近 {LOOKBACK_DAYS} 天 正常住宅）",
                 fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("屋齡（年）", fontsize=11)
    ax.set_ylabel("單價（萬/坪）", fontsize=11)
    ax.set_xlim(-1, 62)
    ax.set_ylim(0, max(200, sub["單價_萬每坪"].quantile(0.99) * 1.05))
    leg = ax.legend(loc="upper right", frameon=True, framealpha=0.95, fontsize=11)
    for h in leg.legend_handles:
        h.set_alpha(1.0)
        h.set_sizes([60])
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("white")
    return _save(fig, "chart_age_price_scatter.png")


def chart_shindian_deep(deep: dict) -> Path:
    """新店 113S1 vs 115S1 — 屋齡 / 單價 / 建物型態 / 摘要 4 panel。"""
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    BAR_COLORS = ("#94A3B8", "#EF4444")  # 113=灰、115=紅

    # Panel 1: 屋齡分布
    ax = axes[0, 0]
    cats = list(deep["113S1"]["age_buckets"].keys())
    v113 = [deep["113S1"]["age_buckets"][c] for c in cats]
    v115 = [deep["115S1"]["age_buckets"][c] for c in cats]
    n113 = sum(v113) or 1
    n115 = sum(v115) or 1
    p113 = [v / n113 * 100 for v in v113]
    p115 = [v / n115 * 100 for v in v115]
    x = range(len(cats))
    w = 0.38
    ax.bar([i - w/2 for i in x], p113, w, color=BAR_COLORS[0], label=f"113Q1 (n={n113})", edgecolor="white")
    ax.bar([i + w/2 for i in x], p115, w, color=BAR_COLORS[1], label=f"115Q1 (n={n115})", edgecolor="white")
    ax.set_xticks(list(x))
    ax.set_xticklabels(cats, rotation=20, ha="right", fontsize=9)
    ax.set_ylabel("佔比 (%)", fontsize=10)
    ax.set_title("屋齡分布｜結構變化", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax.set_facecolor("#FAFAFA")

    # Panel 2: 單價分布
    ax = axes[0, 1]
    cats = list(deep["113S1"]["price_buckets"].keys())
    v113 = [deep["113S1"]["price_buckets"][c] for c in cats]
    v115 = [deep["115S1"]["price_buckets"][c] for c in cats]
    n113 = sum(v113) or 1
    n115 = sum(v115) or 1
    p113 = [v / n113 * 100 for v in v113]
    p115 = [v / n115 * 100 for v in v115]
    x = range(len(cats))
    ax.bar([i - w/2 for i in x], p113, w, color=BAR_COLORS[0], label="113Q1", edgecolor="white")
    ax.bar([i + w/2 for i in x], p115, w, color=BAR_COLORS[1], label="115Q1", edgecolor="white")
    ax.set_xticks(list(x))
    ax.set_xticklabels(cats, fontsize=9)
    ax.set_ylabel("佔比 (%)", fontsize=10)
    ax.set_title("單價區間分布", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax.set_facecolor("#FAFAFA")

    # Panel 3: 建物型態（取兩期都有的 top 4）
    ax = axes[1, 0]
    types_113 = deep["113S1"]["building_type"]
    types_115 = deep["115S1"]["building_type"]
    all_types = sorted(set(list(types_113.keys()) + list(types_115.keys())),
                       key=lambda t: -(types_113.get(t, 0) + types_115.get(t, 0)))[:5]
    v113 = [types_113.get(t, 0) for t in all_types]
    v115 = [types_115.get(t, 0) for t in all_types]
    n113 = sum(types_113.values()) or 1
    n115 = sum(types_115.values()) or 1
    p113 = [v / n113 * 100 for v in v113]
    p115 = [v / n115 * 100 for v in v115]
    x = range(len(all_types))
    ax.bar([i - w/2 for i in x], p113, w, color=BAR_COLORS[0], label="113Q1", edgecolor="white")
    ax.bar([i + w/2 for i in x], p115, w, color=BAR_COLORS[1], label="115Q1", edgecolor="white")
    short = [t.split("(")[0] for t in all_types]
    ax.set_xticks(list(x))
    ax.set_xticklabels(short, rotation=15, ha="right", fontsize=9)
    ax.set_ylabel("佔比 (%)", fontsize=10)
    ax.set_title("建物型態分布", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax.set_facecolor("#FAFAFA")

    # Panel 4: 摘要文字
    ax = axes[1, 1]
    ax.axis("off")
    s113, s115, delta = deep["113S1"], deep["115S1"], deep["delta"]
    text = (
        f"新店區 113Q1 vs 115Q1 摘要\n"
        f"────────────────────\n"
        f"成交筆數       {s113['n']} → {s115['n']}  ({delta['n']:+d})\n"
        f"單價中位（萬/坪） {s113['median']} → {s115['median']}  ({delta['median_pct']:+.1f}%)\n"
        f"總價中位（萬）   {s113['median_total']:,.0f} → {s115['median_total']:,.0f}\n"
        f"建坪中位（坪）   {s113['median_ping']} → {s115['median_ping']}\n"
        f"屋齡中位（年）   {s113['median_age']} → {s115['median_age']}\n"
        f"\n推論：屋齡中位上升 {s115['median_age']-s113['median_age']:+.1f} 年，\n"
        f"成交品結構由「新成屋為主」轉向「中老屋為主」，\n"
        f"單價中位下降反映成交品結構改變，\n"
        f"不一定代表整體房市衰退。"
    )
    ax.text(0.05, 0.95, text, transform=ax.transAxes, fontsize=11,
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.8", facecolor="#FAFAFA",
                      edgecolor="#d2d2d7"))

    fig.suptitle("新店區深度解析｜113Q1 vs 115Q1（為何單價中位數下降？）",
                 fontsize=16, fontweight="bold", y=1.00)
    fig.patch.set_facecolor("white")
    fig.tight_layout()
    return _save(fig, "chart_shindian_deep.png")


def main() -> None:
    pkl = OUT_DIR / "clean_df.pkl"
    if not pkl.exists():
        raise SystemExit("✗ 先跑 analyze_lvr.py")

    df = pd.read_pickle(pkl)
    print(f"→ 載入 {len(df):,} 筆 cleaned data")

    cutoff = datetime.now() - timedelta(days=LOOKBACK_DAYS)
    df_recent = df[df["交易日期"] >= cutoff].copy()
    print(f"→ 近 {LOOKBACK_DAYS} 天：{len(df_recent):,} 筆")

    # 移除舊的 trend chart
    old = CHART_DIR / "chart_quarterly_trend.png"
    if old.exists():
        old.unlink()
        print(f"  ✗ 移除舊圖：{old.name}")

    # 載入新店深度解析資料
    deep_pkl = OUT_DIR / "shindian_deep.pkl"
    deep = pd.read_pickle(deep_pkl) if deep_pkl.exists() else None

    print("\n→ 生成圖表：")
    jobs = [
        (chart_yoy_change, (df,)),
        (chart_city_trend, (df,)),
        (chart_district_compare, (df_recent,)),
        (chart_price_boxplot, (df_recent,)),
        (chart_monthly_volume, (df,)),
        (chart_building_types, (df_recent,)),
        (chart_age_price_scatter, (df_recent,)),
    ]
    if deep:
        jobs.append((chart_shindian_deep, (deep,)))
    for fn, args in jobs:
        path = fn(*args)
        kb = path.stat().st_size / 1024
        print(f"  ✓ {path.name}（{kb:.0f} KB）")

    print(f"\n→ 全部存到 {CHART_DIR.relative_to(Path.cwd())}/")


if __name__ == "__main__":
    main()
