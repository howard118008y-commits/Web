# 交接信｜cx468-web（官網 repo）＋ CX468 雲端維運

> 現況快照，不是 changelog。歷史在 `git log`。
> 最後更新：2026-09-14 15:1x（Phase 3 配色＋二胎頁撥號 CTA，commit `4c50d13`，**16:2x 已 push 上線（7c45acf），線上驗過**；第一節設計／電話兩列與第三節第一、二順位已改，其餘為 14:3x 版）
> 前次：2026-09-14 14:3x（矩陣 session 收工：六頁線上 200 重驗、GSC 六網址 Sir 已送）
> 前次：2026-09-14 04:xx 另一 session 的矩陣第一批（第三節 🟢，已改標為已部署）；再前次 2026-09-09。
> 本次更新原因：Sir 09-14 四項裁示落地（電話兩支為主／售後回租統一 A／企業貸款頁留但健檢在前／文字憲法放鬆改 SEO 為主）＋ 全站配色對齊主頁 Phase 1–2 上線 ＋ 09-11～13 另一 session 153 檔改動全部審過。一、三、四、五節重寫；二節與三節 🟢 保留。

## 一、當前狀態快照（2026-09-20 00:2x 重驗，每項附指令）

| 項目 | 值 | 重驗指令 |
|---|---|---|
| HEAD | **`cb51af5`＝origin/main（09-20 00:2x 重驗；CI＋Pages success 台北 09-20 00:13）**。09-18～19 鏈（cloud-code-d0 主題頁改造，計畫 `行銷產出/策略簡報/2026-09-17-導覽列主題分頁改造計畫.md`）：`8339a2e` B0/B1 private-to-bank → `803c315`／`63b2f6f`／`2315351` Block 3／6／0 → `abcf5f3` B2 三頁 → `ddfbefb` B3 繼承 2＋SLB、B4 企業 2 → `be96724` B5 小工具／案例 8 頁橋接區 → `69e0bf4` p2a 09-19 文章 → `cb51af5` nav 手機選單字色修。其前 `03e9d3e` 新聞卡第 3 週換稿（央行 9/17）、`9468a93` 永和／土城二胎＋geo 77 頁（09-18 00:5x） | `cd ~/cx468-web && git fetch && git status -sb && git log --oneline -12` |
| CI／Pages | `cb51af5` 兩者 success（2026-09-19T16:13Z＝台北 09-20 00:13） | `gh run list -L 3` |
| 工作區 | 09-20 00:2x：**8 個 M 屬 cloud-code-d0**（footer／privacy-policy／banqiao・sanchong・tucheng・xinzhuang・yonghe・zhonghe-corporate-checkup＝媽祖 09-19 兩項全站裁示：「不經第三方表單服務」歸零＋二胎頁尾「免費」鏈改字；媽祖複核中，它自己 commit＋push）——**勿 add／勿 checkout --**；未追蹤 `scripts/archive/goal-scores.jsonl` 非本專案產物勿 add；無 worktree | `git status -s`；`git worktree list`；認領用 `ListAgents`＋`SendMessage` |
| 閘門（乾淨樹） | ci_check **183 檔 0 問題**（09-20 00:2x，只含已追蹤檔的 rsync 樹）；FAQ 同源 **148 頁零漂移／30 頁無 FAQ**；audit-regression **本次未跑**（scratch 的 linkedom 不在；最後一次 18/18 是 09-18 00:4x 的 9468a93 樹）；主題頁 17 頁 `data-include="inline-form"` | `python3 scripts/ci_check.py`；`NODE_PATH=<scratch>/nodedeps/node_modules node scripts/audit-regression.cjs`（需 `npm i linkedom@0.18.12`）；`python3 scripts/audit_faq_samesource.py` |
| 設計（Phase 1–3 全上線） | Phase 3（`4c50d13`）：`footer.html` paper 版（147 頁共用，選擇器掛 `.cx-site-footer` 非 `:where`）；新檔 `theme.css` 掛 A 族 67 頁 `</head>` 前（Sans 內文／Serif 900 標題／hero 漸層 `:has` 排除 `.art-title` 白底型／金鈕＋cream 幽靈鈕）；`style.css` body 字體、`.btn-green/.btn-line` 金、footer 區段移除；60 頁字型 link 補 Sans＋Serif 900、6 頁補 link；C 族 74 頁 `.bt-cta .bt-btn-ghost` 白底細邊；`gen_radar_v4.py` 模板掛 theme.css 並修 f-string 大括號 SyntaxError。Phase 1–2 同前 | 線上 `curl -s https://cx468.com.tw/second-mortgage.html \| grep -c 'bt-hero{background:linear-gradient'` → 1；`grep -l 'data-theme="light"' *.html \| wc -l` → 0 |
| 二胎撥號 CTA（已上線） | 12 個 LINE-only 正文群組各加「撥打 02-2249-0517」（7 頁）＋ lp-zhonghe／lp-tucheng／calculator 來電鈕 0931→02；媽祖 11/11 PASS（`grep -c "tel:0222490517" second-mortgage.html` → 應 ≥4） |
| 追蹤 | `consultation-tracking.js` 掛 **65 頁**（PR#5 補 36 盲頁＋矩陣 6＋5 頁＋radar；實數以 grep 為準）；真瀏覽器實測 glossary／中和售後回租／台北地價稅點 sticky CTA → `line_click`＋`phone_click` 進 dataLayer | `grep -l consultation-tracking.js *.html \| wc -l`；`python3 scripts/ci_check.py` 內建 check_conversion_tracking |
| 電話（Sir 09-14 定） | 02-2249-0517 主 ＋ **0958-139-786 經理鄭小姐**；contact 可見×5＋FAQ schema；footer 兩支；**60 頁** Organization contactPoint = [02, 0958]（含矩陣 6 新頁）；0931 降為工作機／LINE ID | `curl -s https://cx468.com.tw/contact.html \| grep -o 經理鄭小姐 \| wc -l` → 5；`grep -l '+886-958-139-786","contactType' *.html \| wc -l` → 56 |
| NAP geo | **全站 meta geo.position／ICBM＝schema geo＝`24.9944428,121.4900325`**（`2c97ec0`：77 頁＋首頁 meta＋3 支產生器模板）；`area-*.html`／`*-property-finance.html` 的行政區座標是例外不動 | `grep -ho 'geo.position" content="[^"]*"' *.html \| sort \| uniq -c` → 公司值 78＋各區單筆 |
| 售後回租定義 | 全站統一 A 版「並可保有日後依約買回的權利」；「買回權利須另行約定」型改寫 0 | `grep -l '買回權利[須需]另行約定' *.html \| wc -l` → 0 |
| 企業線 | `corporate-loan.html` 保留（index/follow、nav 群組「企業貸款」），首段＋meta 寫明「先做公司財務健檢，健檢看完即使資歷不足也協助媒合企業貸款」；nav 群組健檢排第一 | `curl -s https://cx468.com.tw/corporate-loan.html \| grep -c 先做公司財務健檢` → 2 |
| 「20 年」主詞 | 全站團隊（`cfd7061` 09-09 91 檔）；p2a 模板／小鋮提示詞亦改（跨 repo，見下） | 全站無主詞殘留掃描 0（腳本在 `scripts/fix_20year_subject.py`，冪等） |
| p2a 日更 | Render `cx468-p2a-publish` HEAD `8c9d449`（09-18 GO 閘門拆除：敏感稿不等 GO、SKIP 仍擋）；09-19 已產 `article-sale-leaseback-avoid-fire-sale.html`（`69e0bf4`）；閘門 b FAIL 已印原因（`p2a_job.py:196`）；**排程仍是 `render.yaml:110` draft `0 0`／`:141` publish `0 2`（UTC＝台北 08:00／10:00），T8 要改 `15 9`＋註解同步** | `git -C ~/cx468-fb-news-bot log --oneline -3`；`grep -n schedule ~/cx468-fb-news-bot/render.yaml` |
| linebot／ga4-daily | Render live `37ed7f6`（小鋮提示詞）／`a74f06c`（09-03 卡在本機的健檢修正已推） | Render API `services/*/deploys?limit=1` |
| 三日健檢 | 最新報告 `行銷產出/技術記錄/健檢/2026-09-17.md`；launchd `com.cx468.healthcheck` 在列（exit 0），09-20 這輪看 `healthcheck.out` 尾段；09-17 🔴×6 中新聞卡／Threads／週報三條已解，剩 週報監控瞎（T4）／銀行條文／Meta spend_cap——**收到要有人接**（memory `feedback_act_on_telegram_alerts`） | `grep -n "Telegram 已推" ~/cx468-ga4-daily/logs/healthcheck.out \| tail -3` |
| 廣告（09-17 23:xx 取） | Meta：真正 ACTIVE 4 adset 日預算合計 NT$368（上限 1,500 未超）；近 7 天（09-10～16）NT$6,137→11 名單；balance 1,618／cap 20,000 已花 11,042；被壓 adset 10 支掛 2,100（+CBO 3,400）。Google：餘額 1,811、本月 933、近 7 天 10 支全 0 轉換。**09-17 04:03 新開 `CX_V1_20260916_雙北桃園_7D` 兩平台各一支（流量型；Google 當日 2,658 曝／95 點／$150）——來源與媽祖紀錄待 Sir 說明** | `python3 ~/.cx468/meta_ads_cli.py get act_1693554028195795/campaigns --fields=name,status,daily_budget`；`~/.cx468/gads-venv/bin/python ~/.cx468/gads_accounts.py` |
| Threads | 佇列 **剩 12 則排到 10-01**（09-20 實算，算法 memory `project_threads_autopost`）；每日 12:30；`~/.cx468/threads_token_issued`＝2026-09-18（若該日續期成功，到期約 11-17；T9 要改讀 API 真值）；本機 `threads_token.txt` 仍是死檔 | Render env `THREADS_ACCESS_TOKEN` 打 `graph.threads.net/v1.0/me` |

