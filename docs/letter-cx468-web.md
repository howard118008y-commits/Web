# 交接信｜cx468-web（官網 repo）＋ CX468 雲端維運

> 現況快照，不是 changelog。歷史在 `git log`；本檔上一版（09-20，含 09-14～09-20 六段 session 日誌）在 `git show e1c4b7b:docs/letter-cx468-web.md`。
> 最後更新：2026-09-27 14:0x（SEO 第一順位執行 session：三節第一順位改寫為「已上線／還沒做」；一節 HEAD／工作區兩列重寫）
> 前次：2026-09-27 12:4x（SEO 全流程 session 交接，`f6f0837`）。
> 本次更新原因：Sir 09-27 13 時「全部開始做照順序」＋「部署」。本 session 把第一順位 1→9 照順序做，7 批上線 `22805e9`→`3a6895a`，全部線上 curl 驗過。**一節「設計／電話／追蹤／p2a」與 CI／閘門列仍是舊版，本 session 未重驗**；主 repo 未提交的 `scripts/audit_seo.py` 仍是平行 session 的（含第一順位 #3 的樁頁排除邏輯），別替它 commit。

## 一、當前狀態快照（HEAD／CI／工作區／SEO 四列 2026-09-27 12:4x 重驗；其餘列 09-23 版，每項附指令）

