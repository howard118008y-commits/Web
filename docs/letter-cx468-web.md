# 交接信｜cx468-web（官網 repo）＋ CX468 雲端維運

> 現況快照，不是 changelog。歷史在 `git log`。
> 最後更新：2026-09-09 03:0x（HEAD `1d4586b`，本 session 三筆 commit 皆已 push、線上實測 200）
> 本次更新原因：**Sir 09-09 定調「SEO 成敗看有沒有電話來的客戶」**——第三節優先順序整節依此重寫（產頁降級，量得到電話與 GMB 升為第一）；一節 HEAD／線上數字重驗；五節重寫。
> ⚠️ 二節與三節🟠🟡小節為 9/5 版保留，**本次未重驗**。

## 一、當前狀態快照（2026-09-09 03:0x 重驗，🆕 列為本次實測）

| 項目 | 值 | 重驗指令 |
|---|---|---|
| cx468-web HEAD | `1d4586b`（媽祖複查逐字修正三支在地頁＋area 頁內鏈，平行 session 推的）；本 session 三筆：`8af471e` 內鏈收斂、`e022fb6` 樞紐頁加重、`c742d42` 三重＋新莊在地頁。與 origin/main 一致、已部署 | `cd ~/cx468-web && git status -sb && git log --oneline -6` |
| 工作區 | 乾淨。既有未追蹤 `scripts/archive/goal-scores.jsonl`、`scripts/fix_20year_subject.py`（**勿 add**，非本專案產物） | 同上 |
| Better 版型已套 **66 頁** | 服務 4＋總覽／二胎／新北三頁＝9；在地 area-{tucheng,xindian,banqiao,yonghe,zhonghe} 5；地價稅 guide 4；地價稅試算器 20 縣市頁＋入口頁 21；**第七批（9/5 13:00）在地融資諮詢 {banqiao,sanchong,tucheng}-property-finance 3＋{banqiao,hsinchu}-second-mortgage 2（後兩頁掛 data-cta=line）**；**第八批（9/5 15:00，commit ded7533）小工具 11 頁：{affordability,land-tax,mortgage,purchase-cost,rental-yield,second-mortgage,realestate-tax,vacancy-cost}-calculator＋new-taipei-house-tax＋lvr-observatory＋tools（second-mortgage-calculator 掛 data-cta=line）**；**第九批（9/5 23:40，commit 01e01aa）雜項 9 頁 topic-a/b/c/d＋faq＋about＋knowledge＋glossary＋contact ＋ 生成頁 lvr-presale／lvr-rental（走 build_extras.py 模板）** | `grep -l 'src="nav.js"' *.html \| wc -l` → 67（含首頁）；線上 `curl -s https://cx468.com.tw/penghu-land-value-tax.html \| grep -o 'bt-eyebrow">[^<]*'` |
| nav 現況 | 67 頁 nav.js（含首頁）；**64 頁仍 `data-include="nav"`**；**1 頁仍 `data-include="nav-tool"`**（cx_radar_v4_demo，已裁不套版：每日 indicators workflow 自動覆寫、canonical 指 radar-index） | `grep -l 'data-include="nav"' *.html \| wc -l`；`grep -l 'data-include="nav-tool"' *.html` |
| nav.js 合規模式 | `#nav` 帶 `data-cta="line"` → 右上與手機抽屜「免費評估」鈕改「LINE 線上諮詢」；second-mortgage／xinbei-second-mortgage 已掛 | `curl -s https://cx468.com.tw/second-mortgage.html \| grep -c 'data-cta="line"'` → 1；`curl -s https://cx468.com.tw/nav.js \| grep -c ctaLine` → ≥1 |
| 🆕 二胎樞紐頁 | `second-mortgage.html` 線上 **5,234 中文字／FAQ 10 題**（09-08 前為 2,380／6） | `curl -s https://cx468.com.tw/second-mortgage.html \| grep -c '<details'` → 10 |
| 🆕 二胎在地頁 | **22 支**（本 session +3：新店 4,830／三重 4,731／新莊 5,182 中文字，線上實測） | `for u in xindian sanchong xinzhuang; do curl -s https://cx468.com.tw/$u-second-mortgage.html \| grep -c '<details'; done` → 8 8 8 |
| 🆕 可點電話（render 實測） | 三支新在地頁線上各有 **5 個 `tel:` 連結**（反詐 modal ☎／「撥打 02-2249-0517」／「一鍵撥號」／footer 兩支）＋ **7 個 LINE 連結**。⚠️ **靜態 grep 會誤判為 0**（全靠 include 注入，memory `feedback_audit_cta_needs_render_not_grep`） | playwright 開線上頁跑 `document.querySelectorAll('a[href^="tel:"]').length` |
| 🆕 phone_click 監聽缺口 | 全站 119 頁有 `tel:`、僅 106 頁有 `phone_click`；**缺 10 頁真頁**（含 banqiao／sanchong／tucheng／yonghe／zhonghe-property-finance 五支在地融資諮詢頁、compare-options、glossary、article-foreclosure、new-taipei-house-tax、zhonghe-sale-leaseback） | `comm -23 <(grep -l 'tel:' *.html \| sort) <(grep -l 'phone_click' *.html \| sort)` |
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

