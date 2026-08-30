# 交接信｜cx468-web（官網 repo）＋ CX468 雲端維運

> 現況快照，不是 changelog。歷史在 `git log`。
> 最後重寫：2026-08-29（全站改 AI 時代定位）
> 本次重寫原因：**品牌定位轉向**——Sir 8/29 拍板「繼承時代結束，全站改成 AI 時代」，第一、五節整節重寫。
> ⚠️ 第三、四節多數項目是 **8/14 版留下、本次未重驗**，逐項已標註；接手前先自行查證狀態再行動。

## 一、當前狀態快照

| 項目 | 值 | 重驗指令 |
|---|---|---|
| cx468-web HEAD | `3e60f28`，**ahead 1（未 push，等 Sir 授權部署）** | `cd ~/cx468-web && git status -sb` |
| 工作區 | 乾淨。既有未追蹤 `scripts/archive/goal-scores.jsonl`、`scripts/fix_20year_subject.py`（**勿 add**，非本次產物） | 同上 |
| 線上站點 | 200，**尚未含本次改動** | `curl -s https://cx468.com.tw/ \| grep -c "先問小鋮 AI"` → 現為 0；push 後應為 1 |
| SEO/AEO/GEO | 124 頁。index/services 16/17（唯一失分 `fresh30`），其餘 5 個服務頁 17/17 | `python3 scripts/audit_seo.py` |
| FAQ 同源 | 122 頁、漂移 0 | `python3 scripts/audit_faq_samesource.py` |
| 排程 | `healthcheck`／`indicators-local`／`leadspoll`／`adsreport`／`fanjiuzhang-watch` 五支 launchd 全載入 exit 0 | `launchctl list \| grep cx468` |
| cx468-ga4-daily | `b3902b1`，**ahead 3（別的 session 留的，本次未處理）** | `cd ~/cx468-ga4-daily && git status -sb` |
| cx468-linebot | `c750fd2`，與遠端一致 | `cd ~/cx468-linebot && git status -sb` |

### 🚨 部署前必做

```bash
cd ~/cx468-web && python3 scripts/update_schema_datemod.py
```
`fresh30` 失分＝index/services 的 `dateModified` 落後 git 8–16 天。不同步就上線＝新內容配舊 schema，會擋住重爬（memory `feedback_sitemap_lastmod_gates_indexing`）。

⚠️ **三個路徑陷阱**：
1. 網站程式碼在 `~/cx468-web/`，**不在 iCloud 專案夾**。
2. `行銷產出/`、`知識庫/`、`制度/` 在 **iCloud 專案夾**，在 repo 裡 `ls` 會空手而回。
3. LINE bot 查驗一律用 `~/cx468-linebot`，iCloud 專案夾內那份是凍結殭屍複本。

## 二、可複用資產／程序

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

### 🔴 第一順位：本次改動等部署（唯一本次產生、狀態已實證）

`3e60f28` ahead 1。Sir 尚未說「部署」。要上線時：

```bash
cd ~/cx468-web
python3 scripts/update_schema_datemod.py     # 先同步 dateModified
git fetch && git rebase origin/main
git add <指名檔案>                            # 禁 git add -A
git push
curl -s https://cx468.com.tw/ | grep -c "先問小鋮 AI"   # 應為 1
```
上線後給 Sir URL 清單送 GSC：首頁＋7 個服務頁（services / second-mortgage / sale-leaseback / debt-consolidation / private-to-bank / corporate-checkup / property-management）。

### 🟡 定位轉向的後續（本次未做，Sir 未指示）

1. **nav 的「免費評估」按鈕**：全站共用 nav，二胎頁會繼承。Sir 2026-07 定過二胎主商品場景禁「免費評估」招攬鉤子（memory `feedback_compliance_no_free_eval_second_mortgage`）。既有缺口，已向 Sir 報告、等指示。
2. **lp-\* 與地區變體頁**（`lp-private-to-bank` / `xinbei-*` / `zhonghe-*` / `banqiao-*` 等約 10 頁）本次未加 AI 詢問列。要鋪的話照第二節 ai-bar 掛法，一頁一行。
3. **繼承那 8 頁一行未動**（Sir 拍板保留帶曝光）。若日後要調，先查 canonical 收斂狀態（memory `project_canonical_consolidation`）。
4. **AI 模式預設值**：目前預設「完整版」，AI 模式只記本次瀏覽（sessionStorage）。要改成預設 AI 模式，改 index.html 那行 `sessionStorage.getItem('cxHomeMode') === 'ai'` 即可——但會讓自然搜尋到站的訪客被覆蓋層擋住。

