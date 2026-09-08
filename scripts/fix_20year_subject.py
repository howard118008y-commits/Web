#!/usr/bin/env python3
"""把全站「20 年」的主詞從公司改成團隊。

背景：商業司登記顯示鋮馨租賃有限公司設立於民國114年9月10日（2025-09-10），
至今未滿1年。文案寫「公司深耕20年」與登記資料矛盾，屬廣告不實曝險。
20年是經營團隊的個人資歷，不是公司年資。

用法：
    python3 scripts/fix_20year_subject.py            # 預覽（不寫檔）
    python3 scripts/fix_20year_subject.py --apply    # 實際改檔
    python3 scripts/fix_20year_subject.py --revert   # 從 .bak 還原
"""
import os, sys, shutil

# (原字串, 新字串) — 逐字精確替換，不用 regex，避免誤傷
RULES = [
    ("鋮馨租賃有限公司提供不動產售後回租、貸款整合、民間轉銀行專業諮詢與媒合服務。20 年以上經驗，",
     "鋮馨租賃有限公司提供不動產售後回租、貸款整合、民間轉銀行專業諮詢與媒合服務。團隊 20 年以上經驗，"),
    ("鋮馨租賃有限公司提供不動產融資諮詢、貸款整合、民間轉銀行專業諮詢與媒合服務。20 年以上經驗，",
     "鋮馨租賃有限公司提供不動產融資諮詢、貸款整合、民間轉銀行專業諮詢與媒合服務。團隊 20 年以上經驗，"),
    ("20+ 年不動產租賃經驗", "團隊 20+ 年不動產租賃經驗"),
    ("20+ 年不動產融資經驗", "團隊 20+ 年不動產融資經驗"),
    ("深耕在地 20 年", "團隊在地深耕 20 年"),
    ("深耕在地20年", "團隊在地深耕20年"),
    ("在地深耕 20 年", "團隊在地深耕 20 年"),
    ("在地深耕不動產與資金規劃超過 20 年", "團隊在地深耕不動產與資金規劃超過 20 年"),
    ("在地深耕不動產與資金規劃 20 年以上", "團隊在地深耕不動產與資金規劃 20 年以上"),
    ("深耕不動產租賃超過 20 年", "團隊深耕不動產租賃超過 20 年"),
    ("深耕新北市中和區20年以上", "團隊深耕新北市中和區20年以上"),
    ("深耕不動產租賃 20 年以上", "團隊深耕不動產租賃 20 年以上"),
    ("鋮馨做售後回租的諮詢與媒合，20 年以上不動產經驗。", "鋮馨做售後回租的諮詢與媒合，團隊 20 年以上不動產經驗。"),
    ("20+ 年不動產經驗", "團隊 20+ 年不動產經驗"),
    ("中和在地20年經驗", "團隊中和在地20年經驗"),
    ("鋮馨深耕新北中和 20 年以上", "鋮馨團隊深耕新北中和 20 年以上"),
    ("鋮馨租賃在地 20 年", "鋮馨租賃團隊在地 20 年"),
    ("深耕二十年", "團隊深耕二十年"),
    ("服務永和一帶、在地 20 年", "服務永和一帶、團隊在地 20 年"),
    ("服務永和一帶 · 在地 20 年", "服務永和一帶 · 團隊在地 20 年"),
    ("民間轉銀行。20 年以上經驗，非金融機構。", "民間轉銀行。團隊 20 年以上經驗，非金融機構。"),
    # ── 2026-09-09 稽核補進：以下 47 處主詞是公司但原 21 條規則零命中 ──
    # head/meta/og/twitter（正文對、head 錯的典型；護欄不跟著摘要走）
    ("深耕不動產租賃業超過 20 年", "團隊深耕不動產租賃業超過 20 年"),
    ("深耕不動產租賃 20 年，整合", "團隊深耕不動產租賃 20 年，整合"),
    ("關於鋮馨租賃｜20 年不動產諮詢", "關於鋮馨租賃｜團隊 20 年不動產諮詢"),
    ("深耕 20 年以上、整合", "團隊深耕 20 年以上、整合"),
    ("深耕新北市不動產租賃超過 20 年", "團隊深耕新北市不動產租賃超過 20 年"),
    ("深耕在地不動產與資金規劃超過 20 年", "團隊深耕在地不動產與資金規劃超過 20 年"),
    ("鋮馨深耕中和逾 20 年", "鋮馨團隊深耕中和逾 20 年"),
    # 五支 area 頁的「在地優勢」條目
    ("行情與銀行管道、20 年經驗", "行情與銀行管道、團隊 20 年經驗"),
    # *-property-finance 系列 og/twitter
    ("鋮馨在地 20 年。本公司非金融機構", "鋮馨團隊在地 20 年。本公司非金融機構"),
    # *-property-finance 麵包屑列與內文
    ("一帶 · 在地 20 年", "一帶 · 團隊在地 20 年"),
    ("一帶、在地 20 年；", "一帶、團隊在地 20 年；"),
    ("<strong>在地 20 年</strong>", "<strong>團隊在地 20 年</strong>"),
    # 中和融資諮詢／售後回租
    ("號、在地 20 年，提供諮詢與媒合協助", "號、團隊在地 20 年，提供諮詢與媒合協助"),
    ("<strong>20 年經驗、39 家以上合作銀行</strong>", "<strong>團隊 20 年經驗、39 家以上合作銀行</strong>"),
    ("你。20 年經驗、39 家以上合作銀行。", "你。團隊 20 年經驗、39 家以上合作銀行。"),
    ("選。20 年經驗、39 家以上合作銀行。", "選。團隊 20 年經驗、39 家以上合作銀行。"),
    ("買回的權利。20 年以上經驗，非金融機構。", "買回的權利。團隊 20 年以上經驗，非金融機構。"),
    ("號、在地 20 年；本公司非金融機構", "號、團隊在地 20 年；本公司非金融機構"),
    ("<strong>20 年經驗</strong>：把你的狀況", "<strong>團隊 20 年經驗</strong>：把你的狀況"),
    ("20 年以上不動產經驗，自營業者", "團隊 20 年以上不動產經驗，自營業者"),
    ("中和在地 20 年，金額約市值", "中和團隊在地 20 年，金額約市值"),
    ("中和在地 20 年。本公司非金融機構", "中和團隊在地 20 年。本公司非金融機構"),
    ("中和在地 20 年不動產融資諮詢", "中和團隊在地 20 年不動產融資諮詢"),
    ("新北市中和區在地 20 年不動產融資諮詢", "新北市中和區團隊在地 20 年不動產融資諮詢"),
    ("新北市中和區在地 20 年，名下有房", "新北市中和區團隊在地 20 年，名下有房"),
    # world/（「二十餘年」不含「二十年」，任何 20 年 pattern 都抓不到）
    ("鋮馨租賃 · 中和 · 二十餘年", "鋮馨租賃 · 中和 · 團隊資歷二十餘年"),
    ("在中和中正路 468 號，開了二十多年。", "在中和中正路 468 號；團隊在這一行做了二十多年。"),
    # en/（21 條原規則零英文，--apply 對英文版完全無作用）
    ("20+ years, 39+ partner banks", "Our team's 20+ years, 39+ partner banks"),
    ("20+ years in the Taipei metro", "Our team's 20+ years in the Taipei metro"),
    ("serving property owners for over 20 years", "with a team serving property owners for over 20 years"),
    ("20+ years of Taipei-metro casework", "Our team's 20+ years of Taipei-metro casework"),
]

