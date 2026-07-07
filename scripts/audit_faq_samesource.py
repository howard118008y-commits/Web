#!/usr/bin/env python3
"""FAQPage schema 與可見文字同源稽核（全站，含 index——別排除首頁，2026-07-01 盲點教訓）

用法：python3 scripts/audit_faq_samesource.py
判準：每個 Question.name 與 acceptedAnswer.text 正規化後（剝標籤、去空白、解 entity）
     必須是可見純文字的 substring。任何不中＝漂移＝Google 可能判作弊。
規則出處：memory feedback_faq_schema_same_source。
"""
import glob, re, json, html as H, os, sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def norm(s):
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = H.unescape(s)
    return re.sub(r'\s+', '', s)

aligned, drift, noschema = [], {}, 0
for f in sorted(glob.glob('*.html') + glob.glob('en/*.html')):
    t = open(f, encoding='utf-8').read()
    faqs = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try:
            data = json.loads(m.group(1))
        except Exception:
            drift.setdefault(f, []).append('❌ JSON-LD 解析失敗')
            continue
        for o in (data if isinstance(data, list) else [data]):
            if isinstance(o, dict) and o.get('@type') == 'FAQPage':
                for q in o.get('mainEntity', []):
                    faqs.append((q.get('name', ''), q.get('acceptedAnswer', {}).get('text', '')))
    if not faqs:
        noschema += 1
        continue
    vis = norm(t)
    issues = []
    for qname, qans in faqs:
        if norm(qname) and norm(qname) not in vis:
            issues.append(f'Q漂移: {qname[:44]}')
        if norm(qans) and norm(qans) not in vis:
            issues.append(f'A漂移: {qname[:32]}')
    (drift.setdefault(f, []).extend(issues) if issues else aligned.append(f))

print(f"含 FAQPage: {len(aligned) + len(drift)} 頁｜無: {noschema} 頁")
print(f"✅ 同源 {len(aligned)}｜⚠️ 漂移 {len(drift)}")
for f, iss in sorted(drift.items()):
    print(f"\n== {f}")
    for i in iss:
        print('  ', i)
sys.exit(1 if drift else 0)
