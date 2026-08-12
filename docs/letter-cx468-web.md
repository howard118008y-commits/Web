# 交接信｜cx468-web（官網 repo）＋ CX468 雲端維運

> 現況快照，不是 changelog。歷史在 `git log`。
> 最後重寫：2026-08-12（獲客結構轉向：下游→上游 session 收尾）
> 本次重寫原因：8/05 版的重心是配圖與 Render 帳單，已非現況重心。本 session 老闆拍板**獲客從市場末端轉上游**，網站與廣告雙線都改了方向，舊版「未竟五項」有兩項降級、新增上游內容線與廣告重建線。舊段落已刪除重寫，未堆疊。

## 一、當前狀態快照

| 項目 | 值 | 重驗指令 |
|---|---|---|
| cx468-web HEAD | `77f5b3a`（本 session 四顆：`607000d` 長照 A/B 上線、`a9745be` 標題修復 14 頁、`ef56cf6` 長照 C/D＋B 更正、`2bc6e36` 中性表單） | `cd ~/cx468-web && git log --oneline -6` |
| 本地 vs 遠端 | 一致（本 session 收尾已 rebase） | `git status -sb`；`git ls-remote origin main` |
| 工作區 | 乾淨。既有未追蹤 `scripts/archive/goal-scores.jsonl`（非本 session 產生，**勿 add**） | `git status -sb` |
| 長照系列四篇線上 | 全 200 | `for U in article-reverse-mortgage-declined article-parents-house-sell-or-not article-longterm-care-monthly-gap article-longterm-care-30-coverage; do curl -s -o /dev/null -w "$U %{http_code}\n" https://cx468.com.tw/$U.html; done` |
| FAQ 同源 | 含 FAQPage 120 頁，同源 120、漂移 0 | `python3 scripts/audit_faq_samesource.py` |
| SEO/AEO/GEO | 新頁皆 16/16；全站僅 privacy-policy／terms-of-service 13/16（AEO 豁免既有基線） | `python3 scripts/audit_seo.py` |
| Meta 廣告 | **只剩 1 支在跑**：`inherit-era-img3`（TRAFFIC／LPV、日預算 400、年齡 40–64、Advantage Audience 已關） | 見第二節「廣告查法」 |
| Threads bot | token 已換新（8/9 事故）、防重複機制上線；8/10 12:30 實發成功 | `crn-d8jnsps8aovs73d86pig` log 找 `[OK] posted` |
| LINE OA | 資格四問已上線（含 Q4 貸款狀況）；富者一語推播已改**每週一** 09:00（`cx468-linebot` `dee338e`） | `cd ~/cx468-linebot && git log --oneline -1` |

⚠️ **工作目錄在 `~/cx468-web/`，不在 iCloud 專案夾**（memory: `feedback_icloud_conflict_copies`）。

## 二、可複用資產／程序

### 本 session 的核心判準（比任何腳本都重要）

**「錢字測試」**：搜尋詞裡出現 貸款／借款／額度／利率／過件／財力 任一詞 → 已被代辦與導客聯盟洗滿，我們排不進去也不該搶。真上游詞只帶**事件、稅制、產權、流程、期限、費用名目**。
GSC 實據：106 個帶錢字的詞、867 曝光、**0 點擊**；上游詞 1,135 曝光拿走全部 15 次點擊。
→ 新選題開寫前先過這一關（memory: `project_lead_quality_baseline_and_lateness`）。

### 三套表單 include（不可混用，memory: `feedback_disclaimer_four_variants_and_neutral_cta`）
| 檔案 | 用在哪 | 頁數 |
|---|---|---|
| `lead-form.html` | 「免費評估」帽的頁（轉換主力） | 39 |
| `lead-form-nofree.html` | 二胎主商品場景 | 5 |
| `lead-form-neutral.html` | 中性橋接帽的頁（純衛教／他行商品解釋） | 2（A、D 篇）|

