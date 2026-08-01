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

    # ⚠️ 「跨期追蹤 N 季」刻意不由本腳本更新。
    # 它指的是觀察室**趨勢圖**涵蓋的季數（make_charts.py 的 chart_city_trend，
    # 目前 113Q1→115Q1 共 9 季），資料源是完整歷史；而 lvr-data/ 下的明細 CSV
    # 只有近 180 天（約 3 季）。用明細算會把 9 季錯寫成 3 季——維度不同不可混用。
    # 這欄要改，得跟 make_charts.py 的趨勢圖季數一起動。

    if not districts or not cities or not total:
        print("⚠️  資料不足，跳過更新（不寫入假數字）")
        return 0

    # 筆數顯示：>= 10000 用「N.N 萬」，否則原數字加千分位
    total_disp = f"{total/10000:.1f} 萬" if total >= 10000 else f"{total:,}"

    html = open(TOOLS, encoding="utf-8").read()
    orig = html
    html = re.sub(r'(<div class="bt-big">)\d+(<em>行政區</em></div>)',
                  rf'\g<1>{districts}\g<2>', html)
    html = re.sub(r'(<div class="bt-n">)[^<]*(</div><div class="bt-nl">筆實價資料</div>)',
                  rf'\g<1>{total_disp}\g<2>', html)
    html = re.sub(r'(<div class="bt-n">)[^<]*(</div><div class="bt-nl">縣市</div>)',
                  rf'\g<1>{cities}\g<2>', html)
    if html == orig:
        print(f"✓ 數字已是最新（{districts} 區 / {total_disp} 筆 / {cities} 縣市；季數不由本腳本管）")
        return 0

    open(TOOLS, "w", encoding="utf-8").write(html)
    print(f"✅ 已更新 tools.html：{districts} 行政區 / {total_disp} 筆 / {cities} 縣市（季數維持不動）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
