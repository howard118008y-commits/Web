# 交接信｜cx468-web（官網 repo）＋ CX468 雲端維運

> 現況快照，不是 changelog。歷史在 `git log`。
> 最後重寫：2026-08-14 08:20（回電 SOP＋Google 設定驗收 session 收尾）
> 本次重寫原因：上一版（同日 07:28）的「未竟五項」裡，**第二順位（Google 否定字）與第三順位（回電 SOP）本 session 已結案**，兩段直接刪除重寫、未堆疊。網站程式碼本 session **零改動**，故第一節網站類數值沿用上一版的實跑結果並附重驗指令。新增一個觀察項：名單型活動開跑後首小時零出量。

## 一、當前狀態快照

| 項目 | 值 | 重驗指令 |
|---|---|---|
| cx468-web HEAD | `b79441e`（本 session 前）→ 本次僅本檔一顆 | `cd ~/cx468-web && git log --oneline -5` |
| 本地 vs 遠端 | 一致 | `git status -sb` |
| 工作區 | 乾淨。既有未追蹤 `scripts/archive/goal-scores.jsonl`（**勿 add**） | `git status -sb` |
| 新頁線上 | 全 200（2026-08-14 08:19 實測） | `for U in lp-reverse-mortgage-declined privacy-policy radar-index article-estate-tax-transfer-certificate; do curl -s -o /dev/null -w "$U %{http_code}\n" https://cx468.com.tw/$U.html; done` |
| FAQ 同源 | 121 頁、漂移 0（08-14 07:2x 實跑，本 session 未動網站碼） | `python3 scripts/audit_faq_samesource.py` |
| SEO/AEO/GEO | 123 頁，缺口僅 privacy／terms（AEO 豁免） | `python3 scripts/audit_seo.py` |
| **Meta 廣告** | 兩支 ACTIVE：`rm-declined-leads-202608`（名單型 200/日）、`rm-declined-lp`（流量 100/日）。`inherit-era-img3` PAUSED | 見第二節「Meta 查法」 |
| **Google 廣告** | `rm-declined-search-202608` ENABLED、200/日、TARGET_SPEND。**七項稽核全綠（08-14 08:08 實跑）** | 見第二節「Google 查法」 |
| 名單輪詢 | launchd `com.cx468.leadspoll` 每 15 分鐘，08:07 心跳正常，**目前 0 筆名單** | `launchctl list \| grep cx468`；`tail -3 ~/.cx468/leads/poller.log` |
| 三日健檢 | `com.cx468.healthcheck` 已載入。`~/cx468-ga4-daily` **ahead 2 未 push**（`b6176f7`、`e550612`） | `cd ~/cx468-ga4-daily && git status -sb` |

⚠️ **工作目錄在 `~/cx468-web/`，不在 iCloud 專案夾**（memory: `feedback_icloud_conflict_copies`）。
⚠️ **`行銷產出/`、`知識庫/`、`制度/` 在 iCloud 專案夾，不在 cx468-web repo 裡**——本 session 踩過一次，在 repo 裡 `ls 行銷產出/` 會找不到。

## 二、可複用資產／程序

### 🔑 Meta 權杖（永不過期，本 session 再次實測可用）

| 檔案（皆 chmod 600、不進 git） | 用途 |
|---|---|
| `~/.cx468/fb_system_user.token` | 系統用戶・建廣告／改預算／換素材／開關活動／讀 insights |
| `~/.cx468/fb_page_system.token` | 粉專・建即時表單／抓名單 |
| `~/.cx468/fb_ads_management_long.token` | 舊長效 user token（備援，會過期） |

**打通過程的坑**：個人授權的 `me/accounts` 永遠看不到 BM 資產。正解＝BM → 系統用戶 `CX468FB-Post-System` → 指派粉專＋廣告帳戶（跨 BM 要先「要求存取」）。權限改完 Meta 端要幾分鐘傳播。

### Meta 查法
```bash
T=$(cat ~/.cx468/fb_system_user.token)
curl -sG "https://graph.facebook.com/v21.0/act_1693554028195795/insights" \
  --data-urlencode "access_token=$T" --data-urlencode "level=campaign" \
  --data-urlencode "fields=campaign_name,spend,impressions,inline_link_clicks,ctr,frequency" \
  --data-urlencode "time_range={'since':'2026-08-15','until':'2026-08-17'}" \
  --data-urlencode "time_increment=1"
```
- **帳戶時區＝Asia/Taipei、幣別 TWD**（本 session 實查，`date_preset` 不會有時差陷阱）
- 預算異常先查改動史，別急著喊超支：`/act_xxx/activities?since=YYYY-MM-DD` 過濾 `update_ad_set_budget`。本 session 就靠這支排除一次假超支（8/13 花 259／預算看起來只有 100，實際是當天預算 300、隔日 04:13 才調成 100）
- 建活動必填：`is_adset_budget_sharing_enabled`、`regional_regulated_categories=["TAIWAN_UNIVERSAL"]`、`regional_regulation_identities`（beneficiary/payer 皆 `2154353671792733`）
- 名單型廣告：粉專先接受《名單型廣告服務條款》、creative 的 `link` 必須是外部網址
- creative 一律 `degrees_of_freedom_spec` 全 OPT_OUT，否則 Meta AI 會改寫媽祖核過的字

