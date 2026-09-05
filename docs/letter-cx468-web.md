# 交接信｜cx468-web（官網 repo）＋ CX468 雲端維運

> 現況快照，不是 changelog。歷史在 `git log`。
> 最後更新：2026-09-05 23:45（Better 第九批雜項 9 頁＋lvr 生成頁 2 頁 commit `01e01aa`、affordability 合規句 `790a1d9`，累計 66 頁；**尚未部署，等 Sir 說「部署」**）
> 本次更新原因：一、三、五節更新；四節 1–6 為 8/14 版保留、**本次未重驗**，7 補第九批 GSC 清單。

## 一、當前狀態快照（2026-09-05 23:45 實測）

| 項目 | 值 | 重驗指令 |
|---|---|---|
| cx468-web HEAD | `790a1d9`（本地）；origin/main 仍在 `80cc5cf`——**`01e01aa`＋`790a1d9` 兩筆未 push、未部署**，Sir 說「部署」才走 `/deploy` | `cd ~/cx468-web && git status -sb && git log --oneline -6` |
| 工作區 | 乾淨。既有未追蹤 `scripts/archive/goal-scores.jsonl`、`scripts/fix_20year_subject.py`（**勿 add**，非本專案產物） | 同上 |
| Better 版型已套 **66 頁** | 服務 4＋總覽／二胎／新北三頁＝9；在地 area-{tucheng,xindian,banqiao,yonghe,zhonghe} 5；地價稅 guide 4；地價稅試算器 20 縣市頁＋入口頁 21；**第七批（9/5 13:00）在地融資諮詢 {banqiao,sanchong,tucheng}-property-finance 3＋{banqiao,hsinchu}-second-mortgage 2（後兩頁掛 data-cta=line）**；**第八批（9/5 15:00，commit ded7533）小工具 11 頁：{affordability,land-tax,mortgage,purchase-cost,rental-yield,second-mortgage,realestate-tax,vacancy-cost}-calculator＋new-taipei-house-tax＋lvr-observatory＋tools（second-mortgage-calculator 掛 data-cta=line）**；**第九批（9/5 23:40，commit 01e01aa）雜項 9 頁 topic-a/b/c/d＋faq＋about＋knowledge＋glossary＋contact ＋ 生成頁 lvr-presale／lvr-rental（走 build_extras.py 模板）** | `grep -l 'src="nav.js"' *.html \| wc -l` → 67（含首頁）；線上 `curl -s https://cx468.com.tw/penghu-land-value-tax.html \| grep -o 'bt-eyebrow">[^<]*'` |
| nav 現況 | 67 頁 nav.js（含首頁）；**64 頁仍 `data-include="nav"`**；**1 頁仍 `data-include="nav-tool"`**（cx_radar_v4_demo，已裁不套版：每日 indicators workflow 自動覆寫、canonical 指 radar-index） | `grep -l 'data-include="nav"' *.html \| wc -l`；`grep -l 'data-include="nav-tool"' *.html` |
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

### 🔴 第一順位：Better 版型套到其餘頁（Sir 定調「規格一模一樣、內容換鋮馨」）

已套 55 頁（第七批 5 頁 9/5 13:00、第八批 11 頁 9/5 15:00 上線，commit ded7533）。剩餘候選（9/5 實掃）：

| 群組 | 頁數 | 備註 |
|---|---|---|
| ~~在地頁餘下：{banqiao,sanchong,tucheng}-property-finance＋{banqiao,hsinchu}-second-mortgage~~ ✅ 第七批已上線 | 0 | 反 doorway 定例（memory `project_local_page_series_rules`）；**second-mortgage 兩頁要掛 `data-cta="line"`＋禁「免費評估」** |
| ~~小工具頁 14~~ ✅ 全數上線（第八批 11＋第九批 lvr 2）；cx_radar_v4_demo 裁定不套版（生成頁） | 0 | — |
| ~~專題 topic-a~d、faq、about、knowledge、glossary、contact~~ ✅ 第九批已 commit（01e01aa，待部署） | 0 | topic 四頁段落基準：hero→深藍帶(label+h2+p 靠左+三數字)→麵包屑+quick-answer→指標卡 3 欄→FAQ→名詞(白底)→CTA 帶→bt-dark-card(LINE 金鈕在前)→資料來源；小標一律 bt-label 金色置中 |
| 其餘 `data-include="nav"` 頁（繼承 8 頁保留不動、lp-*、文章頁等） | 64 | `grep -l 'data-include="nav"' *.html` 列清單再分群 |

