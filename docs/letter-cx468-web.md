# 交接信｜cx468-web（官網 repo）＋ CX468 雲端維運

> 現況快照，不是 changelog。歷史在 `git log`。
> 最後重寫：2026-09-05 09:20（Better 版型第四～六批 30 頁上線＋nav 二胎合規修正）
> 本次重寫原因：一、三、五節整節重寫、二節「Better 入口」段補試算器批次規格與線上驗證腳本；四節為 8/14 版保留、**本次未重驗**，接手前先查證。

## 一、當前狀態快照（2026-09-05 09:20 實測）

| 項目 | 值 | 重驗指令 |
|---|---|---|
| cx468-web HEAD | `5449609`＋本封交接信 commit，與 origin/main 一致、已部署（Pages 15 秒生效） | `cd ~/cx468-web && git status -sb && git log --oneline -6` |
| 工作區 | 乾淨。既有未追蹤 `scripts/archive/goal-scores.jsonl`、`scripts/fix_20year_subject.py`（**勿 add**，非本專案產物） | 同上 |
| Better 版型已套 **39 頁** | 服務 4＋總覽／二胎／新北三頁＝9；在地 area-{tucheng,xindian,banqiao,yonghe,zhonghe} 5；地價稅 guide 4；地價稅試算器 20 縣市頁＋入口頁 21 | `grep -l 'src="nav.js"' *.html \| wc -l` → 40（含首頁）；線上 `curl -s https://cx468.com.tw/penghu-land-value-tax.html \| grep -o 'bt-eyebrow">[^<]*'` |
| nav 現況 | 40 頁 nav.js；**74 頁仍 `data-include="nav"`**；**14 頁仍 `data-include="nav-tool"`**（小工具頁，清單見第三節） | `grep -l 'data-include="nav"' *.html \| wc -l`；`grep -l 'data-include="nav-tool"' *.html` |
| nav.js 合規模式 | `#nav` 帶 `data-cta="line"` → 右上與手機抽屜「免費評估」鈕改「LINE 線上諮詢」；second-mortgage／xinbei-second-mortgage 已掛 | `curl -s https://cx468.com.tw/second-mortgage.html \| grep -c 'data-cta="line"'` → 1；`curl -s https://cx468.com.tw/nav.js \| grep -c ctaLine` → ≥1 |
| 全站配色 | 紅 #C61B1C 0 檔 | `grep -l C61B1C *.html \| wc -l` → 0 |
| launchd | `fanjiuzhang-watch`／`healthcheck`／`indicators-local`／`adsreport` 四支 exit 0；**`leadspoll` 不在清單，原因未查** | `launchctl list \| grep cx468` |
| SEO/AEO/GEO 分數、FAQ 同源 | **本次未重跑**（30 頁 FAQ 同源用守恆腳本逐頁驗過 0 漂移；land-value-tax-calculator mismatch=2 是 HEAD 原有的腳本假陰性〔答案含「A：」前綴與行內 strong〕，非漂移） | `python3 scripts/audit_seo.py`、`python3 scripts/audit_faq_samesource.py` |

⚠️ **三個路徑陷阱**：
1. 網站程式碼在 `~/cx468-web/`，**不在 iCloud 專案夾**；iCloud `ＡＩ鋮馨/AI鋮馨官網/` 只是草稿鏡像（第四～六批未同步過去）。
2. `行銷產出/`、`知識庫/`、`制度/` 在 **iCloud 專案夾**，在 repo 裡 `ls` 會空手而回。
3. LINE bot 查驗一律用 `~/cx468-linebot`，iCloud 專案夾內那份是凍結殭屍複本。

🚨 **commit 配方（pre-commit hook 會把工作樹裡所有已修改 html 掃進你的 commit，平行建造者施工中尤其危險）**：`git add <自己的檔> && git commit --no-verify` → `python3 scripts/update_schema_datemod.py && python3 scripts/update_sitemap_lastmod.py`（讀 git commit 日期，所以要 commit 後跑）→ `git add <同一批檔> sitemap.xml && git commit --amend --no-verify --no-edit` → `git show --stat HEAD` 核對檔數。詳 memory `feedback_precommit_hook_sweeps_parallel_session_files`。

## 二、可複用資產／程序（8/29 版保留＋9/5 更新）

### 🆕 Better 對拷專案的入口（9/4 建立，9/5 更新）