⚠️ **三個路徑陷阱**（不變）：
1. 網站程式碼在 `~/cx468-web/`，**不在 iCloud 專案夾**；`行銷產出/`、`知識庫/`、`制度/` 在 iCloud 專案夾。
2. LINE bot 查驗一律用 `~/cx468-linebot`。
3. 本機測試會掃到**別的 session 的未追蹤檔**（本 session 兩次被弄紅）：閘門一律跑在只含已追蹤檔的樹上——`git ls-files -z | rsync -aq --from0 --files-from=- ./ $T/`（非 ASCII 檔名必須 -z/--from0）。

🚨 **commit 配方**：pre-commit hook 會把工作樹所有已修改 html 掃進你的 commit（`.git/hooks/pre-commit:30`）。平行 session 施工中要用 `git add <自己的檔> && git commit --no-verify` → 跑 `update_schema_datemod.py`＋`update_sitemap_lastmod.py` → `--amend --no-verify`。單人時 `git add -u` 即可，但先 `git status -s` 確認 M 全是自己的。**所有 repo 禁 `git add -A`。**

## 二、可複用資產／程序（8/29 版保留＋9/5 更新）

### 🆕 Better 對拷專案的入口（9/4 建立，9/5 更新）

- **拆解報告**：iCloud `行銷產出/策略簡報/2026-09-04-better.com官網拆解.md`（§3 逐頁 section 表、§5 色碼/字級/按鈕/卡片/間距實測、§8 不能照抄的 11 條）。143 張截圖在 `行銷產出/視覺風格/better.com-2026-09-04/`。
- **範本正本**＝`sale-leaseback.html`。變體：debt-consolidation（表格）／corporate-checkup（表單／五步驟）／services（總覽交錯列）／xinbei-sale-leaseback（文章型 h2 映射）／**area-xindian（在地頁：SVG 位置圖＋地圖 iframe＋實價登錄深藍帶＋租金長條圖＋時程＋POI 卡格，五頁段落配色以它為基準）**／**taipei-land-value-tax-guide（長文教學型：級距表 bt-table、範例卡、bt-dark-card 金鈕 CTA）**／**new-taipei-land-value-tax（試算器型：試算器整段原樣進白底 section、JS 零改動；必留三行 CSS 見批次規格）**。
- **nav.js**：淺色 `<div id="nav" data-theme="light"></div>`＋`<script src="nav.js"></script>`，body padding-top 64/58；不帶屬性＝深色。**`data-cta="line"`＝二胎合規模式**（兩顆免費評估鈕改 LINE）。不載 style.css；**不要改 style.css 的 nav 選擇器**。
- **派工規格**（iCloud `行銷產出/技術記錄/`）：
  - `2026-09-05-better版型派工共用規格.md`（硬規則 9 條＋自驗＋回報格式；9/5 已改為「hero 圖／眉標由 prompt 逐頁指定」＋規則 9「script／iframe 全留」）
  - `2026-09-05-地價稅試算器頁批次規格.md`（試算器型專用：script diff 指令、id 計數、handler 集合）
  - `2026-09-05-小工具頁批次規格.md`（第八批：段落→版型對照表＋自驗；主對話另有 scratchpad `calc_verify.py` 思路＝HEAD 版與新版起兩個 http.server、填同值比所有帶數字 id 的文字）
  - ⚠️ **生成頁陷阱**：lvr-observatory／lvr-presale／lvr-rental 由 `scripts/lvr/build_*.py` 產，`.github/workflows/lvr-weekly.yml` 每月 2/12/22 重跑會整頁覆寫；三頁模板 9/5 皆已移植（`LVR_HTML_DEST`／`LVR_PRESALE_DEST`／`LVR_RENTAL_DEST` 可覆寫，本機驗法：`_cache/` 用 `lvr-data/*.json` 建 stub、重生成 diff 只剩時間戳）。**cx_radar_v4_demo.html 也是生成頁**（indicators workflow 每日改寫），不套版。
  - 派系列頁時 prompt 直接給「段落→底色／卡片／寬度」對照表（第四批 5 頁曾各走各的，並排目檢才發現；memory `feedback_parallel_agents_same_choice`）
- **驗收腳本**（同夾；⚠️ `<page>` 一律**不帶 .html**，9/5 起帶了也會自動去掉）：`pw_check.py <base_url> <page>…`（sw/h1/nav 底色/眉標/styleCss/console）；`slices.py <out_dir> <page>…`（本機 :8765 桌機 2400px／手機 3200px 切片截圖，主對話 Read 目檢）；`lvt_verify.py <page>…`（試算器頁：與 HEAD 版填同樣數字比對輸出、手機 scrollWidth、<16px 輸入框數）；`scripts/verify_text_conservation.py <file>`（守恆）。
- **本機目檢**：`cd ~/cx468-web && python3 -m http.server 8765`，Playwright venv `~/pw/bin/python`。Google Maps iframe 在 localhost 回 403（金鑰限 cx468 網域）＝正常，線上不會；LINE QR 在 full-page 截圖裡空白＝lazy 未觸發，非壞圖。
- Token 對照（Better → 鋮馨）：頁底 #F7F5F0、卡片白、次底 #F2EFE8、深帶 #1B2F4A、主 CTA #2F5B8F（hover #26497A）、header CTA 金 #C8945A、眉標 #9A6D3A、文字 #1B2F4A／#5A6878、邊線 #E2DED4、淡藍帶 #EEF2F7；全頁 Noto Sans TC；CTA 64px 圓角 8px；卡片 8px＋shadow-md；section 64/80/96。

### 🆕 本機預覽與真回覆測試（8/29 建立）

```bash
cd ~/cx468-web && python3 -m http.server 8931
cd ~/cx468-linebot && ANTHROPIC_API_KEY="$(cat ~/.cx468/anthropic.key)" PORT=5001 .venv/bin/python app.py
```
chat-widget 只在 `localhost`／`127.0.0.1` 打 :5001，其餘打 Render 正式站。`/chat` 收 `{"messages":[{"role":"user","content":"…"}]}`，**不是** `{"message":"…"}`。

### 🆕 headless 目檢管線（8/29 建立，playwright MCP 被佔時的備援）