判準＝**表單跟著 CTA 帽走**，一頁不得混搭。三檔的**結構與腳本必須同步維護**，只有文案與 hidden 欄位（信件主旨、gtag `form` 參數）可以有差異；`generate_lead` 事件名**不可改**（Ads 主要轉換）。

### 廣告查法（免 Sir 開後台）
token `~/.cx468/fb_ads_management_long.token`，帳戶 `act_1693554028195795`。
```bash
TOKEN=$(cat ~/.cx468/fb_ads_management_long.token)
curl -sG "https://graph.facebook.com/v21.0/act_1693554028195795/campaigns" \
  --data-urlencode "access_token=$TOKEN" --data-urlencode "fields=name,effective_status,daily_budget"
```
- 逐日成效加 `insights?time_increment=1&fields=spend,impressions,cpm,inline_link_clicks,actions`
- 版位／年齡拆解用 `breakdowns=publisher_platform,platform_position` 與 `breakdowns=age,gender`
- ⚠️ 改 targeting 前要先關 `targeting_automation.advantage_audience`（開著時 age_max 改不動，回 error_subcode 1870188）

### Render 狀態查法
鑰匙 `~/.cx468/render_api.key`，owner `tea-d7gmpj57vvec73ag4nbg`。服務 ID：
| 服務 | id |
|---|---|
| cx468-crawl | `crn-d887thjbc2fs73emk9ag` |
| cx468-post | `crn-d887thjbc2fs73emk9a0` |
| cx468-indexing-daily | `crn-d978sr8k1i2s73aabbig` |
| cx468-threads-bot | `crn-d8jnsps8aovs73d86pig` |
| cx468-ga4-daily | `crn-d8jmii6gvqtc73ehq370` |
| cx468-linebot | `srv-d86fe9lckfvc73cmddvg` |
| cx468-fb-news-db | `dpg-d887ss3bc2fs73emjit0-a` |

log：`GET /v1/logs?ownerId=<owner>&resource=<id>&limit=40`（ANSI 色碼要 `re.sub(r'\x1b\[[0-9;]*m','',msg)` 清掉）。
⚠️ **改 queue/env 後別馬上手動觸發 cron**——Render 可能還在用舊 build（8/9 實際踩到：log 顯示新 commit、跑的卻是舊 queue，害 Threads 提前發錯篇）。先確認 `GET /v1/services/<id>/deploys?limit=1` 是 `status=live` 且 commit 對得上。

### 上線驗證（Pages 佇列會塞車）
GitHub Pages 部署曾排隊 10 分鐘後 timeout（8/6 實例，`gh run rerun <id>` 重跑即可）。**用 until 迴圈輪詢實際內容，不要只看 workflow 狀態**：
```bash
until curl -s https://cx468.com.tw/ | grep -q "關鍵句"; do sleep 10; done
```

### 全站視覺目檢管線（2026-08-03 建立，仍有效）
venv：`python3 -m venv pw && ./pw/bin/pip install playwright pillow && ./pw/bin/playwright install chromium`；sitemap 取 URL → 桌機 1280×900／手機 390×844 → `add_init_script` 塞 `localStorage.cx_antifraud_v1` 繞反詐 modal → 捲到底再回頂觸發 GSAP → full_page 截圖 → PIL 切 tile。
⚠️ zsh 不做 `set -- $var` 詞分割，批次迴圈參數要寫死。
⚠️ `img.complete=true` 且 `naturalWidth>0` **不代表畫得出來**，損毀 AVIF 渲染全白 → PIL 逐檔解碼（memory: `feedback_broken_avif_renders_blank`）。

## 三、未竟任務

### 🔴 第一順位：稅務頁接服務層（老闆 2026-08-12 指定，下個 session 首項）

**問題**：上游流量全落在稅務／試算工具頁（`rental-yield-calculator` 352 曝光、`new-taipei-house-tax` 185、`new-taipei-land-value-tax` 122…），**一個服務頁都沒進榜**。人來算完稅就走，中間沒有橋。這是目前最大的漏。