### 🔴 第一順位：讓 SEO 生出「打電話進來的客戶」（Sir 2026-09-09 定調）

**Sir 原話：「SEO 要有電話來的客戶」。** 驗收標準從此不是頁數、字數或排名，是**進線電話數**。
下面依「離一通電話多近」排序，不是依工程量。

**先認清這條鏈條，哪一段斷了就補哪一段：**
`在地詞排到前面 → 使用者點進來 → 頁面上按下撥號 → 電話被接到 → 記進 CRM`

| 段 | 現況（09-09 實測） | 斷了嗎 |
|---|---|---|
| 排名 | 「中和 二胎房貸」自然結果 #1、AI 摘要引用兩篇 | ✅ 沒斷 |
| 點擊 | GSC 28 天商業詞**全部 0 點擊**（房屋二胎 88 曝光/排 50.3、二胎房貸 84/61.1） | ⚠️ 泛詞斷；在地詞本身量小 |
| 按撥號 | 三支新在地頁 render 實測有 5 個 `tel:`、7 個 LINE | ⚠️ 電話被 LINE 蓋過 |
| 量得到 | 10 支真頁有 `tel:` 卻**沒有 `phone_click` 監聽** | 🔴 斷 |
| Local Pack | 鋮馨 **1 則評論**；「中和 二胎房貸」根本沒有 Local Pack | 🔴 斷 |

**依序做這五件：**

**① 補齊 phone_click 監聽（半天，Code 端可自己做完）**
沒有這個，就算電話真的進來也不知道是哪一頁帶來的，等於整條 SEO 沒有回饋迴圈。
缺的 10 頁（`comm` 指令見第一節）：`banqiao/sanchong/tucheng/yonghe/zhonghe-property-finance`（**五支在地融資諮詢頁，正是要接電話的頁**）、`compare-options`、`glossary`、`article-foreclosure`、`new-taipei-house-tax`、`zhonghe-sale-leaseback`。
做法：抄任一支已有監聽的頁（如 `zhonghe-second-mortgage.html`）的 GA 片段；**改完必須 render 驗**不能只 grep（memory `feedback_audit_cta_needs_render_not_grep`）。
接著在 GA4 把 `phone_click` 標成轉換、並確認 landing page 維度切得出來（memory `feedback_ga4_import_needs_conversion_category`、`project_ga4_daily_telegram`）。

**② 二胎頁正文加一顆電話 CTA（半天，需媽祖）**
本 session 寫的樞紐頁與三支在地頁，**正文 CTA 全是「LINE 線上諮詢」**（因二胎場景禁「免費評估」鉤子，我一律選 LINE）。電話只在 include 注入的區塊。
50+ 自營業者（族群 A）習慣打電話不是加 LINE——CTA 帶應該是「LINE ｜ 撥打 02-2249-0517」兩顆並列。
⚠️ 電話鈕本身沒有第六節合規問題，但**文案要過媽祖**；別寫成「免費估價專線」之類的鉤子。

**③ GMB 評論 1→20（只有 Sir 能做，最短路徑）**
手機搜「中和 二胎房貸」按下去就是撥號，Local Pack 是最直接的電話來源。實查：「新北 房屋二胎」Local Pack 第 1 名只有 **17 則**評論，第 2、3 名 **0 則**照樣上榜。鋮馨目前 **1 則**、上月商家檔案被查看 601 次／互動 204 次。
附帶：GMB 最近一則貼文是 4 個月前（09-08 實查，未重驗）。
⛔ 商家名稱**不可**塞「地區＋品項」關鍵字（Local Pack 6 家有 5 家這樣做，違反 Google 政策）；⛔ 類別維持「不動產管理服務」勿改金融類（memory `reference_business_hours_gmb_vs_constitution`）。

**④ 量三支新頁的真實表現，再決定要不要繼續擴（等 2–4 週）**
本 session 上線新店、三重、新莊三支。**先看數據再擴頁**——memory `project_local_page_series_rules` 有 2026-07-23 實測：在地頁 10 支近 28 天合計僅 71 曝光、0 點擊，老闆 07-24 拍板「繼續擴，但 KPI 是地緣佐證不是流量」。
現在 Sir 要的是電話，KPI 換了，**這條舊拍板要重新確認**：如果三支新頁 4 週後仍 0 點擊 0 電話，該把力氣移到 GMB 與站外，而不是再產第 23、24 支。
重驗：`~/cx468-ga4-daily/gsc.py`（service account，未過期）＋ GA4 的 `phone_click` 依 landing page 切。

