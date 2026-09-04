# 交接信｜cx468-web（官網 repo）＋ CX468 雲端維運

> 現況快照，不是 changelog。歷史在 `git log`。
> 最後重寫：2026-09-04 深夜（Better 對拷專案第一頁上線）
> 本次重寫原因：一、三、五節整節重寫；二、四節為 8/29 版保留、**本次未重驗**，接手前先查證。

## 一、當前狀態快照（2026-09-04 22:49 實測）

| 項目 | 值 | 重驗指令 |
|---|---|---|
| cx468-web HEAD | `7403ce9`，與 origin/main 一致、已部署 | `cd ~/cx468-web && git status -sb && git log --oneline -3` |
| 工作區 | 乾淨。既有未追蹤 `scripts/archive/goal-scores.jsonl`、`scripts/fix_20year_subject.py`（**勿 add**，非本 session 產物） | 同上 |
| 售後回租頁（Better 版型原型） | 線上 200、含 `data-theme="light"`、h1＝1 | `curl -s https://cx468.com.tw/sale-leaseback.html \| grep -c 'data-theme="light"'` → 1 |
| nav.js 淺色主題 | 線上 15 處 `cx-light` | `curl -s https://cx468.com.tw/nav.js \| grep -c cx-light` → 15 |
| 首頁 | 200，深色 nav 未受影響（真瀏覽器實開驗過） | `curl -s -o /dev/null -w '%{http_code}' https://cx468.com.tw/` |
| 全站配色 | 149 檔已海軍藍 #1B2F4A＋金 #C8945A（commit b45c85b、3688f39），紅 #C61B1C 0 檔 | `grep -l C61B1C *.html \| wc -l` → 0 |
| launchd | `fanjiuzhang-watch`／`healthcheck`／`indicators-local`／`adsreport` 四支 exit 0；**`leadspoll` 不在清單，原因本次未查** | `launchctl list \| grep cx468` |
| SEO/AEO/GEO 分數、FAQ 同源 | **本次未重跑**（改版頁 FAQ 同源用 evaluate 驗過相等） | `python3 scripts/audit_seo.py`、`python3 scripts/audit_faq_samesource.py` |

⚠️ **三個路徑陷阱**：
1. 網站程式碼在 `~/cx468-web/`，**不在 iCloud 專案夾**；iCloud `ＡＩ鋮馨/AI鋮馨官網/` 只是草稿鏡像（index／intake／sale-leaseback 有副本）。
2. `行銷產出/`、`知識庫/`、`制度/` 在 **iCloud 專案夾**，在 repo 裡 `ls` 會空手而回。
3. LINE bot 查驗一律用 `~/cx468-linebot`，iCloud 專案夾內那份是凍結殭屍複本。

🚨 部署前照舊：`python3 scripts/update_schema_datemod.py` 同步 dateModified（本次 sale-leaseback sitemap lastmod 已是 09-04，未另跑）。

## 二、可複用資產／程序（8/29 版保留＋9/4 新增）

### 🆕 Better 對拷專案的入口（9/4 建立）

- **拆解報告**：iCloud `行銷產出/策略簡報/2026-09-04-better.com官網拆解.md`（365 行：§3 逐頁 section 表、§5 色碼/字級/按鈕/卡片/間距實測、§6 技術棧、§8 不能照抄的 11 條）。143 張截圖在 `行銷產出/視覺風格/better.com-2026-09-04/`（`17-mortgage-*.png`＝內頁模板對標）。
- **內頁模板正本**＝`sale-leaseback.html`（已上線）。全站套用時照它的 `<style>` 與 section 順序：hero 左文右圖 → 深藍帶 → 流程/要點格 → 適合對象 → CTA 帶 → 相關文章 → 案例 → 比較表 → FAQ → LINE → 表單。原型截圖 `行銷產出/視覺風格/better-rebuild-2026-09-04/`。
- **nav.js 淺色主題**：頁面放 `<div id="nav" data-theme="light"></div>` ＋ `<script src="nav.js"></script>`，body `padding-top` 64/58。不帶屬性＝深色（首頁用）。
- 🔴 **`style.css` 雷**：其全域 `nav{height:48px;display:flex}` 會壓壞 nav.js。原型頁直接**不載 style.css**（footer／line-qr／lead-form 自帶 fallback 樣式，實測無破版）。全站套用前要 Sir 拍板：改 style.css 還是逐頁不載。
- **本機目檢**：`cd ~/cx468-web && python3 -m http.server 8765`，Playwright venv 在 session scratchpad（會消失），重建：`python3 -m venv ~/pw && ~/pw/bin/pip install playwright && ~/pw/bin/playwright install chromium`。截圖前 `addInitScript` 設 `localStorage cx_antifraud_v1` 關反詐 modal。
- Token 對照（Better → 鋮馨）：頁底 #F7F5F0、卡片白、次底 #F2EFE8、深帶 #1B2F4A、主 CTA #2F5B8F（hover #26497A）、header CTA 金 #C8945A、眉標 #9A6D3A、文字 #1B2F4A／#5A6878、邊線 #E2DED4、淡藍帶 #EEF2F7；全頁 Noto Sans TC；CTA 64px 圓角 8px；卡片 8px＋shadow-md；section 64/80/96。