| 項目 | 值 | 重驗指令 |
|---|---|---|
| HEAD | **origin/main＝`3a6895a`**。本 session 7 批（皆 `git push origin HEAD:main`）：`22805e9` 反詐頁 4 條反向內鏈 → `3282471` 首頁 title 加售後回租 → `980b76f` 兩頁 CTA 看不見 [nofresh] → `8a5212a` 二胎利率 DefinedTerm（媽祖定版）→ `abd79b1` 20 地價稅頁輸入框 16px [nofresh] → `9521542` /en/ title＋description [nofresh] → `07230de` 全站「本頁最後更新」[nofresh] → `e661f3b` 33 頁 description ≤100 [nofresh] → `3a6895a` 二胎利率頁第二張表（8 筆銀行官網公告）。中間 `525939b` 是 CI 指標自動更新 | `cd ~/cx468-web && git fetch -q && git log --oneline -12 origin/main` |
| CI／Pages | `fca94a7` CI success＋pages build success；`9a800c9` CI success。線上 09-27 12:4x：sale-leaseback／article-loan-fraud-check 200；sale-leaseback「依租約條款保障」2 處；article-sale-leaseback-guide 為 meta refresh stub | `gh run list -L 3`；`curl -s https://cx468.com.tw/sale-leaseback.html \| grep -c 依租約條款保障` → 2；`curl -s https://cx468.com.tw/article-sale-leaseback-guide.html \| grep -c 'http-equiv="refresh"'` → 1 |
| 工作區 | 本 session 施工 worktree `~/cx468-fraudlinks`（detached，已全部 push，可 `git worktree remove ../cx468-fraudlinks`）；`~/cx468-desc` 已移除。**遺留本機分支 `seo-desc-0927`、`seo-0927-fixes`、`seo-0927-articles`**（內容都已進 origin/main，`git branch -D` 被 hook 擋，等 Sir 手刪）。其他 worktree（ga-allow／radar-w4／phase2）是別的 session 的，勿動。改頁仍一律 `git worktree add ../<name> origin/main` 隔離施工，push 用 `git push origin HEAD:main` | `git worktree list`；`git branch --list "seo-*"` |
| SEO（09-27 上線） | 6 核心頁 h1 下首段＝40–80 字答案段；FAQ 補核定數字（SLB 市值 7–9 成、整合月付降 30–50%＋「月付降低不等於總利息減少」）；整合頁 FAQ 改題「每月月付可以降多少」；SLB 風險段；收費統一句（貸款版＋SLB 版「簽約過戶、資金到位後才收」Sir 確認屬實）；「債務整合」同義詞；about schema 刪 0931；**taxID 60602537 共 120 頁**；FAQ 同源 **155/0**；llms.txt 二胎與「免費」拆段＋補 0958。規格正本＝`行銷產出/策略簡報/2026-09-27-SEO全流程行動計畫.md`（媽祖把關版） | `grep -l '"taxID"' *.html \| wc -l` → 120；`python3 scripts/audit_faq_samesource.py` → 同源 155／漂移 0 |
| 閘門（乾淨樹 `git archive origin/main`） | 09-23 03:1x 於 `8237856`：ci_check **190 檔 0**；FAQ 同源 **150/0**；audit-regression **23/23**。之後每個 commit 前各自重跑：`ab50002` ci 190/0＋text 159 零漂移＋regression 23/23＋真瀏覽器 GA 探針 9 頁；`7dd996e` ci 190/0＋FAQ 同源 151/0＋schema==visible True。**regression 需 linkedom**：主 repo 已無，`npm i --prefix <scratch> linkedom && ln -s <scratch>/node_modules node_modules`（跑完 `rm node_modules`） | `python3 scripts/ci_check.py`；`python3 scripts/audit_faq_samesource.py`；`node scripts/audit-regression.cjs` |
| 設計（Apple 流體層，09-23 全站） | 新檔 **`fluid.css`**（75 行）**掛全站 165 頁**（`d1d7d3a` 補 146：139 靜態＋en/index＋lvr×3／radar×2 生成頁；生成模板 `scripts/lvr/build_observatory.py`／`build_extras.py`／`gen_radar_v4.py` 同步改，之後重生成不會掉）。**未掛 20**＝include 片段 11、cx_batch 草稿 4、topic-a~d 模板 4，另 downloads/×4、world/（無 nav 無按壓元件）。sale-leaseback.html 原本沒有 `</head>`，link 放 `<body>` 前。首批 15 頁（`3762746`）＝首頁＋四個下拉裡的 14 頁：按壓回饋（pointer-down 縮 .97、臨界阻尼 spring `linear()` 彈回）、nav 下拉從按鈕長出（blur→清晰）、FAQ `::details-content` 連續展開、tp-h1／art h1／bt-h1 負字距＋小字正字距、hero 進場微升（主圖零延遲）、手機底部條（footer `.cx-sticky-cta`＋topic.css `.tp-bar`）改懸浮玻璃 dock、reduced-motion／transparency／contrast。首頁另有內聯專屬段（AI 卡 View Transition、開關 transform）；**首頁 hero 精簡為眉標／h1／副標／電話鈕／AI 卡，四需求卡／信任列／快捷列／免責搬到 `.hero-more` 第二屏**，文字零增刪。Phase 1–3 配色同 09-20 版 | `grep -l 'fluid.css' *.html \| wc -l` → 164（＋en/index）；`grep -L fluid.css *.html \| wc -l` → 20；`curl -s https://cx468.com.tw/ \| grep -c 'class="hero-more"'` → 1；截圖 `行銷產出/視覺風格/apple-design-2026-09-22/` |
| 電話（09-22 平行 session 改，未重驗） | 憲法第十一節 09-22 改：CTA 兩支 02-2249-0517＋0958-139-786（`bede5bb` 全站 0931→0958）；反詐彈窗／聯絡四處恢復「市話／鄭經理／業務人員 0931」三號並列（`f3b88a2`）。09-20 版的 contactPoint 60 頁等數字未重驗 | `git show f3b88a2 --stat`；`grep -c 0931-087-996 anti-fraud-modal.html contact.html` |
| 追蹤（GA4，09-23 全站統一） | **173 頁 GA config 全走 `analytics-config.js`**（`ab50002`）：page_location／referrer 只留 origin+path、UTM 白名單進 campaign_*。新頁抄 apply.html 三行；子目錄 `../analytics-config.js`；生成頁改模板（gen_radar_v4.py 雙大括號）。驗法＝真瀏覽器帶 `?utm_source=threads&utm_medium=social&utm_campaign=250923&secret=PRIVATE#frag` 抓 `/g/collect`（memory `feedback_ga_config_use_analytics_config_js`）。🔴 09-23 前 63 頁「inline 濾版」丟 UTM，歷史 campaign 數字偏低不可補。NAP geo／SLB 定義／企業線／20 年主詞同 09-20 版未動 | `grep -L analytics-config.js $(grep -l "gtag('config'" *.html)` → 空 |
| p2a／linebot／三日健檢／廣告／Threads | 同 09-20 版，本 session 未碰；p2a 09-22 有產 `article-profitable-company-loan-rejected.html`（`ad8fd75`）＝管線活著 | `git -C ~/cx468-fb-news-bot log --oneline -3`；`grep -n "Telegram 已推" ~/cx468-ga4-daily/logs/healthcheck.out \| tail -3` |

