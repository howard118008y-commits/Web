# 交接信｜cx468-web（官網 repo）＋ CX468 雲端維運

> 現況快照，不是 changelog。歷史在 `git log`。
> 最後重寫：2026-08-14 18:5x（新聞卡換稿＋精進會議落地＋企業貸款新專案線交接）
> 本次重寫原因：上一版（同日 08:20）的「未竟五項」第一順位仍在（8/15 廣告判讀），但**第三順位已結案、GMB 判定被推翻、新增一條專案線（CX-FUNDING）**。故整節重寫、未堆疊。

## 一、當前狀態快照

| 項目 | 值 | 重驗指令 |
|---|---|---|
| cx468-web HEAD | `37aef9c`，與遠端一致 | `cd ~/cx468-web && git status -sb` |
| 工作區 | 乾淨。既有未追蹤 `scripts/archive/goal-scores.jsonl`（**勿 add**） | 同上 |
| cx468-ga4-daily | `c586911`，**ahead 已歸零**（8/14 老闆授權推送）。未追蹤 `baseline.py`／`logs/`（勿 add） | `cd ~/cx468-ga4-daily && git status -sb` |
| 新聞焦點卡 | **央行信用管制成效**（8/14 08:42 上線），下次硬截止 **2026-08-21** | 見第三節「⚠️ 換稿前必讀」 |
| SEO/AEO/GEO | 123 頁，SEO 8 項全 0 缺、GEO 全 0 缺、AEO 僅 privacy／terms（豁免）。radar-index 16/16 | `python3 scripts/audit_seo.py` |
| FAQ 同源 | 121 頁、漂移 0 | `python3 scripts/audit_faq_samesource.py` |
| **Meta 廣告** | 兩支 ACTIVE：`rm-declined-leads-202608`（名單 200/日）、`rm-declined-lp`（流量 100/日）。`inherit-era-img3` 已於 8/14 03:09 暫停 | 見第二節 |
| **Google 廣告** | `rm-declined-search-202608` ENABLED、200/日、七項稽核全綠（8/14 08:08） | 見第二節 |
| 排程 | `com.cx468.healthcheck`／`indicators-local`／`leadspoll` 三支 launchd 全載入 exit 0 | `launchctl list \| grep cx468` |
| 名單 | poller 每 15 分鐘正常心跳，email 側 **1 筆**（LINE 側 28 筆不經此檔） | `tail -3 ~/.cx468/leads/poller.log` |
| **期限型任務** | 回電 SOP 實錄複核 剩 14 天 0/3 通；銀行條文存證複查 剩 28 天 0/1 次 | 見第二節「期限型任務登記表」 |

⚠️ **三個路徑陷阱**：
1. 網站程式碼在 `~/cx468-web/`，**不在 iCloud 專案夾**。
2. `行銷產出/`、`知識庫/`、`制度/`、`鋮馨企業貸款補助/` 在 **iCloud 專案夾**，在 repo 裡 `ls` 會空手而回。
3. LINE bot 查驗一律用 `~/cx468-linebot`，iCloud 專案夾內那份是凍結殭屍複本。

## 二、可複用資產／程序

### 🆕 期限型任務登記表（8/14 精進會議落成）

`~/.cx468/pending_reviews.json` → 三日健檢檢查4 自動倒數，逾期推 Telegram。
**凡是有硬截止、又沒有其他系統在盯的任務，一律登記進去，不要只寫在清單或交接信裡。**
新增任務**改 JSON 即可，不必動程式碼**。分級：已完成🟢可結案／逾期🔴含天數／≤3天🔴／≤7天⚠️／其餘🟢。
程式在 `~/cx468-ga4-daily/health_check.py` 檢查4 第 (5) 段。已測三種邊界。

### 🔑 Meta 權杖（永不過期）

| 檔案（chmod 600、不進 git） | 用途 |
|---|---|
| `~/.cx468/fb_system_user.token` | 系統用戶・建廣告／改預算／換素材／開關／讀 insights |
| `~/.cx468/fb_page_system.token` | 粉專・建即時表單／抓名單 |