```bash
CH="$HOME/Library/Caches/ms-playwright/chromium-1234/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
"$CH" --headless=new --disable-gpu --no-sandbox --remote-debugging-port=9333 --user-data-dir=/tmp/cdpX --window-size=1440,900 about:blank &
```
三個雷（memory `feedback_cdp_screenshot_traps`）：setDeviceMetricsOverride＋截圖會 hang；`/json/new` 可能拍到別的分頁；反詐 modal 先 `localStorage.setItem('cx_antifraud_v1', String(Date.now()))`。

### 🧩 ai-bar.html（8/29）

`<div data-include="ai-bar" data-ai-q="問題一？|問題二？|問題三？"></div>`；顏色自動讀 h1；🔴 元件內用 `document.querySelector('[data-include="ai-bar"]')` 取屬性，**不能用 `currentScript.closest()`**。

### 🔑 Meta 權杖（永不過期）

`~/.cx468/fb_system_user.token`（廣告）／`~/.cx468/fb_page_system.token`（粉專）。
```bash
T=$(cat ~/.cx468/fb_system_user.token)
curl -sG "https://graph.facebook.com/v21.0/act_1693554028195795/insights" --data-urlencode "access_token=$T" --data-urlencode "level=campaign" --data-urlencode "fields=campaign_name,spend,impressions,inline_link_clicks,ctr,frequency" --data-urlencode "date_preset=today"
```

### Google Ads 查法（無 API 金鑰，用指令碼）

後台 → 工具 → 大量操作 → 指令碼：`CX468-設定稽核`、`CX468-地區解碼`（原始碼在 `行銷產出/Google廣告/`）。🔴 新北市 `1012825`、臺北市 `9040379`；出現 `2158` 或 Country ＝鎖到全國。**「查看頁」會假顯示，一律以指令碼／API 為準。**

### GA4

`~/cx468-ga4-daily/cx468-ga4-945f85bddfbd.json`，資源 `535643191`。付費流量判讀對照：`inherit-era-img3` 平均參與 1.0 秒、跳出 92.3%＝誤觸；Google 搜尋 13.1 秒、自然搜尋 30.4 秒。

### 📞 回電 SOP

`行銷產出/LINE/2026-08-14-以房養老來電三句話SOP-FINAL.md` v2。四道閘門：①身分切割 ②「我幫你問問看銀行」禁語 ③轉場售後回租四條件全中 ④**弱勢否決凌駕**。

### 期限型任務登記表

`~/.cx468/pending_reviews.json` → 三日健檢檢查4 自動倒數，逾期推 Telegram。**有硬截止又沒系統在盯的任務一律登記。**

## 三、未竟任務

### 🟢 2026-09-18～19 導覽列主題分頁改造 B0–B5——**已上線（17 頁，cloud-code-d0 建造，HEAD `cb51af5`）**
- 計畫正本 `行銷產出/策略簡報/2026-09-17-導覽列主題分頁改造計畫.md`；模板契約 memory `project_topic_page_template`（topic.css／inline-form 契約／插圖風格常數）。
- 上線鏈：B0/B1 `8339a2e`（private-to-bank 試點＋頁內 2 欄表單）→ Block 3／6／0 `803c315`・`63b2f6f`・`2315351`（自然人憑證一張卡、滿版轉換區＋地址三步選擇、頂部表單同步）→ B2 `abcf5f3`（debt-consolidation／second-mortgage／xinbei-debt-consolidation＋插圖）→ B3＋B4 `ddfbefb`（inherited-property／article-inherited-co-owned-house-stuck／sale-leaseback；corporate-checkup／corporate-loan）→ B5 `be96724`（小工具／案例 8 頁底部橋接區，媽祖 09-19 複核通過）。
- 09-20 00:2x 線上驗：debt-consolidation／second-mortgage／inherited-property／corporate-checkup／private-to-bank 皆 200，`data-include="inline-form"` 命中；`grep -l 'data-include="inline-form"' *.html | wc -l` → 17。
- **未收尾（09-19 會議 §六硬期限，09-20 00:2x 取證）**：`xinbei-debt-consolidation.html` ai-bar 0（要 2）；`llms-full.txt` 無 xinbei（llms.txt 有）；xinbei sitemap lastmod 停 09-17（debt-consolidation 已 09-19）；全站「實際成數」仍 4 頁（要改「實際價金比例」，連 linebot T0 一起）；新北在地頁 HowTo step1/2 反 doorway 改寫未驗。
- d0 手上 8 檔（媽祖兩項全站裁示）見第一節工作區列，它自己 push。

### 🟢 2026-09-14 矩陣擴張第一批（服務軸 6 頁）——**已部署**（另一 session 推 `89d002f` 09-14 14:08，線上 200）

**Sir 09-14 拍板**：矩陣「全做」，順序 ①服務軸 → ③企業健檢 → ②地區軸二胎複製。本批＝①的三條新系列首篇＋售後回租擴 3 支。

| 頁 | 系列 | 骨架（反 doorway 各不同構） | 媽祖 |
|---|---|---|---|
| `yonghe-sale-leaseback.html` | 售後回租擴 | 時間軸：房老→人老→三種處境→估價限制→都更等待 | ✅ |
| `banqiao-sale-leaseback.html` | 售後回租擴 | 三欄屋主對照：舊城老公寓／新板·江翠大樓／浮洲 | ✅ |
| `sanchong-sale-leaseback.html` | 售後回租擴 | 兩張地圖（水／重建）→ 2×2 落格 | ✅（hero 用 `img/gen-sanchong.jpg` AI 圖＋「情境示意圖」，Sir 未裁是否換實景） |
| `banqiao-debt-consolidation.html` | 貸款整合**首篇** | 一個月的扣款日曆 | ✅（一次過） |
| `zhonghe-private-to-bank.html` | 民間轉銀行**首篇** | 帳本兩欄（左：付出去的／右：本金還剩） | ✅ |
| `zhonghe-corporate-checkup.html` | 企業健檢＋媒合**首篇** | 三份文件 × 三種中和公司 | ✅ |

**部署配方**（已執行；留作下一批範本）：`python3 <scratchpad>/deploy_matrix_batch1.py`（sitemap 六筆、llms.txt 六行、`sale-leaseback / debt-consolidation / private-to-bank` 三樞紐 chips 反向內鏈；每步 assert，已乾跑）→ `python3 scripts/ci_check.py` → `git add` 指名 11 檔（6 新頁＋sitemap.xml＋llms.txt＋3 樞紐）→ `git fetch && git rebase origin/main` → push → curl 六頁 200 → 給 Sir GSC 清單：
`https://cx468.com.tw/{yonghe,banqiao,sanchong}-sale-leaseback.html`、`https://cx468.com.tw/banqiao-debt-consolidation.html`、`https://cx468.com.tw/zhonghe-private-to-bank.html`、`https://cx468.com.tw/zhonghe-corporate-checkup.html`。

**素材正本**：`行銷產出/技術記錄/2026-09-09-矩陣擴張素材包.md` v5.1（永和／板橋／三重／中和／板橋整合，全官方出處＋不可寫清單；後續各區擴頁只准用這裡的數字）。

**本批立下的定例（已寫 memory `project_local_page_series_rules`）**：合規脊椎句豁免相似度但子段要量；同系列共用 FAQ 題只留一頁；「不是投資方」禁寫（老闆 07-06 鋮馨會自任承買方）；官方引句內「約」可留、引句外去「約」成確數＝失真；⭐示意例不代入成數／利率／核貸機率；⭐兩機關兩期別不合成一句；⭐隱私／保存期只准逐字抄主頁（企業頁「180 天自動清除」被退，正本「結案後 6 個月內刪除」）；貸款類頁「最低」零出現不開白名單；FAQ 標題禁裸詞（rich result 會摘）；通用型 FAQ 每頁上限三題。

**追蹤**：六頁都掛 `consultation-tracking.js`（不用舊 inline 監聽，避免雙重上報），CTA 帶 `data-link-location`；貸款類三頁 `.bt-btns` 掛 `data-consultation-need`（private_debt／private_to_bank／corporate_loan），`pageNeeds` 表不必改。

