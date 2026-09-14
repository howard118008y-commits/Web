# 交接信｜cx468-web（官網 repo）＋ CX468 雲端維運

> 現況快照，不是 changelog。歷史在 `git log`。
> 最後更新：2026-09-14 15:1x（Phase 3 配色＋二胎頁撥號 CTA，本機 commit `4c50d13` **未 push，等 Sir 說「部署」**；第一節設計／電話兩列與第三節第一、二順位已改，其餘為 14:3x 版）
> 前次：2026-09-14 14:3x（矩陣 session 收工：六頁線上 200 重驗、GSC 六網址 Sir 已送）
> 前次：2026-09-14 04:xx 另一 session 的矩陣第一批（第三節 🟢，已改標為已部署）；再前次 2026-09-09。
> 本次更新原因：Sir 09-14 四項裁示落地（電話兩支為主／售後回租統一 A／企業貸款頁留但健檢在前／文字憲法放鬆改 SEO 為主）＋ 全站配色對齊主頁 Phase 1–2 上線 ＋ 09-11～13 另一 session 153 檔改動全部審過。一、三、四、五節重寫；二節與三節 🟢 保留。

## 一、當前狀態快照（2026-09-14 02:4x 重驗，每項附指令）

| 項目 | 值 | 重驗指令 |
|---|---|---|
| HEAD | 本機 `4c50d13`（Phase 3＋撥號 CTA，144 檔）＋ docs commit；**origin/main 仍在 `d1e3aa1`，未 push**。工作區另有平行 session 未提交的 `corporate-checkup.html`／`corporate-loan.html`／`img/area/*`，不是本 session 的，勿夾帶 | `cd ~/cx468-web && git status -sb && git log --oneline -8` |
| CI／Pages | 兩者 success（`65b192b`） | `gh run list -L 2` |
| 工作區 | 乾淨；唯一未追蹤 `scripts/archive/goal-scores.jsonl`（非本專案產物，**勿 add**） | `git status -s` |
| 閘門（乾淨樹） | ci_check **167 檔 0 問題**；audit-regression **18/18**；FAQ 同源 **133 頁零漂移**；JSON-LD 753 區塊 0 錯 | `python3 scripts/ci_check.py`；`NODE_PATH=<scratch>/nodedeps/node_modules node scripts/audit-regression.cjs`（需 `npm i linkedom@0.18.12`）；`python3 scripts/audit_faq_samesource.py` |
| 設計（Phase 1–3；3 在本機） | Phase 3（`4c50d13`）：`footer.html` paper 版（147 頁共用，選擇器掛 `.cx-site-footer` 非 `:where`）；新檔 `theme.css` 掛 A 族 67 頁 `</head>` 前（Sans 內文／Serif 900 標題／hero 漸層 `:has` 排除 `.art-title` 白底型／金鈕＋cream 幽靈鈕）；`style.css` body 字體、`.btn-green/.btn-line` 金、footer 區段移除；60 頁字型 link 補 Sans＋Serif 900、6 頁補 link；C 族 74 頁 `.bt-cta .bt-btn-ghost` 白底細邊；`gen_radar_v4.py` 模板掛 theme.css 並修 f-string 大括號 SyntaxError。Phase 1–2 同前 | 線上 `curl -s https://cx468.com.tw/second-mortgage.html \| grep -c 'bt-hero{background:linear-gradient'` → 1；`grep -l 'data-theme="light"' *.html \| wc -l` → 0 |
| 二胎撥號 CTA（本機） | 12 個 LINE-only 正文群組各加「撥打 02-2249-0517」（7 頁）＋ lp-zhonghe／lp-tucheng／calculator 來電鈕 0931→02；媽祖 11/11 PASS（`grep -c "tel:0222490517" second-mortgage.html` → 應 ≥4） |
| 追蹤 | `consultation-tracking.js` 掛 **60 頁**（PR#5 補 36 盲頁＋矩陣 6 頁＋radar；實數以 grep 為準）；真瀏覽器實測 glossary／中和售後回租／台北地價稅點 sticky CTA → `line_click`＋`phone_click` 進 dataLayer | `grep -l consultation-tracking.js *.html \| wc -l`；`python3 scripts/ci_check.py` 內建 check_conversion_tracking |
| 電話（Sir 09-14 定） | 02-2249-0517 主 ＋ **0958-139-786 經理鄭小姐**；contact 可見×5＋FAQ schema；footer 兩支；**60 頁** Organization contactPoint = [02, 0958]（含矩陣 6 新頁）；0931 降為工作機／LINE ID | `curl -s https://cx468.com.tw/contact.html \| grep -o 經理鄭小姐 \| wc -l` → 5；`grep -l '+886-958-139-786","contactType' *.html \| wc -l` → 56 |
| 售後回租定義 | 全站統一 A 版「並可保有日後依約買回的權利」；「買回權利須另行約定」型改寫 0 | `grep -l '買回權利[須需]另行約定' *.html \| wc -l` → 0 |
| 企業線 | `corporate-loan.html` 保留（index/follow、nav 群組「企業貸款」），首段＋meta 寫明「先做公司財務健檢，健檢看完即使資歷不足也協助媒合企業貸款」；nav 群組健檢排第一 | `curl -s https://cx468.com.tw/corporate-loan.html \| grep -c 先做公司財務健檢` → 2 |
| 「20 年」主詞 | 全站團隊（`cfd7061` 09-09 91 檔）；p2a 模板／小鋮提示詞亦改（跨 repo，見下） | 全站無主詞殘留掃描 0（腳本在 `scripts/fix_20year_subject.py`，冪等） |
| p2a 日更 | Render `cx468-p2a-publish` live `138ab9b`；09-13 已產 `article-inherited-house-sell-or-keep.html`；模板已改掛 nav.js、org schema 主詞團隊、contactPoint 0958 | `git -C ~/cx468-fb-news-bot log --oneline -2`；`gh api repos/howard118008y-commits/Web/commits?path=article-inherited-house-sell-or-keep.html` |
| linebot／ga4-daily | Render live `37ed7f6`（小鋮提示詞）／`a74f06c`（09-03 卡在本機的健檢修正已推） | Render API `services/*/deploys?limit=1` |
| 三日健檢 | **有推 🔴 到 Telegram**（09-05／08／11 三次列 p2a 停擺）——告警沒壞，是沒人接。09-09「掛 7 天沒人知道」為誤判 | `grep -n "Telegram 已推" ~/cx468-ga4-daily/logs/healthcheck.out \| tail -3` |
| 廣告 | Meta 2 campaign ACTIVE；近 7 天 NT$3,666、11 名單；GA4 -72% 是花費由 8,540 降到 3,666，非追蹤壞 | `~/.cx468/meta_ads_cli.py`／insights `date_preset=last_7d` |
| Threads | Render token 有效、每日 12:30 準時發；**本機 `~/.cx468/threads_token.txt` 是過期舊檔**，拿它測會誤判壞掉 | Render env `THREADS_ACCESS_TOKEN` 打 `graph.threads.net/v1.0/me` |