**為什麼這是對的切點**：查地價稅／房屋稅的人 100% 有房，而**稅要用現金繳**——正是「有房但手上沒現金」的瞬間，且他還沒開始想貸款（沒被錢字污染）。時間點比繼承更準（有法定繳納期限）。

**可執行規格**：

1. **目標頁清單**（依 GSC 曝光排序，全部在 `~/cx468-web/`）：
   - `rental-yield-calculator.html`、`new-taipei-house-tax.html`、`new-taipei-land-value-tax.html`
   - `taipei-land-value-tax.html` / `-guide`、`taichung-land-value-tax.html`、`taoyuan-land-value-tax.html` / `-guide`、`kaohsiung-land-value-tax.html`
   - `land-tax-calculator.html`、`realestate-tax-calculator.html`、`purchase-cost-calculator.html`
   - 資料來源：`行銷產出/週報/2026-08-10-GSC上游關鍵字盤點.md`（119 個上游詞全清單在附錄 A）

2. **橋接元件規格**（新元件，建議 `tax-bridge.html` 走 `data-include`）：
   - 位置：算完稅的結果區**下方**，不是頁首（人要先拿到他要的東西）
   - 內容框架：「稅算出來了，接下來多數人會遇到的問題是——**這筆錢要從哪裡來**」→ 三條中性路徑（自有資金／與家人分攤／以不動產規劃）→ 連到對應服務頁
   - 🔴 **禁招攬鉤與錢字**：不可寫「貸款」「額度」「利率」，否則這頁就從上游掉進下游語意場，前功盡棄
   - 🔴 CTA 帽用**中性橋接帽**（裁示①⑤家族），配 `lead-form-neutral.html`——這些是工具頁不是轉換頁
   - 免責選版：工具頁無商品敘述 → 傾向**衛教版**，但要請媽祖裁（衛教版原本是為政策文寫的）

3. **必經流程**：橋接文案是對客文案 → **必過 `/媽祖把關`**；她第一輪已建立「表單跟著 CTA 帽走」判準，本案沿用但新元件文案仍需逐字核定。

4. **驗收**：橋接元件上線後 4 週回 GSC 看這批頁的「工具頁→服務頁」內部點擊，以及 GA4 這些頁的下一頁路徑。

**相關 memory**：`project_lead_quality_baseline_and_lateness`（為什麼要做）、`feedback_disclaimer_four_variants_and_neutral_cta`（帽與表單規則）、`feedback_provide_url_list_for_gsc`（改完給 URL）。

### 🟡 第二順位：地政士上游通路（要老闆本人）
合作對象：**蘆洲・合一地政士事務所**（老闆既有關係）。研究結論在 `行銷產出/競品研究/2026-08-10-上游獲客研究.md`：
- 🔴 **不能給轉介費**（地政士法 §27(5)，法定後果停業或除名）；**不能在事務所放我方貸款文宣**（§27(4)，台北市已有 6 起以上申誡停業實例）
- 價值主張要講「**幫你把卡在錢上的案子做完**」——遺贈稅法 §41-1／§42：稅沒繳清不能分割、不能設定負擔，地政士自己沒有資金解方就收不了尾
- 量級：新北平均每位地政士約 9.8 件繼承／年，一家事務所 10–30 件／年
- 建議：先把合一當**樣本不是通路**，跑通一個完整案件流程再談擴點

### 🟡 第三順位：其餘上游族群內容
族群排序在 `行銷產出/競品研究/2026-08-10-上游關鍵字族群研究.md`：🥇查封／法拍前期（分最高但品牌風險也最高）、🥈長照（**已完成四篇**）、🥉自營業稅務線（401 報表，對應憲法 A 客群）。
⚠️ 共有／分家線**建議收縮**：「持分」關鍵字被持分收購業者（市價 5–6 折）佔滿，進去會被 Google 與 AI 歸類成同類。
⚠️ 自營業族群最常見的真實請求是「幫我把 401 弄好看一點」——**與客戶佐證文件紅線同級**，內容要主動寫明不代造。