**Meta 查法**：
```bash
T=$(cat ~/.cx468/fb_system_user.token)
curl -sG "https://graph.facebook.com/v21.0/act_1693554028195795/insights" \
  --data-urlencode "access_token=$T" --data-urlencode "level=campaign" \
  --data-urlencode "fields=campaign_name,spend,impressions,inline_link_clicks,ctr,frequency" \
  --data-urlencode "date_preset=today"
```
- 帳戶時區 Asia/Taipei、幣別 TWD
- **配額類數字一定要配改動史看**：`/act_xxx/activities?since=...` 過濾 `spend_limit`／`billing`。`amount_spent` 是「自上次重置起」的累計，不是歷史總量（8/14 踩過，memory `feedback_quota_snapshot_needs_reset_history`）
- 建活動必填：`is_adset_budget_sharing_enabled`、`regional_regulated_categories=["TAIWAN_UNIVERSAL"]`、`regional_regulation_identities`（皆 `2154353671792733`）
- creative 一律 `degrees_of_freedom_spec` 全 OPT_OUT

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
🔴 媽祖裁示：上線兩週內（**8/28 前**）抽聽或自報三通實錄複核。**已進期限型任務登記表自動倒數。**

## 三、未竟任務

### 🔴 第一順位：三支廣告首週判讀（8/15，就是明天）

| 活動 | 管道 | 日預算 |
|---|---|---|
| `rm-declined-leads-202608` | Meta 即時表單 | 200 |
| `rm-declined-lp` | Meta 流量 | 100 |
| `rm-declined-search-202608` | Google 搜尋 | 200 |

**判準表**：frequency > 2.0 → 開 D（子女視角）／連結 CTR < 1% → 開 B（同一間房不同答案）／CTR ≥ 1.5% 且 frequency < 1.5 → 不動／**GA4 平均參與秒數 < 10 秒 → 先修落地頁，別加碼買量**。
素材包：`行銷產出/FB廣告圖/2026-08-12-以房養老被拒-廣告文案-FINAL.md`（B–E 已過媽祖）。

⚠️ **`rm-declined-leads-202608` 零出量已排查完畢（8/14）**：三層 ACTIVE、零 issues、表單 ACTIVE 且合規、粉專名單條款已接受、受眾 140–160 萬、帳戶正常 → **結論是冷啟動，不是故障**。8/15 若仍零曝光，查序：learning stage → `LOWEST_COST_WITHOUT_CAP` 在 58–65 窄齡搶不到版位 → **才輪素材。表單已驗乾淨，別動。**

### 🔴 第二順位：企業貸款補助專案（CX-FUNDING）——新專案線

專案夾：`鋮馨企業貸款補助/`（iCloud 專案夾，三個平放檔：`CLAUDE.md` 29KB／`programs.json` 20 筆方案／`company-facts.json`）

**定位（已判定，勿再誤讀）**：**鋮馨這間公司自己去申請**政府補助／貸款／輔導，**不是新開一條幫客戶辦企業貸款的服務線**。該專案 §0-2 明訂「不得產出對外文案，僅供內部決策與送件準備」；§9.3 紅線禁止出現「我們協助申請」「代辦過件」。唯一與客戶有關的是 §6.3——鋮馨自己不適用的一般政策性貸款轉為 SEO 內容資產。

**專案狀態：`BLOCKED`**，卡 §2 三個未知數：`paid_in_capital`（實收資本額）、`responsible_person_in_labor_insurance_roster`（負責人是否在勞保投保名冊）、`business_scope_codes`（營業項目代碼）。
🔴 該專案自訂鐵則：**任何欄位為 null 時，需要它的任務一律停止並詢問，不得以估算值代替。**

**最高槓桿三件**（依檔案自帶 priority）：
1. **產業競爭力輔導團**（priority 0）—— 免費、無身分門檻、線上入案 `eii.nat.gov.tw/moeai-plus/`。一件事換三個用途：SBIR 技術佐證＋原民會立案基礎＋貸款「曾獲政府輔導培育」免擔保免保人資格。專案稱「CP 值最高的單一動作」。
2. **SBIR Phase 1**（priority 1）—— 150 萬**不用還**、隨到隨審全年開放、通過率約 43%、無身分門檻。已有計畫書骨架 v1（但**該檔不在資料夾內**，見下方落差）。
3. **原住民族事業貸款**（priority 1）—— 額度最大、利率最低（約 1.6%）、以負責人名義申辦不看股權比例。**硬門檻卡在創業輔導課程 0/20 小時。**

