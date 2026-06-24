"""
goal_loop.py — /goal 規格 §5 迴圈 harness（大寫部分=這支實作）
================================================================
評審腦 goal_scorer.py 只打分；這支負責「Playwright 渲染 + 寫 goal-scores.jsonl」。
git commit/revert 由人/上層決定（這支只給 verdict，不自動動 git，避免誤刪）。

用法：
  triage 全站（judge=False，不花 API，建 gate 基線）：
      python goal_loop.py --triage
  單頁完整評分（judge=True，需 ANTHROPIC_API_KEY）：
      python goal_loop.py --page sale-leaseback.html --queries "中和 售後回租 流程" "中和 房屋 售後回租"
  指定多頁 triage：
      python goal_loop.py --triage --only topic-a.html faq.html

渲染走本地 HTTP server + Playwright，會載入 include.js 的 nav/footer（footer 帶 NAP），
所以 NAP gate 看得到 footer 的地址/電話。
"""
import sys, os, re, glob, json, argparse, http.server, socketserver, threading, functools
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from goal_scorer import score_page, append_score, ScoreResult
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent          # CX468/
JSONL = Path(__file__).resolve().parent / "goal-scores.jsonl"
PORT = 3463
FRAGMENTS = {"nav.html","footer.html","lead-form.html","line-qr.html","nav-tool.html","anti-fraud-modal.html"}
BASE = "https://cx468.com.tw"

def real_pages():
    out=[]
    for p in sorted(glob.glob(str(ROOT/"*.html"))):
        fn=os.path.basename(p)
        if fn in FRAGMENTS: continue
        s=open(p,encoding="utf-8",errors="ignore").read()
        if re.search(r'<html',s,re.I) and re.search(r'<head',s,re.I): out.append(fn)
    return out

def render_all(pages):
    handler=functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    httpd=socketserver.TCPServer(("",PORT),handler)
    threading.Thread(target=httpd.serve_forever,daemon=True).start()
    html={}
    with sync_playwright() as p:
        b=p.chromium.launch()
        for fn in pages:
            pg=b.new_page()
            try:
                pg.goto(f"http://localhost:{PORT}/{fn}",wait_until="networkidle",timeout=15000)
                pg.wait_for_timeout(600)           # 等 include.js 注入 nav/footer
                html[fn]=pg.content()
            except Exception as e:
                html[fn]=f"<!--render-error:{e}-->"
            pg.close()
        b.close()
    httpd.shutdown()
    return html

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--triage",action="store_true")
    ap.add_argument("--page")
    ap.add_argument("--queries",nargs="*",default=[])
    ap.add_argument("--only",nargs="*")
    ap.add_argument("--prev",type=float,default=None)
    args=ap.parse_args()

    if args.page:
        pages=[args.page]; judge=True
    else:
        pages=args.only or real_pages(); judge=False

    rendered=render_all(pages)
    results=[]
    for fn in pages:
        h=rendered.get(fn,"")
        archived = bool(re.search(r'name=["\']robots["\'][^>]*noindex', h, re.I))
        url=f"{BASE}/{fn}"
        res=score_page(h, url, target_queries=args.queries, judge=judge,
                       archived=archived, prev_score=args.prev)
        append_score(str(JSONL), res.to_jsonl_row())
        results.append((fn,res))

    # 報表
    if judge:
        fn,res=results[0]
        print(f"\n=== {fn} 完整評分 ===")
        print(f"verdict: {res.verdict} | total: {res.total} | prev: {res.prev_total}")
        for g in res.gates: print(f"  GATE [{'PASS' if g.passed else 'FAIL'}] {g.name}: {g.detail}")
        for k,d in res.dimensions.items():
            print(f"  {k:14s} {d.score}/100 (w{d.weight})  {d.rationale[:70]}")
        print("  reasons:", res.reasons)
    else:
        fails=[(fn,res) for fn,res in results if not res.gates_passed]
        print(f"\n=== TRIAGE：{len(pages)} 頁，gate 未過 {len(fails)} 頁 ===")
        # 各 gate 失敗統計
        from collections import Counter
        c=Counter()
        for fn,res in fails:
            for g in res.gate_failures: c[g]+=1
        print("gate 失敗分布：", dict(c))
        for fn,res in fails:
            print(f"\n🔴 {fn}")
            for g in res.gates:
                if not g.passed: print(f"    [{g.name}] {g.detail}")
    print(f"\n→ 寫入 {JSONL}（{len(results)} 列）")

if __name__=="__main__":
    main()