**接手三步**：① 讀第二節「Better 入口」＋兩份派工規格；② 逐頁指定 hero 圖／眉標／段落配色表寫進 prompt（同系列先做 1 頁當基準）；③ 一頁一建造者平行派（不帶 model 參數）、施工者不 add/commit，主對話跑守恆＋禁語＋`pw_check.py`＋`slices.py` 目檢＋（試算器）`lvt_verify.py`，再照第一節 commit 配方 commit 指名檔案。部署仍須 Sir 說「部署」。

### 🟡 順帶發現、未動（Sir 裁）

1. **nav-tool.html 的 noindex**：只剩 cx_radar_v4_demo／lvr-presale／lvr-rental 3 頁還走 nav-tool（其餘 11 頁 9/5 改 nav.js 後自然解掉）。
2. land-value-tax-calculator.html 正文「目前台北市與新北市已上線，其他縣市陸續建置中」已過時（22 縣市全上線），內容改動需媽祖。
3. 試算器頁 GA 片段沒有其他頁的 line_click／phone_click 事件（原樣未補）。
4. ~~合規：affordability「最優利率」~~ ✅ 媽祖核定句已套（790a1d9）。**新發現**：該頁自始沒有免責尾注（「非金融機構／最終核貸」0 命中；同批 land-tax／purchase-cost／second-mortgage／vacancy-cost 都有）→ 待媽祖給一句、Sir 裁。
5. ~~cx_radar_v4_demo~~ ✅ 裁定不套版（每日 indicators workflow 覆寫、canonical 指 radar-index）。
6. lvr 圖表 PNG 與社群圖卡仍紅系（`scripts/lvr/make_charts.py`／`make_social_cards.py` 產），全站藍金後未跟；改色要動這兩支再等 workflow 重跑。

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
7. 🆕 **GSC 催收**：三份清單在 `行銷產出/技術記錄/`——`2026-09-05-GSC網址清單-better第四五六批.txt`（32 條）、`2026-09-05-GSC網址清單-better第七批在地5頁.txt`（5 條）、`2026-09-05-GSC網址清單-better第八批小工具11頁.txt`（11 條）。單頁走「網址審查→要求建立索引」（每日約 10 條配額，先送二胎與試算器）；Sitemap 欄只放 sitemap.xml。Indexing API 對一般頁無效（indexing_cron.py 檔頭），別再走 API。 **9/5 16:20 實查（Inspection API）：第七＋八批 16 頁全部「已收錄」，但 lastCrawl 全在改版前（最舊 vacancy 06-12）→ 要的是重抓；優先序清單 `2026-09-05-GSC催收優先序-第七八批16頁.txt`（依 lastCrawl 最舊排前）。** 🆕 第九批清單 `2026-09-06-GSC網址清單-better第九批雜項9頁＋lvr2頁.txt`（12 條，含 affordability）——**部署後才送**。

## 五、本 session（9/5 10:00→16:10）做了什麼

Sir 指令：「1」（在地餘 5 頁）→「部署」→「1＋2＋3」（精進會議：平行 session 已開，本 session 只補記）→「1」（小工具 14 頁）→「部署」→「交接＋送索引」。

