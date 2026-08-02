# 全站視覺目檢報告｜2026-08-03

**方法**：sitemap 115 頁，線上版（https://cx468.com.tw）Playwright 真視窗全頁截圖，桌機 1280×900 + 手機 390×844，切片成 1,700+ 張可判讀 tile，12 組 agent 逐張目檢（無抽樣）。
**機掃結果**：0 水平溢出、0 JS 錯誤、0 破圖、footer 全 115 頁到位。
**取樣腳本**：本次用臨時腳本（scratchpad/capture.py，session 結束即失效）；repo 內既有 `scripts/visual_sweep.py` 為視窗版機掃，未含切片目檢。

---

## 一、已用指令複驗＝真缺陷（可直接動手）

| # | 缺陷 | 位置（可重驗） | 複驗指令／證據 |
|---|---|---|---|
| 1 | **AVIF 檔損毀→hero 全白 420px**。瀏覽器回報 `complete:true / naturalWidth 1920`，畫面卻全白 | `img/second-mortgage-rates-hero.avif`（article-second-mortgage-rates.html） | PIL 解碼 `RuntimeError: Failed to decode frame 0: Invalid image grid`；全站 63 個 avif 逐檔測試僅此 1 檔壞。修法：用同名 .jpg（存在、線上 200）重轉 |
| 2 | **首頁 footer 曝私人 Gmail** | `index.html:1428` `jaroma1314@gmail.com ／ cx468468@gmail.com` | `grep -rn jaroma1314 --include=*.html .` 全站僅 1 命中。NAP 黃金標準只認 cx468468@gmail.com |
| 3 | **4 篇 guide 頁 logo 破版**：白底 logo 約 150px 高撐破導覽列、壓進深藍 hero（手機更嚴重，蓋住返回列） | new-taipei / taipei / taoyuan / taichung `-land-value-tax-guide.html` | 桌機截圖親眼確認（主 session 目檢，非 agent 轉述） |
| 4 | **地價稅 4 頁年度自相矛盾**：hero／警語舊年度 vs 名詞解釋 115-116 | chiayi-county(113-114)、hualien(109-110)、taitung(113-114)、yilan(107-108) | `for f in *land-value-tax.html; do grep -o "1[0-9][0-9]-1[0-9][0-9]年" $f|sort -u; done` → 20 頁中僅這 4 頁混雜 |
| 5 | **樣板變數外洩**：頁面直接印出 `{稅率}` | `purchase-cost-calculator.html:361` `契稅（房屋評定現值 × {稅率}）` | `grep -o "{[^}]\{1,12\}}"` 全站僅此 1 處 |
| 6 | **Markdown 星號外洩**：AI 摘要區印出 `**漲幅警示**`／`**跌幅警示**`／`**結構觀察**` | `lvr-observatory.html` | `grep -l "\*\*[^*]\{2,12\}\*\*" *.html` 全站僅此 1 檔 |
| 7 | **14 頁沒載 `style.css`**（系統性根因）：缺全域 `a{text-decoration:none}`、缺品牌按鈕、缺 2026-08 部署的漣漪效果 → 表現為「CTA 按鈕有底線／麵包屑藍字／表單長不一樣」 | article-property-management-fees、article-debt-consolidation、article-second-mortgage-scam、article-sale-leaseback、zhonghe/hsinchu/banqiao/xinbei-second-mortgage、xinbei-sale-leaseback、yonghe-home-loan、xinbei-debt-consolidation、article-private-loan-to-bank、article-second-mortgage-rates、en/index | sitemap 114 個本地檔逐檔 `grep -q style.css`，14 檔未命中 |
| 8 | **南投地價稅試算表少「累進差額」列** | `nantou-land-value-tax.html`（彰化有、南投無） | `grep -c 累進差額`：南投 2、彰化/苗栗 3 |
| 9 | **文案數字與版面不符**：標題「三個理由」下面排四張卡 | `rental-management-news.html` | grep 命中「三個理由，現在委託最划算。」＋截圖四張卡 |

## 二、目檢認定（agent 逐張看圖，未逐項用指令複驗）

依嚴重度排序，同類合併：

