"""
產出 6 張 IG/FB 規格圖卡（1080×1350，4:5）給社群週報用。
存到 CX468/lvr-social-cards/。

card_1_hero.png        — 標題卡
card_2_yoy.png          — 5 精選 + 雙北 YoY 年增率
card_3_city_trend.png   — 4 縣市 9 季均價趨勢
card_4_top_gain.png     — TOP 5 漲幅最強區
card_5_shindian.png     — 新店深度解析洞察
card_6_cta.png          — CTA 卡 (連到觀察室)
"""

from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd

from cjk_font import setup_cjk

OUT_DIR = Path(__file__).resolve().parent / "_cache"
CARD_DIR = OUT_DIR / "social-cards"
CARD_DIR.mkdir(exist_ok=True)

# 1080×1350 @ 100 dpi → figsize=(10.8, 13.5)
FIGSIZE = (10.8, 13.5)
PURPLE = "#7C3AED"
BLUE = "#2563EB"
GREEN = "#16A34A"
ORANGE = "#F59E0B"
RED = "#EF4444"
DARK = "#1d1d1f"
GREY = "#6e6e73"
LIGHT_BG = "#FAFAFA"

setup_cjk()  # 設定中文字型（含 CI/Ubuntu 的 Noto 路徑註冊）— 避免圖卡中文變 □□□
plt.rcParams["savefig.dpi"] = 100
plt.rcParams["savefig.bbox"] = "tight"
plt.rcParams["savefig.pad_inches"] = 0


def _new_card(bg="white"):
    fig = plt.figure(figsize=FIGSIZE, dpi=100)
    fig.patch.set_facecolor(bg)
    return fig


def _save(fig, name: str) -> Path:
    path = CARD_DIR / name
    fig.savefig(path, dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


def _eyebrow_and_title(fig, eyebrow: str, title: str, top=0.92):
    fig.text(0.5, top + 0.02, eyebrow, ha="center", fontsize=14,
             color=(1, 1, 1, 0.85) if fig.get_facecolor() != (1, 1, 1, 1) else GREY,
             weight="bold", style="italic")
    fig.text(0.5, top - 0.04, title, ha="center", fontsize=36,
             color="white" if fig.get_facecolor() != (1, 1, 1, 1) else DARK,
             weight="bold")


def card_1_hero(generated_at: str, season_label: str, n_districts: int) -> Path:
    fig = _new_card()
    # 漸層背景（用 imshow 模擬）
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    # gradient rect (top portion)
    grad = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="square,pad=0",
                                   transform=ax.transAxes,
                                   facecolor=PURPLE, edgecolor="none")
    ax.add_patch(grad)
    # 漸層用兩個 patch + alpha
    ax.add_patch(patches.Rectangle((0, 0.4), 1, 0.6, transform=ax.transAxes,
                                    facecolor=PURPLE, edgecolor="none"))
    ax.add_patch(patches.Rectangle((0, 0.2), 1, 0.5, transform=ax.transAxes,
                                    facecolor=BLUE, alpha=0.6, edgecolor="none"))
    ax.add_patch(patches.Rectangle((0, 0), 1, 0.4, transform=ax.transAxes,
                                    facecolor=GREEN, alpha=0.5, edgecolor="none"))

    # Text
    fig.text(0.5, 0.70, "實價登錄觀察", ha="center", fontsize=64,
             color="white", weight="bold")
    fig.text(0.5, 0.62, season_label + " 報告", ha="center", fontsize=36,
             color="white", weight="600")

    fig.text(0.5, 0.40, "四縣市 · " + str(n_districts) + " 行政區",
             ha="center", fontsize=24, color=(1, 1, 1, 0.92))
    fig.text(0.5, 0.34, "台北 · 新北 · 台中 · 桃園",
             ha="center", fontsize=18, color=(1, 1, 1, 0.78))

    fig.text(0.5, 0.16, "鋮馨租賃｜不動產資料觀察", ha="center", fontsize=18,
             color=(1, 1, 1, 0.85), weight="600")
    fig.text(0.5, 0.10, generated_at, ha="center", fontsize=14,
             color=(1, 1, 1, 0.7))

    return _save(fig, "card_1_hero.png")


