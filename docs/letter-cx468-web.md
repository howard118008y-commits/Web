# 交接信｜cx468-web（官網 repo）＋ CX468 雲端維運

> 現況快照，不是 changelog。歷史在 `git log`。
> 最後重寫：2026-08-05（配圖治理第一批＋Render 帳單排查 session 收尾）
> 本次重寫原因：8/3 版的「未竟五項」第 1 項已完成一半，且新增 Render 維運段落（本 session 才查清）。

## 一、當前狀態快照

| 項目 | 值 | 重驗指令 |
|---|---|---|
| cx468-web HEAD | `4ca230d` 配圖治理第一批（6 檔圖），**已上線驗證** | `cd ~/cx468-web && git log --oneline -1` |
| cx468-fb-news-bot HEAD | `84ab337` render.yaml crawl 降頻＋DB plan 對齊 | `cd ~/cx468-fb-news-bot && git log --oneline -1` |
| 本地 vs 遠端 | 兩 repo 皆一致無 ahead/behind | `git status -sb`；`git ls-remote origin main` |
| 工作區 | 乾淨。cx468-web 有既有未追蹤 `scripts/archive/goal-scores.jsonl`（非本 session 產生，**勿 add**） | `git status -sb` |
| 線上 | 首頁／knowledge／article-sale-leaseback-safety 全 200 | `curl -s -o /dev/null -w '%{http_code}' https://cx468.com.tw/` |
| 換過的 6 張圖 | 線上 bytes 與本機**逐檔一致**（115171/100836/90990/114373/110861/172042） | 見第二節「圖片上線驗證」 |
| Render Blueprint | 四個全 `in_sync`（fb-news-bot／btcucc-radar／ga4-daily／threads-bot） | `curl -H "Authorization: Bearer $(cat ~/.cx468/render_api.key)" https://api.render.com/v1/blueprints` |
| Render cron 排程 | crawl `45 */3 * * *`／post `0 0,4,8 * * *`／indexing `30 1 * * *`／threads `30 4 * * *`／ga4 `0 1 * * *` | 見第二節「Render 狀態查法」 |
| cx468-fb-news-db | `basic_256mb` available（付費，約 US$21/月） | `curl .../v1/postgres/dpg-d887ss3bc2fs73emjit0-a` |

⚠️ **工作目錄在 `~/cx468-web/`，不在 iCloud 專案夾**。iCloud 那份是行銷產出與制度檔（含 `房屋圖片/` 素材庫），動網站程式碼一律走 `~/cx468-web/`（memory: `feedback_icloud_conflict_copies`）。

## 二、可複用資產／程序

### 配圖重取景腳本（本 session 建立）
`recrop.py` 邏輯：等比裁切到目標長寬比（**不變形**）→ LANCZOS 縮放 → `quality=82, optimize, progressive`。
- 來源庫：`/Users/hohomacmini/Library/Mobile Documents/com~apple~CloudDocs/鋮馨cloud code/房屋圖片/`（24 張）
- 原檔備份：`~/cx468-web/img/_original/`（腳本只在該檔首次被動時備份，不覆蓋既有備份）
- 關鍵參數是**垂直錨點 y_frac**：來源多為直幅、目標多為橫幅，中央裁切常把招牌／車牌帶進來，要逐張指定錨點
- 保留原檔名＝零 HTML 改動、零網址／og:image 影響

### 圖庫合規分級（本 session 逐張目檢 24 張，**檔名標籤不可信**）
- **直接可用 6 張**：紅磚三合院迴廊、大同區密集老屋、淡江大橋天際線、信義區雙塔、空拍扭轉高塔、台北101
- **重裁可救 6 張**：三合院紅瓦屋簷（裁車牌/古蹟名）、金黃天際線（裁 THE LIN）、高架橋大樓（裁卡車牌）、空拍黑塔（裁 wework）、建案工地、木造紅燈籠樓
- **必須避用 12 張**，其中 4 張踩紅線：上海商銀＋渣打招牌、聯邦銀行霓虹、武財神幸運輪／刮刮樂（彩券行）、中正紀念堂國旗牆
- ⚠️ 標「乾淨候選」那張右下有卡車車牌＋MOTEL 招牌（memory: `feedback_photo_library_labels_unverified`）
- ⚠️ **圖庫零人像**。Sir 2026-08-05 拍板「先接受純建築，之後補拍」

