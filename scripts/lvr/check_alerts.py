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
THRESHOLD = 30.0  # 只在 YoY 突破 ±30%（重大變動）才推；省 LINE quota
MIN_SAMPLE = 30
WINDOW_FOR_ALERT = 180


def load_previous_state() -> dict:
    if not STATE_FILE.exists():
        return {"alerts": []}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"alerts": []}


def save_state(current_alerts: List[dict], push_ok: bool = True) -> None:
    STATE_FILE.write_text(
        json.dumps({
            "last_run": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "alerts": current_alerts,
            "last_push_ok": push_ok,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def town_key(r: dict) -> str:
    """區域唯一識別。"""
    return f"{r['縣市']}/{r['鄉鎮市區']}"


def format_diff_message(new_in: List[dict], recovered: List[dict],
                         persistent_count: int) -> str:
    """精簡訊息：只列 TOP 1 漲 + TOP 1 跌 + 總筆數，省 LINE quota。"""
    if not new_in and not recovered:
        return f"📊 LVR 警示｜本期無 ±{THRESHOLD:.0f}% 突破變化"

    lines = [f"📊 LVR ±{THRESHOLD:.0f}% 警示｜新 {len(new_in)} / 退出 {len(recovered)}"]

    if new_in:
        gainers = [r for r in new_in if r["1年漲幅"] > 0]
        losers = [r for r in new_in if r["1年漲幅"] < 0]
        if gainers:
            top = max(gainers, key=lambda r: r["1年漲幅"])
            lines.append(f"▲ 漲最強：{top['鄉鎮市區']}({top['縣市']}) +{top['1年漲幅']:.1f}%")
        if losers:
            bot = min(losers, key=lambda r: r["1年漲幅"])
            lines.append(f"▼ 跌最深：{bot['鄉鎮市區']}({bot['縣市']}) {bot['1年漲幅']:.1f}%")
    if recovered:
        lines.append(f"✓ 已回穩：{len(recovered)} 區")
    lines.append("→ cx468.com.tw/lvr-observatory.html")
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

    (OUT_DIR / "alerts_last.txt").write_text(msg, encoding="utf-8")

    state_records = [{
        "縣市": r["縣市"], "鄉鎮市區": r["鄉鎮市區"],
        "1年漲幅": float(r["1年漲幅"]), "n": int(r["n"]),
    } for r in current_records]

    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "").strip()
    user_id = os.environ.get("LINE_USER_ID", "").strip()
    if not token or not user_id:
        print("⚠ LINE 環境變數未設，跳過推播")
        save_state(state_records, push_ok=True)  # 不算失敗、避免下次強推
        return 0

    # 強制重推條件：上次 push 失敗 + 目前仍有警示 → 不管 diff，再試一次
    # 舊 state（沒此欄位）視為 False = 「不確定上次有沒有成功」→ 觸發重推保護
    last_push_ok = prev.get("last_push_ok", False)
    force_retry = current_records and not last_push_ok
    if force_retry:
        print(f"  ⚠ 偵測上次 push 失敗、強制重推 {len(current_records)} 筆當前警示")

    if new_in or recovered or force_retry:
        ok = push_line(msg, token, user_id)
        save_state(state_records, push_ok=ok)
        if not ok:
            print("  ⚠ 本次 push 又失敗，下次跑會再試")
    else:
        print("  → 無狀態變化，依設定不推播")
        save_state(state_records, push_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