### Google Ads 查法（無 API 金鑰，用指令碼）
後台 → 工具 → 大量操作 → 指令碼。**兩支都已建好並實跑過**：

| 指令碼 | 原始碼（iCloud 專案夾） | 用途 |
|---|---|---|
| `CX468-設定稽核` | `行銷產出/Google廣告/audit_campaign.gs` | 七項設定讀 API 真實值 |
| `CX468-地區解碼` | `行銷產出/Google廣告/resolve_geo.gs` | 把 `geoTargetConstants/xxxx` 數字翻成地名 |

**2026-08-14 08:08 實跑結果（全綠）**：狀態 ENABLED／出價 TARGET_SPEND／預算 NT$200／Google 搜尋 true／搜尋夥伴・多媒體・合作夥伴皆 false／廣告 1 支 RSA 審核 APPROVED／關鍵字 10 支／**否定關鍵字 51**（上一版未竟第二順位，本 session 結案）。

🔴 **地區 ID 對照（本 session 實查修正，舊註解是錯的）**：
- **新北市 = `1012825`**、**臺北市 = `9040379`**，兩者皆 City 層級、TW、ENABLED
- 舊版交接信與 `audit_campaign.gs` 註解把兩者標反（誤寫 9040379＝新北），已修正
- 出現 `2158` 或 Target Type = Country ＝ 鎖到台灣全國，預算會被中南部吃掉，要改

**為什麼一定要用指令碼**：Google 建立精靈的「查看頁」會假顯示（memory: `feedback_ad_platform_ui_lies`）。判準一律以指令碼輸出為準。

### GA4（service account，不用另外要金鑰）
`~/cx468-ga4-daily/cx468-ga4-945f85bddfbd.json`，資源 ID `535643191`。
**這是判讀付費流量的必要對照**：`inherit-era-img3` 兩週買進 1,279 個工作階段、平均參與 **1.0 秒**、跳出 92.3%——Meta 後台 CTR 6.85%／CPC 0.93 很漂亮，實際是誤觸。對照組：Google 搜尋 13.1 秒、自然搜尋 30.4 秒（memory: `feedback_cheap_cpc_conversions_are_misclicks`）。

### 📞 回電 SOP（本 session 產出，上一版未竟第三順位，已結案）
`行銷產出/LINE/2026-08-14-以房養老來電三句話SOP-FINAL.md`（iCloud 專案夾）v2、媽祖 2026-08-14 已核。

十節：撥號前 30 秒 → 三句話開場（逐字）→ 依名單狀態三分支 → 六條口語版 → **轉場閘門** → 電話禁語表 → Q&A 八題 → 收尾 → PII 紀律 → 事故回報。

**四道閘門**：① 第一句就身分切割（不是金融機構／不提供以房養老／不代為向銀行接洽）② 「我幫你問問看銀行」列禁語第一條 ③ 轉場售後回租需四條件全中，三要件一口氣講完＋零借貸語彙 ④ **弱勢否決凌駕四條件**。

🔴 **媽祖三行裁示**（下個 session 要盯）：
- 最大殘餘風險＝紙擋不住嘴，只能靠第 10 節事故回報有沒有被執行；**上線兩週內（8/28 前）抽聽或自報三通實錄回媽祖複核**
- 最容易破功的一句＝客戶第二次哀求時的「好啦我幫你問問看」
- 下次複審時機＝落地頁銀行條文改版時，或第一通實際轉場成功的通話紀錄進來時，先到者為準

相關 memory：`feedback_gate_fails_on_urgent_vulnerable`（新）、`feedback_slb_no_lending_vocab`（本 session 補一節）

### 名單輪詢（PII）
`~/.cx468/leads_poller.py`＋launchd `com.cx468.leadspoll`（900 秒）。去重狀態 `~/.cx468/leads/seen_lead_ids.json`——**刪掉會把舊名單全部重推＝同一位長輩被重複致電**。Telegram 目標已實查為 `private` chat（@hohodl1）。

### 銀行條文存證（付費廣告舉證用）
`知識庫/context/銀行條文存證-以房養老-2026-08-12/`：六家 HTML＋第一銀行全頁截圖。
⚠️ **投放期間每 30 天複查（下次 2026-09-11 前）**；任一行改條件 → 當日更新落地頁與查證日或暫停該組。SOP 第 3 節的查證日刻意**不寫死**，順風耳照落地頁當下標示唸。