### 圖片上線驗證（比對 bytes，不看 git log）
```bash
cd ~/cx468-web && for f in article-loan-integration knw-temple; do
  printf "%-28s 線上=%s 本機=%s\n" "$f" \
    "$(curl -s -o /dev/null -w '%{size_download}' "https://cx468.com.tw/img/${f}.jpg?v=$RANDOM")" \
    "$(stat -f '%z' img/${f}.jpg)"; done
```
等 Pages 生效用 until-loop（禁止裸 `sleep`，harness 會擋）：
```bash
LOCAL=$(stat -f "%z" img/X.jpg); until [ "$(curl -s -o /dev/null -w '%{size_download}' "https://cx468.com.tw/img/X.jpg?v=$RANDOM")" = "$LOCAL" ]; do sleep 5; done
```

### Render 狀態查法（免 Sir 截圖）
鑰匙 `~/.cx468/render_api.key`，owner `tea-d7gmpj57vvec73ag4nbg`。服務 ID：
| 服務 | id |
|---|---|
| cx468-crawl | `crn-d887thjbc2fs73emk9ag` |
| cx468-post | `crn-d887thjbc2fs73emk9a0` |
| cx468-indexing-daily | `crn-d978sr8k1i2s73aabbig` |
| cx468-threads-bot | `crn-d8jnsps8aovs73d86pig` |
| cx468-ga4-daily | `crn-d8jmii6gvqtc73ehq370` |
| cx468-fb-news-db | `dpg-d887ss3bc2fs73emjit0-a` |
| fb-news-bot blueprint | `exs-d8878tjeo5us738vnoqg` |

log 查法：`GET /v1/logs?ownerId=<owner>&resource=<id>&startTime=...&endTime=...&limit=40`（訊息帶 ANSI 色碼，用 `re.sub(r'\x1b\[[0-9;]*m','',msg)` 清掉）。
⚠️ **`GET /v1/blueprints/{id}` 回 internal server error**，錯誤詳情只有 Dashboard 頁面看得到。
⚠️ **API 的 PATCH／sync 端點會被 Claude Code 權限攔截** — 改設定只能走 render.yaml + Manual sync，或請 Sir 加 Bash 權限規則。
⚠️ Blueprint 三個坑（plan 語法、error 不自動重試、方案飄移）→ memory: `feedback_render_blueprint_sync_traps`

### 全站視覺目檢管線（2026-08-03 建立，仍有效）
1. venv：`python3 -m venv pw && ./pw/bin/pip install playwright pillow && ./pw/bin/playwright install chromium`
2. sitemap 取 URL → 桌機 1280×900／手機 390×844 → `add_init_script` 塞 `localStorage.cx_antifraud_v1` 繞反詐 modal → 捲到底再回頂觸發 lazy/GSAP → `full_page` 截圖 → PIL 切 tile
3. 分 4 個 range 平行跑，115 頁×2 視窗約 6 分鐘、77MB
- ⚠️ zsh 不做 `set -- $var` 詞分割，批次迴圈參數要寫死
- ⚠️ repo 內 `scripts/visual_sweep.py` 是視窗版機掃（底色/footer/溢出/JS 錯誤），**不含**切片目檢，兩者互補
- 壞圖偵測：`img.complete=true` 且 `naturalWidth>0` **不代表畫得出來**，損毀 AVIF 會渲染全白 → PIL 逐檔解碼（memory: `feedback_broken_avif_renders_blank`）

## 三、未竟任務

### 硬期限相關
- 無。

### 可選不急

1. **配圖治理第二批**（第一批 6 組已上線，這是剩下的）
   - `knw-hillside.jpg` 東北角海岸山景 → 用於 `article-inherited-loan-seized`「房子要被法拍」，**最離題的一張**
   - `knw-arch.jpg` 清水模建築 → knowledge.html **重複用兩次**
   - `audience-credit.jpg` 手捧娃娃屋、`article-home-equity.jpg` 塑膠模型屋＋鑰匙
   - `gen-yonghe.jpg` AI 生成鐵皮天台（用於 yonghe-property-finance）
   - 素材只剩「重裁可救 6 張」可用（見第二節分級），一對一配不完，會需要重複用圖或補拍
   - ⚠️ 稽核報告 `docs/visual-audit-2026-08-03.md` 有兩處與現況不符（本 session 打開圖檔比對過）：`inherit-slb-hero.jpg` 不是塑膠模型屋而是紅磚祖厝（切題但是 AI 生成圖）；`xinbei-hero.jpg` 已經是自家高架橋實景照。**別照抄舊報告，動手前自己開圖看**