- **拆解報告**：iCloud `行銷產出/策略簡報/2026-09-04-better.com官網拆解.md`（§3 逐頁 section 表、§5 色碼/字級/按鈕/卡片/間距實測、§8 不能照抄的 11 條）。143 張截圖在 `行銷產出/視覺風格/better.com-2026-09-04/`。
- **範本正本**＝`sale-leaseback.html`。變體：debt-consolidation（表格）／corporate-checkup（表單／五步驟）／services（總覽交錯列）／xinbei-sale-leaseback（文章型 h2 映射）／**area-xindian（在地頁：SVG 位置圖＋地圖 iframe＋實價登錄深藍帶＋租金長條圖＋時程＋POI 卡格，五頁段落配色以它為基準）**／**taipei-land-value-tax-guide（長文教學型：級距表 bt-table、範例卡、bt-dark-card 金鈕 CTA）**／**new-taipei-land-value-tax（試算器型：試算器整段原樣進白底 section、JS 零改動；必留三行 CSS 見批次規格）**。
- **nav.js**：淺色 `<div id="nav" data-theme="light"></div>`＋`<script src="nav.js"></script>`，body padding-top 64/58；不帶屬性＝深色。**`data-cta="line"`＝二胎合規模式**（兩顆免費評估鈕改 LINE）。不載 style.css；**不要改 style.css 的 nav 選擇器**。
- **派工規格**（iCloud `行銷產出/技術記錄/`）：
  - `2026-09-05-better版型派工共用規格.md`（硬規則 9 條＋自驗＋回報格式；9/5 已改為「hero 圖／眉標由 prompt 逐頁指定」＋規則 9「script／iframe 全留」）
  - `2026-09-05-地價稅試算器頁批次規格.md`（試算器型專用：script diff 指令、id 計數、handler 集合）
  - 派系列頁時 prompt 直接給「段落→底色／卡片／寬度」對照表（第四批 5 頁曾各走各的，並排目檢才發現；memory `feedback_parallel_agents_same_choice`）
- **驗收腳本**（同夾）：`pw_check.py <base_url> <page>…`（sw/h1/nav 底色/眉標/styleCss/console）；`slices.py <out_dir> <page>…`（本機 :8765 桌機 2400px／手機 3200px 切片截圖，主對話 Read 目檢）；`lvt_verify.py <page>…`（試算器頁：與 HEAD 版填同樣數字比對輸出、手機 scrollWidth、<16px 輸入框數）；`scripts/verify_text_conservation.py <file>`（守恆）。
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

### 🔴 第一順位：Better 版型套到其餘頁（Sir 定調「規格一模一樣、內容換鋮馨」）

已套 39 頁。剩餘候選（9/5 實掃）：

| 群組 | 頁數 | 備註 |
|---|---|---|
| 在地頁餘下：{banqiao,sanchong,tucheng}-property-finance＋{banqiao,hsinchu}-second-mortgage | 5 | 反 doorway 定例（memory `project_local_page_series_rules`）；**second-mortgage 兩頁要掛 `data-cta="line"`＋禁「免費評估」** |
| 小工具頁（現用 nav-tool）：affordability-calculator／land-tax-calculator／mortgage-calculator／realestate-tax-calculator／rental-yield-calculator／purchase-cost-calculator／second-mortgage-calculator／vacancy-cost-calculator／new-taipei-house-tax／lvr-observatory／lvr-rental／lvr-presale／tools／cx_radar_v4_demo | 14 | 用試算器批次規格；lvr-* 有即時資料 JS，先各做 1 頁先導；cx_radar_v4_demo 可能是廢頁先問 |
| 專題 topic-a~d、faq、about、knowledge、glossary、contact | 9 | 雜項 |
| 其餘 `data-include="nav"` 頁（繼承 8 頁保留不動、lp-*、文章頁等） | ~60 | `grep -l 'data-include="nav"' *.html` 列清單再分群 |

**接手三步**：① 讀第二節「Better 入口」＋兩份派工規格；② 逐頁指定 hero 圖／眉標／段落配色表寫進 prompt（同系列先做 1 頁當基準）；③ 一頁一建造者平行派（不帶 model 參數）、施工者不 add/commit，主對話跑守恆＋禁語＋`pw_check.py`＋`slices.py` 目檢＋（試算器）`lvt_verify.py`，再照第一節 commit 配方 commit 指名檔案。部署仍須 Sir 說「部署」。

### 🟡 順帶發現、未動（Sir 裁）

1. **nav-tool.html 第 1 行帶 `<meta name="robots" content="noindex">`**，由 include.js 注入還在用它的 14 頁；Google 渲染後可能照 noindex 處理。SEO 是最大目標，建議查 GSC 這 14 頁收錄狀態（第一順位表裡的小工具頁改 nav.js 後自然解掉）。
2. land-value-tax-calculator.html 正文「目前台北市與新北市已上線，其他縣市陸續建置中」已過時（22 縣市全上線），內容改動需媽祖。
3. 試算器頁 GA 片段沒有其他頁的 line_click／phone_click 事件（原樣未補）。

### 🟡 同專案的後續

1. nav.js MENU 原稿 24 個目標頁（compare／prepare／concept-*／investors 等）尚未建；建好才加回 MENU。
2. 全站換 nav.js 是套版型的一部分，不要單獨先換。
3. 首頁形式：SEO/GEO 影響要在精進會議看數據（memory `feedback_seo_aeo_top_priority`）。
4. 不放假客戶評價。
5. iCloud 草稿鏡像 `AI鋮馨官網/` 未同步（可選；正本永遠是 repo）。