def card_2_yoy(df: pd.DataFrame) -> Path:
    FOCUS = ["中和區", "永和區", "板橋區", "新店區", "土城區"]
    COLOR_MAP = {"中和區": PURPLE, "永和區": BLUE, "板橋區": GREEN,
                 "新店區": ORANGE, "土城區": RED,
                 "台北市\n（平均）": "#0F172A", "新北市\n（平均）": PURPLE}
    rows = []
    for town in FOCUS:
        sub = df[df["鄉鎮市區"] == town]
        by_q = sub.groupby("__season")["單價_萬每坪"].median()
        if "114S1" in by_q.index and "115S1" in by_q.index:
            yoy = (by_q["115S1"] - by_q["114S1"]) / by_q["114S1"] * 100
            rows.append((town, yoy, COLOR_MAP[town]))
    for city in ["台北市", "新北市"]:
        sub = df[df["縣市"] == city]
        by_q = sub.groupby("__season")["單價_萬每坪"].median()
        if "114S1" in by_q.index and "115S1" in by_q.index:
            yoy = (by_q["115S1"] - by_q["114S1"]) / by_q["114S1"] * 100
            label = f"{city}\n（平均）"
            rows.append((label, yoy, COLOR_MAP[label]))
    rows.sort(key=lambda x: x[1])
    labels = [r[0] for r in rows]
    values = [r[1] for r in rows]
    colors = [r[2] for r in rows]

    fig = _new_card()
    # eyebrow + title 在頂部
    fig.text(0.5, 0.94, "近 1 年 單價變化 YoY", ha="center", fontsize=22,
             color=GREY, weight="600")
    fig.text(0.5, 0.88, "115Q1 vs 114Q1", ha="center", fontsize=38,
             color=DARK, weight="bold")

    ax = fig.add_axes([0.10, 0.10, 0.80, 0.66])
    bars = ax.bar(labels, values, color=colors, edgecolor="white", linewidth=3)
    for bar, val in zip(bars, values):
        y = val + 1.0 if val >= 0 else val - 1.8
        ax.text(bar.get_x() + bar.get_width() / 2, y,
                f"{val:+.1f}%", ha="center", fontsize=14, weight="bold",
                color=GREEN if val >= 0 else RED)
    ax.axhline(0, color=DARK, linewidth=1.5)
    ax.set_ylabel("年增率 (%)", fontsize=14)
    ax.tick_params(labelsize=11)
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax.set_facecolor(LIGHT_BG)
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.text(0.5, 0.04, "@cx468.com.tw 實價登錄觀察室", ha="center",
             fontsize=12, color=GREY)
    return _save(fig, "card_2_yoy.png")


def card_3_city_trend(df: pd.DataFrame) -> Path:
    CITY_COLOR = {"台北市": "#0F172A", "新北市": PURPLE,
                  "台中市": GREEN, "桃園市": ORANGE}
    pivot = (df.groupby(["__season", "縣市"])["單價_萬每坪"]
             .median().unstack("縣市").sort_index())

    fig = _new_card()
    fig.text(0.5, 0.94, "9 季均價 跨縣市趨勢", ha="center", fontsize=22,
             color=GREY, weight="600")
    fig.text(0.5, 0.88, "四縣市 113Q1 → 115Q1", ha="center", fontsize=34,
             color=DARK, weight="bold")

    ax = fig.add_axes([0.10, 0.16, 0.80, 0.60])
    for city in ["台北市", "新北市", "台中市", "桃園市"]:
        if city not in pivot.columns:
            continue
        ax.plot(pivot.index, pivot[city], marker="o", linewidth=3.5,
                color=CITY_COLOR[city], label=city, markersize=10)
    ax.set_xlabel("季別", fontsize=13)
    ax.set_ylabel("單價中位數（萬/坪）", fontsize=13)
    ax.legend(loc="best", fontsize=14, frameon=True, framealpha=0.95)
    ax.tick_params(labelsize=11)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_facecolor(LIGHT_BG)
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.text(0.5, 0.10, "資料來源：內政部實價登錄 · 已排除特殊交易",
             ha="center", fontsize=13, color=GREY)
    fig.text(0.5, 0.05, "@cx468.com.tw 實價登錄觀察室", ha="center",
             fontsize=12, color=GREY)
    return _save(fig, "card_3_city_trend.png")


