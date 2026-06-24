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

# 代表頁 ↔ 在地目標查詢（取自 /goal 規格附錄 A；judge 用，aeo 維度依此評「直接答案區塊」）
PANEL = {
    "sale-leaseback.html":      ["中和 售後回租 流程", "中和 房屋 售後回租", "售後回租 是什麼"],
    "second-mortgage.html":     ["中和 二胎房貸 條件", "中和 二胎房貸 是什麼", "二胎房貸 利率區間"],
    "debt-consolidation.html":  ["中和 債務整合 找誰", "中和 貸款整合 利息", "貸款整合 是什麼"],
    "private-to-bank.html":     ["民間借款 轉銀行", "民間轉銀行 流程", "民間二胎 轉銀行"],
    "property-management.html": ["中和 包租代管 費用", "包租代管 是什麼", "二房東 合法"],
    "bad-credit-mortgage.html": ["信用瑕疵 房貸", "信用不好 貸款", "聯徵 不良 貸款"],
    "market-insight.html":      ["新北 房市 走勢", "銀行 放貸 寬鬆", "貸款 自辦 找誰"],
    "faq.html":                 ["鋮馨 常見問題", "售後回租 會被騙嗎", "貸款整合 傷信用"],
    "knowledge.html":           ["不動產 財務 知識", "售後回租 貸款整合 差別"],
    "radar-index.html":         ["房貸 市場 指標", "央行 利率 房貸"],
    "topic-a.html":             ["央行 重貼現率 房貸", "房貸利率 走勢"],
    "taipei-land-value-tax.html": ["台北 地價稅 試算", "地價稅 怎麼算"],
    "index.html":               ["名下有房 增貸", "新北 中和 貸款 公司"],
}

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
    ap.add_argument("--panel",action="store_true",help="judge 代表頁(PANEL)，每頁帶其在地查詢")
    ap.add_argument("--prev",type=float,default=None)
    args=ap.parse_args()

    if args.panel:
        pages=[p for p in (args.only or PANEL) if p in PANEL]; judge=True
        qmap=PANEL
    elif args.page:
        pages=[args.page]; judge=True
        qmap={args.page: args.queries}
    else:
        pages=args.only or real_pages(); judge=False
        qmap={}

    rendered=render_all(pages)
    results=[]
    for fn in pages:
        h=rendered.get(fn,"")
        archived = bool(re.search(r'name=["\']robots["\'][^>]*noindex', h, re.I))
        url=f"{BASE}/{fn}"
        queries = qmap.get(fn, args.queries)
        res=score_page(h, url, target_queries=queries, judge=judge,
                       archived=archived, prev_score=args.prev)
        append_score(str(JSONL), res.to_jsonl_row())
        results.append((fn,res))

    # 報表
    if judge:
        if len(results) > 1:
            print(f"\n=== PANEL 評分（{len(results)} 頁）===")
            print(f"{'頁面':32s} {'total':>6s} {'aeo':>4s} {'eeat':>5s} {'clus':>5s} {'tech':>5s} {'conv':>5s}  verdict")
            scored=[]
            for fn,res in results:
                d=res.dimensions
                g=lambda k: ('--' if d[k].score is None else int(d[k].score))
                if res.total is None:
                    print(f"{fn:32s} {'GATE✗':>6s}  {';'.join(res.gate_failures)}")
                else:
                    print(f"{fn:32s} {res.total:6.1f} {g('aeo'):>4} {g('local_eeat'):>5} {g('topic_cluster'):>5} {g('technical'):>5} {g('conversion'):>5}  {res.verdict}")
                    scored.append((res.total,fn))
            if scored:
                scored.sort()
                avg=sum(t for t,_ in scored)/len(scored)
                print(f"\n平均 total: {avg:.1f} | 最弱: {scored[0][1]}({scored[0][0]}) | 最強: {scored[-1][1]}({scored[-1][0]})")
            # 印最弱頁的維度 rationale 供改進
            if scored:
                worst=dict((f,r) for f,r in results)[scored[0][1]]
                print(f"\n— 最弱頁 {scored[0][1]} 各維 rationale —")
                for k,dd in worst.dimensions.items():
                    if dd.rationale: print(f"  {k}: {dd.rationale[:90]}")
        else:
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