**待辦（本批順帶發現，未動）**：
1. ~~三頁行情口徑不一~~ ✅ pf3 `7a03add` 三頁統一 4G；09-17 腳本加土城（五區）。
2. ~~三支 property-finance 88–91% 同構~~ ✅ pf3 `7a03add` 重寫，≤0.20。
3. ~~`b386ad9` 換深藍 hero 後 `.bt-meta`~~ ✅ 第三批 `540c425` 已修（31 頁內聯規則）——原文：`.bt-meta`（日期／作者／閱讀時間列）對比 2.2:1，26 頁含 xindian 全站模板問題 → 設計線修 `.bt-hero .bt-meta` 色。
4. ~~企業兩樞紐無站內連結區~~ ✅ 第二批 `07f9a42` 已加 chips。
5. ~~兩組座標並存~~ ✅ `2c97ec0`（letter-close）：schema 值是 Google 商家檔案實際值（memory `reference_nap_canonical`），錯的是 77 頁 meta＋3 支產生器模板，已全改；areaServed 三重 ✅ `540c425`。
6. ~~企業健檢擴 5 區~~ ✅ `07f9a42`；~~服務軸補滿~~ ✅ `f4c7ae2`；~~地區軸二胎複製~~ ✅ `c5d6789`（letter-close，見下方 🟢 09-18 節）。**矩陣「全做」三順位全部完成，只剩部署。**

**雷（本批踩到）**：研究型 agent「等工兵回報再彙整」＝零交付結束（三次），派工單尾固定加「查到多少先交多少」；平行 session 在建造中途推 `b386ad9` 換皮 138 檔，新頁抄舊 `<style>`＋`data-theme="light"` 會白 nav 壓深藍 hero——動手前 `git log -1` 看有沒有換皮 commit；建造者自驗相似度與媽祖複量差一倍（25.9% vs 48.3%），派工單數字現場量。

### 🟢 2026-09-14 矩陣第二批：企業健檢擴 5 區＋樞紐 chips（待辦 #4、#6）——**已部署**（`07f9a42`，Sir 15:5x 令部署；五頁線上 200、樞紐 chips／sitemap 7／llms 7 已驗、TG 已推；**GSC 五網址等 Sir 送**；上線 24h 內 `git log -1 -- *-corporate-checkup.html` 看誰動過）

| 頁 | 骨架（與首篇「三份文件×三種公司」及彼此互不同構） | 媽祖 |
|---|---|---|
| `banqiao-corporate-checkup.html` | 一筆工程款走五站（訂金→期中／保留款→發票時點→入帳／下包→營所稅） | ✅ 2 處小改已修 |
| `sanchong-corporate-checkup.html` | 健檢報告的五個燈號，各配「三重誰最常亮」 | ✅ 4 處已修 |
| `xinzhuang-corporate-checkup.html` | 退件通知倒推：說法→原因→文件→送件前 30 天 | ✅ 2 處已修 |
| `tucheng-corporate-checkup.html` | 整頁只談集中度（一家大客戶佔幾成） | ✅ 2 處已修 |
| `yonghe-corporate-checkup.html` | 沒有 401 表的公司（小規模營業人／查定課徵軌） | ✅ 一次過 |

**同 commit**：`corporate-checkup.html`／`corporate-loan.html` 加 `.bt-local` chips 區（待辦 #4）；三樞紐（含 zhonghe 首篇）chips 反向連 5 新頁；sitemap +5、llms.txt +5；`img/area/sanchong.jpg`（新北大都會公園）、`xinzhuang.jpg`（副都心）Commons 照＋credits。
**素材**：素材包升 **v5.2 §7** 指向同夾四檔 `2026-09-14-企業健檢五區素材-{A稅籍與統計,B三重新莊工業,C板橋土城永和工業,D普查110}.md`；媽祖報告 `2026-09-14-企業健檢五區媽祖把關.md`。五頁 584 個數字媽祖全回溯。
**驗收**：ci_check 172 檔 0；FAQ 同源 138/138；六頁兩兩 difflib 22–30%、section 零命中、FAQ 只剩隱私脊椎句（媽祖裁豁免，機掃要改「先剝脊椎句再比」）；本機 8 頁 200；桌機 hero 目檢 5 頁、手機 390 無整頁橫捲。
**部署配方**：push 後 curl 五頁 200 → 給 Sir GSC 清單 `https://cx468.com.tw/{banqiao,sanchong,xinzhuang,tucheng,yonghe}-corporate-checkup.html` → 三日健檢看 coverageState。已連同 `4c50d13`（Phase 3 配色 144 檔）一起上線。
**順帶發現、未動**：①首篇＋09-14 六頁 FAQ「＋」雙加號（`.plus::before` 與 literal ＋並存，b386ad9 帶進）→ 一支 sed；②企業系列 6 頁都不掛 ai-bar（樞紐有）→ Sir 裁要不要全系列補；③LocalBusiness schema `areaServed` 缺三重／新莊／土城（待辦 #5 同批）；④媽祖 §7.5 地標已補登素材包 §7；⑤研究型 agent 仍會「等工兵回報」結束，一催即交（memory 已有）；⑥新 memory `feedback_template_bugs_copied_by_builders`。

### 🟢 2026-09-15 矩陣第三批：服務軸補滿 6 頁＋待辦 #3／#10 三件——**已上線（09-17 23:07 隨 pf3 一起推，rebase 後 SHA 3b7f0aa／f4c7ae2；六頁線上 200）**（原文保留：`540c425` 機械四項 → `53f50ff` 六頁；Sir 令部署才推；**推的順序：本 repo 先推，再讓 cloud-code-78 的 `pf3-rewrite`（worktree `~/cx468-pf3`，三支 property-finance 重寫＋三支 SLB 4G 換數）rebase 推——它的 chips 連到本批新頁，反過來會 404**）

| 頁 | 骨架（與首篇及彼此互不同構，整頁 ≤30%／FAQ 逐題 ≤49%） | 媽祖 |
|---|---|---|
| `zhonghe-debt-consolidation.html` | 整合前的三張單據（信貸繳款單／卡帳單／民間借據）逐欄→整合後一張對帳單 | ✅ 深讀 5 處已修 |
| `yonghe-debt-consolidation.html` | 兩代同住的家：房在父母名下、債在子女身上，三種家庭配置 | ✅ 6 處已修 |
| `sanchong-debt-consolidation.html` | 月付吃掉薪水幾成：三情境（不寫百分比門檻） | ✅ 4 處已修 |
| `banqiao-private-to-bank.html` | 四個卡關點（本金→順位→鑑價→收入） | ✅ 次分區行情全刪 |
| `yonghe-private-to-bank.html` | 年齡與年期：人的年齡×房的年齡→三種家庭配置 | ✅ 5 處已修 |
| `sanchong-private-to-bank.html` | 分階段時間線（理清→部分轉→全轉），全頁不寫時長 | ✅ FAQ Q6 換題 |