2. **Postgres `cx468-fb-news-db` 每月 US$21.02**（本次帳單最大單項，Sir 尚未決定去留）
   - 真因：5/22 建立、6/22 `updatedAt`——**免費 30 天期滿被自動升級成付費**
   - 實際用途只有兩張表：`news`（`src/db.py:118` `prune_old_news(hours=48)`，每次爬 insert 約 62 筆）、`promo_log`。資料量幾百筆卻付 256MB 付費方案
   - 搬走的話要改 `~/cx468-fb-news-bot/src/db.py`；⚠️ Render cron job **沒有 persistent disk**，不能直接換 SQLite

3. **goshoot GitHub Actions「Daily site audit」連續失敗**（另一 repo、另一事業線）
   - `gh run list --repo howard118008y-commits/goshoot.com.tw --workflow "Daily site audit"` — 7/29 起每天 6:30 全紅
   - 不是程式壞掉：稽核抓到 **22 個 SEO 缺失後 exit 1**，所以每天寄信
   - 缺失集中在 4 檔：`goshoot-mobile.html`／`homepage-cover-preview.html`／`ichiban-story.html`／`pools.html`，缺 canonical／og:image／twitter:card／JSON-LD，且四檔都不在 sitemap
   - `homepage-cover-preview.html` 看名字像預覽檔，可能該排除稽核而非補 meta

4. **手機表格逐字直排**：8+ 頁共用同型 table CSS。建議一律 `overflow-x:auto` ＋首欄 `min-width`／`nowrap` ＋捲動提示

5. **設計系統收斂**：兩套表單元件（底線式＋圖示卡 vs 灰底框＋原生 select，後者在 article-home-equity／article-second-mortgage／hsinchu-second-mortgage／article-second-mortgage-rates）；舊綠 `#16A34A` 殘留 7 頁 → `#048456`；market-insight／rental-management-news／glossary／compare-options 整頁藍色系

6. **topic-a/b/c/d 快速答案數字與 radar-index 對不上**：真實來源是 `cx_data.json`（`fetch_indicators.py` 餵），建議寫成 build 期腳本重寫四頁數字＋統一月/季口徑標示；**勿手改**

7. **`#0071e3` 藍**：58 檔 262 處。建議只改「文字連結」用途（`color:#0071e3`）→ 品牌綠 `#048456`，`background:`／`border:` 用途另案

### 日常常態
- 每天 12:00 精進會議（session 級排程，每個 session 要重設）
- 三日健檢 launchd `com.cx468.healthcheck`（memory: `project_three_day_healthcheck`）
- 曝光每日巡檢 08:12（memory: `project_daily_exposure_patrol`）
- **Render／FB／Threads 現況（本 session 實查）**：threads-bot 8/3–8/5 連 3 天成功（最近 post id `18364103452240816`）；FB bot 8/5 16:00 已發（post id `1079210581947639_122119993857339172`）；`TELEGRAM_BOT_TOKEN`/`CHAT_ID` **仍未設**，fb-news-bot 的管理通知只印 stdout；LINE 群推已停用（OA 配額耗盡）

## 四、等使用者的事項

1. **crawl 降頻的第一次驗收**：新排程 `45 */3 * * *` 的首跑是 **UTC 09:45（台北 17:45）**，本 session 收尾時尚未到。下個 session 開場先查一次 log 確認有正常跑完、`[crawl] inserted N` 數字正常，才算結案
2. **Postgres US$21.02 去留**（見未竟第 2 項）——搬走要改程式，留著就是每月固定成本
3. **配圖第二批的補拍決策**：圖庫零人像，Sir 已定「先接受純建築、之後補拍」；真人素材要他本人提供或授權採購
4. **Render API 寫入權限**：改排程／觸發 sync 都被 Claude Code 權限攔截，目前只能 Sir 到 Dashboard 按 Manual sync。要免除這道人工，需在設定加 Bash 允許規則
5. **goshoot 稽核 22 項**（見未竟第 3 項）——跨事業線，要不要現在修是 Sir 的排序決定