## 三、未竟任務

### 🔴 第一順位：三支廣告首週判讀（8/15，就是明天）
| 活動 | 管道 | 日預算 | 目標 |
|---|---|---|---|
| `rm-declined-leads-202608` | Meta 即時表單 | 200 | 收姓名電話 |
| `rm-declined-lp` | Meta 流量 | 100 | 進落地頁 |
| `rm-declined-search-202608` | Google 搜尋 | 200 | 進落地頁 |

**判準表**：
- frequency > 2.0 → 受眾疲乏，開 D（子女視角）
- 連結 CTR < 1% → Hook 不夠力，開 B（同一間房不同答案）
- CTR ≥ 1.5% 且 frequency < 1.5 → 不動，繼續學
- **GA4 平均參與秒數 < 10 秒 → 流量品質差，先修落地頁，別加碼買量**

素材包：`行銷產出/FB廣告圖/2026-08-12-以房養老被拒-廣告文案-FINAL.md`（B–E 四組已過媽祖）。

⚠️ **順帶查一件事**：`rm-declined-leads-202608` 於 8/14 07:16 啟動，到 08:20 為止**零曝光零花費**（廣告 effective_status ACTIVE、`ad_review_feedback` 空白，非退件）。名單型活動首日冷啟動屬正常，但**8/15 若仍是零出量就要查**——先看 adset 的 `effective_status` 與受眾規模，別直接歸咎素材。

### 🔴 第二順位：地政士上游通路（要老闆本人）
合作對象**蘆洲・合一地政士事務所**。面談包已過媽祖：`行銷產出/策略簡報/2026-08-12-合一地政士事務所面談包-FINAL.md`。
🔴 四條紅線：不給轉介費（§27(5)）、**不由地政士轉發我方連結**（§27(3)(4)）、不在事務所放文宣、不接觸銀行行員。詳見 memory `project_land_agent_channel_heyi`。
**為什麼升到第二**：名單品質基線顯示真病是「進線太晚（已問過多家）」不是分佈，解方＝時機前移＋地政士上游通路（memory: `project_lead_quality_baseline_and_lateness`）。

### 🟡 第三順位：回電 SOP 實地複核（8/28 前）
SOP 已上架但**還沒有任何一通實際來電驗證過**。媽祖要求上線兩週內抽聽或自報三通實錄。名單一進來就開始算。

### 🟢 可選不急
1. **新聞焦點卡硬截止**：🔴 **2026-08-21** 滿 7 天須換稿、**2026-09-01** 六都公布 8 月數字前絕對換。健檢檢查4 會推 Telegram。
2. **`~/cx468-ga4-daily` ahead 2 未 push**（健檢檢查4 的兩顆 commit）。
3. **GEO 站外 GMB**：座標與 NAP 已對齊。剩「補完商家檔案類別、次要電話 0958-139-786、照片、收評論」——要老闆 Google 帳號登入。
4. **Anthropic auto-reload 未開**（餘額約 $19.88，月用量約 $7.66，健檢有探針）。
5. **Postgres `cx468-fb-news-db` 每月 US$21.02**、**手機表格逐字直排**、**設計系統收斂**（舊綠 `#16A34A` 殘留 7 頁、`#0071e3` 藍 58 檔）。
6. **goshoot「Daily site audit」連續失敗**（跨事業線）。

### 日常常態
- 每天 12:00 精進會議（**session 級排程，每個 session 要用 CronCreate 重設**）
- 三日健檢 launchd `com.cx468.healthcheck`（檢查4：新聞卡年齡／Threads token 倒數／queue 存量／Anthropic 餘額）
- 名單輪詢 launchd `com.cx468.leadspoll` 每 15 分鐘
- 曝光每日巡檢 08:12、Threads 每日 12:30（queue 排到 8/31）
- ⚠️ **Threads token 2026-10 月初到期**，換發後務必更新 `~/.cx468/threads_token_issued`

## 四、等使用者的事項

1. **合一地政士事務所洽談**——只有老闆本人能談（第二順位）
2. **名單進來後的回電**——SOP 已備妥，**回電前務必先讀**；名單**禁止回灌 Meta 做自訂受眾／類似受眾**
3. **通話實錄回報**——8/28 前三通，交媽祖複核
4. **Anthropic auto-reload**：console.anthropic.com → Billing → 建議「低於 $5 自動補到 $50」
5. **GMB 補完＋收評論**——要 Google 帳號登入
6. **是否新開「客服話術」資料夾**：本次 SOP 暫放 `行銷產出/LINE/`（沿用既有話術檔慣例）。新類型開夾須老闆核准。