**同批機械四項（`540c425`，目檢 14/14 過）**：`.bt-hero .bt-meta{color:rgba(242,239,232,.82)}` 31 頁對比 2.37→8.41（C 族內聯，不掛 theme.css）；FAQ 雙加號 9 頁 span 清空；LocalBusiness `areaServed` 73 頁統一 7 區（中和/永和/板橋/土城/新店/新莊/三重）；企業健檢 6 頁 hero 掛 `data-include="ai-bar"`（各頁專屬三題）。
**行情口徑**：六頁全用 **4G**（素材包檔尾「§6 行情 4G 口徑統一表」；正本 `技術記錄/2026-09-14-行情口徑統一-4G.md`；腳本 `~/.cx468/lvr/lvr_4g_unified.py`，重跑 `cd ~/.cx468/lvr && python3 lvr_4g_unified.py`）。**舊值（三重 43.0／67.0／3.9、永和 48.9／64.1、中和 43.9／60.5、板橋 84.9／44.5／69.9／37.5）判不可重現、全站禁用**；三支 SLB 頁的換數在 pf3-rewrite。115S3 季檔 10/1 出來要九頁一起重跑。
**媽祖報告**：`行銷產出/技術記錄/2026-09-14-服務軸補滿六頁媽祖把關.md`；兩裁決：人保「保人／連帶保人」、共同債務人「共同借款人」、物保「擔保品提供人」三詞三義各一說法；板橋次分區行情選刪。
**驗收**：ci_check 178 檔 0；FAQ 同源 144/144；fresh 驗收（內鏈 0 404／JSON-LD 36 區塊可解析／麵包屑 3=3／手機 390 無橫捲／console 0）。
**部署後**：curl 六頁 200 → GSC 網址審查清單 `https://cx468.com.tw/{zhonghe,yonghe,sanchong}-debt-consolidation.html`、`https://cx468.com.tw/{banqiao,yonghe,sanchong}-private-to-bank.html` → 三日健檢看 coverageState。
**順帶發現、未動**：①整合／轉銀行系列（含兩首篇）不掛 ai-bar，企業系列現在有——要不要全系列補，Sir 裁；②`area-*.html`、`financing-data.html` 的 `areaServed` 是自己的格式（3 區／5 區）未動；③`lvr-observatory/presale/rental` 本來就有 `.bt-hero .bt-meta` 規則；④待辦 #6 下一批＝地區軸二胎複製（Sir 排第三、風險最高）。
**雷（本批踩到）**：⚠️ 同一條交接信待辦被兩個 session 同時領走（property-finance 重寫），建造者互相覆寫一輪——派建造者前 `git status -s` 看 M 檔＋`ListAgents` 問對方在做哪條，重疊就讓（memory `feedback_parallel_session_moves_head_mid_diagnosis` 已補）；媽祖 agent 又一次「等工兵回報」零交付結束，一催即交（工兵之後自己也會回報到主對話，別重複派）。

### 🟢 2026-09-18 地區軸二胎複製（永和／土城）＋ geo 統一——**已上線（`9468a93`，Sir 00:5x 令部署；兩頁 200、about geo 1、樞紐 chips 2、sitemap 2、llms 2；TG 已推；GSC 2 網址等 Sir 送）**

**範圍定義**：七區二胎在地頁原缺永和、土城（土城只有 noindex 的 `lp-tucheng-second-mortgage.html`）；本批補齊 `yonghe-second-mortgage.html`、`tucheng-second-mortgage.html`，七區（中和／板橋／三重／新莊／新店／永和／土城）二胎頁全有。

| 頁 | 骨架（與六支二胎頁＋同區既有頁互不同構） | 媽祖 |
|---|---|---|
| `yonghe-second-mortgage.html` | 先翻謄本他項權利部：三種起點（空白／清償未塗銷／餘額仍在）→ 最高限額抵押權「擔保債權總金額≠餘額」→ 三型態×三屋齡世代殘值算式（變數留空） | ✅ 必修 6＋建議 5 全套用（head 頻率語改條件句、BreadcrumbList 三層、meta 120 字、四區對照帶 n、起點一內鏈 yonghe-home-loan） |
| `tucheng-second-mortgage.html` | 屋齡卡在 30–40 年那一層：40 年+ 占比五區裡數字最小、老屋集中 30–40 年 → 殘值與可承作年期一起看；分區降為一段非脊椎（媽祖：已到上限，複查別再加） | ✅ 必修 2＋建議 6 全套用（FAQ Q6 絕對句、BreadcrumbList 三層、35／45 示意屋齡改層界、「不在住宅」絕對句、DefinedTerm 內規口吻、引句補全） |

**素材**：永和只用素材包 §2＋§6（§6 永和列 09-18 補齊總價中位／屋齡中位／逾 30 年九欄，§0 geo 行改對）；土城 `技術記錄/2026-09-17-土城二胎素材.md`（關公，8A–8H，31 條 .gov.tw 出處；8H 不可寫 20 條）；素材包 §8 指向。行情 4G 五區（`scripts/lvr/lvr_4g_unified.py` TOWNS 加土城，四區數字不變；`技術記錄/2026-09-14-行情口徑統一-4G.md` §④）。**115S3 於 10/1 發布後：三支 SLB＋第三批 6 頁＋本批 2 頁＝11 頁一起重跑。**
**媽祖報告**：`技術記錄/2026-09-17-地區軸二胎永和土城媽祖把關.md`（兩節，含數字回溯表）。裁決三點記在 memory `project_local_page_series_rules`（09-17/18 追加六條：麵包屑層數、head 零頻率語、meta ≤120、對照帶 n、同骨架不跨區、同腳本欄位要登 §6）。
**接線（同 commit）**：sitemap +2、llms.txt +2、`second-mortgage.html` 樞紐 chips +2、永和 5 頁＋土城 2 頁同區 chips 各 +1（`yonghe-home-loan.html` 無 chips 區未動；`tucheng-property-finance.html` 加在「延伸閱讀」行）。
**驗收**：ci_check 181 檔 0；FAQ 同源 147/0；audit-regression 18/18；相似度 永和 11 列整頁 ≤0.21／逐段 ≤0.53／FAQ ≤0.45，土城 10 列整頁 ≤0.14；禁語 grep 兩頁各只剩 Organization 脊椎句「不保證每案均可向全部機構申請」（媽祖裁豁免）；桌機 1440＋手機 390 目檢（`.playwright-mcp/{yonghe,tucheng}-sm-{desktop,mobile390}.jpg`）無橫捲、console 0；consultation-tracking.js 各 1、tel:0222490517 各 3、geo 各 3。
**部署配方（✅ 09-18 00:5x 已照做：ff 合併→push→CI/Pages success→curl 全 200→TG→worktree 收）**：`cd ~/cx468-web && git fetch && git log --oneline origin/main..letter-close`（看清楚只有本批 3 個 commit）→ `git merge --ff-only letter-close`（若 origin/main 已前進：先 `git -C ~/cx468-letter rebase origin/main` 再 ff）→ `git push` → `gh run list -L 2` 兩者 success → `curl -s -o /dev/null -w '%{http_code}\n' https://cx468.com.tw/{yonghe,tucheng}-second-mortgage.html` 皆 200 → `curl -s https://cx468.com.tw/about.html | grep -c '24.9944428;121.4900325'` → 1 → `python3 ~/.cx468/tg_notify.py`（memory `feedback_push_deploy_urls_to_telegram`）→ 給 Sir GSC 網址審查清單：`https://cx468.com.tw/yonghe-second-mortgage.html`、`https://cx468.com.tw/tucheng-second-mortgage.html`（geo 77 頁不必送，等自然重爬）→ `git worktree remove ~/cx468-letter && git branch -d letter-close`。
**順帶發現、未動（Sir 裁或另批）**：①`xinzhuang／sanchong／banqiao-second-mortgage.html` BreadcrumbList 2 層 vs 可見 3 層（媽祖 09-17 查到），一支 python 可修；②「閱讀時間約 8 分鐘」全站 32 頁版型 chrome 含「約」，要拿要一批；③`llms-full.txt` 沒有任何矩陣頁（`grep -c yonghe-sale-leaseback llms-full.txt` → 0），只有 llms.txt 有；④手機 390 有 13.3px 的 input 來自共用 include（footer／聊天元件），違 iOS 16px 規則（memory `feedback_ios_input_zoom_16px`），非本批檔。
**雷（本批）**：①派工單抄素材包數字前要現場 grep——我寫「§6 有 1,400／48.3／99%」但檔案沒有那些欄位，媽祖判派工單與檔案不符（memory `feedback_dispatch_prompt_must_requote_from_current_file` 又中一次）；②zsh 不分詞：`F=$(grep -l …); sed … $F` 會把整串當一個檔名（File name too long），要 `grep -l … | xargs sed`；③update_schema_datemod.py 會把「git 日期已變但 dateModified 沒跟上」的別人頁一起拉進你的 commit（本批 2c97ec0 多帶 13 頁 area-*／property-finance／land-value-tax-guide 的 dateModified 09-14→09-17），屬 hook 設計行為、要在 commit 訊息講。

### 🟢 2026-09-17 pf3-rewrite 已上線（`7a03add`，Sir 23:0x 令部署；含第三批 3b7f0aa／f4c7ae2／2449dd2 一起推；12 頁 200、sitemap 含 6 新頁、TG 已推 GSC 清單）