EXTS = (".html", ".json", ".txt")
# docs/ 與 制度/ 是歷史紀錄與稽核檔，改了會抹掉當時的觀測值；
# 且 EXTS 含 .txt 後，寫在 docs/ 的預覽 diff 會被自己掃到（2026-09-09 踩過，188→380 處）。
SKIP_DIRS = {"node_modules", ".git", "scripts", "docs", "制度"}

# 媽祖 2026-08-27 掃描退回：這些「20 年」的主詞不是鋮馨，補主詞會把案例／參數改壞。
# 整檔排除（全檔的 20 年都是持有年數級距，改了還會弄壞計算機 UI）
SKIP_FILES = set()
# 主詞是客戶不是我方的句子。2026-09-09 媽祖指出：這個常數原本宣稱是閘門，
# 但 apply_rules() 從未引用它（零引用死碼），保護清單之所以安全，靠的是規則
# 字串本身精確到不會命中，不是有東西在擋。改成真正的斷言，讓它名實相符。
CUSTOMER_SUBJECT_PHRASES = (
    "經營近 20 年",        # article-self-employed-loan：案例中自營業者客戶的生意
    "做了二十年生意",       # second-mortgage：同理目標客群的處境
)


def apply_rules(text):
    """套用 RULES，兩階段佔位符法。

    2026-09-09 稽核發現兩個會毀站的缺陷，這裡一次修掉：

    (1) 規則互吃：rule「深耕在地 20 年」的替換結果「團隊在地深耕 20 年」
        內含另一條 rule 的 old「在地深耕 20 年」，依序 str.replace 會二次
        命中，實測五支 area 頁全部產出「團隊團隊在地深耕 20 年」。
        解法：先把每個命中換成不可能再被命中的佔位符，全部掃完才還原。

    (2) 不具冪等：已人工修好的「團隊 20+ 年不動產租賃經驗」，其中的
        「20+ 年不動產租賃經驗」仍是某條 rule 的 old，重跑會疊成
        「團隊 團隊 20+ 年…」。實測第二次 --apply 有 29 檔會再變動，
        且會用改壞的內容覆蓋 .bak20y，--revert 從此失效。
        解法：命中點往前看 6 個字，已有「團隊」就跳過。
    """
    hits = 0
    # 階段一：命中 -> 佔位符
    for i, (old, rep) in enumerate(RULES):
        if old not in text:
            continue
        out, pos = [], 0
        token = "\x00%d\x00" % i
        while True:
            j = text.find(old, pos)
            if j < 0:
                out.append(text[pos:]); break
            # 冪等守衛：前面已經有主詞就不再補。
            # 中文看前 6 字的「團隊」；英文 new 是「Our team's」不含中文，
            # 必須另外看前 12 字的 team（2026-09-09 媽祖實測：補了英文規則卻沿用
            # 補之前的冪等結論，en/index.html 第 2 次跑會疊成「Our team's Our team's」）。
            if "團隊" in text[max(0, j - 6):j] or "team" in text[max(0, j - 12):j].lower():
                out.append(text[pos:j + len(old)]); pos = j + len(old); continue
            out.append(text[pos:j]); out.append(token)
            pos = j + len(old); hits += 1
        text = "".join(out)
    # 階段二：佔位符 -> 新字串（此時不會再被任何規則掃到）
    for i, (old, rep) in enumerate(RULES):
        text = text.replace("\x00%d\x00" % i, rep)
    return text, hits