⚠️ **三個路徑陷阱**（不變）：
1. 網站程式碼在 `~/cx468-web/`，**不在 iCloud 專案夾**；`行銷產出/`、`知識庫/`、`制度/` 在 iCloud 專案夾。
2. LINE bot 查驗一律用 `~/cx468-linebot`。
3. 本機測試會掃到**別的 session 的未追蹤檔**（本 session 兩次被弄紅）：閘門一律跑在只含已追蹤檔的樹上——`git ls-files -z | rsync -aq --from0 --files-from=- ./ $T/`（非 ASCII 檔名必須 -z/--from0）。

🚨 **commit 配方**：pre-commit hook 會把工作樹所有已修改 html 掃進你的 commit（`.git/hooks/pre-commit:30`）。平行 session 施工中要用 `git add <自己的檔> && git commit --no-verify` → 跑 `update_schema_datemod.py`＋`update_sitemap_lastmod.py` → `--amend --no-verify`。單人時 `git add -u` 即可，但先 `git status -s` 確認 M 全是自己的。**所有 repo 禁 `git add -A`。**

## 二、可複用資產／程序（8/29 版保留＋9/5 更新）

### 🆕 Better 對拷專案的入口（9/4 建立，9/5 更新）

- **拆解報告**：iCloud `行銷產出/策略簡報/2026-09-04-better.com官網拆解.md`（§3 逐頁 section 表、§5 色碼/字級/按鈕/卡片/間距實測、§8 不能照抄的 11 條）。143 張截圖在 `行銷產出/視覺風格/better.com-2026-09-04/`。
- **範本正本**＝`sale-leaseback.html`。變體：debt-consolidation（表格）／corporate-checkup（表單／五步驟）／services（總覽交錯列）／xinbei-sale-leaseback（文章型 h2 映射）／**area-xindian（在地頁：SVG 位置圖＋地圖 iframe＋實價登錄深藍帶＋租金長條圖＋時程＋POI 卡格，五頁段落配色以它為基準）**／**taipei-land-value-tax-guide（長文教學型：級距表 bt-table、範例卡、bt-dark-card 金鈕 CTA）**／**new-taipei-land-value-tax（試算器型：試算器整段原樣進白底 section、JS 零改動；必留三行 CSS 見批次規格）**。
- **nav.js**：淺色 `<div id="nav" data-theme="light"></div>`＋`<script src="nav.js"></script>`，body padding-top 64/58；不帶屬性＝深色。**`data-cta="line"`＝二胎合規模式**（兩顆免費評估鈕改 LINE）。不載 style.css；**不要改 style.css 的 nav 選擇器**。
- **派工規格**（iCloud `行銷產出/技術記錄/`）：
  - `2026-09-05-better版型派工共用規格.md`（硬規則 9 條＋自驗＋回報格式；9/5 已改為「hero 圖／眉標由 prompt 逐頁指定」＋規則 9「script／iframe 全留」）
  - `2026-09-05-地價稅試算器頁批次規格.md`（試算器型專用：script diff 指令、id 計數、handler 集合）
  - `2026-09-05-小工具頁批次規格.md`（第八批：段落→版型對照表＋自驗；主對話另有 scratchpad `calc_verify.py` 思路＝HEAD 版與新版起兩個 http.server、填同值比所有帶數字 id 的文字）
  - ⚠️ **生成頁陷阱**：lvr-observatory／lvr-presale／lvr-rental 由 `scripts/lvr/build_*.py` 產，`.github/workflows/lvr-weekly.yml` 每月 2/12/22 重跑會整頁覆寫；三頁模板 9/5 皆已移植（`LVR_HTML_DEST`／`LVR_PRESALE_DEST`／`LVR_RENTAL_DEST` 可覆寫，本機驗法：`_cache/` 用 `lvr-data/*.json` 建 stub、重生成 diff 只剩時間戳）。**cx_radar_v4_demo.html 也是生成頁**（indicators workflow 每日改寫），不套版。
  - 派系列頁時 prompt 直接給「段落→底色／卡片／寬度」對照表（第四批 5 頁曾各走各的，並排目檢才發現；memory `feedback_parallel_agents_same_choice`）