**⑤ 台北市 12 區在地頁（目前不建議做）**
台北市 12 區 0 支在地頁看起來是最大缺口，但我方**在台北市沒有實體據點**，doorway 風險比新北高，且 GMB 服務區域對不上。**建議等 ④ 的數字出來再議。**

**接手前必讀的禁忌（沿用，未變）：**
- ⛔ **當舖鉤子詞一個都不能抄**：免留車／免聯徵／免保人／審核寬鬆／過件率／當日撥款／最低利率 1% 起／銀行不借沒關係——14 類全中憲法第六節。我方替代鉤子是「被拒絕過還有路」。
- ⛔ 二胎主商品場景禁「免費評估／免費諮詢」（memory `feedback_compliance_no_free_eval_second_mortgage`）。
- ⚠️ 在地頁一律走反 doorway 八條定例（memory `project_local_page_series_rules`）。**媽祖 09-09 追加：第 23 支起，防詐段的「查商工登記／審核前先收費是警訊／打 165」共用脊椎改成一句話＋內鏈 `article-second-mortgage-scam.html`，不再逐篇改寫**；三支頁的防詐段原本互相 92% 相似，是 doorway 指紋。
- ⚠️ 引用 `lvr-data/` 前先比對同夾 last-commit（memory `feedback_stale_data_file_in_fresh_pipeline`）：**`雙北全區排名_近180天.csv` 停更在 2026-05-29**，當期正本是 `排名_w180.json`（09-02）。我用錯過一次，整頁主論述反轉、被媽祖退件。
- ⚠️ 內容產出派 DeerFlow **必須拆小段**＋給停止條件＋明設 `recursion_limit`，否則 `GraphRecursionError` 繞 100 步零產出、exit code 仍是 0。

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
8. 🔴 **GMB 評論衝量＝第一順位第③項**（只有 Sir 能做，09-08 實查、09-09 未重驗）：鋮馨 **1 則評論**，「新北 房屋二胎」Local Pack 第 1 名只有 17 則、第 2/3 名 0 則照樣上榜——**從 1 衝到 20 就有機會進地圖包，而地圖包是手機直接按撥號的入口**。上月商家檔案被查看 601 次、互動 204 次；GMB 最近一則貼文已是 4 個月前。
9. 🆕 **`cx468-crawl` 是否降頻**：一天跑 12 次，超過 Sir 定的「重複檢查一天不超過三次」，但它不打 Anthropic 不花 API 錢。降頻代價是新聞最晚 8 小時才被抓到。**Sir 未裁，未動**。

10. 🆕 **配圖要不要換真人照片**（09-09）：三重用 `img/gen-sanchong.jpg`、新莊用 `img/gen-city-newtaipei.jpg`，都是 AI 生成圖，新莊那張還是泛新北市景不是新莊。媽祖提醒：板橋篇當年就是這個問題被換掉、待裁至今（memory `project_photo_library`：老闆偏好真人照片）。**不擋上線，等 Sir 裁。**
11. 🆕 **`Organization` schema 的「20 年」主詞是公司**（09-09 媽祖兩度點名）：head JSON-LD 寫「鋮馨租賃有限公司提供…20 年以上經驗」，但公司 114/9 設立未滿一年，主詞只能是團隊（memory `feedback_company_age_vs_team_experience`）。**全站 81 頁共用同一字串**，單頁改只會造成不一致。媽祖給的句子：`鋮馨租賃有限公司提供不動產售後回租、貸款整合、民間轉銀行專業諮詢與媒合服務。團隊具 20 年以上不動產租賃與融資媒合經驗，整合 39 家以上合作銀行。`（順手補回「39」前漏掉的半形空格）。⚠️ 工作區有一支 untracked `scripts/fix_20year_subject.py`，**不是本 session 產物、動它之前先確認來源**。
12. 🆕 **「成數最高 9 成」沒說明是一、二胎合計**（09-09 媽祖提）：全站 9 處同型措辭，示意例算式用的是合併成數，讀者可能誤讀成二胎單獨可貸 9 成。要改就全站同步改。**未動。**

## 五、本 session（2026-09-08 19:00 → 09-09 03:0x）做了什麼

起點是交接信第三節第一順位「SEO 地區×品項矩陣」，Sir 令「開始改動 全部流程開始做」，收尾時 Sir 定調 **「SEO 要有電話來的客戶」**（已寫進第三節）。

