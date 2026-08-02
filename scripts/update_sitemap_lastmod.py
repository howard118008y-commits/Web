#!/usr/bin/env python3
"""把 sitemap.xml 的 <lastmod> 同步成各 HTML 檔的最後 commit 日期。

為什麼需要：`indexing_cron.py` 是靠 sitemap 的 lastmod 挑「近 N 天更動頁」送 Google
Indexing API。lastmod 寫死不動 → 改了頁面也不會被送出、主力頁一路不重爬
（2026-08-02 實測：全站 lastmod 停在 2026-06-29，當天改的 11 頁全部漏送）。

用法：
    python3 scripts/update_sitemap_lastmod.py           # 就地更新
    python3 scripts/update_sitemap_lastmod.py --check   # 只報告差異，不寫檔（CI 用）

規則：
- 以 `git log -1 --format=%cs <file>` 的 committer date 為準（未追蹤檔跳過）。
- 已有 <lastmod> 就改值，沒有就補在 </loc> 之後。
- 只動 lastmod，不碰 loc / changefreq / priority 的順序與縮排。
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITEMAP = ROOT / "sitemap.xml"
BASE = "https://cx468.com.tw/"


def git_date(rel_path: Path) -> str | None:
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(rel_path)],
                             cwd=ROOT, capture_output=True, text=True, check=True)
        return out.stdout.strip() or None
    except subprocess.CalledProcessError:
        return None


def main() -> int:
    check_only = "--check" in sys.argv
    xml = SITEMAP.read_text(encoding="utf-8")
    changed, missing_file, added = [], [], 0

    def fix(block: str) -> str:
        nonlocal added
        loc_m = re.search(r"<loc>\s*(.*?)\s*</loc>", block, re.S)
        if not loc_m:
            return block
        url = loc_m.group(1)
        rel = url.replace(BASE, "").split("?")[0] or "index.html"
        f = ROOT / rel
        if not f.is_file():
            missing_file.append(rel)
            return block
        d = git_date(Path(rel))
        if not d:
            return block
        lm = re.search(r"<lastmod>\s*(.*?)\s*</lastmod>", block)
        if lm:
            if lm.group(1) == d:
                return block
            changed.append((rel, lm.group(1), d))
            return block[:lm.start()] + f"<lastmod>{d}</lastmod>" + block[lm.end():]
        added += 1
        changed.append((rel, "(無)", d))
        return block.replace(loc_m.group(0), loc_m.group(0) + f"\n    <lastmod>{d}</lastmod>", 1)

    new_xml = re.sub(r"<url>.*?</url>", lambda m: fix(m.group(0)), xml, flags=re.S)

    for rel, old, new in changed:
        print(f"  {old:>12} → {new}  {rel}")
    if missing_file:
        print(f"  ⚠️ sitemap 有 {len(missing_file)} 條找不到對應檔案：{', '.join(missing_file[:6])}")
    print(f"{len(changed)} 條 lastmod 需更新（其中 {added} 條原本沒有 lastmod）")

    if check_only:
        return 1 if changed else 0
    if changed:
        SITEMAP.write_text(new_xml, encoding="utf-8")
        print("已寫入 sitemap.xml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