- **驗收腳本**（同夾；⚠️ `<page>` 一律**不帶 .html**，9/5 起帶了也會自動去掉）：`pw_check.py <base_url> <page>…`（sw/h1/nav 底色/眉標/styleCss/console）；`slices.py <out_dir> <page>…`（本機 :8765 桌機 2400px／手機 3200px 切片截圖，主對話 Read 目檢）；`lvt_verify.py <page>…`（試算器頁：與 HEAD 版填同樣數字比對輸出、手機 scrollWidth、<16px 輸入框數）；`scripts/verify_text_conservation.py <file>`（守恆）。
- **本機目檢**：`cd ~/cx468-web && python3 -m http.server 8765`，Playwright venv `~/pw/bin/python`。Google Maps iframe 在 localhost 回 403（金鑰限 cx468 網域）＝正常，線上不會；LINE QR 在 full-page 截圖裡空白＝lazy 未觸發，非壞圖。
- Token 對照（Better → 鋮馨）：頁底 #F7F5F0、卡片白、次底 #F2EFE8、深帶 #1B2F4A、主 CTA #2F5B8F（hover #26497A）、header CTA 金 #C8945A、眉標 #9A6D3A、文字 #1B2F4A／#5A6878、邊線 #E2DED4、淡藍帶 #EEF2F7；全頁 Noto Sans TC；CTA 64px 圓角 8px；卡片 8px＋shadow-md；section 64/80/96。

### 🆕 本機預覽與真回覆測試（8/29 建立）

```bash
cd ~/cx468-web && python3 -m http.server 8931
cd ~/cx468-linebot && ANTHROPIC_API_KEY="$(cat ~/.cx468/anthropic.key)" PORT=5001 .venv/bin/python app.py
```
chat-widget 只在 `localhost`／`127.0.0.1` 打 :5001，其餘打 Render 正式站。`/chat` 收 `{"messages":[{"role":"user","content":"…"}]}`，**不是** `{"message":"…"}`。

### 🆕 headless 目檢管線（8/29 建立，playwright MCP 被佔時的備援）

```bash
CH="$HOME/Library/Caches/ms-playwright/chromium-1234/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
"$CH" --headless=new --disable-gpu --no-sandbox --remote-debugging-port=9333 --user-data-dir=/tmp/cdpX --window-size=1440,900 about:blank &
```
三個雷（memory `feedback_cdp_screenshot_traps`）：setDeviceMetricsOverride＋截圖會 hang；`/json/new` 可能拍到別的分頁；反詐 modal 先 `localStorage.setItem('cx_antifraud_v1', String(Date.now()))`。

### 🧩 ai-bar.html（8/29）

