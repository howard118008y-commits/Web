# 交接信｜cx468-web（官網 repo）

> 現況快照，不是 changelog。歷史在 `git log`。
> 最後重寫：2026-08-03（全站視覺目檢 session 收尾）

## 一、當前狀態快照

| 項目 | 值 | 重驗指令 |
|---|---|---|
| HEAD | `f48ae87` fix(visual): 全站目檢第一批 9 類缺陷修補（32 檔），**已上線驗證** | `cd ~/cx468-web && git log --oneline -1` |
| 本地 vs 遠端 | 一致（`main...origin/main`，無 ahead/behind） | `git status -sb`；`git ls-remote origin HEAD` |
| 工作區 | 乾淨，僅一個既有未追蹤檔 `scripts/archive/goal-scores.jsonl`（非本 session 產生，勿 add） | `git status -sb` |
| 線上 | 首頁與關鍵頁全 200 | `curl -s -o /dev/null -w '%{http_code}' https://cx468.com.tw/` |
| 頁面數 | sitemap 115 筆、repo 根目錄 132 個 html | `grep -c '<loc>' sitemap.xml` |
| 本 session 程式碼改動 | 目檢 115 頁 → 修 9 類缺陷、32 檔，已 push 並線上驗證通過 | `git show --stat HEAD`；驗證清單見 `docs/visual-audit-2026-08-03.md` 的修補紀錄 |

⚠️ **工作目錄在 `~/cx468-web/`，不在 iCloud 專案夾**。iCloud 那份是行銷產出與制度檔，動網站程式碼一律走 `~/cx468-web/`（memory: `feedback_icloud_conflict_copies`）。

## 二、可複用資產／程序

### 全站視覺目檢管線（本 session 建立，可重跑）
1. 建 venv 裝 playwright + pillow（chromium 本機已有快取）：
   `python3 -m venv pw && ./pw/bin/pip install playwright pillow && ./pw/bin/playwright install chromium`
2. 取樣腳本邏輯（臨時檔已隨 session 目錄失效，重寫約 40 行）：sitemap 取 URL → 桌機 1280×900／手機 390×844 兩個 context → `add_init_script` 塞 `localStorage.cx_antifraud_v1` 繞過反詐 modal → 捲到底再回頂觸發 lazy/GSAP → `full_page` 截圖 → PIL 切成桌機 1000×1250、手機 390×950 的 tile
3. 分 4 個 range 平行跑（`capture.py vs 0 29` 這種），115 頁×2 視窗約 6 分鐘、77MB
4. 派 12 組 agent 每組約 10 頁，逐張 Read tile
- ⚠️ zsh 不做 `set -- $var` 詞分割，批次迴圈要直接寫死參數
- ⚠️ repo 內既有 `scripts/visual_sweep.py` 是視窗版機掃（底色/footer/溢出/JS 錯誤），**不含**切片目檢，兩者互補

### 壞圖偵測（本 session 新雷點）
`img.complete=true` 且 `naturalWidth>0` **不代表畫得出來**。損毀 AVIF 會回報正常但渲染全白。偵測法：PIL 逐檔解碼。
memory: `feedback_broken_avif_renders_blank`

## 三、未竟任務

### 硬期限相關
- 無。本 session 未觸發任何期限型任務。

### 可選不急（本 session 產出，全部待修）
> 第一節 9 項已於 2026-08-03 全數修完並上線（見報告開頭的修補紀錄），以下是**還沒動**的。
> 老闆 2026-08-05 已口頭認可「以你建議的修改」，但當次 session 隨即收尾部署，實際未動工——下個 session 可直接接手，動工前再確認一次範圍。

1. **配圖治理**：約 12 處離題 hero（美國 IRS 報稅表單＝article-inherited-shared-ownership、洛杉磯地標×2＝knowledge.html、廟宇/廟會照×3、塑膠模型屋×3、北美豪宅客廳×2）。素材庫 `鋮馨cloud code/房屋圖片/`（24 張，檔名已標「已用/未用/避用」但**標籤不保證乾淨**，用前逐張 Read 目檢，memory: `feedback_photo_library_labels_unverified`）
2. **手機表格逐字直排**：8+ 頁共用同型 table CSS。建議一律 `overflow-x:auto` ＋首欄 `min-width`／`nowrap` ＋捲動提示（比逐頁改卡片式風險低）
3. **設計系統收斂**：兩套表單元件（底線式＋圖示卡 vs 灰底框＋原生 select，後者在 article-home-equity/article-second-mortgage/hsinchu-second-mortgage/article-second-mortgage-rates）；舊綠 #16A34A 殘留 7 頁 → #048456；market-insight/rental-management-news/glossary/compare-options 整頁藍色系
4. **topic-a/b/c/d 快速答案數字與 radar-index 對不上**：真實來源是 `cx_data.json`（`fetch_indicators.py` 餵），建議寫成 build 期腳本重寫四頁數字＋統一月/季口徑標示；勿手改
5. **`#0071e3` 藍**：58 檔 262 處。建議只改「文字連結」用途（`color:#0071e3`）→ 品牌綠 #048456，`background:`／`border:` 用途另案，避免整站按鈕變色

### 日常常態
- 每天 12:00 精進會議（session 級排程，每個 session 要重設）
- 三日健檢 launchd `com.cx468.healthcheck`（memory: `project_three_day_healthcheck`）
- 曝光每日巡檢 08:12（memory: `project_daily_exposure_patrol`）

## 四、等使用者的事項

1. **修補授權**：報告第一節 9 項都是可直接動手的小改動，但需要老闆說「開始修」＋修完說「部署」才 push（部署鐵則：不可從條件句推定授權）
2. **`#0071e3` 藍字要不要收斂到品牌色**：全站 58 檔 262 處，是既有慣用連結色不是 bug，改與不改是老闆決策
3. **topic-a/b/c/d 快速答案數字與 radar-index 對不上**：需老闆或關公判定哪邊是舊值、月/季口徑怎麼統一，才知道要改哪邊
4. **配圖替換**：老闆偏好真人真實照片，換哪張需要他點頭
