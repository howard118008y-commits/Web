#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""同步全站 JSON-LD dateModified 到 git 最後實質 commit 日。

定例（memory：顯示層時間戳不寫死）：dateModified 必須綁資料源＝git 歷史。
- 只改 <script type="application/ld+json"> 區塊內的 "dateModified" 字串值；
  datePublished 與可見文字一律不碰。
- 「實質 commit」＝排除訊息含 [datemod-sync] 的同步 commit（本腳本自己的
  commit 用該標記，避免修日期→commit→git 日期變今天→下次又要修的死循環）。
- 自動更新頁（radar-index 等由 workflow 天天 commit 的頁）git 日期天天變，
  同步到最新屬正常行為。
- 跑完輸出報告到 /tmp/datemod_report.txt（改了幾頁、各頁新舊值）。

用法：python3 scripts/update_schema_datemod.py [--dry-run]
"""
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = "/tmp/datemod_report.txt"
SYNC_MARKER = "datemod-sync"  # commit 訊息含 [datemod-sync] 者不算實質 commit

LDJSON_RE = re.compile(
    r'(<script[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
    re.I | re.S,
)
DATEMOD_RE = re.compile(r'("dateModified"\s*:\s*")([^"]+)(")')


def git_last_real_commit_date(relpath):
    """該檔最後「實質」commit 日（YYYY-MM-DD），排除 [datemod-sync] commit。"""
    out = subprocess.run(
        ["git", "log", "-1", "--format=%cs",
         "--invert-grep", "--grep", SYNC_MARKER, "--", relpath],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.strip()
    return out or None


def collect_html():
    files = []
    for p in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(p, ROOT)
        if rel.split(os.sep)[0] in (".git", "node_modules", "scripts"):
            continue
        files.append(p)
    return files


def process_file(path, dry_run=False):
    """回傳 (changes, warnings)；changes=[(old, new), ...]"""
    rel = os.path.relpath(path, ROOT)
    src = open(path, encoding="utf-8").read()
    if '"dateModified"' not in src:
        return [], []

    git_date = git_last_real_commit_date(rel)
    if not git_date:
        return [], [f"{rel}: 無 git 歷史（未 commit？），跳過"]

    changes, warnings = [], []

    def repl_block(m):
        head, body, tail = m.group(1), m.group(2), m.group(3)

        def repl_date(dm):
            old = dm.group(2)
            if old == git_date:
                return dm.group(0)
            changes.append((old, git_date))
            return dm.group(1) + git_date + dm.group(3)

        new_body = DATEMOD_RE.sub(repl_date, body)
        if new_body != body:
            try:
                json.loads(new_body)
            except ValueError as e:
                warnings.append(f"{rel}: 改後 JSON-LD 解析失敗（{e}），已還原該區塊")
                # 還原：不動這個區塊
                for _ in DATEMOD_RE.finditer(body):
                    pass
                return head + body + tail
        return head + new_body + tail

    new_src = LDJSON_RE.sub(repl_block, src)

    # JSON-LD 區塊之外若還有 dateModified（inline JS 等），只警示不動
    outside = len(DATEMOD_RE.findall(LDJSON_RE.sub("", src)))
    if outside:
        warnings.append(f"{rel}: {outside} 處 dateModified 在 JSON-LD 之外，未動")

    if changes and not dry_run:
        open(path, "w", encoding="utf-8").write(new_src)
    return changes, warnings


def main():
    dry_run = "--dry-run" in sys.argv
    changed_pages, all_warnings, lines = [], [], []

    for path in collect_html():
        rel = os.path.relpath(path, ROOT)
        changes, warnings = process_file(path, dry_run)
        all_warnings.extend(warnings)
        if changes:
            changed_pages.append(rel)
            for old, new in changes:
                lines.append(f"{rel}: {old} -> {new}")

    header = [
        f"JSON-LD dateModified 同步報告{'（dry-run）' if dry_run else ''}",
        f"改動頁數：{len(changed_pages)}",
        "",
    ]
    body = lines + ([""] + ["⚠️ " + w for w in all_warnings] if all_warnings else [])
    report = "\n".join(header + body) + "\n"
    open(REPORT, "w", encoding="utf-8").write(report)
    print(report)
    print(f"報告已存：{REPORT}")


if __name__ == "__main__":
    main()
