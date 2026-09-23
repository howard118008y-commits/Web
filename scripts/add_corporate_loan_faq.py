#!/usr/bin/env python3
"""corporate-loan.html FAQ 補 8 題（3→11）。同源生成：可見 DOM 與 FAQPage JSON-LD 由同一份 FAQS 渲染，
禁止手寫兩份（memory feedback_faq_schema_same_source）。冪等：已含第 1 題即跳過。
用法：/usr/bin/python3 scripts/add_corporate_loan_faq.py
驗證：/usr/bin/python3 scripts/audit_faq_samesource.py ； python3 scripts/add_faq_items.py --verify --all
"""
import datetime, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "corporate-loan.html"

FAQS = [
    ("企業貸款諮詢是什麼？鋮馨負責哪一段？",
     "我們先做公司財務健檢：整理三年 401 表、營所稅申報書與公司存摺，看金流、還款來源與客戶集中度；健檢後協助媒合銀行送件。鋮馨不放貸，核貸由金融機構決定。"),
    ("公司成立未滿一年、還沒有 401 表，可以談嗎？",
     "可以先談。健檢會改用稅籍資料、存摺往來與負責人狀況看體質；資歷不足也協助媒合，但能否受理、額度與條件由各機構依個案審核決定。"),
    ("公司財務健檢要準備哪三份文件？",
     "近三年全部期別的 401 表、近三年營所稅結算申報書、近 12 個月全部帳戶的公司存摺明細。有不動產擔保品再補權狀或謄本；面談帶紙本或手機照片即可。"),
    ("銀行審核企業貸款，主要看哪些指標？",
     "健檢用五項指標對照銀行視角：金流勾稽率、申報營收年增率、還款覆蓋率試算、單一客戶集中度、負責人聯徵概況。各銀行權重不同，實際審核以各機構為準。"),
    ("企業貸款利率大概多少？可以貸多少？",
     "沒有通用數字。利率、額度與年限由各金融機構依公司營收、金流、擔保品與負責人信用逐案核定，本站不報價；健檢先把資料整理好，再比較各家正式條件。"),
    ("被銀行退件過，多久可以再送件？",
     "沒有固定間隔。退件原因通常在資料：申報營收與存摺對不上、營收下滑、客戶集中或聯徵待說明。先做健檢找出紅燈、補齊文件，再依個案評估送件時機。"),
    ("負責人名下有房子，對企業貸款有幫助嗎？",
     "可能有。負責人不動產可一併評估是否作為擔保或另一條資金路徑，但公司本身的金流與還款來源仍是主要審核依據，是否採計由金融機構決定。"),
    ("健檢與媒合怎麼收費？",
     "不申請不收費，面談不收費。30 分鐘簡版健檢不收費；後續完整送件包製備屬顧問服務，範圍與計費方式在面談時先書面說明，不會事後追加。"),
]

ITEM = '<h3 class="bt-h4">{q}</h3><p class="bt-p">{a}</p>'
# 既有第 3 題答案，全檔唯一（grep -c → 1）；新題接在它後面、cx-call-block 前面
ANCHOR = '<p class="bt-p">不會。額度、利率、費用與時程依個案審核和正式條件為準，最終核貸由金融機構決定。</p>'
LD_RE = re.compile(r'(<script type="application/ld\+json">)(\{[^<]*?"@type": "FAQPage"[^<]*?\})(</script>)')
DATEMOD_RE = re.compile(r'("dateModified"\s*:\s*")(\d{4}-\d{2}-\d{2})(")')

html = PAGE.read_text(encoding="utf-8")
if FAQS[0][0] in html:
    raise SystemExit("skip：已含新題（冪等）")
assert html.count(ANCHOR) == 1, "FAQ 末題 anchor 不唯一，先看 corporate-loan.html:392"
html = html.replace(ANCHOR, ANCHOR + "".join(ITEM.format(q=q, a=a) for q, a in FAQS))

def _extend(m):
    data = json.loads(m.group(2))
    for q, a in FAQS:
        data["mainEntity"].append({"@type": "Question", "name": q,
                                   "acceptedAnswer": {"@type": "Answer", "text": a}})
    return m.group(1) + json.dumps(data, ensure_ascii=False) + m.group(3)

html, n = LD_RE.subn(_extend, html)
assert n == 1, f"FAQPage JSON-LD 命中 {n} 次（預期 1）"
today = datetime.date.today().isoformat()
html = DATEMOD_RE.sub(lambda m: m.group(1) + today + m.group(3), html)
PAGE.write_text(html, encoding="utf-8")
print(f"corporate-loan.html: +{len(FAQS)} 題（共 {3 + len(FAQS)}），dateModified→{today}")
