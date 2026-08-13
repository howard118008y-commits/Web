# 交接信｜cx468-web（官網 repo）＋ CX468 雲端維運

> 現況快照，不是 changelog。歷史在 `git log`。
> 最後重寫：2026-08-14（付費獲客三線齊發＋Meta 永久權杖打通 session 收尾）
> 本次重寫原因：8/12 版的重心是「上游內容轉向」，內容線已落地；本 session 重心移到**付費獲客與工具權限**——Meta 名單型廣告上線、Google 搜尋廣告上線、Meta 系統用戶永久權杖打通、名單自動推播接好。舊版「未竟五項」有三項完成、兩項降級。舊段落已刪除重寫，未堆疊。

## 一、當前狀態快照

| 項目 | 值 | 重驗指令 |
|---|---|---|
| cx468-web HEAD | `09b4966`（本 session 四顆：`8c6fa0d` 稅務權威文、`2b7a6ae` 廣告 LP、`4ce0f78` 座標校正 75 頁、`b4362e8` 新聞卡＋更新頻率、`09b4966` 隱私權政策） | `cd ~/cx468-web && git log --oneline -6` |
| 本地 vs 遠端 | 一致 | `git status -sb`；`git ls-remote origin main` |
| 工作區 | 乾淨。既有未追蹤 `scripts/archive/goal-scores.jsonl`（非本 session 產生，**勿 add**） | `git status -sb` |
| 新頁線上 | 全 200 | `for U in article-estate-tax-transfer-certificate lp-reverse-mortgage-declined privacy-policy radar-index; do curl -s -o /dev/null -w "$U %{http_code}\n" https://cx468.com.tw/$U.html; done` |
| FAQ 同源 | 121 頁、漂移 0 | `python3 scripts/audit_faq_samesource.py` |
| SEO/AEO/GEO | 123 頁，缺口僅 privacy／terms（AEO 豁免） | `python3 scripts/audit_seo.py` |
| **Meta 廣告** | **兩支 ACTIVE**：`rm-declined-leads-202608`（名單型 200/日）、`rm-declined-lp`（流量 100/日）。`inherit-era-img3` 已 PAUSED | 見第二節「Meta 查法」 |
| **Google 廣告** | `rm-declined-search-202608` ACTIVE、200/日、最大化點擊 | 見第二節「Google 查法」 |
| 名單輪詢 | launchd `com.cx468.leadspoll` 每 15 分鐘 | `launchctl list \| grep cx468`；`tail -3 ~/.cx468/leads/poller.log` |
| 三日健檢 | 已加「檢查4 週期任務時效」（commit `b6176f7`，本機未 push） | `cd ~/cx468-ga4-daily && ./venv/bin/python -c "import health_check as h;[print(l) for l in h.check4_stale()]"` |

⚠️ **工作目錄在 `~/cx468-web/`，不在 iCloud 專案夾**（memory: `feedback_icloud_conflict_copies`）。

## 二、可複用資產／程序

### 🔑 Meta 權杖（本 session 最大解鎖，永不過期）

| 檔案（皆 chmod 600、不進 git） | 用途 |
|---|---|
| `~/.cx468/fb_system_user.token` | 系統用戶・建廣告／改預算／換素材／開關活動 |
| `~/.cx468/fb_page_system.token` | 粉專・建即時表單／抓名單 |
| `~/.cx468/fb_ads_management_long.token` | 舊的長效 user token（備援，會過期） |

**打通過程的坑（別再走一次）**：粉專掛在 BM「程子顥」（`business_id=823252302396450`）、廣告帳戶原屬「程式設計｜ai 數位轉型實驗室」BM。個人授權的 `me/accounts` **永遠看不到 BM 資產**，Graph API Explorer 的粉專清單也不會出現。正解是 BM → 系統用戶 `CX468FB-Post-System` → 指派粉專＋廣告帳戶資產（廣告帳戶要先跨 BM「要求存取」再核准）。權限改完 Meta 端**要幾分鐘傳播**，立刻測會誤判成沒權限。

