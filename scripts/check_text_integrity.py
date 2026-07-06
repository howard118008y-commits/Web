#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""換裝文字完整性檢查：工作樹 vs git HEAD
比對：①可見文字（去 script/style 後的 text nodes）②所有 JSON-LD 區塊
容許：純 CSS/class/style 屬性差異。任何文字增刪 = FAIL。
用法：python3 check_text_integrity.py <repo_dir> <file1> <file2> ...
"""
import subprocess, sys, re, json, difflib
from html.parser import HTMLParser

class TextExtract(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self.skip = [], 0
        self.ldjson = []
        self._in_ld = False
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
            if tag == 'script' and any(k == 'type' and 'ld+json' in (v or '') for k, v in attrs):
                self._in_ld = True
    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = max(0, self.skip - 1)
            self._in_ld = False
    def handle_data(self, d):
        if self._in_ld:
            self.ldjson.append(d)
        elif self.skip == 0:
            t = d.strip()
            if t:
                self.parts.append(re.sub(r'\s+', ' ', t))

def extract(html):
    p = TextExtract()
    p.feed(html)
    ld = []
    for block in p.ldjson:
        try:
            ld.append(json.dumps(json.loads(block), ensure_ascii=False, sort_keys=True))
        except Exception:
            ld.append('RAW:' + re.sub(r'\s+', ' ', block.strip()))
    return p.parts, ld

repo, files = sys.argv[1], sys.argv[2:]
fail = 0
for f in files:
    old = subprocess.run(['git', '-C', repo, 'show', f'HEAD:{f}'],
                         capture_output=True, text=True).stdout
    new = open(f'{repo}/{f}', encoding='utf-8').read()
    ot, old_ld = extract(old)
    nt, new_ld = extract(new)
    probs = []
    if ot != nt:
        diff = list(difflib.unified_diff(ot, nt, lineterm='', n=0))[2:8]
        probs.append('可見文字漂移: ' + ' | '.join(diff))
    if old_ld != new_ld:
        probs.append(f'JSON-LD 漂移（{len(old_ld)}→{len(new_ld)} 塊）')
        for i, (a, b) in enumerate(zip(old_ld, new_ld)):
            if a != b:
                probs.append(f'  第{i}塊不同')
    if probs:
        fail += 1
        print(f'❌ {f}')
        for p_ in probs: print('   ' + p_[:300])
    else:
        print(f'✅ {f} 文字/schema 零漂移（可見文字 {len(nt)} 節點、LD {len(new_ld)} 塊）')
sys.exit(1 if fail else 0)