**做了什麼**（09-14 夜 cloud-code-78 施工，09-17 部署）：
- `{yonghe,banqiao,sanchong}-property-finance.html` 反 doorway 重寫：整頁相似 0.88–0.91 → ≤0.20（逐段最高 0.464）；骨架各異（退件四關決策樹／順序題／三種資金時間表）；地標 12／20／12；素材包 v5.2 數字逐句帶期別機關、不引坪價；防詐一句＋內鏈；CTA LINE＋`tel:0222490517`；同區服務 chips（含 6 新頁）。規則全在 memory `project_local_page_series_rules`。
- `{yonghe,banqiao,sanchong}-sale-leaseback.html` 行情統一 **4G 口徑**（115S1+S2，關公重跑，`技術記錄/2026-09-14-行情口徑統一-4G.md`）：三重「三區最低」不成立→改真實敘述（板橋 45.0＜三重 45.6＜永和 51.7）；不可重現的板橋新板／舊城數字與永和透天列已刪；口徑句三頁一致。腳本 `scripts/lvr/lvr_4g_unified.py`，資料 zip 在 `~/.cx468/lvr/`；**115S3 於 10/1 發布後，所有引用行情的頁（含第三批 6 頁）一起重跑**。素材包尾「## 6 行情 4G 口徑統一表」為四區唯一正本，舊值不得再用。
- 媽祖報告 `技術記錄/2026-09-14-pf3重寫與4G口徑媽祖把關.md`（必修 2＋建議 8 全套用）；fresh 目檢 12 張通過。

**重驗指令**：`curl -s https://cx468.com.tw/yonghe-property-finance.html | grep -c '第一關｜年齡與年限'` → 1；`curl -s https://cx468.com.tw/sanchong-sale-leaseback.html | grep -c '只高 1.3%'` → 3；`python3 scripts/ci_check.py` → 179 檔 0。

**閉環待辦**：①GSC 12 網址（TG 09-17 23:1x 那則）→ 三日健檢看 coverageState；②`anti-fraud-modal.html:124` 無 utm／gclid 自然流量自動全屏彈窗——手機插頁式判罰風險，另案查；③精進會議 12:00 cron 是 session-only，09-07～09-16 零份會議＝沒 session 活著就不開，改 launchd／雲端 routine 交 Sir 裁。

**等 Sir**：①GSC 12 網址審查（TG 09-17 23:1x）；②精進會議排程改制（launchd／雲端 routine）裁示；③首頁 `index.html` 自帶 footer 仍列 0931 要不要改 0958；④三重／新莊 AI 配圖換不換實景；⑤`anti-fraud-modal.html:124` 自然流量全屏彈窗要不要另案查。

**雷（本批）**：平行 session 在共用樹整檔覆寫半成品＋其 pre-commit 掃走 M 檔 → 成果一律搬 `git worktree` 分支、共用樹 `checkout --` 還原、sitemap lastmod 留到 rebase 後（memory `feedback_parallel_session_moves_head_mid_diagnosis` 09-14 追加）。

### 🟢 Phase 3 已上線（`4c50d13`，7c45acf push，theme.css／footer／撥號 CTA 線上驗過）

做了什麼見第一節「設計」列。**push 後要驗**：`curl -s https://cx468.com.tw/theme.css | head -c 80`（200 且有內容）、`curl -s https://cx468.com.tw/about.html | grep -c theme.css` → 1、無痕開 about／article-second-mortgage／apply／bad-credit-mortgage 看 footer paper 底與金鈕；然後給 Sir GSC 清單（11 個電話 CTA 頁優先，A 族零文字頁不必送）。
**沒做／順帶發現**：①首頁 `index.html` 自帶 footer 仍列 0931（非 0958 經理鄭小姐）——首頁是 Sir 親審版，未動，等他裁；②全站 40 頁正文仍有「0931-087-996」可見（政策是降次要不是刪，未動）；③`.art-tag` 藍色膠囊（9 頁白底文章）沒改，與主頁不衝突。

### ~~🔴 第一順位：全站配色對齊主頁 Phase 3~~（已做，原規劃留檔）

現況差距在 **A 族 59 頁**（載 style.css 的文章／apply 等）與 **144 頁共用的 footer.html**：nav 已深、但內文仍系統字體、標題 600、CTA LINE 綠、頁尾舊版深藍。分析員估 6–7 小時，零文字變動、不過媽祖。

依序：
1. **footer.html 改主頁 paper 版**（一檔通吃 144 頁，最高槓桿）。主頁自帶 `.foot`（paper 底、ink 字、4 欄、Serif h4）——抄它的結構與 CSS 進 footer.html，**保留** sticky CTA、`data-link-location`、noindex meta、兩支電話。改完先目檢 10 頁再全站。
2. **style.css**：body 字體 系統→`'Noto Sans TC',…`；`.btn-green/.btn-line` LINE 綠→金；51 頁 fonts link 只載 Serif 要加 Sans（sed）。
3. **theme.css 覆寫層**：A 族內聯 `<style>` 全在 style.css 之後，同特異性蓋不過——在 `</head>` 前加一支 `theme.css`（`.art-hero h1{font-weight:900}`、`.page-hero` 深藍改森林藍漸層等）。
4. 生成頁（`cx_radar_v4_demo`／`radar-index`／`lvr-*`）改模板不改產物（memory `feedback_generated_pages_overwritten_by_workflow`）。

**工具與閘門**（本 session 驗過）：換皮腳本邏輯在 memory `project_homepage_green_rebuild`（`scratchpad/phase2.py` 已隨 session 消失，照 memory 重寫 10 分鐘）；零文字閘門 `python3 scripts/check_text_integrity.py . $(git diff --name-only -- '*.html')`（zsh 要 `$(...)` 才斷詞）；staging：`python3 -m http.server 8765` 在乾淨樹上跑，playwright 截 `second-mortgage／contact／about／article-second-mortgage／apply` 桌機＋手機看過再推。
**雷**：ai-bar 膠囊等 include 注入的樣式會蓋掉同特異性規則，覆寫要 `.bt-hero .aib .aib-chips button{…!important}`；矩陣 🟢 待辦 #3 的 `.bt-meta` 深底對比 2.2:1 也在這批一起修。

### 🔴 第二順位：讓 SEO 生出「打電話進來的客戶」（Sir 09-09 定調，狀態更新）

| 段 | 09-09 | 09-14 現況 |
|---|---|---|
| 量得到 | 10 頁沒 `phone_click` | ✅ **PR#5 已補 36 盲頁**，真瀏覽器驗過事件進 GA4 |
| 按撥號 | 電話被 LINE 蓋過 | ✅ `4c50d13` 已上線：12 群組加「撥打 02-2249-0517」＋3 頁 0931→02，媽祖 PASS；GSC 11 頁清單 Sir 16:2x 收到（TG） |
| Local Pack | GMB 1 則評論 | 🔴 未動，只有 Sir 能做（第四節 #8） |
| 量表現 | 三支新頁等 2–4 週 | 09-09 上線至今 5 天，還不能判；`~/cx468-ga4-daily/gsc.py`＋GA4 `phone_click` 依 landing page |
| 台北 12 區 | 不建議 | 不變 |

**接手前必讀禁忌**（不變）：當舖鉤子詞 14 類全禁；二胎場景禁「免費評估」；在地頁走反 doorway 定例（memory `project_local_page_series_rules`）；`lvr-data/雙北全區排名_近180天.csv` 停更 05-29，當期正本 `排名_w180.json`；DeerFlow 派工要拆小段＋`recursion_limit`。

### 🟡 順帶發現、未動（Sir 裁或另案）