`<div data-include="ai-bar" data-ai-q="問題一？|問題二？|問題三？"></div>`；顏色自動讀 h1；🔴 元件內用 `document.querySelector('[data-include="ai-bar"]')` 取屬性，**不能用 `currentScript.closest()`**。

### 🔑 Meta 權杖（永不過期）

`~/.cx468/fb_system_user.token`（廣告）／`~/.cx468/fb_page_system.token`（粉專）。
```bash
T=$(cat ~/.cx468/fb_system_user.token)
curl -sG "https://graph.facebook.com/v21.0/act_1693554028195795/insights" --data-urlencode "access_token=$T" --data-urlencode "level=campaign" --data-urlencode "fields=campaign_name,spend,impressions,inline_link_clicks,ctr,frequency" --data-urlencode "date_preset=today"
```

### Google Ads 查法（無 API 金鑰，用指令碼）

後台 → 工具 → 大量操作 → 指令碼：`CX468-設定稽核`、`CX468-地區解碼`（原始碼在 `行銷產出/Google廣告/`）。🔴 新北市 `1012825`、臺北市 `9040379`；出現 `2158` 或 Country ＝鎖到全國。**「查看頁」會假顯示，一律以指令碼／API 為準。**

### GA4

`~/cx468-ga4-daily/cx468-ga4-945f85bddfbd.json`，資源 `535643191`。付費流量判讀對照：`inherit-era-img3` 平均參與 1.0 秒、跳出 92.3%＝誤觸；Google 搜尋 13.1 秒、自然搜尋 30.4 秒。

### 📞 回電 SOP

`行銷產出/LINE/2026-08-14-以房養老來電三句話SOP-FINAL.md` v2。四道閘門：①身分切割 ②「我幫你問問看銀行」禁語 ③轉場售後回租四條件全中 ④**弱勢否決凌駕**。

### 期限型任務登記表

`~/.cx468/pending_reviews.json` → 三日健檢檢查4 自動倒數，逾期推 Telegram。**有硬截止又沒系統在盯的任務一律登記。**

## 三、未竟任務

### 🟢 2026-09-14 矩陣擴張第一批（服務軸 6 頁）——**已部署**（另一 session 推 `89d002f` 09-14 14:08，線上 200）

**Sir 09-14 拍板**：矩陣「全做」，順序 ①服務軸 → ③企業健檢 → ②地區軸二胎複製。本批＝①的三條新系列首篇＋售後回租擴 3 支。

| 頁 | 系列 | 骨架（反 doorway 各不同構） | 媽祖 |
|---|---|---|---|
| `yonghe-sale-leaseback.html` | 售後回租擴 | 時間軸：房老→人老→三種處境→估價限制→都更等待 | ✅ |
| `banqiao-sale-leaseback.html` | 售後回租擴 | 三欄屋主對照：舊城老公寓／新板·江翠大樓／浮洲 | ✅ |
| `sanchong-sale-leaseback.html` | 售後回租擴 | 兩張地圖（水／重建）→ 2×2 落格 | ✅（hero 用 `img/gen-sanchong.jpg` AI 圖＋「情境示意圖」，Sir 未裁是否換實景） |
| `banqiao-debt-consolidation.html` | 貸款整合**首篇** | 一個月的扣款日曆 | ✅（一次過） |
| `zhonghe-private-to-bank.html` | 民間轉銀行**首篇** | 帳本兩欄（左：付出去的／右：本金還剩） | ✅ |
| `zhonghe-corporate-checkup.html` | 企業健檢＋媒合**首篇** | 三份文件 × 三種中和公司 | ✅ |

**部署配方**（已執行；留作下一批範本）：`python3 <scratchpad>/deploy_matrix_batch1.py`（sitemap 六筆、llms.txt 六行、`sale-leaseback / debt-consolidation / private-to-bank` 三樞紐 chips 反向內鏈；每步 assert，已乾跑）→ `python3 scripts/ci_check.py` → `git add` 指名 11 檔（6 新頁＋sitemap.xml＋llms.txt＋3 樞紐）→ `git fetch && git rebase origin/main` → push → curl 六頁 200 → 給 Sir GSC 清單：
`https://cx468.com.tw/{yonghe,banqiao,sanchong}-sale-leaseback.html`、`https://cx468.com.tw/banqiao-debt-consolidation.html`、`https://cx468.com.tw/zhonghe-private-to-bank.html`、`https://cx468.com.tw/zhonghe-corporate-checkup.html`。

**素材正本**：`行銷產出/技術記錄/2026-09-09-矩陣擴張素材包.md` v5.1（永和／板橋／三重／中和／板橋整合，全官方出處＋不可寫清單；後續各區擴頁只准用這裡的數字）。