### 客戶第一眼看得到
- **首頁手機 hero 日曆卡裸奔**：「面談時段・線上預約」卡無底色，日期數字裸疊在城市照上（桌機無此元件）
- **三頁手機漢堡選單變白色實心方塊**：index / sale-leaseback / inherited-property（其餘頁正常三線）
- **五個區域頁租金長條圖 5 條 bar 全空**：area-zhonghe/yonghe/banqiao/xindian/tucheng（數值有出來、填色沒有；疑 JS 動畫未觸發，建議真機複驗）
- **手機表格逐字直排**（同一份 table CSS，一次可修多頁）：article-property-management-fees、article-foreclosure、article-loan-rejected-first-step、market-insight、financing-data、sale-leaseback、article-retirement-property、DSR 等
- **112 表格右欄被裁**、090/091 排名表主指標在畫面外

### 配圖治理（老闆偏好真人真實照片）
- **美國素材**：article-inherited-shared-ownership hero＝美國 IRS 報稅表單；knowledge.html 兩張卡＝洛杉磯迪士尼音樂廳；article-private-to-bank／article-private-loan-to-bank＝歐美古典石造建築
- **廟宇／廟會照**用於「被銀行拒貸」「繼承房子貸款」「房貸繳不出來」等金融題材（knowledge.html）
- **塑膠模型屋／娃娃屋**：article-bad-credit-loan、article-home-equity、article-inherited-sale-leaseback
- **北美豪宅客廳**：article-rental-management、article-property-management-fees
- **離題**：article-inherited-loan-seized（山林海岸）、article-sale-leaseback-safety（玻璃帷幕商辦）、xinbei-sale-leaseback（高架橋下）、yonghe-property-finance（頂樓鐵皮天台）
- **重複用圖**：knowledge.html 內 4 組圖各用兩次；article-second-mortgage-scam 與 zhonghe-second-mortgage 共用同一張 hero

### 設計系統分裂（範圍大，建議專案化）
- **兩套表單元件**：底線式＋5 張圖示選項卡（多數頁） vs 灰底框＋原生 select（article-home-equity、article-second-mortgage、hsinchu-second-mortgage、article-second-mortgage-rates）；送出鈕文案也不同（「送出，預約免費評估」vs「送出，專員主動回電」）
- **舊綠 #16A34A 殘留**：second-mortgage-calculator、affordability-calculator、mortgage-calculator、rental-yield-calculator、land-tax-calculator、evaluate、五個 area 頁時間軸
- **非品牌色系整頁**：market-insight／rental-management-news（藍）、glossary／compare-options（深藍 #093154＋寶藍 #2254C7）、land-value-tax-calculator 系列（金橘／藍色帶）、四篇 guide（深藍 hero＋亮藍 CTA）
- **CTA 模板原封貼上**：inherited-property、article-inherited-sale-leaseback 的深色區塊直接放【免費評估你的狀況】全形括號＋裸網址 `https://lin.ee/PHIfSoY`
- **emoji 當 icon**：second-mortgage、debt-consolidation、property-management、evaluate（與線稿 SVG icon 並存）
- **土黃／金棕非品牌色**：article-self-employed-loan 次要 CTA（土黃底深綠字，對比極低幾乎讀不出）、article-sale-leaseback-safety 等三頁清單勾勾

### 資料一致性（需人工判定，勿直接當 bug 修）
- **topic-a/b/c/d 快速答案數字全部與 radar-index 對不上**（房貸利率 2.322% vs 2.299%、台股 47,101 vs 43,120 等），且月/季口徑不一。建議改為與 `cx_data.json` 同源動態產生
- **topic-a 卡片標籤露出「DEMO 系列」**

## 三、已排除的假警報（勿再列為缺陷）
- `article-private-loan-credit-damage.html` 「民間借款累積到　　　　」疑似缺數字 → 線上實測 `900 萬元` 顏色 `rgb(29,29,31)`、visibility visible，**是截圖假象**
- Google 地圖區塊空白＝headless 無 API key，線上正常
- 右下角「鋮 AI」浮動鈕＝正常元件
- `#0071e3` 藍字：全站 58 檔 262 處，是既有慣用連結色，**非單頁漏套色**；要不要收斂到品牌色是老闆的決策，不是 bug

## 四、建議修補順序
1. 第一節 9 項（皆已複驗，改動小、風險低）
2. 手機表格逐字直排（一份 CSS 影響多頁）
3. 14 頁補載 style.css（要先確認不會撞頁內自訂樣式）
4. 配圖治理（走 `房屋圖片/` 真實圖庫，需老闆確認選圖）
5. 設計系統收斂（專案級，建議另開 session 立項）