1. **90 頁 GA config 沒濾 query/fragment**（只有掛追蹤器的 60 頁有濾）——隱私與 analytics 乾淨度，一支 sed 可解，但要目檢 GA 沒斷。
2. 矩陣 🟢 待辦 #1–#6（口徑統一／三支 property-finance 同構 88–91%／`.bt-meta` 對比／企業兩樞紐無 chips／geo 座標兩組並存／企業健檢擴 5 區）。
3. 「成數最高 9 成」未說明一二胎合計（09-09 媽祖提，全站 9 處同型）。
4. nav.js 的 `data-cta="line"` LINE 變體已被 5c66121 拿掉，`ctaLine` 成死變數、L122 註解過時（講一聲，未動）。
5. `codex/verify-live-20260911` 分支殘留 1 個 commit（純驗證腳本），可刪。
6. lvr 圖表 PNG 與社群圖卡仍紅系（`scripts/lvr/make_charts.py`／`make_social_cards.py`）。
7. `land-value-tax-calculator.html`「其他縣市陸續建置中」已過時（需媽祖）；`affordability-calculator` 無免責尾注。
8. linebot：隱藏號碼來電逐通建新 person 灌漏斗（`crm_calls.py:119-125`）；`privacy-policy.html §6` 沒提電話管道。

### 日常常態

- 每天 12:00 精進會議（session 級排程，每個 session 用 CronCreate 重設）——**最新正本 `行銷產出/精進會議/2026-09-19.md`**（含 `2026-09-19-媽祖覆核.md`），其 §六＝下一場 Step 0 基準、§八「下次先驗五件」。09-17 §六硬期限現況（09-20 00:2x 取證）：新聞卡 ✅ `03e9d3e`、Threads ≥14 ✅（現剩 12 到 10-01）、週報 W37＋W38 ✅ 09-19 補寫、p2a 三修 🟡（GO 拆除＋FAIL 印原因已做，排程 17:15 未改＝T8）、**T0 小鋮「最低」雙護欄 ❌ 未動（`~/cx468-linebot/app.py:1844/1931/1941` 三處原樣，HEAD `37ed7f6`，期限 09-20）**。09-19 §六今日／明日硬期限：B2 sitemap ✅、llms.txt 接入 ✅、xinbei ai-bar ❌、「實際成數」❌ 4 頁、EP31+／新北 HowTo 未驗、iPAS Sir 09-22。
- 三日健檢 `com.cx468.healthcheck` 會推 🔴 到 Telegram——**收到要有人接**（memory `feedback_act_on_telegram_alerts`）；09-08 那則還躺著「Meta spend_cap 決策逾期」「週報監控瞎了」等 4 條。
- Threads 12:30；p2a 17:15（敏感稿要人回 GO，memory `feedback_human_go_gate_deadlocks_pipeline`）；`cx468-crawl` 每 2 小時。
- 換新聞卡前 `git log --oneline -5 -- radar-index.html` 算服役天數。

## 四、等使用者的事項

0. 🔴 **GSC 送 2 網址**（09-18 已上線）：`https://cx468.com.tw/yonghe-second-mortgage.html`、`https://cx468.com.tw/tucheng-second-mortgage.html`（TG 09-18 00:5x 那則）；之後三日健檢看 coverageState。原「等 Sir 五項」（GSC 12 網址／精進會議排程改制／首頁 footer 0931／三重新莊 AI 配圖／anti-fraud-modal 自然流量彈窗）不變。
0-1. 🔴 **待裁清單以 `精進會議/2026-09-19.md` §六「🔴 Sir 決策」九項為準**（新增：Meta 11 支 adset 自身 ACTIVE 未爆彈、Google 餘額 10/02 見底、private-to-bank-search 零曝光查或關、`Chengxin_V1_Final_4K.mp4` 誤傳翻舊帳頻道建議下架、翻舊帳 09-22 斷更、Anthropic Admin key）；09-17 六件仍未答：①Meta spend_cap（逾 29 天，不回＝維持）②精進會議觸發改 launchd／雲端 routine ③CX_V1_20260916 誰建的、過媽祖沒（09-20 滿 3 天要決定續停）④anti-fraud-modal 三選一（已擴散 145 頁）⑤反詐文／EP15／C-v3＋比特幣起源 private＋銀行條文封存否 ⑥整合／轉銀行系列補 ai-bar 否。
1. 🔴 **GMB 評論 1→20**（第二順位③，只有 Sir 能做）：「新北 房屋二胎」Local Pack 第 1 名 17 則、第 2/3 名 0 則照樣上榜。⛔ 商家名不塞關鍵字、類別維持「不動產管理服務」。
2. 🔴 **Telegram 三日健檢的 🔴 要有人接**：09-08 推播列了「Meta spend_cap 決策逾期 18 天」「行銷週報檢查失效（launchd 無 iCloud 權限）」「銀行條文存證複查」——本 session 只修了 p2a 那條。
3. **GSC 催收**：`docs/2026-09-09-GSC待送清單-額度滿順延.txt`（12＋6 條，09-14 已追加 contact／corporate-loan／sale-leaseback-guide 等）；矩陣 6 頁清單在第三節 🟢——**Sir 09-14 14:2x 已逐一送「網址審查→要求建立索引」**；**第二批 5 頁 `https://cx468.com.tw/{banqiao,sanchong,xinzhuang,tucheng,yonghe}-corporate-checkup.html` 16:2x 上線，等 Sir 送**，下一步是三日健檢看 coverageState＋lastCrawlTime（memory `feedback_indexed_but_stale_crawl`），別再重送。Sitemap 欄只放 sitemap.xml。
4. **Anthropic 帳務**：auto-reload 未開、無 Admin key、9 服務共用一把 key（09-08 起未變）。
5. **配圖要不要換真人照片**：三重／新莊／三重售後回租用 AI 生成圖（memory `project_photo_library`：老闆偏好真人）。未擋上線。
6. **`cx468-crawl` 一天 12 次要不要降頻**（不花 API 錢，只違「一天不超過三次」原則）。
7. **PR#5 之外的 GA4 事件設定**：`phone_click`／`line_click` 在 GA4 是否已標關鍵事件、landing page 維度切得出來（memory `feedback_ga4_import_needs_conversion_category`）——站上發得出，後台我看不到。
8. 名單回電 SOP、合一地政士洽談、企業貸款專案三處不一致（8/14 起未變）。
10. ~~**矩陣第二批順帶三件待裁**~~ ✅ 三件 `540c425` 全做（Sir 09-14 令「1＋2＋3＋4」）；原文：（16:3x 報過、未動）：①首篇 zhonghe＋09-14 六頁 FAQ「＋」雙加號（新 5 頁已修，舊 7 頁一支 sed：把 `<span class="plus">＋</span>` 改空 span）；②企業系列 6 頁都不掛 ai-bar（樞紐有）要不要全系列補；③LocalBusiness `areaServed` 缺三重／新莊／土城（併待辦 #5）。
9. ~~0958 上不上官網~~ ✅ 09-14 定：上，稱「經理鄭小姐」。~~企業貸款頁留不留~~ ✅ 留，健檢在前。~~售後回租兩套定義~~ ✅ 統一 A。~~「20 年」主詞~~ ✅ 全站＋跨 repo 已改。

## 五、本 session（2026-09-14 00:48 → 02:4x）做了什麼

### 5-1 審 09-11～13 另一 session 的 153 檔（4 個審查員＋自己重算）
PR#3／#4 合併內容全審：合規禁語全是闢謠語境、FAQ 同源 127/127、內鏈 0 斷、隱私乾淨、linebot 電話進線零紅字（18 測試過）。抓到的真問題：**PR#5（36 頁追蹤斷掉）沒合併**、0958 私人手機上了 contact 可見面＋schema、`corporate-loan.html` 撞 08-24 令、第七節逐字句被改寫兩套定義並存、「39 家合作」→「曾送件」76 檔無記錄。Sir 的裁示把後四項變成政策（見四節 #9）。

### 5-2 落地四項裁示（`c919489`）＋合併 PR#5（`41763c8`）
細節見第一節表。跨 repo：fb-news-bot `138ab9b`（p2a 模板 nav.js、org schema 主詞／電話）、linebot `37ed7f6`（小鋮提示詞）、ga4-daily 推出卡了 11 天的 `a74f06c`。CLAUDE.md 第一／二／七節同步改。

### 5-3 全站配色對齊主頁 Phase 1–2（`b386ad9`，134 檔，零文字變動）
三族量化→staging 截圖→Sir 看過→推。Phase 3 見三節第一順位。