⚠️ **四個路徑／平行陷阱**：
1. 網站程式碼在 `~/cx468-web/`，**不在 iCloud 專案夾**；`行銷產出/`、`知識庫/`、`制度/` 在 iCloud 專案夾。
2. LINE bot 查驗一律用 `~/cx468-linebot`。
3. 本機閘門一律跑在只含已追蹤檔的樹上——`git ls-files -z | rsync -aq --from0 --files-from=- ./ $T/`。
4. **平行 session 會把你工作樹裡未驗完的 diff 夾進它的 commit 並 push**（09-22 實踩：首頁 apple-design 第一輪被 NAP session 的 `f3b88a2` 帶上線）。改任何頁一律 `git worktree add <scratch>/cx-wt-<task> HEAD` → 在隔離樹改＋驗＋commit 到分支 → Sir 說部署才 `rebase origin/main` ＋ `merge --ff-only`（memory `feedback_parallel_session_moves_head_mid_diagnosis`）。

🚨 **commit 配方**：pre-commit hook 會把工作樹所有已修改 html 掃進你的 commit（`.git/hooks/pre-commit:30`），還會自動加 sitemap／鮮度欄位。平行 session 施工中要用 `git add <自己的檔> && git commit --no-verify` → 跑 `update_schema_datemod.py`＋`update_sitemap_lastmod.py` → `--amend --no-verify`。單人時 `git add -u` 即可，但先 `git status -s` 確認 M 全是自己的。**所有 repo 禁 `git add -A`。**

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

### 🆕 Apple 流體層 fluid.css（9/22–23 建立）
- **掛法**：`<link rel="stylesheet" href="fluid.css">` 放 `</head>` 前、該頁自家 CSS（含 consultation.css／topic.css／theme.css）之後，同特異性靠順序蓋過；`<body ontouchstart="">` 讓 iOS Safari 觸控時套 `:active`。nav.js 注入的樣式在 head 尾，比 fluid.css 晚，所以 nav 覆蓋用 `.cx-menu>li .cx-dd`（0,2,1）壓 `.cx-dd`（0,1,0）；footer.html 的底部條是 `:where()` 零特異性，隨便壓；consultation.css 的 `!important` 要同特異性＋後載＋`!important`。
- **改版型**：新增按壓元件＝改 fluid.css 頂部 PRESS 名單（三處同步：transition 規則、`:active`、reduced-motion 的 `transform:none`）；新增 hero 進場＝改 REVEAL 名單（bt-hero／art-hero／tp-hero-text 三版型各有 nth 延遲）。
- **spring 曲線**：`--spring` 是臨界阻尼（damping 1.0、response .4s）採樣成 `linear()` 21 點，末點必須是 `1`（曾寫 0.997 讓 `animation-fill-mode:both` 停在 99.7% 透明度）；前面一行 `cubic-bezier(.22,1,.36,1)` 是不支援 linear() 的 fallback。
- **驗收**：文字守恆用 `scripts/check_text_integrity.py`（比順序；首頁這種搬位置的改動要另用 Counter 多重集比，腳本在 session 對話裡、10 行可重寫）；視覺用 playwright MCP：**navigate 之後才 resize**（navigate 會重設 viewport）、截圖只能存專案根下、fullPage 會把 fixed nav 印在頁中（memory `feedback_playwright_mcp_viewport_and_paths`）；本機預覽 `python3 -m http.server 8766 --bind 127.0.0.1`（背景 task）＋ `open http://127.0.0.1:8766/index.html` 給 Sir 摸。
- **純版型 commit 加 `[nofresh]`**（09-23 老闆定）：`update_schema_datemod.py`／`update_sitemap_lastmod.py` 都用 `git log --invert-grep --grep '\[nofresh\]'` 取日期，訊息帶這個標記的 commit 不算實質修改→dateModified／lastmod 不動、indexing cron 不送。驗法：`python3 scripts/update_schema_datemod.py --dry-run`＋`update_sitemap_lastmod.py --check` 應 0 頁。⚠️ pre-commit hook 在 commit 建立前跑，**`--amend` 補標記時要 `--no-verify`**，否則 hook 會先按未標記的舊 commit 把日期全推上去。
- **隔離配方（已驗證可行）**：`git worktree add <scratch>/cx-wt-hero HEAD && git -C <wt> checkout -b apple-design` → 改＋驗＋commit → `git -C <wt> rebase origin/main && git merge --ff-only apple-design && git push` → `git worktree remove --force <wt> && git branch -d apple-design`。