### 🆕 本機預覽與真回覆測試（8/29 建立）

```bash
# 靜態站
cd ~/cx468-web && python3 -m http.server 8931
# chat API（沒開的話小鋮只會回「連線暫時不穩」）
cd ~/cx468-linebot && ANTHROPIC_API_KEY="$(cat ~/.cx468/anthropic.key)" PORT=5001 .venv/bin/python app.py
```
chat-widget 只在 `localhost`／`127.0.0.1` 打 :5001，其餘打 Render 正式站。
`/chat` 收 `{"messages":[{"role":"user","content":"…"}]}`，**不是** `{"message":"…"}`（送錯回 400）。

### 🆕 headless 目檢管線（8/29 建立，比 playwright MCP 可靠）

playwright MCP 會被別的 session 佔住（`Browser is already in use`）。改用 CDP：

```bash
CH="$HOME/Library/Caches/ms-playwright/chromium-1234/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
"$CH" --headless=new --disable-gpu --no-sandbox --remote-debugging-port=9333 \
      --user-data-dir=/tmp/cdpX --window-size=1440,900 about:blank &
```
Node v26 內建 WebSocket，直接寫 CDP client。三個雷（memory `feedback_cdp_screenshot_traps`）：
- `Emulation.setDeviceMetricsOverride` ＋ `Page.captureScreenshot` 會**永久 hang**。要換視窗尺寸就重啟 chrome 帶 `--window-size`。
- 用 `/json/new` 開分頁後截圖可能拍到**別的 active 分頁**。附著到啟動時那個分頁、反覆 `Page.navigate` 才穩。
- 反詐 modal 會擋住目檢：先 `localStorage.setItem('cx_antifraud_v1', String(Date.now()))` 再 reload。

### 🧩 ai-bar.html（8/29 新元件）

服務頁 AI 詢問列。掛法：頁面 hero 內插一行
```html
<div data-include="ai-bar" data-ai-q="問題一？|問題二？|問題三？"></div>
```
- chips 文字＝問題前 14 字；點擊送全文給小鋮，開全屏對話（`window.cxAskFull`）。
- 顏色與對齊**自動讀該頁 h1**，深底淺底都不用改 CSS。
- 🔴 `include.js` 會在 script 執行後移除容器 div，所以元件內是用 `document.querySelector('[data-include="ai-bar"]')` 取 `data-ai-q`，**不能用 `currentScript.closest()`**（會靜默退回預設題）。

### 🔑 Meta 權杖（永不過期）

| 檔案（chmod 600、不進 git） | 用途 |
|---|---|
| `~/.cx468/fb_system_user.token` | 系統用戶・建廣告／改預算／換素材／開關／讀 insights |
| `~/.cx468/fb_page_system.token` | 粉專・建即時表單／抓名單 |

```bash
T=$(cat ~/.cx468/fb_system_user.token)
curl -sG "https://graph.facebook.com/v21.0/act_1693554028195795/insights" \
  --data-urlencode "access_token=$T" --data-urlencode "level=campaign" \
  --data-urlencode "fields=campaign_name,spend,impressions,inline_link_clicks,ctr,frequency" \
  --data-urlencode "date_preset=today"
```

### Google Ads 查法（無 API 金鑰，用指令碼）

後台 → 工具 → 大量操作 → 指令碼。兩支已建好：`CX468-設定稽核`、`CX468-地區解碼`（原始碼在 `行銷產出/Google廣告/`）。
🔴 地區 ID：**新北市 `1012825`、臺北市 `9040379`**，皆 City 層級。出現 `2158` 或 Country ＝鎖到全國要改。
**後台「查看頁」會假顯示，判準一律以指令碼／API 輸出為準。**

### GA4

