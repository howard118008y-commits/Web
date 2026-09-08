# 交接信｜cx468-web（官網 repo）＋ CX468 雲端維運

> 現況快照，不是 changelog。歷史在 `git log`。
> 最後更新：2026-09-08 18:40（SEO 內鏈收斂 7 頁 commit `a1bdb25`，**Sir 令「推」已 push、線上 7 頁內鏈實測全命中**）
> 本次更新原因：一節 HEAD 更新；三節新增 🔴 第一順位「SEO 地區×品項矩陣」（Sir 09-08 指定下個 session 主線）、Better 版型順延為第二；五節重寫。
> ⚠️ 二節與三節其餘小節為 9/5 版保留，**本次未重驗**。

## 一、當前狀態快照（2026-09-08 18:40 實測）

| 項目 | 值 | 重驗指令 |
|---|---|---|
| cx468-web HEAD | `a1bdb25`（SEO 內鏈收斂 7 頁，線上實測 7/7 命中）；前一個 `3b06bda` 是 indicators workflow 自動 commit；`0be1b9e`＋本封 docs commit，與 origin/main 一致、已部署（線上 topic-a 等 12 頁 nav.js=1、affordability 新句=1） | `cd ~/cx468-web && git status -sb && git log --oneline -6` |
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

### 🔴 第一順位：SEO 地區 × 品項矩陣擴張（Sir 2026-09-08 指定，下個 session 主線）

**起因**：Sir 聽前公司同仁說當舖靠網站 SEO 做到「一個月 30 通以上電話」，要求參考做法。09-08 實查結論如下。

**已查證的事實（都可重驗）**：

| 事實 | 數字 | 重驗法 |
|---|---|---|
| GSC 近 28 天（08-09→09-05） | 曝光 12,829、點擊 362、CTR 2.82%、均排 10.29 | `~/cx468-ga4-daily/gsc.py`（service account，非 OAuth，未過期） |
| **商業詞全部 0 點擊** | 房屋二胎 88 曝光/排 50.3、二胎房貸 84/61.1、售後回租 40/25.3、二胎 38/39.9 | 同上 |
| 曝光集中在工具頁 | rental-yield-calculator 1,962 曝光/20 點擊；搜「租金報酬率」的是房東不是客戶 | 同上 |
| **但在地詞我們是第 1 名** | 「中和 二胎房貸」自然 #1 `second-mortgage.html`、#3 `zhonghe-second-mortgage.html`，**Google AI 摘要引用我方兩篇** | 實機 Playwright、`pws=0`、定位新北中和 |
| **關鍵字自相殘殺** | 全站 **21 頁** title 帶「二胎」，最大一頁僅 2,796 字 | `grep -l '<title>[^<]*二胎' *.html` |
| 對照組：華德當舖 | 141 頁；**樞紐頁 `/moto-loan/` 7,559 字＋FAQ 8 題**；地區頁 45 支各 2,085 字（同模板）＋FAQ 2 題＋1 案例 | nicepawn.com.tw/sitemap |
| 對照組：大展當舖 | 155 頁，其中 **94 頁是 FAQ 一題一頁**，單題頁 2,917 字 | 24079222.com |
| GMB 差距 | 鋮馨 **1 則評論**（上月 601 次查看、204 次互動）；「新北 房屋二胎」Local Pack 第 1 名只有 **17 則**，第 2、3 名 **0 則照樣上榜** | 實機搜尋 |
| Local Pack 有無 | 「新北 房屋二胎」有、「中和 貸款諮詢」有、「中和 二胎房貸」**無**（只有付費地點） | 同上 |

**核心判斷**：泛詞打不贏（對手是當舖／代書／財務公司，砸廣告），**加地區詞就贏**。當舖的「地區 × 品項矩陣」是我方唯一打得贏的戰場，缺的是覆蓋面。

**已完成（09-08，`a1bdb25`）**：7 頁補上指向樞紐頁 `second-mortgage.html` 的內鏈，線上 7/7 命中。原本 12/18 已連，補完剩下 7 頁。

**下一步（未做，依序）**：
1. **改指向**：`compare-options.html` 等多頁的「二胎」主連結指向 `article-second-mortgage.html`（文章）而非樞紐頁，兩頁仍在互搶。光加連結不夠。
2. **樞紐頁加重**：`second-mortgage.html` 現僅 2,004 中文字／FAQ 6 題，對照華德樞紐 7,559 字／FAQ 8 題，缺口 3.8 倍。
3. **矩陣擴張**：既有 19 支在地頁（中和 5、板橋 3、永和 3、土城 3、新店 1、三重 1）；**台北市 12 區完全沒有在地服務頁**；新北未做：新莊、蘆洲、樹林、汐止、淡水、林口、三峽、五股、泰山等。
4. **GMB 評論**：只能 Sir 做，從 1 衝到 20 就有機會進 Local Pack。