**🔴 唯一硬期限：2026-09-22 中午 iPAS 報名截止**（距今 39 天）。
**⏳ 時效**：`programs.json` 多數 `verified_at` 為 2026-08-12、`revalidate_after_days: 90` → **2026-11-10 起全部須重新查證**。

---

#### 📄 下一個工作（老闆 8/14 指定）：工序＋條件對照 PDF

**產出**：一份 UI 清楚、可直接預覽的 PDF，回答「鋮馨要做這個企業貸款，**需要哪些工序、符合哪些條件**」。

**素材全部現成，不用重新研究**——該專案 CLAUDE.md 已寫好：
- §2.2 決策樹（以勞保投保名冊為分岔點的分流邏輯）
- §3 資格總表（14 方案 × 判定／額度／卡點）
- §4.5 貸款應備文件 8 項 checkbox
- §8 執行時序（8.1 本週四動作／8.2 三通電話含問句逐字／8.3 硬期限／8.5 時程軸）
- §9 資格檢核表（通用排除 6 條／執行地雷 4 條／對外紅線 6 條）
- §11 任務看板（四色 12 個 checkbox，目前**無一勾選**）

**PDF 建議結構**（供下個 session 參考，非定案）：
1. 封面＋一頁摘要：現在卡在哪三個數字、解鎖後能拿到什麼
2. **決策樹圖**（§2.2）——投保名冊 in/out 兩條路徑分流，這是全案樞紐
3. **方案資格總表**（§3）——✅適用／❌不適用／⚠️待確認 三色
4. **工序時序圖**（§8.5）——含 9/22 iPAS 硬期限標記
5. **應備文件 checklist**（§4.5＋5 份待調文件）
6. **紅線頁**（§9.3 六條，不得暗示與政府機關有從屬或代辦關係）

**做 PDF 的工具**：有 `make-pdf` skill 可用；或寫 HTML 再列印成 PDF（本專案熟悉的路數，且能做出好看的 UI）。
**⚠️ 紀律**：null 欄位一律如實標「待確認」，**不可用估算值或一般常識填空**——這份會拿去做送件準備，編造會出事。這也正是 PDF 的價值：讓老闆一眼看到卡點在哪。

#### 🔴 該專案三處資料不一致（做 PDF 前先跟老闆確認）

| 欄位 | `company-facts.json` | 憲法 CLAUDE.md | 處置 |
|---|---|---|---|
| 統一編號 | `null` | `60602537` | 直接補上即可 |
| email | `jaroma1314@gmail.com`／`cz468@gmail.com` | `cx468468@gmail.com` | **問老闆哪個是對的** |
| 合作銀行 | 「**40+**」 | 「39 家以上」，且**明文禁寫「逾40家」** | 🔴 **踩憲法紅線，須改為「39 家以上」**（memory `feedback_ad_claims_match_constitution`） |

**另有目錄落差**：該專案 §0 宣告的結構是 `data/`、`docs/`、`tracking/` 子夾，實際是三個檔平放；`docs/sbir-phase1-outline.md`（宣稱「已有 v1」）**不在資料夾內**，位置未載——下個 session 要先找它或確認是否根本沒建。

### 🟡 第三順位：回電 SOP 實地複核（8/28 前）

SOP 已上架但**還沒有任何一通實際來電驗證過**。媽祖要求兩週內抽聽或自報三通實錄。**已進期限型任務登記表自動倒數（剩 14 天，0/3 通）。**

### 🟢 可選不急