**本批立下的定例（已寫 memory `project_local_page_series_rules`）**：合規脊椎句豁免相似度但子段要量；同系列共用 FAQ 題只留一頁；「不是投資方」禁寫（老闆 07-06 鋮馨會自任承買方）；官方引句內「約」可留、引句外去「約」成確數＝失真；⭐示意例不代入成數／利率／核貸機率；⭐兩機關兩期別不合成一句；⭐隱私／保存期只准逐字抄主頁（企業頁「180 天自動清除」被退，正本「結案後 6 個月內刪除」）；貸款類頁「最低」零出現不開白名單；FAQ 標題禁裸詞（rich result 會摘）；通用型 FAQ 每頁上限三題。

**追蹤**：六頁都掛 `consultation-tracking.js`（不用舊 inline 監聽，避免雙重上報），CTA 帶 `data-link-location`；貸款類三頁 `.bt-btns` 掛 `data-consultation-need`（private_debt／private_to_bank／corporate_loan），`pageNeeds` 表不必改。

**待辦（本批順帶發現，未動）**：
1. 三頁行情「自行統計」口徑不一（永和／板橋用 09-09 篩法、三重用 09-14 篩法）→ 三重頁已加口徑註先上；關公用 4G 口徑重跑永和、板橋表後統一。
2. `yonghe/banqiao/sanchong-property-finance.html` 兩兩 88–91% 同構（媽祖：真 doorway 風險是這三支舊頁，不是新頁）→ 重寫差異化，另開 session。
3. `b386ad9` 換深藍 hero 後 `.bt-meta`（日期／作者／閱讀時間列）對比 2.2:1，26 頁含 xindian 全站模板問題 → 設計線修 `.bt-hero .bt-meta` 色。
4. 企業兩樞紐 `corporate-checkup.html`／`corporate-loan.html` 無任何站內連結區（廣告落地頁式）→ 加 chips 區才能反向連在地頁。
5. 93 頁 LocalBusiness schema geo `24.9944,121.4900` vs 65 頁 meta geo `25.0070;121.4912` 兩組座標並存 → 關公實查中正路 468 號座標後全站統一；schema areaServed 缺三重。
6. 下一批：企業健檢擴 5 區（板橋／三重／新莊／土城／永和；素材包 §5H/5J 方法照抄，各區工業區／工廠數要重查）→ 服務軸補滿 → 最後地區軸二胎複製（風險最高、Sir 排第三）。

**雷（本批踩到）**：研究型 agent「等工兵回報再彙整」＝零交付結束（三次），派工單尾固定加「查到多少先交多少」；平行 session 在建造中途推 `b386ad9` 換皮 138 檔，新頁抄舊 `<style>`＋`data-theme="light"` 會白 nav 壓深藍 hero——動手前 `git log -1` 看有沒有換皮 commit；建造者自驗相似度與媽祖複量差一倍（25.9% vs 48.3%），派工單數字現場量。

### 🟢 2026-09-14 矩陣第二批：企業健檢擴 5 區＋樞紐 chips（待辦 #4、#6）——**已部署**（`07f9a42`，Sir 15:5x 令部署；五頁線上 200、樞紐 chips／sitemap 7／llms 7 已驗、TG 已推；**GSC 五網址等 Sir 送**；上線 24h 內 `git log -1 -- *-corporate-checkup.html` 看誰動過）

| 頁 | 骨架（與首篇「三份文件×三種公司」及彼此互不同構） | 媽祖 |
|---|---|---|
| `banqiao-corporate-checkup.html` | 一筆工程款走五站（訂金→期中／保留款→發票時點→入帳／下包→營所稅） | ✅ 2 處小改已修 |
| `sanchong-corporate-checkup.html` | 健檢報告的五個燈號，各配「三重誰最常亮」 | ✅ 4 處已修 |
| `xinzhuang-corporate-checkup.html` | 退件通知倒推：說法→原因→文件→送件前 30 天 | ✅ 2 處已修 |
| `tucheng-corporate-checkup.html` | 整頁只談集中度（一家大客戶佔幾成） | ✅ 2 處已修 |
| `yonghe-corporate-checkup.html` | 沒有 401 表的公司（小規模營業人／查定課徵軌） | ✅ 一次過 |