### ⚠️ 以下為 8/29 版留下、未重驗

- lp-\*／地區變體頁未鋪 ai-bar；繼承 8 頁保留不動；AI 模式預設值仍「完整版」。
- 8/14 遺留：廣告首週判讀、新聞卡截止、回電 SOP 複核、CX-FUNDING 三處不一致、Anthropic auto-reload、Postgres 月費、Threads token（約 2026-10-08 到期，換發後更新 `~/.cx468/threads_token_issued`）。

### 日常常態

- 每天 12:00 精進會議（session 級排程，每個 session 用 CronCreate 重設）。
- 三日健檢 `com.cx468.healthcheck`；本機指標；曝光巡檢 08:12；Threads 12:30；`leadspoll` 目前不在 launchd 清單（見第一節）。
- 換新聞卡前 `git log --oneline -5 -- radar-index.html` 算服役天數；改卡片註解格式會弄壞 `~/cx468-ga4-daily/health_check.py` regex。

## 四、等使用者的事項

> 1–6 為 8/14 版留下、本次未重驗。

1. 🔴 **GMB 影片驗證**——GEO 站外總開關。站外簡介工作 7/23 已完成 90%（四平台結案，別再誤判「未動」）；剩服務區域／次要電話／「更多」屬性等驗證通過。帶法：`行銷產出/技術記錄/2026-08-14-GMB驗證解鎖checklist.md`
2. **企業貸款專案三處資料不一致**＋三個阻塞數字（資本額／勞保投保名冊／營業項目代碼）
3. **Meta `spend_cap`**——8/14 估約 8/22 撞頂，**日期已過，務必先查現值**
4. **Anthropic auto-reload**：console.anthropic.com → Billing，建議「低於 $5 自動補到 $50」
5. **名單回電**——SOP 已備妥，回電前務必先讀；名單**禁止回灌 Meta 做自訂受眾／類似受眾**
6. **合一地政士事務所洽談**——只有老闆本人能談（面談包已過媽祖，四條紅線見 memory `project_land_agent_channel_heyi`）
7. 🆕 **GSC 催收**：32 條網址清單在 `行銷產出/技術記錄/2026-09-05-GSC網址清單-better第四五六批.txt`，單頁走「網址審查→要求建立索引」；Sitemap 欄只放 sitemap.xml。

## 五、本 session（9/5 07:40→09:20）做了什麼

Sir 指令：「1＋2＋3」（在地 5 頁／nav 合規／地價稅 25 頁）→「部署」→「交接」。

| 事項 | 證據 |
|---|---|
| nav 二胎合規：nav.js 加 `data-cta="line"` 模式，兩頁掛屬性 | `802c8ae`（nav.js +17/−4）；線上兩頁 nav「免費評估」0、CTA＝LINE 線上諮詢，對照頁 services 仍 2 |
| 第四批在地 5 頁（5 建造者平行；並排目檢後再發 12 點配色對照表對齊） | `3119424`（5 檔 +2097/−903）；守恆 0／禁語 2=2／FAQ 0 漂移；順帶修 `.bar-fill{display:block}`（長條圖原本畫不出來） |
| 第五批 4 guide＋新北試算器先導 | `04c6c5f`（5 檔 +1842/−883）；主對話補修：台中藍鈕白字、台北 CTA 改 dark-card、新北麵包屑進 hero、卡片 min-height、先導頁手機溢出 16px＋輸入框 16px |
| 第六批 20 試算器頁（5 建造者 ×4 頁，先導頁當範本） | `5449609`（20 檔 +6824/−2531）；`lvt_verify.py` 20 頁試算結果與 HEAD 逐值相同、手機 sw=390、輸入框 ≥16px、console 0 |
| 部署 | fetch+rebase+push，`ls-remote`＝本機 5449609；Pages 15 秒；線上 30 頁 200＋眉標＋nav.js＋無 style.css；Playwright 線上 6 頁桌機手機 console 0、Maps 無 403、長條圖 10 條、澎湖試算手機實測 24,000 元 |
| 落地 | memory 補：`feedback_precommit_hook_sweeps_parallel_session_files`（commit 配方）、`feedback_parallel_agents_same_choice`（段落配色對照表）；iCloud 技術記錄新增試算器批次規格＋`lvt_verify.py`＋`slices.py`＋GSC 網址清單 |

建造者回報的可接受偏差（未改）：guide 頁 hero 圖 4/5 直裁橫幅；試算器頁各自查價機制（proxy／openOfficialQuery／無鈕）原樣；keelung 名詞解釋＋在地資訊兩段放 CTA 後；JSON-LD dateModified 由鮮度腳本統一為 commit 日。
