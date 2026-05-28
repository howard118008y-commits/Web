"""
偵測 YoY 突破 ±20% 的行政區，透過 LINE Messaging API 推送警示。

環境變數（需設成 GitHub Action secret）：
- LINE_CHANNEL_ACCESS_TOKEN  (LINE Developers Console → Messaging API channel)
- LINE_USER_ID               (你個人 LINE 的 User ID，透過 webhook event 抓)

若任一未設，僅 print 警示內容、不發推播（CI 不致命）。
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import List

import pandas as pd

OUT_DIR = Path(__file__).resolve().parent / "_cache"
THRESHOLD = 20.0  # ±20%
MIN_SAMPLE = 30   # 樣本太小不算
WINDOW_FOR_ALERT = 180


def format_message(gainers: List[dict], losers: List[dict]) -> str:
    lines = ["📊 實價登錄 YoY 異常警示", "─" * 22]
    if not gainers and not losers:
        lines.append("本週 75 區無區域 YoY 突破 ±20%（穩定）")
        return "\n".join(lines)

    lines.append(f"75 區中 {len(gainers) + len(losers)} 個區域突破 ±20%")
    lines.append("")
    if gainers:
        lines.append(f"▲ 漲幅 ({len(gainers)} 區)：")
        for r in gainers[:10]:
            lines.append(f"  {r['鄉鎮市區']}（{r['縣市']}） +{r['1年漲幅']:.1f}% (n={int(r['n'])})")
        if len(gainers) > 10:
            lines.append(f"  …另 {len(gainers)-10} 區")
        lines.append("")
    if losers:
        lines.append(f"▼ 跌幅 ({len(losers)} 區)：")
        for r in losers[:10]:
            lines.append(f"  {r['鄉鎮市區']}（{r['縣市']}） {r['1年漲幅']:.1f}% (n={int(r['n'])})")
        if len(losers) > 10:
            lines.append(f"  …另 {len(losers)-10} 區")
        lines.append("")
    lines.append("完整報告 → cx468.com.tw/lvr-observatory.html")
    return "\n".join(lines)


def push_line(text: str, token: str, user_id: str) -> bool:
    url = "https://api.line.me/v2/bot/message/push"
    body = json.dumps({
        "to": user_id,
        "messages": [{"type": "text", "text": text}]
    }).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"  ✓ LINE push 成功（HTTP {resp.status}）")
            return True
    except urllib.error.HTTPError as e:
        print(f"  ✗ LINE push 失敗（HTTP {e.code}）：{e.read().decode('utf-8', errors='ignore')[:200]}")
        return False
    except Exception as e:
        print(f"  ✗ LINE push 失敗：{e}")
        return False


def main() -> int:
    pkl = OUT_DIR / f"ranking_w{WINDOW_FOR_ALERT}.pkl"
    if not pkl.exists():
        print(f"✗ 找不到 {pkl.name}")
        return 1

    ranking = pd.read_pickle(pkl)
    # 篩有 1年漲幅 + 樣本 OK
    valid = ranking.dropna(subset=["1年漲幅"])
    valid = valid[valid["n"] >= MIN_SAMPLE]

    gainers = valid[valid["1年漲幅"] >= THRESHOLD].sort_values("1年漲幅", ascending=False)
    losers = valid[valid["1年漲幅"] <= -THRESHOLD].sort_values("1年漲幅")

    print(f"→ 檢測：YoY ≥ +{THRESHOLD}% → {len(gainers)} 區、YoY ≤ -{THRESHOLD}% → {len(losers)} 區")

    message = format_message(gainers.to_dict("records"), losers.to_dict("records"))
    print("\n----- 警示訊息 -----")
    print(message)
    print("--------------------\n")

    # 存一份 log
    log_path = OUT_DIR / "alerts_last.txt"
    log_path.write_text(message, encoding="utf-8")

    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "").strip()
    user_id = os.environ.get("LINE_USER_ID", "").strip()
    if not token or not user_id:
        print("⚠ LINE_CHANNEL_ACCESS_TOKEN 或 LINE_USER_ID 未設，跳過推播")
        return 0

    if not gainers.empty or not losers.empty:
        push_line(message, token, user_id)
    else:
        print("  → 無異常區，依設定不推播平靜訊息")

    return 0


if __name__ == "__main__":
    sys.exit(main())