def card_4_top_gain(ranking: pd.DataFrame) -> Path:
    # 拉 YoY 漲幅 TOP 5（先排除樣本太小）
    valid = ranking.dropna(subset=["1年漲幅"])
    valid = valid[valid["n"] >= 30]
    top5 = valid.nlargest(5, "1年漲幅")

    fig = _new_card()
    fig.text(0.5, 0.94, "近 1 年 漲幅 TOP 5", ha="center", fontsize=22,
             color=GREY, weight="600")
    fig.text(0.5, 0.88, "漲最強的 5 個區", ha="center", fontsize=34,
             color=DARK, weight="bold")

    y0 = 0.74
    row_h = 0.12
    for i, (_, r) in enumerate(top5.iterrows()):
        y = y0 - i * row_h
        fig.text(0.08, y, f"{i+1}", fontsize=42, color=PURPLE,
                 weight="bold", va="center")
        fig.text(0.18, y + 0.020, r["鄉鎮市區"], fontsize=24,
                 color=DARK, weight="bold", va="center")
        fig.text(0.18, y - 0.018, r["縣市"] + f" · 樣本 {int(r['n'])}",
                 fontsize=12, color=GREY, va="center")
        fig.text(0.92, y + 0.020, f"+{r['1年漲幅']:.1f}%",
                 fontsize=28, color=GREEN, weight="bold",
                 ha="right", va="center")
        fig.text(0.92, y - 0.018, f"{r['單價中位']:.1f} 萬/坪",
                 fontsize=12, color=GREY, ha="right", va="center")
        if i < 4:
            line = patches.Rectangle((0.06, y - row_h/2 + 0.012), 0.88, 0.001,
                                      transform=fig.transFigure, facecolor="#e8e8ed")
            fig.patches.append(line)

    fig.text(0.5, 0.05, "@cx468.com.tw 實價登錄觀察室", ha="center",
             fontsize=12, color=GREY)
    return _save(fig, "card_4_top_gain.png")


def card_5_shindian(deep: dict) -> Path:
    fig = _new_card("#FEF3C7")  # 暖黃背景代表 spotlight
    fig.text(0.5, 0.93, "本期 Spotlight", ha="center", fontsize=20,
             color="#92400E", weight="600")
    fig.text(0.5, 0.86, "新店單價降，是房市衰退嗎？", ha="center", fontsize=30,
             color=DARK, weight="bold")
    fig.text(0.5, 0.79, "不是。是成交品結構改變。", ha="center", fontsize=22,
             color="#92400E", weight="bold")

    s113, s115, delta = deep["113S1"], deep["115S1"], deep["delta"]

    # 三組數據對比
    rows = [
        ("成交量", f"{s113['n']} → {s115['n']}", f"{delta['n']:+d} 筆", RED),
        ("單價中位", f"{s113['median']} → {s115['median']} 萬/坪", f"{delta['median_pct']:+.1f}%", RED),
        ("屋齡中位", f"{s113['median_age']} → {s115['median_age']} 年",
         f"+{s115['median_age']-s113['median_age']:.1f} 年", "#92400E"),
    ]
    y0 = 0.62
    for i, (label, change, delta_str, color) in enumerate(rows):
        y = y0 - i * 0.13
        # background card
        rect = patches.FancyBboxPatch((0.08, y - 0.05), 0.84, 0.10,
                                      boxstyle="round,pad=0.02",
                                      facecolor="white", edgecolor="none",
                                      transform=fig.transFigure)
        fig.patches.append(rect)
        fig.text(0.12, y, label, fontsize=15, color=GREY, va="center")
        fig.text(0.50, y, change, fontsize=20, color=DARK, weight="bold", va="center")
        fig.text(0.88, y, delta_str, fontsize=18, color=color,
                 weight="bold", ha="right", va="center")

    fig.text(0.5, 0.16, "→ 113Q1 新成屋帶量、115Q1 新成屋移轉停止",
             ha="center", fontsize=14, color=DARK)
    fig.text(0.5, 0.12, "→ 成交品從「新屋為主」轉「老屋為主」",
             ha="center", fontsize=14, color=DARK)
    fig.text(0.5, 0.08, "→ 中位數下降反映結構變化、非市場衰退",
             ha="center", fontsize=14, color=DARK, weight="bold")

    fig.text(0.5, 0.03, "完整分析 → cx468.com.tw/lvr-observatory.html",
             ha="center", fontsize=11, color=GREY)
    return _save(fig, "card_5_shindian.png")


