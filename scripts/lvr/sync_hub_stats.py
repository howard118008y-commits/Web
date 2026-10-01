#!/usr/bin/env python3
"""同步 tools.html 的「實價資料中心」統計數字到真實資料規模。

背景：這四個數字（行政區/資料筆數/季數/縣市）原本寫死在 HTML，資料長大後就失真
（2026-08-01 查到寫 75 區、實際 81 區；寫 290k+ 筆、全站查無來源）。
比照「顯示層時間戳不寫死」的原則，改由本腳本從 lvr-data/ 實算後回寫。
由 .github/workflows/lvr-weekly.yml 在每次資料更新後自動執行。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "lvr-data")
TOOLS = os.path.join(ROOT, "tools.html")


def load(name):
    p = os.path.join(DATA, name)
    if not os.path.isfile(p):
        return []
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    return d if isinstance(d, list) else []


def main():
    # 行政區數與縣市數取最大母體（w365 買賣）
    sale365 = load("排名_w365.json")
    sale180 = load("排名_w180.json")
    presale = load("presale_ranking_w180.json")
    rental = load("rental_ranking_w180.json")

    districts = len({x.get("鄉鎮市區") for x in sale365} |
                    {x.get("鄉鎮市區") for x in sale180} |
                    {x.get("鄉鎮市區") for x in presale} |
                    {x.get("鄉鎮市區") for x in rental}) or 0
    cities = len({x.get("縣市") for x in sale365 if x.get("縣市")}) or 0

    # 分析中的交易筆數＝買賣(365天) + 預售(180天) + 租屋(180天)
    total = (sum(x.get("n", 0) for x in sale365)
             + sum(x.get("n", 0) for x in presale)
             + sum(x.get("n", 0) for x in rental))

    # 「跨期追蹤 N 季」＝觀察室趨勢圖涵蓋的季數，來源是 lvr-data/city_trend.json 的 seasons
    # （make_charts.py 產出，完整歷史）。⚠️ 不可用明細 CSV 算（只有近 180 天≈3 季，維度不同）。
    trend_path = os.path.join(DATA, "city_trend.json")
    seasons = 0
    if os.path.isfile(trend_path):
        with open(trend_path, encoding="utf-8") as f:
            seasons = len(json.load(f).get("seasons", []))

    if not districts or not cities or not total or not seasons:
        print("⚠️  資料不足，跳過更新（不寫入假數字）")
        return 0

    # 筆數顯示：>= 10000 用「N.N 萬」，否則原數字加千分位
    total_disp = f"{total/10000:.1f} 萬" if total >= 10000 else f"{total:,}"

    html = open(TOOLS, encoding="utf-8").read()
    orig = html
    # tools.html 現行結構：<div class="bt-def-num">數字</div><div class="bt-def-label">標籤</div>
    def sub(label, value):
        nonlocal html
        html, n = re.subn(r'(<div class="bt-def-num">)[^<]*(</div><div class="bt-def-label">' + label + r'</div>)',
                          lambda m: m.group(1) + value + m.group(2), html)
        return n

    hits = (sub("行政區", str(districts)) + sub("筆實價資料", total_disp)
            + sub("跨期追蹤", f"{seasons} 季") + sub("縣市", str(cities)))
    print(f"regex 命中 {hits}/4")
    if hits != 4:
        print("✗ tools.html 結構變了，regex 對不上（應命中 4 欄）")
        return 1
    if html == orig:
        print(f"✓ 數字已是最新（{districts} 區 / {total_disp} 筆 / {cities} 縣市；{seasons} 季）")
        return 0

    open(TOOLS, "w", encoding="utf-8").write(html)
    print(f"✅ 已更新 tools.html：{districts} 行政區 / {total_disp} 筆 / {cities} 縣市 / {seasons} 季")
    return 0


if __name__ == "__main__":
    sys.exit(main())