1. **新聞焦點卡下次硬截止 2026-08-21**。
   ⚠️ **換稿前必讀**：先跑 `git log --oneline -5 -- radar-index.html` 查上次換稿時間算**實際服役天數**。硬截止日是**到期日不是動手日**——8/14 就因為讀錯而同日換了兩次，舊卡只活 6 小時 41 分（memory `feedback_check_content_age_before_rotating`）。
   ⚠️ 改卡片註解格式會弄壞 `~/cx468-ga4-daily/health_check.py` 的 regex（跨 repo 字串耦合，8/14 踩過，memory `feedback_cross_repo_string_coupling`）。
2. **Anthropic auto-reload**（本機查不到，API 無餘額端點，只能 console 看）。
3. **Postgres `cx468-fb-news-db` 每月 US$21.02**、手機表格逐字直排、設計系統收斂（舊綠 `#16A34A` 殘留 7 頁、`#0071e3` 藍 58 檔）。
4. **goshoot「Daily site audit」連續失敗**（跨事業線）。

### 日常常態

- 每天 12:00 精進會議（**session 級排程，每個 session 要用 CronCreate 重設**）
- 三日健檢 `com.cx468.healthcheck`（檢查4 五項：新聞卡年齡／Threads token／queue 存量／Anthropic 餘額／**期限型任務登記表**）
- 名單輪詢 `com.cx468.leadspoll` 每 15 分鐘｜本機指標 5/25 號 10:30｜曝光巡檢 08:12｜Threads 12:30（queue 排到 8/31）
- ⚠️ **Threads token 剩 55 天（約 2026-10-08 到期）**，換發後務必更新 `~/.cx468/threads_token_issued`

## 四、等使用者的事項

1. 🔴 **GMB 影片驗證**——GEO 站外總開關，卡三週。**站外簡介工作 7/23 就做完 90%**（四平台結案，別再誤判「未動」）；剩服務區域／次要電話／「更多」屬性三項全部等驗證通過。逐步帶法：`行銷產出/技術記錄/2026-08-14-GMB驗證解鎖checklist.md`
2. **企業貸款專案三處資料不一致**（統編／email／合作銀行 40+）＋三個阻塞數字（資本額／勞保投保名冊／營業項目代碼）
3. **Meta `spend_cap`**：剩 2,483（距 8/5 重置 9 天），日花約 300 → 約 **8/22** 撞頂。撞到全帳戶停投，兩支廣告一起死
4. **Anthropic auto-reload**：console.anthropic.com → Billing，建議「低於 $5 自動補到 $50」
5. **名單進來後的回電**——SOP 已備妥，**回電前務必先讀**；名單**禁止回灌 Meta 做自訂受眾／類似受眾**
6. **通話實錄回報**——8/28 前三通，交媽祖複核
7. **合一地政士事務所洽談**——只有老闆本人能談（面談包 `行銷產出/策略簡報/2026-08-12-合一地政士事務所面談包-FINAL.md` 已過媽祖，四條紅線見 memory `project_land_agent_channel_heyi`）

## 五、本 session（8/14 早–晚）做了什麼

| 事項 | 證據 |
|---|---|
| Meta leads 零出量全鏈路排查 → 判定冷啟動非故障 | API 實讀三層狀態＋表單＋粉專條款＋受眾規模 |
| 新聞焦點卡換稿（央行信用管制成效）上線 | `37aef9c`，媽祖零必改通過，線上像素驗證（動態範圍 170、101 色塊） |
| 精進會議：Step 0 七項驗收、教訓落地 4 條 | `行銷產出/精進會議/2026-08-14.md` |
| 檢查4 增列期限型任務登記表 | `c586911`，六項全綠＋三種邊界已測 |
| **推翻 GMB「四次未動」誤判** | 7/23 稽核檔第八節有完整執行紀錄＋截圖證據 |
| GMB 驗證解鎖 checklist | `行銷產出/技術記錄/2026-08-14-GMB驗證解鎖checklist.md` |
| 企業貸款專案情報掃描 | 本檔第三節第二順位 |

**本 session 落地的 memory**：`feedback_check_content_age_before_rotating`、`feedback_cross_repo_string_coupling`、`feedback_quota_snapshot_needs_reset_history`（新）／`feedback_disclaimer_four_variants_and_neutral_cta`、`feedback_verify_external_artifact_not_logs`（更新）