### ⚠️ 以下為 8/14 版留下、**本次未重驗**，接手前先查證

- 三支廣告首週判讀（原訂 8/15）、新聞焦點卡硬截止（原訂 8/21）、回電 SOP 實錄複核（原訂 8/28）——**三個日期都已過**，狀態不明，先查 `~/.cx468/pending_reviews.json` 與健檢報告再決定。
- 企業貸款補助專案（CX-FUNDING）三處資料不一致＋三個阻塞數字。
- Anthropic auto-reload、Postgres `cx468-fb-news-db` 每月 US$21.02、設計系統收斂（舊綠 `#16A34A` 殘留 7 頁、`#0071e3` 藍 58 檔）。
- ⚠️ Threads token 8/14 時剩 55 天（約 2026-10-08 到期），換發後更新 `~/.cx468/threads_token_issued`。

### 日常常態

- 每天 12:00 精進會議（**session 級排程，每個 session 要用 CronCreate 重設**）
- 三日健檢 `com.cx468.healthcheck`（檢查4 五項）
- 名單輪詢 `com.cx468.leadspoll` 每 15 分鐘｜本機指標 5/25 號 10:30｜曝光巡檢 08:12｜Threads 12:30
- ⚠️ 換新聞卡前先跑 `git log --oneline -5 -- radar-index.html` 算實際服役天數；硬截止日是**到期日不是動手日**（memory `feedback_check_content_age_before_rotating`）。改卡片註解格式會弄壞 `~/cx468-ga4-daily/health_check.py` 的 regex（memory `feedback_cross_repo_string_coupling`）。

## 四、等使用者的事項

> 1–6 為 8/14 版留下、本次未重驗。

1. 🔴 **GMB 影片驗證**——GEO 站外總開關。站外簡介工作 7/23 已完成 90%（四平台結案，別再誤判「未動」）；剩服務區域／次要電話／「更多」屬性等驗證通過。帶法：`行銷產出/技術記錄/2026-08-14-GMB驗證解鎖checklist.md`
2. **企業貸款專案三處資料不一致**＋三個阻塞數字（資本額／勞保投保名冊／營業項目代碼）
3. **Meta `spend_cap`**——8/14 估約 8/22 撞頂，**日期已過，務必先查現值**
4. **Anthropic auto-reload**：console.anthropic.com → Billing，建議「低於 $5 自動補到 $50」
5. **名單回電**——SOP 已備妥，回電前務必先讀；名單**禁止回灌 Meta 做自訂受眾／類似受眾**
6. **合一地政士事務所洽談**——只有老闆本人能談（面談包已過媽祖，四條紅線見 memory `project_land_agent_channel_heyi`）
7. 🆕 **本次改動的部署授權**——Sir 說「部署」才 push（見第三節第一順位）

## 五、本 session（8/29）做了什麼

Sir 拍板：**繼承時代結束，全站改成 AI 時代定位**。對標 better.com 的 Betsy AI 首頁。

| 事項 | 證據 |
|---|---|
| better.com 實抓分析（SPA，WebFetch 只拿得到 nav，要 headless render） | 整頁只剩 nav／AI 對話 hero／免責 footer；傳統首頁收進 Classic Mode |
| 首頁定位轉向：eyebrow／h1／副標／CTA 移除繼承語 | h1 改「房子的問題，先問小鋮 AI」；順修「深耕二十年」主詞為團隊 |
| AI 模式全屏入口（覆蓋層，DOM 不動） | 首訪 overlay `on=false` 實測；SEO 稽核 16/17 不變、字數 3,798、h2 12、內鏈 21 全不動 |
| chat-widget 新增 `window.cxAskFull()` | 全屏對話＋遮罩，關閉自動復原，內頁 widget 未受影響 |
| ai-bar.html 掛進 7 個服務頁 | 7 頁 chips 逐頁正確、無 JS 錯、點 chip 進全屏對話真回覆 |
| 修 sale-leaseback h1 被 nav 蓋住 | 桌機＋手機兩組 CSS；修後 7 頁桌機／手機皆 0 頁被蓋 |
| 合規掃描 | 我的改動 0 命中；SLB chips 無 借/貸/押/還款/利息/贖回 |

**Sir 的定位判斷**（寫下來免得下個 session 重問）：繼承內容頁保留帶曝光，定位層改 AI；服務頁鋪 AI 入口，文章頁不鋪。

**本 session 落地的 memory**：`feedback_shared_component_into_existing_hero`、`feedback_cdp_screenshot_traps`（皆新）