### 5-4 CI 修（`65b192b`）
`cx_radar_v4_demo.html` 每日重生蓋掉 PR#5 的追蹤器 → 改 `gen_radar_v4.py` 模板；矩陣 6 新頁 GA config 去參數。

### 5-5 更正自己 09-09 的一句話
「p2a 掛 7 天沒人知道」錯——三日健檢 09-05／08／11 三次都推了 🔴 到 Telegram。監控沒瞎，是告警沒人接。

### 5-6 新寫 memory
`feedback_constitution_wording_loosened_seo_first`（文字放鬆·SEO 為主）、`feedback_parallel_session_moves_head_mid_diagnosis` 追加（別人未追蹤檔弄紅本機測試→乾淨樹閘門）、`project_homepage_green_rebuild` 追加（換皮 token／Phase 3 清單）、`reference_nap_canonical`／`project_corporate_checkup` 更新。

## 六、本 session（2026-09-14 14:3x → 15:1x）做了什麼

Sir 指令「1＋2」＝Phase 3 配色＋二胎頁撥號 CTA。兩件都做完、閘門全綠、Sir 16:2x 說「部署」→ push `7c45acf`（連帶平行 session 的矩陣第二批 07f9a42 一起上線，已向 Sir 報備、他 ok）。
- Phase 3：見第一節「設計」列。目檢：乾淨樹 staging 桌機 1280／手機 390，footer 8 頁、hero＋CTA 16 頁（截圖在 session scratchpad，已隨 session 消失；重拍照第二節 headless 管線）。
- 撥號 CTA：偵察 agent 普查 17 頁 → 12 個 LINE-only 群組；媽祖 11/11 PASS。
- 順手修：`gen_radar_v4.py` 在 `65b192b` 被貼進未雙寫大括號的 JS 物件 → f-string SyntaxError，隔天 `update_indicators` 排程會炸；已修並重生產物（diff 只剩 head 兩行＋時間戳）。memory `feedback_python_compat_silent_failure` 追加一段。
- 平行 session 雷再踩一次：工作區有別人的 `corporate-*.html`／`img/area/*` 未提交；本 session 用 `git add <指名檔> && git commit --no-verify` → 跑兩支鮮度腳本 → 只 re-add 自己 commit 過的檔 → `--amend`。配方有效，照抄。

## 七、本 session（2026-09-14 14:3x → 16:3x）做了什麼：交接信待辦 #4＋#6

- **#4** `corporate-checkup.html`／`corporate-loan.html` 加 `.bt-local` chips 區（6 鏈）。
- **#6** 企業健檢擴 5 區：關公 ×3 路（稅籍自算／三重新莊工業／板橋土城永和工業）＋普查工兵 → 素材四檔（素材包 v5.2 §7）→ 5 個 fable 建造者並行、五種骨架 → 機掃（difflib／FAQ 同源／ci／禁語）＋ 5 頁桌機 hero・手機 390 目檢 → 媽祖 10 處小改已修（報告 `行銷產出/技術記錄/2026-09-14-企業健檢五區媽祖把關.md`）→ `07f9a42` → Sir 令部署 → 線上 5 頁 200、TG 已推。
- 三重／新莊新配 Commons 照（`img/area/sanchong.jpg` 新北大都會公園、`xinzhuang.jpg` 副都心；credits.json 已補）。
- 統一：五頁不掛 ai-bar（首篇無）、FAQ「＋」單一、下載清單連結文字＝「企業週轉資料清單」。
- 雷：①研究型 agent 又「等工兵回報」結束（關公 A），一催即交；②建造者整包對拷把樣板雙加號 bug 抄進 4 頁、3 頁自加 ai-bar——memory `feedback_template_bugs_copied_by_builders`；③push 撞平行 session 同秒推同一 HEAD（remote rejected 但內容已在遠端），`git fetch` 比 hash 再判。
- 機掃改進待做：difflib FAQ 比對前先剝主頁隱私脊椎句（媽祖 §7.1）；`scratchpad/simcheck.py` 是暫存，下次要用先落 `scripts/`。

## 八、本 session（2026-09-14 17:1x → 09-18 04:3x，cloud-code-aa）做了什麼

1. **機械四項**（`3b7f0aa`）＋**矩陣第三批服務軸補滿 6 頁**（`f4c7ae2`）：細節在第三節 🟢 09-15 段；媽祖報告 `技術記錄/2026-09-14-服務軸補滿六頁媽祖把關.md`；六頁行情全換 4G。隨 pf3 鏈 09-17 23:07 上線。
2. 待辦 ③ property-finance 重寫與另一 session 撞車（互覆寫一輪）→ 停自家建造者、讓出；分工與部署順序談定（memory `feedback_parallel_session_moves_head_mid_diagnosis` 兩側視角）。
3. **09-17 精進會議主席**（正本 `行銷產出/精進會議/2026-09-17.md`）：Step 0 對 09-07 清單 13 項取證（✅5／⚠️2／❌5／🚫2）；六將取數（GSC 28 天曝光 +37%、點擊 +13%、排名 10.16→9.07；稽核 149 頁 142 滿分；健檢 🔴6；木吒沉默失敗 7 條；小鋮週抽查 15 則＝真人 5 全過、prompt 固定句「最低」1 則踩線，媽祖改法字串在會議檔第三節）。
4. memory 追加四處：`feedback_session_start_review_meeting`、`feedback_traffic_drop_check_ad_spend_first` 第 5 條、`feedback_eval_loop_burned_api_credit`、`feedback_parallel_session_moves_head_mid_diagnosis`。
5. **刻意沒做**：小鋮「最低」雙護欄修改（動 `~/cx468-linebot/app.py` prompt＋regex＋跑評測＋部署，列 T0）；新聞卡換稿、Threads 補稿、週報 W37（硬期限，另開 session）。

## 九、本 session（2026-09-17 23:1x → 09-18 05:0x，接手信 1263629）做了什麼

「把交接信做完」：矩陣待辦 #1／#2（pf3 已結）、#5 geo 兩組座標（`2c97ec0`：77 頁 meta＋首頁＋3 支產生器）、#6 地區軸二胎複製（`c5d6789`：永和／土城二胎頁＋接線）——**矩陣「全做」三順位全部完成並上線 `9468a93`**（Sir 00:5x 令部署），細節全在第三節 🟢 09-18；交接信 `7d8fa93`。memory 追加：`reference_nap_canonical`（NAP 三處同掃）、`project_local_page_series_rules`（09-17/18 六條）、`feedback_dispatch_prompt_must_requote_from_current_file`（§6 欄位抄錯實例）、`feedback_parallel_session_moves_head_mid_diagnosis`（datemod 拉別人頁＋zsh 不分詞）。**刻意沒做**：第三節 🟡 順帶發現（GA config 濾 query／「9 成」一二胎合計／nav.js 死變數／lvr 圖表紅系／計算器過時句／linebot 兩條）與 🟢 09-18 順帶發現四條（三支二胎頁麵包屑層數／「約 8 分鐘」／llms-full 無矩陣頁／共用 include 13.3px input）皆標「Sir 裁或另批」未動；土城頁 `tucheng-property-finance.html` L340 自稱「融資租賃業者」沿用未改。


## 十、本 session（2026-09-18 06:2x → 09-20 00:3x，cloud-code-0a）做了什麼

零建造。接手信 `64dc29f` 後任務欄空白，Sir 09-20 00:1x 令跑 /handover。做的事：①09-17 §六硬期限現場取證（結果在「日常常態」）；②12:00 精進會議 cron 重設過（session-only，本 session 收工即失效——09-19 那場由另一 session 主持）；③平行 session 認領：cloud-code-97＝地區軸二胎收尾（已結）、cloud-code-d0＝主題頁 B0–B5＋媽祖兩項全站裁示 8 檔（進行中）；④memory `project_threads_autopost` 補「剩幾天」算法（曾誤報 108 則）。**刻意沒做**：T0 小鋮雙護欄（09-20 到期、要算錢跑評測、Sir 令部署才推）；xinbei ai-bar／llms-full／「實際成數」四頁——都在 d0 的主題頁範圍，避免撞車未動。
