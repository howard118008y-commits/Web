#!/usr/bin/env python3
"""文字守恆驗證：python3 verify_text.py <file.html>
比對 git HEAD 版 vs 工作區版的可見文字（去 script/style/noscript），列出「舊有新無」與「新有舊無」；
另檢 h1 數、JSON-LD 可 parse、FAQPage schema 的 Q/A 是否逐字出現在可見文字。"""
import sys, subprocess, json, re, os
from collections import Counter
from html.parser import HTMLParser

class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.skip=0; s.chunks=[]; s.h1=0; s.ld=[]; s.inld=False; s.buf=''
    def handle_starttag(s,t,a):
        d=dict(a)
        if t in('script','style','noscript'):
            s.skip+=1
            if t=='script' and d.get('type')=='application/ld+json': s.inld=True; s.buf=''
        if t=='h1': s.h1+=1
    def handle_endtag(s,t):
        if t in('script','style','noscript'):
            s.skip-=1
            if s.inld: s.ld.append(s.buf); s.inld=False
    def handle_data(s,d):
        if s.inld: s.buf+=d; return
        if s.skip: return
        for line in d.split('\n'):
            x=re.sub(r'\s+',' ',line).strip()
            if x: s.chunks.append(x)

def parse(html):
    p=P(); p.feed(html); return p

f=sys.argv[1]
old=subprocess.run(['git','show',f'HEAD:{os.path.basename(f)}'],capture_output=True,text=True,cwd=os.path.dirname(os.path.abspath(f))).stdout
new=open(f,encoding='utf-8').read()
po,pn=parse(old),parse(new)
co,cn=Counter(po.chunks),Counter(pn.chunks)
missing=co-cn; added=cn-co
print(f'== {os.path.basename(f)} ==')
print(f'h1 count: {pn.h1}')
ok=True
for i,b in enumerate(pn.ld):
    try: json.loads(b)
    except Exception as e: ok=False; print(f'JSON-LD #{i} PARSE FAIL: {e}')
print(f'JSON-LD blocks: {len(pn.ld)} parse {"OK" if ok else "FAIL"} (old had {len(po.ld)})')
vis=' '.join(pn.chunks)
faqmiss=0; faqn=0
for b in pn.ld:
    try: j=json.loads(b)
    except: continue
    js=j if isinstance(j,list) else [j]
    for o in js:
        if o.get('@type')=='FAQPage':
            for q in o.get('mainEntity',[]):
                faqn+=1
                qt=re.sub(r'\s+',' ',q.get('name','')).strip(); at=re.sub(r'\s+',' ',q.get('acceptedAnswer',{}).get('text','')).strip()
                for t in (qt,at):
                    if t and t not in vis: faqmiss+=1; print('FAQ schema text NOT in visible:', t[:60])
print(f'FAQ items: {faqn}, mismatches: {faqmiss}')
print(f'\n-- 舊有新無 ({sum(missing.values())}) --')
for k,v in missing.items(): print(f'  [{v}] {k[:120]}')
print(f'\n-- 新有舊無 ({sum(added.values())}) --')
for k,v in added.items(): print(f'  [{v}] {k[:120]}')