### 🟢 可選不急
1. **宜蘭／台東地價稅頁資料過期**：`yilan-land-value-tax.html` 描述寫「107-108 年累進起點地價」、`taitung-land-value-tax.html` 寫「113-114 年」，title 卻掛 2026。要查官方最新數字才能改，**勿臆造**。
2. **「租機報酬率」191 曝光、排名 4.5、90 天 0 點擊**：全站具名查詢第一名，落在 `rental-yield-calculator.html`。「租機」字面是機具租賃（無此業務），也可能是「租金」錯字。**單獨查核，別混進標題修復的成效判讀**。
3. **配圖治理第二批**：`knw-hillside.jpg`（海岸山景用在法拍文，最離題）、`knw-arch.jpg`（knowledge.html 重複用兩次）、`audience-credit.jpg`、`article-home-equity.jpg`、`gen-yonghe.jpg`。素材只剩「重裁可救 6 張」（圖庫分級見 memory `feedback_photo_library_labels_unverified`），一對一配不完。
4. **Postgres `cx468-fb-news-db` 每月 US$21.02**：免費 30 天期滿自動升級付費。實際只有兩張表、資料幾百筆。搬走要改 `~/cx468-fb-news-bot/src/db.py`；⚠️ Render cron job 無 persistent disk，不能直接換 SQLite。
5. **手機表格逐字直排**（8+ 頁共用同型 table CSS）、**設計系統收斂**（兩套表單元件、舊綠 `#16A34A` 殘留 7 頁、`#0071e3` 藍 58 檔 262 處）。
6. **goshoot「Daily site audit」連續失敗**（跨事業線）：稽核抓到 22 個 SEO 缺失後 exit 1，缺失集中在 4 檔（`goshoot-mobile` / `homepage-cover-preview` / `ichiban-story` / `pools`）。

### 日常常態
- 每天 12:00 精進會議（session 級排程，每個 session 要重設）
- 三日健檢 launchd `com.cx468.healthcheck`（memory: `project_three_day_healthcheck`）
- 曝光每日巡檢 08:12（memory: `project_daily_exposure_patrol`）
- Threads 自動發文每日 12:30，繼承系列排到 **8/29**（queue 在 `~/cx468-threads-bot/queue.json`）
- ⚠️ **Threads 長效 token 約 60 天到期且過期後不能 refresh**，下次到期約 2026-10 月初。重產路徑在 memory `project_threads_autopost`

## 四、等使用者的事項

1. **GSC 網址審查**：14 條稅務／工具頁老闆 8/12 已送。**還沒送的 6 條**——
   `article-longterm-care-monthly-gap.html`、`article-longterm-care-30-coverage.html`、`article-parents-house-sell-or-not.html`、`article-reverse-mortgage-declined.html`、`knowledge.html`（Sitemap 欄只放 `sitemap.xml`）
2. **合一地政士事務所洽談**（未竟第二順位）——只有老闆本人能談
3. **廣告要不要加值**：目前只剩 1 支在跑、日燒 400，runway 兩週以上，不急。等上游內容累積出訊號再決定重開幾支
4. **10 筆 A/B/C 基線已收**（8/10：`C C B A A A B C A C`，A×4／B×2／C×4）——但老闆補註「**A 級全是貸滿件、做不了**」，所以下次標記要分「A（有空間）／A-（有房沒空間）」
5. **Postgres US$21.02 去留**（未竟可選第 4 項）
6. **Render API 寫入權限**：改排程／觸發 sync 會被 Claude Code 權限攔截，需要老闆在設定加 Bash 允許規則，或他本人到 Dashboard 按 Manual sync
