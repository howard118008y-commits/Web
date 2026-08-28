#!/usr/bin/env python3
"""掃全站 HTML，產出 site-index.json 給官網 AI 助理「小鋮」當網站內容索引。

為什麼需要：小鋮的 system prompt 原本把服務寫死成「三大服務」，2026-08-24 開的
公司財務健檢沒進去，訪客問企業健檢會得到「沒有這個服務」（2026-08-29 老闆實測踩到）。
寫死的清單每加一頁就會再過期一次，所以改成：本檔每週掃站產出索引，小鋮啟動時抓
線上這份 JSON，網站有新頁面就自動知道。

用法：
    python3 scripts/build_site_index.py            # 就地產出 site-index.json
    python3 scripts/build_site_index.py --check    # 只報告差異、不寫檔（CI 用）

規則：
- 只收「訪客該被導去」的頁：排除片段檔（nav/footer/chat-widget…）、表單片段、
  廣告落地頁（lp-*，只給付費流量看，不該由小鋮主動推）、開發用暫存頁。
- noindex 但真實存在的服務頁（corporate-checkup、apply）要收——那是刻意不進
  自然搜尋，不是不存在。
- 標題與描述直接取頁面 <title> / meta description：已上線＝已過媽祖，不另生新文案。
"""
import json
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site-index.json"
BASE = "https://cx468.com.tw/"

# 片段檔與非導流頁：被 include.js 注入的組件、表單片段、開發暫存頁
EXCLUDE_EXACT = {
    "nav.html", "nav-tool.html", "footer.html", "trust-block.html",
    "chat-widget.html", "anti-fraud-modal.html", "line-qr.html",
    "lead-form.html", "lead-form-neutral.html", "lead-form-nofree.html",
    "cx_radar_v4_demo.html",
}
EXCLUDE_PREFIX = ("lp-", "cx_batch")

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S | re.I)
DESC_RE = re.compile(
    r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', re.S | re.I)

# 檔名前綴 → 分類，讓小鋮知道該推服務頁還是知識文章
CATEGORIES = [
    ("article-", "知識文章"),
    ("area-", "在地服務"),
    ("faq", "常見問題"),
]


def clean(raw: str) -> str:
    return re.sub(r"\s+", " ", unescape(raw)).strip()


def category(name: str, title: str) -> str:
    for prefix, label in CATEGORIES:
        if name.startswith(prefix):
            return label
    if "計算" in title or "calculator" in name:
        return "試算工具"
    if re.match(r"^(zhonghe|yonghe|banqiao|tucheng|sanchong|xindian|xinbei)-", name):
        return "在地服務"
    return "服務與說明"


def collect() -> list[dict]:
    pages = []
    for path in sorted(ROOT.glob("*.html")):
        name = path.name
        if name in EXCLUDE_EXACT or name.startswith(EXCLUDE_PREFIX):
            continue
        html = path.read_text(encoding="utf-8", errors="ignore")
        t = TITLE_RE.search(html)
        d = DESC_RE.search(html)
        if not t:
            continue
        title = clean(t.group(1))
        pages.append({
            "url": BASE + name,
            "title": title,
            "desc": clean(d.group(1)) if d else "",
            "category": category(name, title),
        })
    return pages


def main() -> int:
    pages = collect()
    payload = {"site": BASE, "count": len(pages), "pages": pages}
    text = json.dumps(payload, ensure_ascii=False, indent=1) + "\n"

    old = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    if "--check" in sys.argv:
        if text == old:
            print(f"✓ site-index.json 已是最新（{len(pages)} 頁）")
            return 0
        print(f"✗ site-index.json 過期，需重跑（現有 vs 掃得 {len(pages)} 頁）")
        return 1

    OUT.write_text(text, encoding="utf-8")
    print(f"✓ 產出 site-index.json：{len(pages)} 頁")
    for label in sorted({p["category"] for p in pages}):
        n = sum(1 for p in pages if p["category"] == label)
        print(f"   {label}：{n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
