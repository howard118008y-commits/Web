# 交接信｜cx468-web（官網 repo）＋ CX468 雲端維運

> 現況快照，不是 changelog。歷史在 `git log`；本檔上一版（09-20，含 09-14～09-20 六段 session 日誌）在 `git show e1c4b7b:docs/letter-cx468-web.md`。
> 最後更新：2026-09-23 13:0x（首頁 3 題 FAQ 上線）｜05:4x（🟡#1 GA config 全站結案）｜05:0x（三節 🟡#4 nav.js 死碼結案）｜03:1x（閘門列補三道數字）｜02:5x（fluid.css 補掛全站 146 頁＋生成頁模板＋鮮度腳本 [nofresh] 標記，HEAD `d1d7d3a`；一節 HEAD／CI／設計三列改寫、二節 fluid 段加標記一行、三節 #9 結案）
> 前次：2026-09-23 01:0x（Apple 流體層 fluid.css＋首頁精簡 hero 上線，HEAD `3762746`；一、三節重寫，二節保留＋新增 fluid 段，四節加一行）
> 前次：2026-09-20 00:2x（主題分頁改造 B0–B5 上線 `cb51af5`）。
> 本次更新原因：Sir 09-23 02:0x 選「全站＋生成頁模板一起做」＋「不跳鮮度，加 [nofresh]」＋「部署」。平行 session 同時段推了案例分享 01–05（`381d865`／`d154ef1`／`1df8999`／`a7c67cc`），本 session rebase 過、未重驗其內容。
> 前次原因：Sir 09-22 令「用 apple-design skill 改首頁」→ 看過隔離版精簡 hero 說「很好、幾個網頁都改」→ 09-23 令「部署」。另 09-22 平行 session 做了電話 NAP（`bede5bb` CTA 0931→0958 全站、`f3b88a2` 反詐／聯絡四處三號並列）與媽祖 T0-c（`19d0a5b` 4 頁「實際價金比例」），本 session 只從 git log 看到、未重驗其內容。

## 一、當前狀態快照（2026-09-23 01:0x 重驗，每項附指令）

| 項目 | 值 | 重驗指令 |
|---|---|---|
| HEAD | **`d1d7d3a`＝origin/main**（fluid.css 全站 146 頁＋3 支生成模板＋2 支鮮度腳本，151 檔；訊息帶 `[nofresh]`）。其前 `a7c67cc`／`1df8999`／`d154ef1`／`381d865`／`22317e8`／`f2e4cf8` 案例分享 01–05 故事頁（平行 session）。09-22～23 鏈：`f3b88a2` NAP 三號並列 → `19d0a5b` 4 頁實際價金比例 → `80b34a6`／`c04b130`／`1bd1259` 自動資料 → `ad8fd75` p2a 09-22 文章 → `e9270e7` 首頁精簡 hero → `3762746` fluid.css 掛 15 頁。其前 `cb51af5` 主題頁改造（09-20） | `cd ~/cx468-web && git fetch && git status -sb && git log --oneline -10` |
| CI／Pages | `d1d7d3a` push 於台北 09-23 02:5x（線上驗證見四節 -1 與 memory `project_apple_design_branch`）；前一版 `3762746` CI＋pages 皆 success | `gh run list -L 3`；`curl -s -o /dev/null -w '%{http_code}' https://cx468.com.tw/fluid.css`；`curl -s https://cx468.com.tw/ \| grep -c hero-more` |
| 工作區 | 乾淨（只剩未追蹤 `scripts/archive/goal-scores.jsonl`，非本專案產物勿 add）。`git worktree list` 另有兩個別的 session 的 audit/phase2 worktree（`/private/tmp/cx468-phase2-20260921`、`~/Documents/Codex/.../site-phase2`），不是本 session 的，勿動 | `git status -s`；`git worktree list` |
| 閘門（乾淨樹 `git archive origin/main`，09-23 03:1x 於 `8237856`） | ci_check **190 檔 0 問題**；FAQ 同源 **150 頁零漂移／35 頁無 FAQ**；audit-regression **23/23**（09-18 是 18/18，平行 session 加了 Phase 2 五組；需 `node_modules/linkedom`，主 repo 已有、未追蹤）；check_text_integrity 146 頁零漂移（`d1d7d3a` 前驗）；首頁可見文字 184 節點 | `python3 scripts/ci_check.py`；`python3 scripts/audit_faq_samesource.py`；`ln -s ~/cx468-web/node_modules node_modules && node scripts/audit-regression.cjs`；`python3 scripts/check_text_integrity.py . <檔>` |
| 設計（Apple 流體層，09-23 全站） | 新檔 **`fluid.css`**（75 行）**掛全站 165 頁**（`d1d7d3a` 補 146：139 靜態＋en/index＋lvr×3／radar×2 生成頁；生成模板 `scripts/lvr/build_observatory.py`／`build_extras.py`／`gen_radar_v4.py` 同步改，之後重生成不會掉）。**未掛 20**＝include 片段 11、cx_batch 草稿 4、topic-a~d 模板 4，另 downloads/×4、world/（無 nav 無按壓元件）。sale-leaseback.html 原本沒有 `</head>`，link 放 `<body>` 前。首批 15 頁（`3762746`）＝首頁＋四個下拉裡的 14 頁：按壓回饋（pointer-down 縮 .97、臨界阻尼 spring `linear()` 彈回）、nav 下拉從按鈕長出（blur→清晰）、FAQ `::details-content` 連續展開、tp-h1／art h1／bt-h1 負字距＋小字正字距、hero 進場微升（主圖零延遲）、手機底部條（footer `.cx-sticky-cta`＋topic.css `.tp-bar`）改懸浮玻璃 dock、reduced-motion／transparency／contrast。首頁另有內聯專屬段（AI 卡 View Transition、開關 transform）；**首頁 hero 精簡為眉標／h1／副標／電話鈕／AI 卡，四需求卡／信任列／快捷列／免責搬到 `.hero-more` 第二屏**，文字零增刪。Phase 1–3 配色同 09-20 版 | `grep -l 'fluid.css' *.html \| wc -l` → 164（＋en/index）；`grep -L fluid.css *.html \| wc -l` → 20；`curl -s https://cx468.com.tw/ \| grep -c 'class="hero-more"'` → 1；截圖 `行銷產出/視覺風格/apple-design-2026-09-22/` |
| 電話（09-22 平行 session 改，未重驗） | 憲法第十一節 09-22 改：CTA 兩支 02-2249-0517＋0958-139-786（`bede5bb` 全站 0931→0958）；反詐彈窗／聯絡四處恢復「市話／鄭經理／業務人員 0931」三號並列（`f3b88a2`）。09-20 版的 contactPoint 60 頁等數字未重驗 | `git show f3b88a2 --stat`；`grep -c 0931-087-996 anti-fraud-modal.html contact.html` |
| 追蹤／NAP geo／售後回租定義／企業線／「20 年」主詞 | 同 09-20 版（本 session 未動、未重驗）：`consultation-tracking.js` 65 頁；geo `24.9944428,121.4900325` 77 頁；SLB 統一 A 版；corporate-loan 健檢在前；20 年主詞＝團隊 | 見 `git show e1c4b7b:docs/letter-cx468-web.md` 第一節各列指令 |
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