def assert_no_damage(path, text, original=""):
    """改完的內容不得出現這些壞句。原腳本只把自檢 grep 印出來給人跑，
    而且那串 pattern 抓不到「團隊團隊」，跑完會靜默過關。改成硬斷言。"""
    bad = ["團隊團隊", "團隊 團隊", "團隊20年", "未滿團隊", "做了團隊",
           "經營近 團隊", "團隊團隊團隊",
           # 英文疊字（守衛與斷言原本三道防線都只想著中文）
           "Our team's Our team's", "with a team with a team", "team's team's"]
    found = [b for b in bad if b in text]
    if found:
        raise SystemExit("中止：%s 會產生壞句 %s。沒有任何檔案被寫入。" % (path, found))
    # 客戶主詞句必須逐字存活——補主詞會把客戶案例改成我方資歷
    for ph in CUSTOMER_SUBJECT_PHRASES:
        if ph in original and ph not in text:
            raise SystemExit("中止：%s 動到了客戶主詞句「%s」。沒有任何檔案被寫入。" % (path, ph))


def walk():
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in sorted(files):
            if f.endswith(EXTS) and f not in SKIP_FILES:
                yield os.path.join(root, f)

def main():
    apply_ = "--apply" in sys.argv
    revert = "--revert" in sys.argv

    if revert:
        n = 0
        for p in walk():
            bak = p + ".bak20y"
            if os.path.exists(bak):
                shutil.move(bak, p); n += 1
        print(f"已還原 {n} 個檔案")
        return

    total_files = total_hits = 0
    for p in walk():
        try:
            t = open(p, encoding="utf-8").read()
        except Exception:
            continue
        new, hits = apply_rules(t)
        if not hits:
            continue
        total_files += 1; total_hits += hits
        print(f"{'改' if apply_ else '待改'} {p}  ({hits} 處)")
        assert_no_damage(p, new, t)
        if apply_:
            open(p, "w", encoding="utf-8").write(new)

    print(f"\n{'已修改' if apply_ else '預覽'}：{total_files} 檔、{total_hits} 處")
    if not apply_:
        print("實際執行： python3 scripts/fix_20year_subject.py --apply")
    else:
        print("還原：git checkout -- <檔案>（不再產生 .bak20y，repo 本身就是備份）")
        print("⚠️ 改完務必驗 JSON-LD 語法，並確認 git status 只含預期檔案再 push。")
        print("✅ 壞句斷言已內建於 assert_no_damage()，寫檔前自動擋，不需人工 grep。")

if __name__ == "__main__":
    main()
