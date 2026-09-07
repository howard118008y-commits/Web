# 全站視覺目檢｜2026-09-07（Step 0 同日）

取樣：sitemap 123 頁 × 桌機 1280×900／手機 390×844（Playwright 真視窗）→ 慢捲（300px/120ms）＋注入 `*{opacity:1!important;...}` 殺動畫 → full_page → 切片。
**2,096 tiles**（246 張截圖，零截圖錯誤）。目檢：10 組 agent 逐張 Read，實讀加總 **2,096**，與磁碟一致（兩組首報加總算錯，用 `comm` 雙向差集複核為零漏讀）。
複驗：所有線索以線上 Playwright 量 DOM／讀原始碼定讞，共 17 條線索 → **真缺陷 9、假象 6、設計債 2**。

## 一、定讞真缺陷

### 🔴 內容正確性（09-01 已報、一週未修）
1. **4 個縣市地價稅頁稅基過期**：`yilan`（107-108）、`hualien`（109-110）、`chiayi-county`／`taitung`（113-114）；其餘 19 頁已 115-116（commit `5449609` 批次未含這 4 頁）。
2. **`market-insight.html` 停在 2025**（2025×11、2026×2，meta description「2024–2025」）；**`rental-management-news.html` 同病**（2025×7）。

### 🟡 09-04 全站改色漏網（純 CSS）
3. `article-private-to-bank.html` hero/CTA `#2d1a00` 深棕；`article-credit-repair.html` `#1a0a2e` 深紫；`article-rental-management.html` `#0a2a1a` 深綠——其餘 32 篇 article 皆海軍藍家族。
4. `evaluate.html:99` `.cta-section{background:#000}`＋舊綠光暈 `rgba(6,199,85)`／按鈕 `#048456`。
5. `taoyuan-`／`taichung-land-value-tax-guide.html` 試算 CTA 缺 `bt-btn-gold` class（台北頁有）。

### 🟡 版面
6. `xinbei-sale-leaseback.html:546-549` 相關文章第 4 卡：前 3 卡「→」打在 h3 文字內，第 4 卡改用 `.arrow::after`，被 `space-between` 推到底部。
7. `article-property-management-fees.html`／`article-debt-consolidation.html` 手機表格：`.table-wrap{overflow-x:auto}` 但 table 無 `min-width`，欄被壓到 14–28px，中文逐字換行（th 高 80–140px）。

### 🔴 站外連動
8. `article-dajiale-lottery-1980s.html` 嵌入翻舊帳 EP5（`-nfICq-MGK4`）顯示「影片擁有者已禁止在其他網站上播放」——翻舊帳上傳流程 `part=status` 未帶 `embeddable`，全頻道 31 支皆 False（09-07 會議記錄曾判「不再動」，但官網嵌入就會掛）。

## 二、設計債（需 Sir 拍板）
9. **兩套 nav 並存**：舊版 `data-include="nav"`＋`nav.html` **64 檔**（含 apply、consultation-topics、zhonghe-second-mortgage、yonghe-home-loan、大量 article-*），新版 `id="nav"`＋`nav.js` 67 檔；19 檔兩者皆無（法遵頁）。同系列在地頁使用者跳轉會看到兩種選單。
10. **免責句逐頁手寫已漂移**：「本公司為融資租賃業者，非金融機構」16 檔（含 index.html 兩處、area-*、*-property-finance、lvr-*）；「非金融機構、不放貸」20 檔；lvr-* 又是第三種。非共用 footer，無同源。

## 三、假象（不修，記入管線雷點）
- 桌機 nav 下拉全展開（10 組全報）＝截圖注入 `opacity:1!important` 把 `.cx-dd{opacity:0}` 逼出來；`aria-expanded=false`、線上 opacity 0。
- `debt-consolidation` H1「漏字」＝同上，下拉蓋住字；DOM 文字完整。
- `consultation-topics` 卡片 CTA 壓字＝`.ct-card-go{opacity:0}` 只 hover 顯示，同根因。
- `article-inherited-co-owned-house-stuck` nav 遮 h1＝fixed nav bottom 48 / h1 top 586，零重疊。
- `vacancy-cost-calculator`「00,000 元」＝里程碼動畫 0.8s 中途幀，3 秒後 `#totalLoss`=69,900。
- `rental-yield-calculator` 敏感度圖空白＝svg path 四點 y 8→58 有資料。
- `article-second-mortgage-rates` 手機截字＝table 520px 在 overflow-x:auto 內可橫滑。

## 四、管線教訓（已寫 memory）
- 殺動畫 CSS 不能用 `opacity:1!important` 全域：會把靠 opacity 隱藏的 nav 下拉、hover CTA 一起顯形，10 組全部誤報。改成只對 reveal 類 selector（`[data-reveal]`、`.gsap-*`、`.reveal`）放行，或截圖前用 JS 把 `.cx-dd`／`.ct-card-go` 設 `display:none`。
- agent 自報張數對不上，先叫它 `comm` 雙向差集，本次兩組都是加總算錯非漏讀。