def card_6_cta() -> Path:
    fig = _new_card()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.add_patch(patches.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                                    facecolor=PURPLE, edgecolor="none"))
    ax.add_patch(patches.Rectangle((0, 0), 1, 0.55, transform=ax.transAxes,
                                    facecolor=BLUE, alpha=0.8, edgecolor="none"))

    fig.text(0.5, 0.78, "想看完整報告？", ha="center", fontsize=32,
             color="white", weight="bold")
    fig.text(0.5, 0.71, "75 行政區 · 4 縣市 · 4 時間窗", ha="center",
             fontsize=18, color=(1, 1, 1, 0.85))

    # 中央大按鈕區
    rect = patches.FancyBboxPatch((0.18, 0.42), 0.64, 0.18,
                                  boxstyle="round,pad=0.04",
                                  facecolor="white", edgecolor="none",
                                  transform=fig.transFigure)
    fig.patches.append(rect)
    fig.text(0.5, 0.55, "實價登錄觀察室", ha="center", fontsize=24,
             color=PURPLE, weight="bold")
    fig.text(0.5, 0.48, "cx468.com.tw/lvr-observatory.html",
             ha="center", fontsize=13, color=DARK)

    fig.text(0.5, 0.28, "想知道你的房子能借多少？", ha="center",
             fontsize=20, color="white", weight="600")
    fig.text(0.5, 0.20, "二胎可貸額度試算 · LINE 線上諮詢",
             ha="center", fontsize=16, color=(1, 1, 1, 0.85))

    fig.text(0.5, 0.08, "鋮馨租賃｜02-2249-0517", ha="center",
             fontsize=14, color=(1, 1, 1, 0.7))
    return _save(fig, "card_6_cta.png")


def main() -> None:
    df = pd.read_pickle(OUT_DIR / "clean_df.pkl")
    ranking_180 = pd.read_pickle(OUT_DIR / "ranking_w180.pkl")
    deep = pd.read_pickle(OUT_DIR / "shindian_deep.pkl")
    season_label = df["__season"].max().replace("S", "Q")
    generated_at = datetime.now().strftime("%Y-%m-%d")
    n_districts = len(ranking_180)

    print("→ 生成 6 張社群圖卡（1080×1350）：")
    jobs = [
        (card_1_hero, (generated_at, season_label, n_districts)),
        (card_2_yoy, (df,)),
        (card_3_city_trend, (df,)),
        (card_4_top_gain, (ranking_180,)),
        (card_5_shindian, (deep,)),
        (card_6_cta, ()),
    ]
    for fn, args in jobs:
        path = fn(*args)
        kb = path.stat().st_size / 1024
        print(f"  ✓ {path.name}（{kb:.0f} KB）")
    print(f"\n→ 全部存到 {CARD_DIR.relative_to(Path.cwd())}/")


if __name__ == "__main__":
    main()