**同 commit**：`corporate-checkup.html`／`corporate-loan.html` 加 `.bt-local` chips 區（待辦 #4）；三樞紐（含 zhonghe 首篇）chips 反向連 5 新頁；sitemap +5、llms.txt +5；`img/area/sanchong.jpg`（新北大都會公園）、`xinzhuang.jpg`（副都心）Commons 照＋credits。
**素材**：素材包升 **v5.2 §7** 指向同夾四檔 `2026-09-14-企業健檢五區素材-{A稅籍與統計,B三重新莊工業,C板橋土城永和工業,D普查110}.md`；媽祖報告 `2026-09-14-企業健檢五區媽祖把關.md`。五頁 584 個數字媽祖全回溯。
**驗收**：ci_check 172 檔 0；FAQ 同源 138/138；六頁兩兩 difflib 22–30%、section 零命中、FAQ 只剩隱私脊椎句（媽祖裁豁免，機掃要改「先剝脊椎句再比」）；本機 8 頁 200；桌機 hero 目檢 5 頁、手機 390 無整頁橫捲。
**部署配方**：push 後 curl 五頁 200 → 給 Sir GSC 清單 `https://cx468.com.tw/{banqiao,sanchong,xinzhuang,tucheng,yonghe}-corporate-checkup.html` → 三日健檢看 coverageState。已連同 `4c50d13`（Phase 3 配色 144 檔）一起上線。
**順帶發現、未動**：①首篇＋09-14 六頁 FAQ「＋」雙加號（`.plus::before` 與 literal ＋並存，b386ad9 帶進）→ 一支 sed；②企業系列 6 頁都不掛 ai-bar（樞紐有）→ Sir 裁要不要全系列補；③LocalBusiness schema `areaServed` 缺三重／新莊／土城（待辦 #5 同批）；④媽祖 §7.5 地標已補登素材包 §7；⑤研究型 agent 仍會「等工兵回報」結束，一催即交（memory 已有）；⑥新 memory `feedback_template_bugs_copied_by_builders`。

### 🟢 Phase 3 已做（`4c50d13` 本機，待 Sir 說「部署」才 push）

做了什麼見第一節「設計」列。**push 後要驗**：`curl -s https://cx468.com.tw/theme.css | head -c 80`（200 且有內容）、`curl -s https://cx468.com.tw/about.html | grep -c theme.css` → 1、無痕開 about／article-second-mortgage／apply／bad-credit-mortgage 看 footer paper 底與金鈕；然後給 Sir GSC 清單（11 個電話 CTA 頁優先，A 族零文字頁不必送）。
**沒做／順帶發現**：①首頁 `index.html` 自帶 footer 仍列 0931（非 0958 經理鄭小姐）——首頁是 Sir 親審版，未動，等他裁；②全站 40 頁正文仍有「0931-087-996」可見（政策是降次要不是刪，未動）；③`.art-tag` 藍色膠囊（9 頁白底文章）沒改，與主頁不衝突。

### ~~🔴 第一順位：全站配色對齊主頁 Phase 3~~（已做，原規劃留檔）

現況差距在 **A 族 59 頁**（載 style.css 的文章／apply 等）與 **144 頁共用的 footer.html**：nav 已深、但內文仍系統字體、標題 600、CTA LINE 綠、頁尾舊版深藍。分析員估 6–7 小時，零文字變動、不過媽祖。

依序：
1. **footer.html 改主頁 paper 版**（一檔通吃 144 頁，最高槓桿）。主頁自帶 `.foot`（paper 底、ink 字、4 欄、Serif h4）——抄它的結構與 CSS 進 footer.html，**保留** sticky CTA、`data-link-location`、noindex meta、兩支電話。改完先目檢 10 頁再全站。
2. **style.css**：body 字體 系統→`'Noto Sans TC',…`；`.btn-green/.btn-line` LINE 綠→金；51 頁 fonts link 只載 Serif 要加 Sans（sed）。
3. **theme.css 覆寫層**：A 族內聯 `<style>` 全在 style.css 之後，同特異性蓋不過——在 `</head>` 前加一支 `theme.css`（`.art-hero h1{font-weight:900}`、`.page-hero` 深藍改森林藍漸層等）。
4. 生成頁（`cx_radar_v4_demo`／`radar-index`／`lvr-*`）改模板不改產物（memory `feedback_generated_pages_overwritten_by_workflow`）。

**工具與閘門**（本 session 驗過）：換皮腳本邏輯在 memory `project_homepage_green_rebuild`（`scratchpad/phase2.py` 已隨 session 消失，照 memory 重寫 10 分鐘）；零文字閘門 `python3 scripts/check_text_integrity.py . $(git diff --name-only -- '*.html')`（zsh 要 `$(...)` 才斷詞）；staging：`python3 -m http.server 8765` 在乾淨樹上跑，playwright 截 `second-mortgage／contact／about／article-second-mortgage／apply` 桌機＋手機看過再推。
**雷**：ai-bar 膠囊等 include 注入的樣式會蓋掉同特異性規則，覆寫要 `.bt-hero .aib .aib-chips button{…!important}`；矩陣 🟢 待辦 #3 的 `.bt-meta` 深底對比 2.2:1 也在這批一起修。