**接手前必讀的禁忌**：
- ⛔ **當舖鉤子詞一個都不能抄**：免留車／免聯徵／免保人／審核寬鬆／過件率／當日撥款／最低利率 1% 起／銀行不借沒關係——實查列出 14 類全中憲法第六節。我方替代鉤子是「被拒絕過還有路」（三家銀行拒絕、月付繳不出來、只繳利息本金不動）。
- ⛔ **商家名塞關鍵字不可學**：Local Pack 6 家有 5 家把「地區+品項」整串塞進 GMB 名稱，違反 Google 政策；台北當舖 Pack 第 1 名的金成當舖用純法定名稱照樣贏。
- ⛔ 我方 GMB 類別是「不動產管理服務」，合規正確，**勿改成金融類**。GMB 營業時間 10:00–17:00 也是對的，勿改（memory `reference_business_hours_gmb_vs_constitution`）。
- ⚠️ 內容產出派 DeerFlow **必須拆小段**：整包 7,000 字派工會 `GraphRecursionError`（09-08 踩過，100 步繞圈、零產出、exit code 仍是 0 假成功）。派工必給停止條件、限制搜尋次數、明設 `recursion_limit`。
- 相關 memory：`project_local_page_series_rules`、`feedback_positioning_advisor_not_agent`、`feedback_compliance_no_free_eval_second_mortgage`、`reference_business_hours_gmb_vs_constitution`、`project_seo_geo_aeo_overhaul`

### 🟠 第二順位：Better 版型套到其餘頁（Sir 定調「規格一模一樣、內容換鋮馨」）

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
4. 🔴 **Anthropic 帳務**（09-08 更新）：當日餘額歸零害小鋮啞掉半天，Sir 已儲值。仍待辦：①**開啟 auto-reload**（Billing，建議低於 $5 自動補到 $50）②**開一把 Admin key** 丟 `~/.cx468/`——目前沒有，查用量 API 會被擋，只能靠反推 ③ 其餘 9 個服務仍共用一把 key，建議比照 DeerFlow 分 Workspace，Usage 才分得出誰花的
5. **名單回電**——SOP 已備妥，回電前務必先讀；名單**禁止回灌 Meta 做自訂受眾／類似受眾**
6. **合一地政士事務所洽談**——只有老闆本人能談（面談包已過媽祖，四條紅線見 memory `project_land_agent_channel_heyi`）
7. 🆕 **GSC 催收**：三份清單在 `行銷產出/技術記錄/`——`2026-09-05-GSC網址清單-better第四五六批.txt`（32 條）、`2026-09-05-GSC網址清單-better第七批在地5頁.txt`（5 條）、`2026-09-05-GSC網址清單-better第八批小工具11頁.txt`（11 條）。單頁走「網址審查→要求建立索引」（每日約 10 條配額，先送二胎與試算器）；Sitemap 欄只放 sitemap.xml。Indexing API 對一般頁無效（indexing_cron.py 檔頭），別再走 API。 **9/5 16:20 實查（Inspection API）：第七＋八批 16 頁全部「已收錄」，但 lastCrawl 全在改版前（最舊 vacancy 06-12）→ 要的是重抓；優先序清單 `2026-09-05-GSC催收優先序-第七八批16頁.txt`（依 lastCrawl 最舊排前）。** 🆕 第九批清單 `2026-09-06-GSC網址清單-better第九批雜項9頁＋lvr2頁.txt`（12 條，含 affordability）——已部署，可送。
8. 🆕 **GMB 評論衝量**（只有 Sir 能做，09-08 實查）：鋮馨目前 **1 則評論**，「新北 房屋二胎」Local Pack 第 1 名只有 17 則、第 2/3 名 0 則照樣上榜——**從 1 衝到 20 就有機會進地圖包**。上月商家檔案被查看 601 次、互動 204 次，轉換成評論的比例極低。GMB 最近一則貼文已是 4 個月前。
9. 🆕 **`cx468-crawl` 是否降頻**：一天跑 12 次，超過 Sir 定的「重複檢查一天不超過三次」，但它不打 Anthropic 不花 API 錢。降頻代價是新聞最晚 8 小時才被抓到。**Sir 未裁，未動**。

## 五、本 session（2026-09-08 14:00→18:45）做了什麼

起點是 Sir 問「當舖靠 SEO 一個月接 30 通電話，我也要」，中途插入一場 API 餘額歸零事故，最後回到 SEO。