## 三、未竟任務

### 🔴 第一順位：09-27 SEO 全流程——剩下的（09-27 下午 session 已照順序做完大半）

報告與規格入口：行動計畫總表 23 列＝`行銷產出/策略簡報/2026-09-27-SEO全流程行動計畫.md`；三篇內容 FINAL＝`行銷產出/官網文章草稿/2026-09-27-*-FINAL.md`；競品三家＝台灣理財通 imoney.com.tw／好事貸 houseloan.tw／OK忠訓 okbank.com（Sir 說的「鋮馨租賃工作台」本機／Artifacts／Notion 都找不到，要 Sir 給連結）。

**09-27 下午已上線（見一節 HEAD 列）**：反詐頁 4 條反向內鏈；首頁 title 插「售後回租」（接二胎後，保留 09-11 電話先行排序；site-index.json 每週 workflow 自動更新，沒手改）；兩頁 CTA 看不見（全站 63 頁 `.cta-box` 實渲染量對比度，只有 article-private-loan-to-bank 金字壓金底、article-private-loan-credit-damage 藍字壓藍底 <2:1）；二胎利率頁 DefinedTerm「可動用額度」改扣一胎剩餘本金（媽祖逐字句）＋第二張表 8 筆銀行官網公告（凱基次順位／台新／玉山／遠東／王道／陽信×2／新光，逐家複驗原文；台中銀行連不上、三信基準日 110/9/1 剔除）；/en/ title 57、description 151 字元；20 地價稅頁「公告地價」輸入框 16px；33 頁 description ≤100 字（媽祖修改後 PASS，og／twitter／schema 同源）；全站「本頁最後更新」（`include.js` 讀 JSON-LD 最大 dateModified，159 頁顯示、7 頁已有字樣跳過、15 頁無 dateModified 不顯示）。

**硬期限**
1. **二胎利率頁每季複驗，首次 2026-12-27**：已登記 `~/.cx468/pending_reviews.json`（三日健檢到期前 7 天推）。範圍＝兩張表共 10 筆，網址在該頁「資料來源」清單；玉山活動 2026-12-31 到期必查；陽信在 Cloudflare Turnstile 後面、新光是 JS 頁，要 headless。媽祖限制五條：只引機構自行公告數字＋來源＋查詢日；區間句同段帶「非鋮馨報價、利率因人而異、非承諾」；民法 16% 上限句不與具名銀行同句；「起／最低」不作招攬語；銀行改公告即改＋dateModified 同步，數字改動仍過媽祖。09-27 追加：**這兩張表只能活在本頁，不得搬進廣告或社群**。

