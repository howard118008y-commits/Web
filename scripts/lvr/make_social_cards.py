"""
產出 6 張 IG/FB 規格圖卡（1080×1350，4:5）給社群週報用。
存到 CX468/lvr-social-cards/。

card_1_hero.png        — 標題卡
card_2_yoy.png          — 5 精選 + 雙北 YoY 年增率
card_3_city_trend.png   — 4 縣市 N 季均價趨勢（N 依資料實際季數）
card_4_top_gain.png     — TOP 5 漲幅最強區
card_5_shindian.png     — 新店深度解析洞察
card_6_cta.png          — CTA 卡 (連到觀察室)
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd

from cjk_font import setup_cjk

OUT_DIR = Path(__file__).resolve().parent / "_cache"
CARD_DIR = Path(os.environ.get("SOCIAL_CARD_DIR") or OUT_DIR / "social-cards")  # 預設路徑不變；env 供本機試跑導向別處
CARD_DIR.mkdir(parents=True, exist_ok=True)

# 1080×1350 @ 100 dpi → figsize=(10.8, 13.5)
FIGSIZE = (10.8, 13.5)
# 米米配色（2026-09-28 老闆定；2026-10-01 圖卡同步）：橘底配墨字、橘/咖啡金不當小字
INK = "#3C1E0E"      # 墨：文字與深色底
CREAM = "#FCF6EA"    # 米白：主底
ORANGE = "#F5621C"   # 主色：色塊／線條／大字（不配白字）
DEEP = "#B8440C"     # 深橘：橘色小字改用
GOLD = "#C8945A"     # 咖啡金：只當線條／色塊點綴
PURPLE = ORANGE      # 變數名沿用（原品牌紅），現指主色
DARK = INK
GREY = "#6B4A35"     # 次要文字（米白底對比 >7）
LIGHT_BG = "#F6EBD6"
RULE = "#E8DCC4"

setup_cjk()  # 設定中文字型（含 CI/Ubuntu 的 Noto 路徑註冊）— 避免圖卡中文變 □□□
plt.rcParams["savefig.dpi"] = 100
plt.rcParams["savefig.bbox"] = "tight"
plt.rcParams["savefig.pad_inches"] = 0


def _new_card(bg=CREAM):
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
             color=(1, 1, 1, 0.85) if fig.get_facecolor() != matplotlib.colors.to_rgba(CREAM) else GREY,
             weight="bold", style="italic")
    fig.text(0.5, top - 0.04, title, ha="center", fontsize=36,
             color="white" if fig.get_facecolor() != matplotlib.colors.to_rgba(CREAM) else DARK,
             weight="bold")


def card_1_hero(generated_at: str, season_label: str, n_districts: int) -> Path:
    fig = _new_card()
    # 墨底＋橘色帶（橘不配白字，文字一律米白）
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.add_patch(patches.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                                    facecolor=INK, edgecolor="none"))
    ax.add_patch(patches.Rectangle((0, 0.52), 1, 0.012, transform=ax.transAxes,
                                    facecolor=ORANGE, edgecolor="none"))

    # Text
    fig.text(0.5, 0.70, "實價登錄觀察", ha="center", fontsize=64,
             color=CREAM, weight="bold")
    fig.text(0.5, 0.62, season_label + " 報告", ha="center", fontsize=36,
             color=CREAM, weight="600")

    fig.text(0.5, 0.40, "四縣市 · " + str(n_districts) + " 行政區",
             ha="center", fontsize=24, color=CREAM)
    fig.text(0.5, 0.34, "台北 · 新北 · 台中 · 桃園",
             ha="center", fontsize=18, color=GOLD)

    fig.text(0.5, 0.16, "鋮馨租賃｜不動產資料觀察", ha="center", fontsize=18,
             color=CREAM, weight="600")
    fig.text(0.5, 0.10, generated_at, ha="center", fontsize=14,
             color=GOLD)

    return _save(fig, "card_1_hero.png")


def card_2_yoy(df: pd.DataFrame) -> Path:
    FOCUS = ["中和區", "永和區", "板橋區", "新店區", "土城區"]
    COLOR_MAP = {"中和區": ORANGE, "永和區": INK, "板橋區": GOLD,
                 "新店區": DEEP, "土城區": "#8A5A2B",
                 "台北市\n（平均）": "#6B4A35", "新北市\n（平均）": "#E58A55"}
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
    bars = ax.bar(labels, values, color=colors, edgecolor=CREAM, linewidth=3)
    for bar, val in zip(bars, values):
        y = val + 1.0 if val >= 0 else val - 1.8
        ax.text(bar.get_x() + bar.get_width() / 2, y,
                f"{val:+.1f}%", ha="center", fontsize=14, weight="bold",
                color=DEEP if val >= 0 else INK)
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
    CITY_COLOR = {"台北市": INK, "新北市": ORANGE,
                  "台中市": GOLD, "桃園市": DEEP}
    pivot = (df.groupby(["__season", "縣市"])["單價_萬每坪"]
             .median().unstack("縣市").sort_index())

    fig = _new_card()
    n_seasons = pivot.index.nunique()
    first_q, last_q = (str(pivot.index[0]).replace("S", "Q"), str(pivot.index[-1]).replace("S", "Q"))
    fig.text(0.5, 0.94, f"{n_seasons} 季均價 跨縣市趨勢", ha="center", fontsize=22,
             color=GREY, weight="600")
    fig.text(0.5, 0.88, f"四縣市 {first_q} → {last_q}", ha="center", fontsize=34,
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
        fig.text(0.08, y, f"{i+1}", fontsize=42, color=DEEP,
                 weight="bold", va="center")
        fig.text(0.18, y + 0.020, r["鄉鎮市區"], fontsize=24,
                 color=DARK, weight="bold", va="center")
        fig.text(0.18, y - 0.018, r["縣市"] + f" · 樣本 {int(r['n'])}",
                 fontsize=12, color=GREY, va="center")
        fig.text(0.92, y + 0.020, f"+{r['1年漲幅']:.1f}%",
                 fontsize=28, color=DEEP, weight="bold",
                 ha="right", va="center")
        fig.text(0.92, y - 0.018, f"{r['單價中位']:.1f} 萬/坪",
                 fontsize=12, color=GREY, ha="right", va="center")
        if i < 4:
            line = patches.Rectangle((0.06, y - row_h/2 + 0.012), 0.88, 0.001,
                                      transform=fig.transFigure, facecolor=RULE)
            fig.patches.append(line)

    fig.text(0.5, 0.05, "@cx468.com.tw 實價登錄觀察室", ha="center",
             fontsize=12, color=GREY)
    return _save(fig, "card_4_top_gain.png")


def card_5_shindian(deep: dict) -> Path:
    # 起訖季與行政區取自資料（deep 內除 delta／district 外的兩個季別 key，字串序＝時間序）
    q0, q1 = sorted(k for k in deep if k not in ("delta", "district"))
    s113, s115, delta = deep[q0], deep[q1], deep["delta"]
    town = deep.get("district", "新店區")
    town_short = town[:-1] if town.endswith("區") else town
    q0l, q1l = q0.replace("S", "Q"), q1.replace("S", "Q")
    fig = _new_card(LIGHT_BG)  # 深一階米色代表 spotlight
    fig.text(0.5, 0.93, "本期 Spotlight", ha="center", fontsize=20,
             color=DEEP, weight="600")
    fig.text(0.5, 0.86, f"{town_short}單價降，是房市衰退嗎？", ha="center", fontsize=30,
             color=DARK, weight="bold")
    fig.text(0.5, 0.79, "不是。是成交品結構改變。", ha="center", fontsize=22,
             color=DEEP, weight="bold")

    # 三組數據對比
    rows = [
        ("成交量", f"{s113['n']} → {s115['n']}", f"{delta['n']:+d} 筆", DEEP),
        ("單價中位", f"{s113['median']} → {s115['median']} 萬/坪", f"{delta['median_pct']:+.1f}%", DEEP),
        ("屋齡中位", f"{s113['median_age']} → {s115['median_age']} 年",
         f"+{s115['median_age']-s113['median_age']:.1f} 年", DEEP),
    ]
    y0 = 0.62
    for i, (label, change, delta_str, color) in enumerate(rows):
        y = y0 - i * 0.13
        # background card
        rect = patches.FancyBboxPatch((0.08, y - 0.05), 0.84, 0.10,
                                      boxstyle="round,pad=0.02",
                                      facecolor=CREAM, edgecolor="none",
                                      transform=fig.transFigure)
        fig.patches.append(rect)
        fig.text(0.12, y, label, fontsize=15, color=GREY, va="center")
        fig.text(0.50, y, change, fontsize=20, color=DARK, weight="bold", va="center")
        fig.text(0.88, y, delta_str, fontsize=18, color=color,
                 weight="bold", ha="right", va="center")

    fig.text(0.5, 0.16, f"→ {q0l} 新成屋帶量、{q1l} 新成屋移轉停止",
             ha="center", fontsize=14, color=DARK)
    fig.text(0.5, 0.12, "→ 成交品從「新屋為主」轉「老屋為主」",
             ha="center", fontsize=14, color=DARK)
    fig.text(0.5, 0.08, "→ 中位數下降反映結構變化、非市場衰退",
             ha="center", fontsize=14, color=DARK, weight="bold")

    fig.text(0.5, 0.03, "完整分析 → cx468.com.tw/lvr-observatory.html",
             ha="center", fontsize=11, color=GREY)
    return _save(fig, "card_5_shindian.png")


def card_6_cta(n_districts: int) -> Path:
    fig = _new_card()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.add_patch(patches.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                                    facecolor=INK, edgecolor="none"))

    fig.text(0.5, 0.78, "想看完整報告？", ha="center", fontsize=32,
             color=CREAM, weight="bold")
    fig.text(0.5, 0.71, f"{n_districts} 行政區 · 4 縣市 · 4 時間窗", ha="center",
             fontsize=18, color=CREAM)

    # 中央大按鈕區
    rect = patches.FancyBboxPatch((0.18, 0.42), 0.64, 0.18,
                                  boxstyle="round,pad=0.04",
                                  facecolor=CREAM, edgecolor="none",
                                  transform=fig.transFigure)
    fig.patches.append(rect)
    fig.text(0.5, 0.55, "實價登錄觀察室", ha="center", fontsize=24,
             color=INK, weight="bold")
    fig.text(0.5, 0.48, "cx468.com.tw/lvr-observatory.html",
             ha="center", fontsize=13, color=INK)

    fig.text(0.5, 0.28, "想知道你的房子能借多少？", ha="center",
             fontsize=20, color=CREAM, weight="600")
    fig.text(0.5, 0.20, "二胎可貸額度試算 · LINE 線上諮詢",
             ha="center", fontsize=16, color=CREAM)

    fig.text(0.5, 0.08, "鋮馨租賃｜02-2249-0517", ha="center",
             fontsize=14, color=GOLD)
    return _save(fig, "card_6_cta.png")


def main() -> None:
    df = pd.read_pickle(OUT_DIR / "clean_df.pkl")
    ranking_180 = pd.read_pickle(OUT_DIR / "ranking_w180.pkl")
    deep = pd.read_pickle(OUT_DIR / "shindian_deep.pkl")
    season_label = df["__season"].max().replace("S", "Q")
    generated_at = datetime.now().strftime("%Y-%m-%d")
    # 行政區數＝買賣 180／365 天＋預售＋租屋四份排名的聯集（與 tools.html 同口徑）；缺檔就略過
    towns = set(ranking_180["鄉鎮市區"])
    for name in ("ranking_w365.pkl", "presale_ranking_w180.pkl", "rental_ranking_w180.pkl"):
        f = OUT_DIR / name
        if f.exists():
            towns |= set(pd.read_pickle(f)["鄉鎮市區"])
    n_districts = len(towns)

    print("→ 生成 6 張社群圖卡（1080×1350）：")
    jobs = [
        (card_1_hero, (generated_at, season_label, n_districts)),
        (card_2_yoy, (df,)),
        (card_3_city_trend, (df,)),
        (card_4_top_gain, (ranking_180,)),
        (card_5_shindian, (deep,)),
        (card_6_cta, (n_districts,)),
    ]
    for fn, args in jobs:
        path = fn(*args)
        kb = path.stat().st_size / 1024
        print(f"  ✓ {path.name}（{kb:.0f} KB）")
    print(f"\n→ 全部存到 {CARD_DIR}/")


if __name__ == "__main__":
    main()