### 5-1 SEO 調查與內鏈收斂（已上線）
- 兩隻 agent 平行實查：我方現況（19 支在地頁、GSC 28 天數據、電話 CTA 現況）＋當舖業者打法拆解（3 家 sitemap、Local Pack、14 類禁用鉤子詞）。結論全數寫入第三節第一順位。
- **推翻兩個原本的假設**：①「工具頁缺內鏈」——實查內鏈本來就有（租金報酬率頁 6 個、繼承頁 10 個），CTR 低是搜尋意圖問題不是內鏈問題；②「二胎房貸排 61 名所以打不贏」——加了地區詞「中和 二胎房貸」我方是自然結果第 1 名，AI 摘要還引用兩篇。
- **已上線**：7 頁補內鏈到樞紐頁（`a1bdb25`），線上 7/7 實測命中。
- 重驗：`for u in tools glossary compare-options article-loan-integration article-second-mortgage-scam xinbei-second-mortgage yonghe-home-loan; do curl -s "https://cx468.com.tw/$u.html" | grep -c 'href="second-mortgage.html"'; done` → 全部 1

### 5-2 Anthropic API 餘額歸零事故（已排除）
- 14:2x 發現 `credit balance is too low`，**同一把 key 注入 9 個 Render 服務**（env group `cx468-shared-secrets`），小鋮 LINE AI 客服對客戶啞掉。
- **根因**：09-05 一天跑了 **12 輪全量 eval、879 題、約 $52.7**。eval 是本機 in-process 跑的**不經 Render，log 完全查不到**，所以第一輪反推誤把 `cx468-crawl`（一天 12 次）當頭號嫌疑——實際上它程式碼零呼叫 Anthropic，完全清白。
- 事故時間軸（Render log 原文）：09-04 23:51 首次餘額不足 → 09-06 06:14 恢復 → **09-07 10:34Z 撞月度支出上限**（錯誤字串與餘額歸零不同）→ 09-08 台北 14:1x 仍可用 → 之後歸零。
- Sir 已儲值，18:3x 實測兩把 key 皆可用，小鋮線上實測回話 200／237 字／禁語零命中。

### 5-3 eval 花錢閘門（已 push，cx468-linebot `467d810`）
三道閘門，先撞到哪個算哪個：
| 閘門 | 上限 | commit |
|---|---|---|
| 預設只跑 13 題 trap 合規題（全量要 `--full`） | $4.02 → **$0.78** | `08d3b2f` |
| **每日執行 3 次**（Sir 令：重複檢查一天不超過三次） | — | `467d810` |
| 每日累計 150 題 | $9 硬頂 | `476797a` |
- 補掉的洞：原本 lock 只認 `is_full`（沒帶 `--ids/--type`），用 `--ids` 列滿全部 67 個題目 id 即可偽裝抽測跑全量，且估價 $4.02 低於 $5 門檻，**兩道閘門同時失效**。
- 設計要點：**先記帳再開跑**，中途失敗也算，堵住「失敗→重跑」繞過上限。
- 實測：149+13 擋下且不記帳、`--ids` 列滿 67 題擋下、連跑 4 次第 4 次擋下、單題放行記帳 1。
- 套回 09-05：$52.74 → 最多 $2.34。

### 5-4 DeerFlow 金鑰隔離（已完成）
- DeerFlow（`~/deer-flow`，Sir 09-05 要求安裝）原本與 9 個線上服務**共用同一把 key**，且設定用最貴的 `claude-fable-5-1`（$10/$50）。
- 09-08 兩次派工全失敗（`GraphRecursionError` 100 步繞圈；第二次撞餘額歸零），**exit code 都是 0**，檔案零落地——不驗檔案就會被騙過去。
- 歷史成績：4 個 thread、348 步、**1 成 2 敗 1 測試**。唯一成功產出是 `行銷產出/競品研究/2026-09-06-中和區近三個月房價走勢-助理研究.md`（2,138 字、31 個來源、數字抽驗過）。
- **已改為 workspace-scoped key**（Console → Workspaces → deerflow，Sir 設了預算上限），與 `~/.cx468/anthropic.key` 完全分離，實測有效。重驗：比對 `~/deer-flow/.env` 與 `~/.cx468/anthropic.key` 尾碼應不同。
- ⚠️ 換 key 不等於隔離預算——**同帳號所有 key 共用餘額池**，只有 Workspace 能設獨立上限。其餘 9 個服務目前仍共用一把，未分。

### 5-5 Sir 的兩個裁示
1. **GMB 營業時間 10:00–17:00 不改**——「10 點才算是鋮馨租賃店裡有人」。我原本誤判為與憲法 09:00–18:00 不一致的缺失，Sir 當場否決。已寫 memory `reference_business_hours_gmb_vs_constitution`，NAP 稽核時營業時間欄排除比對。
2. **重複檢查的東西一天不超過三次**——已寫 memory `feedback_repeated_check_max_three_per_day`，並落實到 eval。盤點全部排程後只有 `cx468-crawl`（12 次/日）超標，但它不打 Anthropic 不花 API 錢，**是否降頻 Sir 未裁，未動**。

### 5-6 本 session 新增的 memory
- `feedback_repeated_check_max_three_per_day`——重複檢查每日 3 次硬閘門、先記帳再開跑
- `reference_business_hours_gmb_vs_constitution`——GMB 時間 10-17 是對的，勿建議改