### 5-1 二胎商業意圖內鏈收斂（`8af471e`，已上線）
- `compare-options.html` 決策卡「了解二胎」由文章頁改指樞紐頁；5 頁補樞紐頁連結，錨文各異避免過度優化；資訊型錨文（「二胎房貸是什麼」）保留給 `article-second-mortgage.html`。
- ⚠️ **這筆是被平行 session 順手 push 上線的**（我沒 push，第三次 fetch 才發現它已在 origin/main）——共用工作目錄裡「commit 了但未授權部署」不成立，memory `feedback_parallel_session_moves_head_mid_diagnosis` 已追加此型。
- 後續平行 session 又推了 `eb25e79` 做錨文強弱優化（方向一致，未衝突）。

### 5-2 樞紐頁加重（`e022fb6`，已上線）
`second-mortgage.html` **2,380 → 5,234 中文字、FAQ 6 → 10 題**（對照組華德當舖樞紐頁 7,559 字／FAQ 8 題）。新增六段：額度算式＋示意試算／三管道比較表（含月息年化換算）／申辦五步／文件清單／被婉拒五原因與替代路徑／費用四項與查證。
媽祖 PASS with edits，五處必改全套：「保證核貸」否定句改寫、SLB 帶過句調序、年息 3%→3.4% 對齊本頁區間、示意試算加註假設數字、「一至三週」因事實表無來源改成無數字版。
重驗：`curl -s https://cx468.com.tw/second-mortgage.html | grep -c '<details'` → 10

### 5-3 在地頁 +3 支（`c742d42` ＋ 平行 session 的 `1d4586b`，已上線）
| 頁 | 線上字數 | 軸線（刻意各不同構） |
|---|---|---|
| `xindian-second-mortgage.html` | 4,830 | 區內五生活圈實價落差（安坑 35 萬 → 大坪林 71 萬） |
| `sanchong-second-mortgage.html` | 4,731 | 單價與總價是兩件事（蘆洲當教學例） |
| `xinzhuang-second-mortgage.html` | 5,182 | 使用分區這道分水嶺＋上下新莊兩市場 |

在地頁總數 **19 → 22 支**。三支各 FAQ 8 題、schema 與可見 DOM 逐字全等、具名地標 16–35 個、`ci_check` 0 問題。

### 5-4 媽祖三輪把關擋下的兩類錯（**這節是本 session 最有價值的部分**）
**A. 資料源過期，害整頁主論述反轉。** 我用 `lvr-data/雙北全區排名_近180天.csv` 寫三重＋新莊，媽祖查出它 **last-commit 停在 2026-05-29**，同夾其他 7 支都是 09-02。當期數字下「三重單價高過板橋」是**錯的**（56.3 < 60.0），屋齡論據也消失。兩頁全部改讀 `排名_w180.json` 重寫。→ memory `feedback_stale_data_file_in_fresh_pipeline`
**B. 兩個會害屋主得到相反結論的事實錯誤（新莊頁）。** 原稿教屋主「看土地謄本的使用分區欄」——**都市土地那一欄本來就空白**，照做會誤判「我不是工業宅」；且分區證明是**區公所**核發不是地政事務所。依媽祖逐字稿全部改正，並移除維基來源與工業宅的捷運站指名（對丹鳳／迴龍住戶財產的負面評價）。
**C. doorway 指紋。** 三支頁防詐段互相 92%、FAQ 一題 97% 相似——只換地名。換角度重寫後降至 44–61%；利率句依定例第 6 條保留逐字統一，題目與首句各自在地化。

### 5-5 順手發現、已寫 memory
- `feedback_stale_data_file_in_fresh_pipeline`（新）：資料夾自動更新 ≠ 每個檔都新，引用前比對同夾 last-commit。
- `feedback_parallel_session_moves_head_mid_diagnosis`（追加）：平行 session 的 push 會把你還沒要上線的本地 commit 一起帶走。
- `project_local_page_series_rules`（更新）：定例第 6 條的利率舊值 3%–8% 已全站絕跡，改記 3.4%–10%，勿反向照舊值改頁。

### 5-6 本 session 的兩個 harness 事故
- **Fable 額度滿（429）**：三個查證 agent 第一輪全掛、零產出。依憲法第九節改 `model: opus` 重跑成功。
- **`update_schema_datemod.py` 會順手改到無關檔**：每跑一次就把 `mortgage-calculator.html`／`affordability-calculator.html`／`second-mortgage-calculator.html` 的 `dateModified` 一起改；本 session 三度 `git checkout` 還原，未夾帶進 commit。**下次跑完記得 `git status` 看一眼。**