### Meta 查法
```bash
T=$(cat ~/.cx468/fb_system_user.token)
curl -sG "https://graph.facebook.com/v21.0/act_1693554028195795/insights" \
  --data-urlencode "access_token=$T" --data-urlencode "level=campaign" \
  --data-urlencode "fields=campaign_name,spend,impressions,inline_link_clicks,cpm" \
  --data-urlencode "date_preset=today"
```
- 建活動必填：`is_adset_budget_sharing_enabled`、`regional_regulated_categories=["TAIWAN_UNIVERSAL"]`、`regional_regulation_identities`（beneficiary/payer 皆 `2154353671792733`）
- 名單型廣告額外要求：粉專先接受《名單型廣告服務條款》、creative 的 `link` **必須是外部網址**（填粉專網址會被擋）
- creative 一律 `degrees_of_freedom_spec` 全 OPT_OUT，否則 Meta AI 會改寫媽祖核過的字

### Google Ads 查法（無 API 金鑰，用指令碼）
後台 → 工具 → 大量操作 → 指令碼 → `CX468-設定稽核`（腳本原始碼：`行銷產出/Google廣告/audit_campaign.gs`）。
**為什麼要它**：Google 建立精靈的「查看頁」會**假顯示**——實測顯示「地區：所有國家」「AI Max 已開啟」「廣告：無」，但 API 讀出來三項全是對的。**判準一律以指令碼輸出為準**。

### GA4（本來就有，不用另外要金鑰）
service account 在 `~/cx468-ga4-daily/cx468-ga4-945f85bddfbd.json`，資源 ID `535643191`。
```bash
cd ~/cx468-ga4-daily && GOOGLE_SA_FILE=$PWD/cx468-ga4-945f85bddfbd.json ./venv/bin/python -c "..."
```
**本 session 靠它抓到最重要的發現**：`inherit-era-img3` 兩週買進 1,279 個工作階段、**平均參與 1.0 秒**、跳出率 92.3%——Meta 後台看起來 CTR 6.85%／CPC 0.93 很漂亮，實際是誤觸。對照組：Google 搜尋 13.1 秒、自然搜尋 30.4 秒。**判讀付費流量一律並排 GA4 平均參與秒數**（memory: `feedback_cheap_cpc_conversions_are_misclicks`）。

### 名單輪詢（PII，紀律見 memory）
`~/.cx468/leads_poller.py`＋launchd `com.cx468.leadspoll`（900 秒）。去重狀態 `~/.cx468/leads/seen_lead_ids.json`——**刪掉會把舊名單全部重推＝同一位長輩被重複致電**。Telegram 目標已實查為 `private` chat（@hohodl1），非群組。

### 銀行條文存證（付費廣告舉證用）
`知識庫/context/銀行條文存證-以房養老-2026-08-12/`：五家 HTML＋第一銀行全頁截圖（該頁 JS 渲染 curl 抓不到）。
⚠️ **投放期間每 30 天複查一次**；任一行改條件 → 當日更新落地頁與查證日或暫停該組。

### 上線驗證（Pages 佇列會塞車）
```bash
until curl -s https://cx468.com.tw/ | grep -q "關鍵句"; do sleep 10; done
```
本 session 四次部署皆 40–90 秒生效。

## 三、未竟任務

### 🔴 第一順位：三支廣告的首週判讀（8/15–8/17）
三支同題材、不同管道，**這是本 session 最大的實驗**：

| 活動 | 管道 | 日預算 | 目標 |
|---|---|---|---|
| `rm-declined-leads-202608` | Meta 即時表單 | 200 | 收姓名電話 |
| `rm-declined-lp` | Meta 流量 | 100 | 進落地頁 |
| `rm-declined-search-202608` | Google 搜尋 | 200 | 進落地頁 |