`~/cx468-ga4-daily/cx468-ga4-945f85bddfbd.json`，資源 ID `535643191`。
**判讀付費流量的必要對照**：`inherit-era-img3` 兩週買 1,279 個工作階段、平均參與 **1.0 秒**、跳出 92.3%，Meta 後台 CTR 6.85%／CPC 0.93 很漂亮實際是誤觸。對照組：Google 搜尋 13.1 秒、自然搜尋 30.4 秒。

### 📞 回電 SOP

`行銷產出/LINE/2026-08-14-以房養老來電三句話SOP-FINAL.md` v2，媽祖已核。
四道閘門：①第一句身分切割 ②「我幫你問問看銀行」列禁語第一條 ③轉場售後回租需四條件全中 ④**弱勢否決凌駕四條件**。

### 期限型任務登記表

`~/.cx468/pending_reviews.json` → 三日健檢檢查4 自動倒數，逾期推 Telegram。
**凡是有硬截止、又沒有其他系統在盯的任務，一律登記進去。** 新增改 JSON 即可，不必動程式碼。

## 三、未竟任務

### 🔴 第一順位：Better 版型套到其餘服務頁（Sir 定調「規格一模一樣、內容換鋮馨」）

先向 Sir 要三條拍板（9/4 已提、尚未回）：①眉標用「房屋售後回租」型還是原「不動產售後回租 · Sale-Leaseback」型 ②`style.css` 改全域 nav 規則還是逐頁不載 ③深藍底上的 CTA 用金色可否。
拍板後下一批：`debt-consolidation.html`／`private-to-bank.html`／`corporate-checkup.html`（各 449／589／353 行），每頁規則同原型：**文字一字不改、只換版型**、FAQ schema 與可見文字同源、h1＝1、console 0 error、手機 scrollWidth 390、禁語掃 0 新增；二胎相關頁記得「免費評估」禁令（memory `feedback_compliance_no_free_eval_second_mortgage`）。派工模板：本 session 給建造者的 prompt 要點都在第二節「Better 對拷專案的入口」。部署仍須 Sir 說「部署」，一律指名檔案。

### 🟡 同專案的後續

1. nav.js MENU 原稿 24 個目標頁（compare／prepare／concept-*／investors 等）尚未建（memory `project_homepage_green_rebuild`）；建好才加回 MENU。
2. 141 頁仍用 `data-include="nav"`（舊 nav.html）。全站換 nav.js 是套版型的一部分，不要單獨先換。
3. 首頁形式：Better 首頁是單屏 AI 框；我方首頁已縮到只剩快速答案框（commit ea9fbaa 移除 FAQ/名詞/工具段與 FAQPage schema）。SEO/GEO 是最大目標（memory `feedback_seo_aeo_top_priority`），首頁可索引內容減少的影響下次精進會議要看數據。
4. 不放假客戶評價（Better 每頁有五星語錄，我方無可查證來源）。

### ⚠️ 以下為 8/29 版留下、本次未重驗

- nav「免費評估」按鈕在二胎頁的合規缺口（8/29 已報 Sir、未指示）。
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

## 五、本 session（9/4 晚）做了什麼

Sir 指令：「官網要改成 better.com 這樣，先把它每一步點過、測過、記錄下來」→「做下一步」→「部署」→「交接」。

| 事項 | 證據 |
|---|---|
| better.com 全站拆解（24 頁桌機＋手機截圖、5 下拉、漏斗走到第 4 步停在地址個資、3 計算器改值、getComputedStyle 實量、curl robots/sitemap） | 報告 365 行＋143 張截圖（路徑見第二節）；playwright MCP 全程被佔，改本機 Playwright |
| 售後回租頁重排成 Better /mortgage 版型＋nav.js 加 light 主題 | commit `7403ce9`（+446/−460）；文字守恆：新版多出的只有「相關文章」「房屋售後回租」眉標與 nav 選單字 |
| 驗收 | console 0 error；h1＝1；6 段 JSON-LD parse OK；FAQ 同源相等；手機 scrollWidth 390；金管會 8 禁語 0；SLB 借貸語彙 0 新增 |
| 部署 | fetch+rebase+push，`git ls-remote`＝本機；線上 60 秒後生效，真瀏覽器 nav 底色 rgb(255,255,255) |
| 手機修 | 浮動小鋮鈕蓋住 ai-bar 送出鈕 → 本頁 CSS `padding-right:70px`＋grid `minmax(0,1fr)` |

**Sir 未回的三條拍板**見第三節第一順位。**本 session 落地的 memory**：`project_homepage_green_rebuild` 追加兩段（報告位置、原型狀態與 style.css 雷）。

