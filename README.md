# 鋮馨租賃有限公司 · 官方網站

不動產售後回租 · 民間轉銀行貸款 · 包租代管 · 服務新北萬華．全台據點

## 公司資訊

- **地址**：新北市中和區中正路 468 號
- **聯絡電話**：02-2249-0517 ／ 0931-087-996
- **官方網站**：[cx468.com.tw](https://cx468.com.tw)
- **LINE 官方帳號**：[加入好友](https://lin.ee/PHIfSoY)

## 網站頁面

### 主要頁面

| 頁面 | 內容 |
| --- | --- |
| `index.html` | 首頁（Hero + 三大服務 + 客戶見證 + CTA） |
| `about.html` | 關於鋮馨（公司沿革 + 經營理念 + 團隊介紹） |
| `services.html` | 服務總覽（售後回租 + 貸款整合 + 包租代管） |
| `evaluate.html` | 免費評估表單 |
| `contact.html` | 聯絡我們（地圖 + 交通 + 表單） |
| `faq.html` | 常見問題 |

### 服務專頁

| 頁面 | 內容 |
| --- | --- |
| `sale-leaseback.html` | 不動產售後回租 |
| `private-to-bank.html` | 民間轉銀行貸款 |
| `loan-process.html` | 貸款整合流程 |
| `rental-management-news.html` | 包租代管動態 |

### 知識中心

| 頁面 | 內容 |
| --- | --- |
| `knowledge.html` | 知識專欄總覽 |
| `market-insight.html` | 房市觀察 |
| `article-bank-audit.html` | 銀行徵信全攻略 |
| `article-credit-repair.html` | 信用修復指南 |
| `article-home-equity.html` | 房屋淨值貸款 |
| `article-loan-integration.html` | 貸款整合解析 |
| `article-private-to-bank.html` | 民間轉銀行實務 |
| `article-rental-management.html` | 包租代管入門 |
| `article-sale-leaseback-guide.html` | 售後回租完整指南 |
| `article-second-mortgage.html` | 二胎房貸介紹 |

### 免費試算工具（7 個）

| 頁面 | 內容 |
| --- | --- |
| `tools.html` | 工具總覽 |
| `mortgage-calculator.html` | 房貸試算表 |
| `affordability-calculator.html` | 貸款負擔能力試算 |
| `rental-yield-calculator.html` | 租金報酬試算 |
| `purchase-cost-calculator.html` | 購屋總費用試算 |
| `land-tax-calculator.html` | 土地增值稅試算 |
| `realestate-tax-calculator.html` | 房地合一稅試算 |
| `vacancy-cost-calculator.html` | 空屋成本試算 |

## 技術說明

- 純 HTML / CSS / JavaScript · 無框架
- RWD 響應式 · 支援桌面、平板、手機
- 全站靜態頁 · 適合 GitHub Pages、Cloudflare Pages 部署
- SEO 優化 · 內含 `sitemap.xml`、`robots.txt`、Google Site Verification
- 自訂網域：`cx468.com.tw`（透過 `CNAME` 設定）

## 本地預覽

```bash
# 方法 1：Python 內建伺服器
python3 -m http.server 8000

# 方法 2：Node.js（需先安裝 http-server）
npx http-server -p 8000
```

開啟瀏覽器前往 `http://localhost:8000` 即可預覽。

## 部署

本專案為靜態網站，可直接推送至下列服務：

- **GitHub Pages**：`Settings → Pages → Source` 選擇 `main` 分支根目錄
- **Cloudflare Pages**：連結 GitHub 倉庫，Build command 留空，Output directory 設為 `/`
- **Netlify**：拖曳整個資料夾即可部署

## 檔案結構

```
CX468/
├── index.html              # 首頁
├── about.html              # 關於我們
├── services.html           # 服務總覽
├── tools.html              # 試算工具總覽
├── knowledge.html          # 知識專欄
├── faq.html                # 常見問題
├── contact.html            # 聯絡我們
├── evaluate.html           # 免費評估
├── nav.html / footer.html  # 共用導覽列與頁尾
├── include.js              # 動態載入 nav / footer
├── style.css               # 全站樣式
├── article-*.html          # 知識文章
├── *-calculator.html       # 試算工具
├── img/                    # 圖片資源
├── favicon-*.png           # 網站圖示
├── sitemap.xml             # 網站地圖
├── robots.txt              # 爬蟲規則
└── CNAME                   # 自訂網域設定
```

## 版權

Copyright © 2026 鋮馨租賃有限公司 · 版權所有