**判準表（8/15 依此決定 B–E 變體要不要開）**：
- frequency > 2.0 → 受眾疲乏，開 D（子女視角）
- 連結 CTR < 1% → Hook 不夠力，開 B（同一間房不同答案）
- CTR ≥ 1.5% 且 frequency < 1.5 → 不動，繼續學
- **GA4 平均參與秒數 < 10 秒 → 流量品質差，先修落地頁，別加碼買量**

素材包：`行銷產出/FB廣告圖/2026-08-12-以房養老被拒-廣告文案-FINAL.md`（B–E 四組已過媽祖）。

### 🔴 第二順位：Google 廣告否定關鍵字驗數
老闆已貼 51 個否定字但**未回報存檔結果**。跑一次 `CX468-設定稽核` 指令碼，看最後一行「否定關鍵字數量」是否為 51。0 就是沒存進去——沒有它，「以房養老 利率／試算／代辦」會直接進來燒錢。

### 🟡 第三順位：順風耳〈以房養老來電三句話 SOP〉
媽祖硬要求，**名單已經開始進來了才做等於來不及**。第一句必須身分切割（「我們不是銀行，也不提供以房養老」）。出稿要過媽祖。理由：表單守住了、電話裡一句「我幫你問問看銀行」全破功。

### 🟡 第四順位：地政士上游通路（要老闆本人）
合作對象**蘆洲・合一地政士事務所**。面談包已過媽祖：`行銷產出/策略簡報/2026-08-12-合一地政士事務所面談包-FINAL.md`。
🔴 四條紅線：不給轉介費（§27(5)）、**不由地政士轉發我方連結**（§27(3)(4)，我方 LP 有 CTA 不是零招攬頁）、不在事務所放文宣、不接觸銀行行員。詳見 memory `project_land_agent_channel_heyi`。

### 🟢 可選不急
1. **新聞焦點卡硬截止**：🔴 **2026-08-21** 滿 7 天須換稿、**2026-09-01** 六都公布 8 月數字前絕對換。健檢檢查4 會自動盯並推 Telegram。
2. **GEO 站外 GMB**：座標與 NAP 已對齊（本 session 修好 75 頁差 1.4 公里的錯誤座標＋FB 粉專營業時間／郵遞區號）。剩「補完商家檔案類別、次要電話 0958-139-786、照片、收評論」——要老闆 Google 帳號登入。
3. **Anthropic auto-reload 未開**：老闆按了 X 跳過。健檢檢查4 已加餘額探針，餘額不足會紅字告警。餘額現為 $19.88，月用量約 $7.66。
4. **Postgres `cx468-fb-news-db` 每月 US$21.02**、**手機表格逐字直排**、**設計系統收斂**（舊綠 `#16A34A` 殘留 7 頁、`#0071e3` 藍 58 檔）。
5. **goshoot「Daily site audit」連續失敗**（跨事業線）。

### 日常常態
- 每天 12:00 精進會議（session 級排程，每個 session 要重設）
- 三日健檢 launchd `com.cx468.healthcheck`——**已加檢查4**：新聞卡年齡／Threads token 倒數／queue 存量／Anthropic 餘額探針
- 名單輪詢 launchd `com.cx468.leadspoll` 每 15 分鐘
- 曝光每日巡檢 08:12、Threads 每日 12:30（queue 排到 8/31）
- ⚠️ **Threads token 2026-10 月初到期**，換發後**務必更新 `~/.cx468/threads_token_issued`** 的日期，否則健檢倒數是錯的

## 四、等使用者的事項

1. **Google 廣告否定字確認**（第二順位）——跑稽核腳本看數量
2. **合一地政士事務所洽談**——只有老闆本人能談
3. **Anthropic auto-reload**：console.anthropic.com → Billing → 建議設「低於 $5 自動補到 $50」
4. **GMB 補完＋收評論**——要 Google 帳號登入
5. **名單進來後的回電**：名單推到 Telegram（private chat）。⚠️ 回電前務必先看 SOP（第三順位），且**名單禁止回灌 Meta 做自訂受眾／類似受眾**
6. **FB 粉專城市欄**現為 `Zhonghe District`（比原要求更準，已結案，不需再動）
