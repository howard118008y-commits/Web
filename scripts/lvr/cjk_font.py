"""
cjk_font.py — 讓 matplotlib 在任何環境都能顯示繁體中文，不出現 □□□ 豆腐框。

為什麼需要這支：
  在 GitHub Actions (Ubuntu) 上，就算已 `apt-get install fonts-noto-cjk`，
  直接寫 plt.rcParams["font.sans-serif"] = ["Noto Sans CJK TC", ...] 仍會失敗。
  因為 matplotlib 掃描 NotoSansCJK-Regular.ttc 時只註冊「第 0 個 face」，
  其 family 名是 "Noto Sans CJK JP"（不是 "...TC"）→ 名稱比對不到
  → 退回 DejaVu Sans → 中文全變豆腐框。

解法：直接用「字型檔路徑」把字型註冊進來，再讀回它真正的 family 名來指定，
不再靠猜名字比對。
  - Ubuntu/CI：抓 fonts-noto-cjk 的 .ttc（JP face 仍含全部 CJK 漢字，繁中可正常顯示）
  - macOS 本機：找不到 Noto 路徑 → 回退到用名稱指定 "PingFang TC"（本機原本就 OK）
"""
from __future__ import annotations

import glob
import os

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

# 只列 Linux/CI 的 Noto 路徑；macOS 走下方名稱回退，維持原本行為。
_FONT_PATHS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
]
_FONT_GLOBS = [
    "/usr/share/fonts/**/NotoSansCJK*.ttc",
    "/usr/share/fonts/**/NotoSansCJK*.otf",
    "/usr/share/fonts/**/NotoSansTC*.otf",
]

# macOS／一般情況的名稱回退清單（最後一定保留 DejaVu Sans 當英數字保底）
_NAME_FALLBACK = [
    "PingFang TC", "Heiti TC", "Noto Sans CJK TC", "Noto Sans TC", "DejaVu Sans",
]


def _find_font_file() -> str | None:
    for p in _FONT_PATHS:
        if os.path.exists(p):
            return p
    for pattern in _FONT_GLOBS:
        hits = sorted(glob.glob(pattern, recursive=True))
        if hits:
            return hits[0]
    return None


def setup_cjk() -> str:
    """設定 matplotlib 中文字型，回傳實際採用的字型名稱。各產圖腳本開頭呼叫一次即可。"""
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["font.family"] = "sans-serif"

    path = _find_font_file()
    if path:
        try:
            fm.fontManager.addfont(path)
            real_name = fm.FontProperties(fname=path).get_name()
            plt.rcParams["font.sans-serif"] = [real_name, *_NAME_FALLBACK]
            print(f"[cjk_font] 使用字型：{real_name}（{path}）")
            return real_name
        except Exception as e:  # noqa: BLE001 — 任何讀檔/註冊失敗都退回名稱清單
            print(f"[cjk_font] 註冊 {path} 失敗，改用名稱回退：{e}")

    plt.rcParams["font.sans-serif"] = _NAME_FALLBACK
    print("[cjk_font] 找不到 Noto 字型檔，使用名稱回退清單（macOS 本機可用）")
    return _NAME_FALLBACK[0]