### 🟢 近期已上線（對照用，細節見 git log 與 09-20 版信）
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

- 每天 12:00 精進會議（session 級排程，每個 session 用 CronCreate 重設）——**最新正本 `行銷產出/精進會議/2026-09-19.md`**（含 `2026-09-19-媽祖覆核.md`），其 §六＝下一場 Step 0 基準、§八「下次先驗五件」。09-17 §六硬期限現況（09-20 00:2x 取證）：新聞卡 ✅ `03e9d3e`、Threads ≥14 ✅（現剩 12 到 10-01）、週報 W37＋W38 ✅ 09-19 補寫、p2a 三修 🟡（GO 拆除＋FAIL 印原因已做，排程 17:15 未改＝T8）、**T0 小鋮「最低」雙護欄 ❌ 未動（`~/cx468-linebot/app.py:1844/1931/1941` 三處原樣，HEAD `37ed7f6`，期限 09-20）**。09-19 §六今日／明日硬期限：B2 sitemap ✅、llms.txt 接入 ✅、xinbei ai-bar ❌、「實際成數」❌ 4 頁、EP31+／新北 HowTo 未驗、iPAS Sir 09-22。
- 三日健檢 `com.cx468.healthcheck` 會推 🔴 到 Telegram——**收到要有人接**（memory `feedback_act_on_telegram_alerts`）；09-08 那則還躺著「Meta spend_cap 決策逾期」「週報監控瞎了」等 4 條。
- Threads 12:30；p2a 17:15（敏感稿要人回 GO，memory `feedback_human_go_gate_deadlocks_pipeline`）；`cx468-crawl` 每 2 小時。
- 換新聞卡前 `git log --oneline -5 -- radar-index.html` 算服役天數。

## 四、等使用者的事項

-1. 🟡 **GSC（非必送）**：09-23 兩批（15 頁 `3762746`＋146 頁 `d1d7d3a`）都是版型／CSS，內容未變，且第二批帶 `[nofresh]` 日期不動；要送就送首頁 `https://cx468.com.tw/` 一條即可。
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

## 五、歷史
各 session 做了什麼不再堆在這裡：`git log --oneline --since=2026-09-01`，以及 `git show e1c4b7b:docs/letter-cx468-web.md` 第五～十節（09-14～09-20 六段）。
