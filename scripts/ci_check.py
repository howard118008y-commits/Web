#!/usr/bin/env python3
"""最小 CI 檢查：HTML 標籤平衡 + 內部連結完整性。零依賴，只用標準庫。"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "node_modules", "scripts", "world"}
BALANCE_TAGS = ["div", "section", "table", "tr", "td", "ul", "ol", "li", "a"]

VOID_TAGS = {"br", "img", "input", "hr", "meta", "link", "source", "col", "area", "base", "embed", "track", "wbr"}


def find_html_files():
    files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for f in filenames:
            if f.endswith(".html"):
                files.append(os.path.join(dirpath, f))
    return sorted(files)


SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)


def strip_scripts(html):
    """移除 <script> 區塊，避免 JS 動態組裝的 HTML 字串（innerHTML/template literal）誤判標籤不平衡。"""
    return SCRIPT_RE.sub("", html)


def check_tag_balance(path, html):
    errors = []
    static_html = strip_scripts(html)
    for tag in BALANCE_TAGS:
        opens = len(re.findall(r"<%s(?:\s[^>]*)?>" % tag, static_html, re.IGNORECASE))
        closes = len(re.findall(r"</%s\s*>" % tag, static_html, re.IGNORECASE))
        if opens != closes:
            errors.append(f"  <{tag}> 開 {opens} 個，閉 {closes} 個，對不上（僅計靜態 HTML，已排除 <script> 區塊）")
    return errors


LINK_RE = re.compile(r'''(?:href|src)=["']([^"'#][^"']*)["']''')


def check_internal_links(path, html, all_files_set):
    errors = []
    base_dir = os.path.dirname(path)
    for m in LINK_RE.finditer(html):
        target = m.group(1)
        if "${" in target or "{{" in target or "<%" in target:
            continue  # JS template literal / 樣板占位符，非真實連結
        if re.match(r"^(https?:|mailto:|tel:|javascript:|data:|//)", target):
            continue
        if target.startswith("/"):
            continue  # 絕對站內路徑，交給部署後的線上連結檢查處理，避免本機路徑誤判
        clean = target.split("#")[0].split("?")[0]
        if not clean:
            continue
        resolved = os.path.normpath(os.path.join(base_dir, clean))
        if os.path.isdir(resolved):
            if not os.path.isfile(os.path.join(resolved, "index.html")):
                errors.append(f"  連結目標資料夾內沒有 index.html：{target}")
            continue
        if not os.path.isfile(resolved):
            errors.append(f"  連結目標不存在：{target}")
    return errors


def main():
    files = find_html_files()
    all_files_set = set(files)
    total_errors = 0
    for path in files:
        rel = os.path.relpath(path, ROOT)
        try:
            html = open(path, encoding="utf-8", errors="ignore").read()
        except Exception as e:
            print(f"❌ {rel}: 無法讀取 ({e})")
            total_errors += 1
            continue
        errs = check_tag_balance(path, html) + check_internal_links(path, html, all_files_set)
        if errs:
            print(f"❌ {rel}")
            for e in errs:
                print(e)
            total_errors += len(errs)
    print(f"\n掃描 {len(files)} 個 HTML 檔，發現 {total_errors} 個問題")
    if total_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