**還沒做**
2. **`audit_seo.py` 排除 meta refresh stub**：平行 session 未提交的 diff（09-27 12:25）已含這段邏輯，等它 commit；別替它 commit。
3. **審稿人具名 Person／reviewedBy**：要 Sir 指定人名（建議鄭經理或 Sir），範本在行動計畫二-9；沒名字不上。
4. **等 Sir 裁**：ai-bar.html 要不要 robots Disallow（Jarvis 建議維持現狀）；cx_radar_v4_demo canonical；Core Web Vitals（Sir 手動跑 PSI 網頁版）；每服務獨立 FAQ 頁（Jarvis 異議：faq.html＋各服務頁已有同源 FAQ，再開獨立頁＝重複內容，建議不做）；案例庫擴充（要 Sir 給新的真實匿名案例，不虛構）；18 頁 CTA 白字金底按鈕對比 2.68:1（未達 AA，品牌設計，改不改色）。
5. **媽祖備註下一輪**：xinzhuang-second-mortgage 的 twitter／JSON-LD「近 180 天…每坪 47.9 萬」無日期錨，同型病掃一次各 `*-second-mortgage` 的 og／twitter／schema；financing-data「售後回租成數」可改「金額佔市值比例」。
6. `second-mortgage.html` 收合區 `.bt-p` 內鏈 5 條與內文同色無底線（看不出是連結）；全站同寫法頁未掃。
7. `scripts/generate_city_calculators.py` **模板落後產物**（缺 fluid.css／analytics-config.js／dateModified）：重生前先補模板，否則洗掉 GA 設定。
8. 行動計畫總表 23 列：除上面 2–7 與 Sir 待裁項，其餘已全部上線。

**已確認不用做**：首頁 Lighthouse `fh-…ecs.us-west-2.on.aws`——乾淨瀏覽器開線上首頁無此請求、repo 零引用，來自當時 Lighthouse 環境（瀏覽器擴充）；about schema 0931 早已刪；債務協商專頁由 article-debt-negotiation-vs-consolidation 承接。**不跟進**：AggregateRating 自評、LoanOrCredit schema、全台縣市頁量產。

### 🟢 近期已上線（對照用，細節見 git log 與 09-20 版信）
- 09-27 `9a800c9` 反詐總整理新頁＋二胎利率／債務協商改寫；`783fbb0`／`90de4f3` SEO 行動計畫 9 項（本 session，媽祖把關版）
- 09-23 `7dd996e` 首頁恢復精簡 3 題 FAQ（Sir 12:4x 裁；媽祖條件 PASS 補 0958；同源 151/0；index 15/17→16/17，definedterm 仍留白）；`ab50002` GA config 全站 173 頁；`c4ff7c5` nav.js 死碼；`d1d7d3a` fluid.css 全站（本 session）
- 09-23 `3762746`／`e9270e7` Apple 流體層 15 頁＋首頁精簡 hero（本 session）
- 09-22 `f3b88a2` NAP 三號並列、`bede5bb` CTA 0931→0958、`19d0a5b` 4 頁實際價金比例（平行 session）
- 09-20 `cb51af5` 導覽列主題分頁改造 B0–B5（17 頁）；09-18 `9468a93` 永和／土城二胎＋geo 77 頁；09-17 `7a03add` pf3-rewrite＋第三批 6 頁（`3b7f0aa`／`f4c7ae2`）
- 09-14～15 `89d002f` 矩陣第一批 6 頁、`07f9a42` 第二批 5 頁、`4c50d13` Phase 3 配色＋二胎撥號 CTA、`b386ad9` Phase 1–2

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

