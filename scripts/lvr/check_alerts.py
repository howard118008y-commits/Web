"""
偵測 YoY 突破 ±20% 的行政區，state-aware：只通知「本期新進入 / 新恢復」的區。
透過 LINE Messaging API 推送。

State 檔：_cache/alert_state.json （前次警示的區清單）
- 跨 run 透過 actions/cache 持久化

環境變數：
- LINE_CHANNEL_ACCESS_TOKEN  (LINE Developers Console)
- LINE_USER_ID               (你個人 LINE User ID)

未設則僅 print log。
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import List, Set

import pandas as pd

OUT_DIR = Path(__file__).resolve().parent / "_cache"
STATE_FILE = OUT_DIR / "alert_state.json"
THRESHOLD = 20.0
MIN_SAMPLE = 30
WINDOW_FOR_ALERT = 180


def load_previous_state() -> dict:
    if not STATE_FILE.exists():
        return {"alerts": []}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"alerts": []}


def save_state(current_alerts: List[dict]) -> None:
    STATE_FILE.write_text(
        json.dumps({
            "last_run": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "alerts": current_alerts,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def town_key(r: dict) -> str:
    """區域唯一識別。"""
    return f"{r['縣市']}/{r['鄉鎮市區']}"


def format_diff_message(new_in: List[dict], recovered: List[dict],
                         persistent_count: int) -> str:
    lines = ["📊 實價登錄 YoY 警示（狀態變化）", "─" * 22]
    if not new_in and not recovered:
        lines.append(f"本期無新警示變化（{persistent_count} 區持續突破 ±{THRESHOLD}%）")
        return "\n".join(lines)

    if new_in:
        lines.append(f"⚠ 新進入警示 ({len(new_in)} 區)：")
        for r in new_in[:15]:
            arrow = "▲" if r["1年漲幅"] > 0 else "▼"
            lines.append(f"  {arrow} {r['鄉鎮市區']}（{r['縣市']}） {r['1年漲幅']:+.1f}% (n={int(r['n'])})")
        if len(new_in) > 15:
            lines.append(f"  …另 {len(new_in)-15} 區")
        lines.append("")
    if recovered:
        lines.append(f"✓ 回到正常區間 ({len(recovered)} 區)：")
        for r in recovered[:15]:
            lines.append(f"  {r['鄉鎮市區']}（{r['縣市']}） 已退出 ±{THRESHOLD}% 區間")
        if len(recovered) > 15:
            lines.append(f"  …另 {len(recovered)-15} 區")
        lines.append("")
    if persistent_count:
        lines.append(f"（另有 {persistent_count} 區持續突破中，本次不重複通知）")
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
        msg = e.read().decode("utf-8", errors="ignore")[:200]
        print(f"  ✗ LINE push 失敗（HTTP {e.code}）：{msg}")
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
    valid = ranking.dropna(subset=["1年漲幅"])
    valid = valid[valid["n"] >= MIN_SAMPLE]

    # 當前警示集合（含原始 row data）
    current_alerts = valid[(valid["1年漲幅"] >= THRESHOLD) | (valid["1年漲幅"] <= -THRESHOLD)]
    current_records = current_alerts.to_dict("records")
    current_keys: Set[str] = {town_key(r) for r in current_records}

    # 讀前次 state
    prev = load_previous_state()
    prev_keys: Set[str] = {town_key(r) for r in prev.get("alerts", [])}

    # Diff
    new_in_keys = current_keys - prev_keys
    recovered_keys = prev_keys - current_keys
    persistent_keys = current_keys & prev_keys

    new_in = [r for r in current_records if town_key(r) in new_in_keys]
    recovered = [r for r in prev.get("alerts", []) if town_key(r) in recovered_keys]
    new_in.sort(key=lambda r: abs(r.get("1年漲幅", 0)), reverse=True)

    print(f"→ 當前警示 {len(current_alerts)} 區；前次 {len(prev_keys)} 區")
    print(f"  新進入 {len(new_in_keys)}、回到正常 {len(recovered_keys)}、持續 {len(persistent_keys)}")

    msg = format_diff_message(new_in, recovered, len(persistent_keys))
    print("\n----- 訊息 -----")
    print(msg)
    print("----------------\n")

    # 寫 log（state 留到 push 完成後再更新）
    (OUT_DIR / "alerts_last.txt").write_text(msg, encoding="utf-8")

    state_records = [{
        "縣市": r["縣市"], "鄉鎮市區": r["鄉鎮市區"],
        "1年漲幅": float(r["1年漲幅"]), "n": int(r["n"]),
    } for r in current_records]

    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "").strip()
    user_id = os.environ.get("LINE_USER_ID", "").strip()
    if not token or not user_id:
        print("⚠ LINE 環境變數未設，跳過推播")
        save_state(state_records)  # 沒設 LINE 就直接記 state、避免每次都當「新」
        return 0

    if new_in or recovered:
        ok = push_line(msg, token, user_id)
        if ok:
            save_state(state_records)
        else:
            print("  ⚠ push 失敗，state 不更新（下次跑會再嘗試）")
    else:
        print("  → 無狀態變化，依設定不推播")
        save_state(state_records)  # 沒變化也要保存 state（保持最新）
    return 0


if __name__ == "__main__":
    sys.exit(main())
