# 交接信｜cx468-web（官網 repo）

> 現況快照，不是 changelog。歷史在 `git log`。
> 最後重寫：2026-08-03（全站視覺目檢 session 收尾）

## 一、當前狀態快照

| 項目 | 值 | 重驗指令 |
|---|---|---|
| HEAD | `d59e795` feat(ui): 導入 Uiverse 元件並全部改綁品牌色 | `cd ~/cx468-web && git log --oneline -1` |
| 本地 vs 遠端 | 一致（`main...origin/main`，無 ahead/behind） | `git status -sb`；`git ls-remote origin HEAD` |
| 工作區 | 乾淨，僅一個既有未追蹤檔 `scripts/archive/goal-scores.jsonl`（非本 session 產生，勿 add） | `git status -sb` |
| 線上 | 首頁與關鍵頁全 200 | `curl -s -o /dev/null -w '%{http_code}' https://cx468.com.tw/` |
| 頁面數 | sitemap 115 筆、repo 根目錄 132 個 html | `grep -c '<loc>' sitemap.xml` |
| 本 session 程式碼改動 | **零**。純唯讀目檢，只新增 `docs/` 兩份文件 | `git show --stat HEAD` |

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
1. **`docs/visual-audit-2026-08-03.md` 第一節 9 項已複驗缺陷** ← 下個 session 的第一順位入口。每項都附了重驗指令，動手前先自己跑一次確認還在。修完要逐頁瀏覽器 render 驗（memory: `feedback_browser_verify_every_page`）
2. 手機表格逐字直排（同一份 table CSS 影響 8+ 頁）
3. 14 頁補載 `style.css`（清單在報告第一節第 7 列；要先確認不撞頁內自訂樣式）
4. 配圖治理：美國 IRS 表單／洛杉磯地標／廟宇照／塑膠模型屋，換 `房屋圖片/` 真實圖庫（需老闆選圖，memory: `feedback_boss_prefers_human_visuals`、`feedback_photo_library_labels_unverified`）
5. 設計系統收斂（兩套表單元件、舊綠 #16A34A 殘留、非品牌色整頁）——專案級，建議獨立立項

### 日常常態
- 每天 12:00 精進會議（session 級排程，每個 session 要重設）
- 三日健檢 launchd `com.cx468.healthcheck`（memory: `project_three_day_healthcheck`）
- 曝光每日巡檢 08:12（memory: `project_daily_exposure_patrol`）

## 四、等使用者的事項

1. **修補授權**：報告第一節 9 項都是可直接動手的小改動，但需要老闆說「開始修」＋修完說「部署」才 push（部署鐵則：不可從條件句推定授權）
2. **`#0071e3` 藍字要不要收斂到品牌色**：全站 58 檔 262 處，是既有慣用連結色不是 bug，改與不改是老闆決策
3. **topic-a/b/c/d 快速答案數字與 radar-index 對不上**：需老闆或關公判定哪邊是舊值、月/季口徑怎麼統一，才知道要改哪邊
4. **配圖替換**：老闆偏好真人真實照片，換哪張需要他點頭