1. ~~**90 頁 GA config 沒濾 query/fragment**~~ ✅ `ab50002`（09-23 05:4x）全站 173 頁統一走 `analytics-config.js`（含 3 支生成模板）；順帶把 63 頁「inline 濾版」也換掉——那版有濾但**丟 UTM**（Threads/FB 帶 utm 進來記成 direct/referral）。**新頁一律抄 apply.html 的三行 GA 區塊**（`<script src="analytics-config.js">`＋gtag config 吃 `window.cxAnalyticsConfig`），驗法：真瀏覽器帶 `?utm_source=threads&utm_medium=social&utm_campaign=250923&secret=PRIVATE#frag` 看 collect 的 dl／cs／cm／cn（腳本思路：playwright 抓 `/g/collect` 請求）。
2. 矩陣 🟢 待辦 #1–#6（口徑統一／三支 property-finance 同構 88–91%／`.bt-meta` 對比／企業兩樞紐無 chips／geo 座標兩組並存／企業健檢擴 5 區）。
3. 「成數最高 9 成」未說明一二胎合計（09-09 媽祖提，全站 9 處同型）。
4. ~~nav.js `ctaLine` 死變數／L122 過時註解~~ ✅ `c4ff7c5` 清掉（09-23 05:0x）；`data-cta="line"` 屬性仍由 footer.html 讀，頁面上不要拿掉。
5. `codex/verify-live-20260911` 分支殘留 1 個 commit（純驗證腳本），可刪。
6. lvr 圖表 PNG 與社群圖卡仍紅系（`scripts/lvr/make_charts.py`／`make_social_cards.py`）。
7. `land-value-tax-calculator.html`「其他縣市陸續建置中」已過時（需媽祖）；`affordability-calculator` 無免責尾注。
8. linebot：隱藏號碼來電逐通建新 person 灌漏斗（`crm_calls.py:119-125`）；`privacy-policy.html §6` 沒提電話管道。
9. ~~**fluid.css 未掛的頁**~~ ✅ `d1d7d3a` 全站掛齊（09-23）。原文：售後回租／小工具兩個下拉的目標頁（sale-leaseback、tools-lab/deed-reader、zhonghe-second-mortgage、new-taipei-house-tax、tools 等）＋其餘 ~170 頁——掛法一行 link＋`<body ontouchstart="">`（memory `project_apple_design_branch`）；nav.js 本體未動，下拉 materialize 只在掛了的頁生效。
10. 首頁內聯 `<style>` 的按壓名單（.chip/.quick a/.three a/.float 等）與 fluid.css 的 PRESS 名單各管各的，`.cx-needs a/.cx-call-primary/.cx-sticky-cta a` 兩邊都列（值相同、無害）；反詐彈窗 `.afm-btn` 自帶 CSS 蓋掉按壓回饋，未硬打。

### 日常常態

- 每天 12:00 精進會議（session 級排程，每個 session 用 CronCreate 重設）——**最新正本 `行銷產出/精進會議/2026-09-27.md`**（09-27 另一 session 主持；本 session 待辦七項已寫在其「## 補記（12:32，SEO 全流程 session）」）。以下 09-17／09-19 硬期限現況是舊快照、未重驗：09-17 §六硬期限現況（09-20 00:2x 取證）：新聞卡 ✅ `03e9d3e`、Threads ≥14 ✅（現剩 12 到 10-01）、週報 W37＋W38 ✅ 09-19 補寫、p2a 三修 🟡（GO 拆除＋FAIL 印原因已做，排程 17:15 未改＝T8）、**T0 小鋮「最低」雙護欄 ❌ 未動（`~/cx468-linebot/app.py:1844/1931/1941` 三處原樣，HEAD `37ed7f6`，期限 09-20）**。09-19 §六今日／明日硬期限：B2 sitemap ✅、llms.txt 接入 ✅、xinbei ai-bar ❌、「實際成數」❌ 4 頁、EP31+／新北 HowTo 未驗、iPAS Sir 09-22。
- 三日健檢 `com.cx468.healthcheck` 會推 🔴 到 Telegram——**收到要有人接**（memory `feedback_act_on_telegram_alerts`）；09-08 那則還躺著「Meta spend_cap 決策逾期」「週報監控瞎了」等 4 條。
- Threads 12:30；p2a 17:15（敏感稿要人回 GO，memory `feedback_human_go_gate_deadlocks_pipeline`）；`cx468-crawl` 每 2 小時。
- 換新聞卡前 `git log --oneline -5 -- radar-index.html` 算服役天數。

## 四、等使用者的事項