### 🔴 第二順位：讓 SEO 生出「打電話進來的客戶」（Sir 09-09 定調，狀態更新）

| 段 | 09-09 | 09-14 現況 |
|---|---|---|
| 量得到 | 10 頁沒 `phone_click` | ✅ **PR#5 已補 36 盲頁**，真瀏覽器驗過事件進 GA4 |
| 按撥號 | 電話被 LINE 蓋過 | ✅ `4c50d13`：12 群組加「撥打 02-2249-0517」＋3 頁 0931→02，媽祖 PASS（本機，待 push） |
| Local Pack | GMB 1 則評論 | 🔴 未動，只有 Sir 能做（第四節 #8） |
| 量表現 | 三支新頁等 2–4 週 | 09-09 上線至今 5 天，還不能判；`~/cx468-ga4-daily/gsc.py`＋GA4 `phone_click` 依 landing page |
| 台北 12 區 | 不建議 | 不變 |

**接手前必讀禁忌**（不變）：當舖鉤子詞 14 類全禁；二胎場景禁「免費評估」；在地頁走反 doorway 定例（memory `project_local_page_series_rules`）；`lvr-data/雙北全區排名_近180天.csv` 停更 05-29，當期正本 `排名_w180.json`；DeerFlow 派工要拆小段＋`recursion_limit`。

### 🟡 順帶發現、未動（Sir 裁或另案）

1. **90 頁 GA config 沒濾 query/fragment**（只有掛追蹤器的 60 頁有濾）——隱私與 analytics 乾淨度，一支 sed 可解，但要目檢 GA 沒斷。
2. 矩陣 🟢 待辦 #1–#6（口徑統一／三支 property-finance 同構 88–91%／`.bt-meta` 對比／企業兩樞紐無 chips／geo 座標兩組並存／企業健檢擴 5 區）。
3. 「成數最高 9 成」未說明一二胎合計（09-09 媽祖提，全站 9 處同型）。
4. nav.js 的 `data-cta="line"` LINE 變體已被 5c66121 拿掉，`ctaLine` 成死變數、L122 註解過時（講一聲，未動）。
5. `codex/verify-live-20260911` 分支殘留 1 個 commit（純驗證腳本），可刪。
6. lvr 圖表 PNG 與社群圖卡仍紅系（`scripts/lvr/make_charts.py`／`make_social_cards.py`）。
7. `land-value-tax-calculator.html`「其他縣市陸續建置中」已過時（需媽祖）；`affordability-calculator` 無免責尾注。
8. linebot：隱藏號碼來電逐通建新 person 灌漏斗（`crm_calls.py:119-125`）；`privacy-policy.html §6` 沒提電話管道。

### 日常常態

- 每天 12:00 精進會議（session 級排程，每個 session 用 CronCreate 重設）。
- 三日健檢 `com.cx468.healthcheck` 會推 🔴 到 Telegram——**收到要有人接**（memory `feedback_act_on_telegram_alerts`）；09-08 那則還躺著「Meta spend_cap 決策逾期」「週報監控瞎了」等 4 條。
- Threads 12:30；p2a 17:15（敏感稿要人回 GO，memory `feedback_human_go_gate_deadlocks_pipeline`）；`cx468-crawl` 每 2 小時。
- 換新聞卡前 `git log --oneline -5 -- radar-index.html` 算服役天數。

## 四、等使用者的事項