| 事項 | 證據 |
|---|---|
| 第七批在地 5 頁（{banqiao,sanchong,tucheng}-property-finance＋{banqiao,hsinchu}-second-mortgage） | `c2eb699`→rebase `05d4f37`；守恆 0／FAQ 0 漂移／禁語 old=new；二胎兩頁 data-cta=line；線上 5 頁 200 |
| 第八批小工具 11 頁（試算器 9＋lvr-observatory＋tools） | `6b61818`→rebase `ded7533`；script diff 0、id 全保留、HEAD vs 新版填同值輸出逐 id 相同（土增稅 829 id）；72 片截圖目檢；線上 11 頁 200、Playwright console 0 |
| lvr 生成器模板同步 | 同 commit：`scripts/lvr/build_observatory.py` +346/−123，`LVR_HTML_DEST` 可覆寫，stub 生成 vs 手工 diff 0 |
| 主對話統一分歧 | 第七批：bt-who 底色／四卡寬度／相關文章 4 欄；第八批：試算器外框 bt-in、英文小標 bt-label 置 h1 上、快速答案鈕 LINE 藍＋電話 ghost、表單 CTA 主藍、二胎眉標改「二胎房貸試算」 |
| 精進會議 | 12:46 版由平行 session 產出；本 session 加「八、補記」＋行動項 15 |
| 落地 | 技術記錄：`2026-09-05-小工具頁批次規格.md`、GSC 第八批清單；`pw_check.py`／`slices.py` 加去 .html 防呆；memory 新增 `feedback_generated_pages_overwritten_by_workflow`、補 `feedback_parallel_agents_same_choice` 一行 |

雷點（本 session 親踩）：①`pw_check.py`／`slices.py` 參數不帶 .html（已防呆）；②反詐 modal 鎖捲動→整頁截圖要先 `localStorage.setItem('cx_antifraud_v1',…)`；③`indexing_cron.py` 本機跑近 7 天更動頁 50 頁逐一 Inspection 會超過 10 分鐘，要查特定頁自寫精簡版（scratchpad `inspect16.py` 思路：直接打 `searchconsole.googleapis.com/v1/urlInspection/index:inspect`）。

## 五之二、本 session（9/5 23:22→23:45）做了什麼

Sir 指令：「1＋2＋3＋4」（雜項 9 頁／lvr 移植／兩件待拍板／精進會議 Step 0）。

| 事項 | 證據 |
|---|---|
| 第九批雜項 9 頁（topic-a/b/c/d、faq、about、knowledge、glossary、contact） | commit `01e01aa`；守恆 9 頁「舊有新無」0（contact 舊徽章 1）、「新有舊無」僅眉標；faq mismatch 10＝HEAD 基線假陰性；全站 `audit_faq_samesource.py` 122 同源 0 漂移；禁語 old=new；pw_check 桌機/手機 11 頁 console 0；88 片截圖目檢 |
| topic 四頁分歧統一 | 一個建造者對齊：section 序列四頁 `sort -u`=1；藍帶 h2 靠左；小標 bt-label 置中；dark-card LINE 金鈕在前 |
| lvr-presale／lvr-rental 生成器移植 | 同 commit：`build_extras.py` 409 行改、`aeo_blocks.py` +41（純新增）；重生成 vs repo diff 只剩時間戳；observatory 迴歸未跑（`_cache` 缺 pkl，替代驗證 head_jsonld 逐字相符） |
| affordability「最優利率」 | 媽祖判必改，定稿句已套，commit `790a1d9`；全站 `最優利率|最佳利率|最低利率` 其他 0 命中 |
| cx_radar_v4_demo | 裁不套版（理由見一節 nav 現況） |
| 精進會議 Step 0 | 寫進 `行銷產出/精進會議/2026-09-05.md` 第十節（M1 ✅、其餘未動屬同日正常、M8 MEMORY.md 反向增長 213 行） |
| 落地 | GSC 第九批清單；memory `feedback_generated_pages_overwritten_by_workflow` 補 cx_radar 一段 |

雷點（本 session）：①zsh 裡 `F="a b c"; git add $F` 不會分詞（pathspec 找不到），用陣列 `F=(a b c); "${F[@]}"`；②topic 四頁的 nav 不是 data-include，是 inline `fetch('nav.html')`，grep `data-include="nav"` 會漏掉它們；③平行建造者同系列 4 頁仍各走各的（順序／小標／鈕序），主對話並排目檢後再派一個統一，比 prompt 寫再細都保險。