-1. 🔴 **GSC 送索引（09-27 12:20 URL Inspection API 全站 161 頁實查取代舊清單）**：已收錄 149／已發現未收錄 9／Google 不知道 3。每天約 10 條，分三天：**D1** article-loan-fraud-check、yonghe-private-to-bank、sanchong-private-to-bank、sale-leaseback、debt-consolidation、private-to-bank、second-mortgage、article-second-mortgage-rates、article-debt-negotiation-vs-consolidation、corporate-checkup；**D2** corporate-loan、about、article-inherited-house-sell-or-keep、article-seized-house-still-has-options、yonghe／sanchong／xinzhuang-corporate-checkup、yonghe-debt-consolidation、banqiao-sale-leaseback、sanchong-debt-consolidation；**D3** banqiao-private-to-bank、inherited-property、knowledge、case-zhonghe-consolidation、case-private-to-bank、xinbei-debt-consolidation（全部前綴 `https://cx468.com.tw/`）。其餘約 100 頁是已收錄的小改，靠 sitemap。舊清單的 yonghe／tucheng-second-mortgage、banqiao／tucheng-corporate-checkup 已收錄，不用再送。Sir 送了哪些本 session 不知道——下次用 API 重查 coverageState＋lastCrawlTime 對帳，別照抄本清單（memory `feedback_indexed_but_stale_crawl`）。
0. 🟡 **Sir 手動清掉兩個本機分支** seo-0927-fixes、seo-0927-articles（內容已在 origin/main；agent 執行強制刪除會被 hook 擋）。
0-1. 🔴 **待裁清單以 `精進會議/2026-09-19.md` §六「🔴 Sir 決策」九項為準**（新增：Meta 11 支 adset 自身 ACTIVE 未爆彈、Google 餘額 10/02 見底、private-to-bank-search 零曝光查或關、`Chengxin_V1_Final_4K.mp4` 誤傳翻舊帳頻道建議下架、翻舊帳 09-22 斷更、Anthropic Admin key）；09-17 六件仍未答：①Meta spend_cap（逾 29 天，不回＝維持）②精進會議觸發改 launchd／雲端 routine ③CX_V1_20260916 誰建的、過媽祖沒（09-20 滿 3 天要決定續停）④anti-fraud-modal 三選一（已擴散 145 頁）⑤反詐文／EP15／C-v3＋比特幣起源 private＋銀行條文封存否 ⑥整合／轉銀行系列補 ai-bar 否。
1. 🔴 **GMB 評論 1→20**（第二順位③，只有 Sir 能做）：「新北 房屋二胎」Local Pack 第 1 名 17 則、第 2/3 名 0 則照樣上榜。⛔ 商家名不塞關鍵字、類別維持「不動產管理服務」。
2. 🔴 **Telegram 三日健檢的 🔴 要有人接**：09-08 推播列了「Meta spend_cap 決策逾期 18 天」「行銷週報檢查失效（launchd 無 iCloud 權限）」「銀行條文存證複查」——本 session 只修了 p2a 那條。
4. **Anthropic 帳務**：auto-reload 未開、無 Admin key、9 服務共用一把 key（09-08 起未變）。
5. **配圖要不要換真人照片**：三重／新莊／三重售後回租用 AI 生成圖（memory `project_photo_library`：老闆偏好真人）。未擋上線。
6. **`cx468-crawl` 一天 12 次要不要降頻**（不花 API 錢，只違「一天不超過三次」原則）。
7. **PR#5 之外的 GA4 事件設定**：`phone_click`／`line_click` 在 GA4 是否已標關鍵事件、landing page 維度切得出來（memory `feedback_ga4_import_needs_conversion_category`）——站上發得出，後台我看不到。
8. 名單回電 SOP、合一地政士洽談、企業貸款專案三處不一致（8/14 起未變）。
10. ~~**矩陣第二批順帶三件待裁**~~ ✅ 三件 `540c425` 全做（Sir 09-14 令「1＋2＋3＋4」）；原文：（16:3x 報過、未動）：①首篇 zhonghe＋09-14 六頁 FAQ「＋」雙加號（新 5 頁已修，舊 7 頁一支 sed：把 `<span class="plus">＋</span>` 改空 span）；②企業系列 6 頁都不掛 ai-bar（樞紐有）要不要全系列補；③LocalBusiness `areaServed` 缺三重／新莊／土城（併待辦 #5）。
9. ~~0958 上不上官網~~ ✅ 09-14 定：上，稱「經理鄭小姐」。~~企業貸款頁留不留~~ ✅ 留，健檢在前。~~售後回租兩套定義~~ ✅ 統一 A。~~「20 年」主詞~~ ✅ 全站＋跨 repo 已改。

## 五、歷史
各 session 做了什麼不再堆在這裡：`git log --oneline --since=2026-09-01`，以及 `git show e1c4b7b:docs/letter-cx468-web.md` 第五～十節（09-14～09-20 六段）。