1. 🔴 **GMB 評論 1→20**（第二順位③，只有 Sir 能做）：「新北 房屋二胎」Local Pack 第 1 名 17 則、第 2/3 名 0 則照樣上榜。⛔ 商家名不塞關鍵字、類別維持「不動產管理服務」。
2. 🔴 **Telegram 三日健檢的 🔴 要有人接**：09-08 推播列了「Meta spend_cap 決策逾期 18 天」「行銷週報檢查失效（launchd 無 iCloud 權限）」「銀行條文存證複查」——本 session 只修了 p2a 那條。
3. **GSC 催收**：`docs/2026-09-09-GSC待送清單-額度滿順延.txt`（12＋6 條，09-14 已追加 contact／corporate-loan／sale-leaseback-guide 等）；矩陣 6 頁清單在第三節 🟢——**Sir 09-14 14:2x 已逐一送「網址審查→要求建立索引」**，下一步是三日健檢看 coverageState＋lastCrawlTime（memory `feedback_indexed_but_stale_crawl`），別再重送。Sitemap 欄只放 sitemap.xml。
4. **Anthropic 帳務**：auto-reload 未開、無 Admin key、9 服務共用一把 key（09-08 起未變）。
5. **配圖要不要換真人照片**：三重／新莊／三重售後回租用 AI 生成圖（memory `project_photo_library`：老闆偏好真人）。未擋上線。
6. **`cx468-crawl` 一天 12 次要不要降頻**（不花 API 錢，只違「一天不超過三次」原則）。
7. **PR#5 之外的 GA4 事件設定**：`phone_click`／`line_click` 在 GA4 是否已標關鍵事件、landing page 維度切得出來（memory `feedback_ga4_import_needs_conversion_category`）——站上發得出，後台我看不到。
8. 名單回電 SOP、合一地政士洽談、企業貸款專案三處不一致（8/14 起未變）。
9. ~~0958 上不上官網~~ ✅ 09-14 定：上，稱「經理鄭小姐」。~~企業貸款頁留不留~~ ✅ 留，健檢在前。~~售後回租兩套定義~~ ✅ 統一 A。~~「20 年」主詞~~ ✅ 全站＋跨 repo 已改。

## 五、本 session（2026-09-14 00:48 → 02:4x）做了什麼

### 5-1 審 09-11～13 另一 session 的 153 檔（4 個審查員＋自己重算）
PR#3／#4 合併內容全審：合規禁語全是闢謠語境、FAQ 同源 127/127、內鏈 0 斷、隱私乾淨、linebot 電話進線零紅字（18 測試過）。抓到的真問題：**PR#5（36 頁追蹤斷掉）沒合併**、0958 私人手機上了 contact 可見面＋schema、`corporate-loan.html` 撞 08-24 令、第七節逐字句被改寫兩套定義並存、「39 家合作」→「曾送件」76 檔無記錄。Sir 的裁示把後四項變成政策（見四節 #9）。

### 5-2 落地四項裁示（`c919489`）＋合併 PR#5（`41763c8`）
細節見第一節表。跨 repo：fb-news-bot `138ab9b`（p2a 模板 nav.js、org schema 主詞／電話）、linebot `37ed7f6`（小鋮提示詞）、ga4-daily 推出卡了 11 天的 `a74f06c`。CLAUDE.md 第一／二／七節同步改。

### 5-3 全站配色對齊主頁 Phase 1–2（`b386ad9`，134 檔，零文字變動）
三族量化→staging 截圖→Sir 看過→推。Phase 3 見三節第一順位。

### 5-4 CI 修（`65b192b`）
`cx_radar_v4_demo.html` 每日重生蓋掉 PR#5 的追蹤器 → 改 `gen_radar_v4.py` 模板；矩陣 6 新頁 GA config 去參數。

### 5-5 更正自己 09-09 的一句話
「p2a 掛 7 天沒人知道」錯——三日健檢 09-05／08／11 三次都推了 🔴 到 Telegram。監控沒瞎，是告警沒人接。

### 5-6 新寫 memory
`feedback_constitution_wording_loosened_seo_first`（文字放鬆·SEO 為主）、`feedback_parallel_session_moves_head_mid_diagnosis` 追加（別人未追蹤檔弄紅本機測試→乾淨樹閘門）、`project_homepage_green_rebuild` 追加（換皮 token／Phase 3 清單）、`reference_nap_canonical`／`project_corporate_checkup` 更新。

## 六、本 session（2026-09-14 14:3x → 15:1x）做了什麼

Sir 指令「1＋2」＝Phase 3 配色＋二胎頁撥號 CTA。兩件都做完、閘門全綠、**本機 commit `4c50d13` 未 push**。
- Phase 3：見第一節「設計」列。目檢：乾淨樹 staging 桌機 1280／手機 390，footer 8 頁、hero＋CTA 16 頁（截圖在 session scratchpad，已隨 session 消失；重拍照第二節 headless 管線）。
- 撥號 CTA：偵察 agent 普查 17 頁 → 12 個 LINE-only 群組；媽祖 11/11 PASS。
- 順手修：`gen_radar_v4.py` 在 `65b192b` 被貼進未雙寫大括號的 JS 物件 → f-string SyntaxError，隔天 `update_indicators` 排程會炸；已修並重生產物（diff 只剩 head 兩行＋時間戳）。memory `feedback_python_compat_silent_failure` 追加一段。
- 平行 session 雷再踩一次：工作區有別人的 `corporate-*.html`／`img/area/*` 未提交；本 session 用 `git add <指名檔> && git commit --no-verify` → 跑兩支鮮度腳本 → 只 re-add 自己 commit 過的檔 → `--amend`。配方有效，照抄。
