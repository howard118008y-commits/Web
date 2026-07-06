#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全站視覺機掃：sitemap 每頁 → 底色/footer數/nav/紫殘留/水平溢出/JS錯誤 ＋ 截圖存證"""
import json, re, sys
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright

SITE = 'https://cx468.com.tw'
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)

xml = urlopen(SITE + '/sitemap.xml', timeout=20).read().decode()
urls = re.findall(r'<loc>([^<]+)</loc>', xml)
for extra in (SITE + '/cx_radar_v4_demo.html',):
    if extra not in urls:
        urls.append(extra)
seen = list(dict.fromkeys(urls))

res, errs = [], []
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 1280, 'height': 800})
    ctx.add_init_script("try{localStorage.setItem('cx_antifraud_v1',String(Date.now()))}catch(e){}")
    pg = ctx.new_page()
    pg.on('pageerror', lambda e: errs.append(str(e)[:80]))
    for i, u in enumerate(seen):
        errs.clear()
        row = {'i': i, 'url': u.replace(SITE, '') or '/'}
        try:
            pg.goto(u, timeout=25000, wait_until='load')
            pg.wait_for_timeout(650)
            m = pg.evaluate("""()=>{
              const bodyBg=getComputedStyle(document.body).backgroundColor;
              const htmlBg=getComputedStyle(document.documentElement).backgroundColor;
              const foot=document.querySelectorAll('[data-include="footer"]').length;
              const footerEls=document.querySelectorAll('footer').length;
              const nav=!!document.querySelector('nav');
              const purple=(document.documentElement.outerHTML.match(/#7c3aed|#8b5cf6|#a78bfa|#6d28d9|#9333ea/gi)||[]).length;
              const ox=document.documentElement.scrollWidth-window.innerWidth;
              const h1=(document.querySelector('h1')||{}).innerText||'';
              return {bodyBg,htmlBg,foot,footerEls,nav,purple,ox,h1:h1.slice(0,24)};
            }""")
            row.update(m)
            row['jsErr'] = len(errs)
            name = re.sub(r'[^a-z0-9]+', '-', row['url'].lower()).strip('-') or 'home'
            pg.screenshot(path=str(OUT / f'{i:03d}-{name[:40]}.jpeg'), type='jpeg', quality=45)
        except Exception as e:
            row['fail'] = str(e)[:90]
        res.append(row)
    b.close()

(OUT / 'sweep.json').write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')

WHITE = ('rgb(255, 255, 255)', 'rgba(0, 0, 0, 0)')
flags = []
for r in res:
    why = []
    if r.get('fail'): why.append('載入失敗')
    if r.get('foot', 1) != 1: why.append(f"footer include×{r.get('foot')}")
    if r.get('footerEls', 1) > 1: why.append(f"footer元素×{r.get('footerEls')}")
    if r.get('purple', 0) > 0: why.append(f"紫殘留×{r.get('purple')}")
    if r.get('ox', 0) > 2: why.append(f"水平溢出{r.get('ox')}px")
    if not r.get('fail') and r.get('bodyBg') not in WHITE: why.append(f"底色 {r.get('bodyBg')}")
    if not r.get('fail') and not r.get('nav', True): why.append('無nav')
    if r.get('jsErr', 0) > 0: why.append(f"JS錯誤×{r.get('jsErr')}")
    if why:
        flags.append({'url': r['url'], 'why': why, 'h1': r.get('h1', ''), 'i': r['i']})

print(json.dumps(flags, ensure_ascii=False, indent=1))
print(f'TOTAL={len(res)} FLAGGED={len(flags)}')
