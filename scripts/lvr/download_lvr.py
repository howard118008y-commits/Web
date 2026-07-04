"""
從內政部「不動產成交案件實際資訊資料供應系統」下載指定季別 + 當期 mini-package。

兩階段：
1. 季別下載（非本期 tab）：113S1 ~ 115S2 共 10 季。
   已收檔的舊季「已存在則 skip」；仍在增補期的新季（季末後 FRESH_DAYS 內，
   內政部每旬會往季 zip 增補交易）即使已存在也刪掉重抓，否則資料凍結在第一次下載日。
2. 當期下載（本期 tab）：最新 10 天 mini-package，每次 action 都拉一份

mini-package 命名：lvr_mini_YYYYMMDD.zip
analyze_lvr.py 會用 編號 dedupe 處理重複交易。
"""

from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

OUT_DIR = Path(__file__).resolve().parent / "_cache"
OUT_DIR.mkdir(exist_ok=True)

URL = "https://plvr.land.moi.gov.tw/DownloadOpenData"
SEASONS = [
    "115S2", "115S1",
    "114S4", "114S3", "114S2", "114S1",
    "113S4", "113S3", "113S2", "113S1",
]

# 季末之後多少天內視為「仍在增補」（登記時滯＋公告節奏約兩個月，抓 75 天保險）
FRESH_DAYS = 75


def season_end(season: str) -> datetime:
    """民國季別（如 115S2）→ 該季最後一天（西元）"""
    year = int(season[:3]) + 1911
    month, day = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}[int(season[-1])]
    return datetime(year, month, day)


def is_fresh(season: str) -> bool:
    return (datetime.now() - season_end(season)).days < FRESH_DAYS


def download_season(page, season: str) -> Path:
    print(f"\n=== 下載 {season} ===")
    # 切到「非本期下載」tab（每次重新點，確保 state 乾淨）
    page.click("a:has-text('非本期下載')")
    page.wait_for_selector("#historySeason_id", state="visible", timeout=15_000)
    page.wait_for_timeout(800)

    # 選擇季別
    page.select_option("#historySeason_id", season)
    print(f"  → 季別：{season}")

    # 選擇 CSV 格式（非本期 tab 內的 select 跟本期共用 id）
    page.select_option("#fileFormatId", "csv")
    print("  → 格式：csv")

    # 全國 radio（預設應已選，但保險起見再勾一次）
    # 「非本期」tab 下「前季下載」的全國 radio
    page.evaluate(
        r"""() => {
          document.querySelectorAll('input[type=radio]').forEach(el => {
            if (el.offsetParent !== null && /全國/.test(el.parentElement?.innerText || '')) {
              el.checked = true;
            }
          });
        }"""
    )

    # 觸發下載：input#downloadBtnId → preDownload()
    # 用 expect_download() 攔截瀏覽器下載事件
    target = OUT_DIR / f"lvr_{season}.zip"
    try:
        with page.expect_download(timeout=60_000) as dl_info:
            page.click("#downloadBtnId")
            # 若彈出授權 modal，自動按確定
            try:
                page.wait_for_selector("#modal-confirm-confirm", state="visible", timeout=3_000)
                print("  → 偵測到 modal，按確定")
                page.click("#modal-confirm-confirm")
            except PWTimeout:
                pass  # 沒 modal，繼續
        dl = dl_info.value
        dl.save_as(str(target))
        size_mb = target.stat().st_size / 1024 / 1024
        print(f"  ✓ 已存：{target.name}（{size_mb:.1f} MB）")
        return target
    except PWTimeout:
        print(f"  ✗ {season} 下載逾時")
        raise


def download_current_period(page) -> Path:
    """下載「本期下載」tab 的最新 10 天 mini-package（全國 CSV zip）。"""
    print(f"\n=== 下載當期 mini-package ===")
    # 切回「本期下載」tab
    page.click("a:has-text('本期下載')")
    page.wait_for_selector("#fileFormatId", state="visible", timeout=15_000)
    page.wait_for_timeout(800)

    page.select_option("#fileFormatId", "csv")
    print("  → 格式：csv")

    # 本期 tab 預設選「全國」radio，保險再勾一次
    page.evaluate(
        r"""() => {
          document.querySelectorAll('input[type=radio]').forEach(el => {
            if (el.offsetParent !== null && /全國/.test(el.parentElement?.innerText || '')) {
              el.checked = true;
            }
          });
        }"""
    )

    today = datetime.now().strftime("%Y%m%d")
    target = OUT_DIR / f"lvr_mini_{today}.zip"
    if target.exists():
        print(f"  → 已存在 {target.name}（今日已抓過），跳過")
        return target

    # 找當前 visible 的 preDownload() button（本期 tab 是 <a>、非本期是 <input>）
    btns = page.locator('[onclick*="preDownload"]')
    btn_to_click = None
    for i in range(btns.count()):
        b = btns.nth(i)
        if b.is_visible():
            btn_to_click = b
            break
    if btn_to_click is None:
        print("  ⚠ 找不到 visible 下載 button，跳過 mini-package")
        return None

    try:
        with page.expect_download(timeout=60_000) as dl_info:
            btn_to_click.click()
            try:
                page.wait_for_selector("#modal-confirm-confirm", state="visible", timeout=3_000)
                print("  → 偵測到 modal，按確定")
                page.click("#modal-confirm-confirm")
            except PWTimeout:
                pass
        dl_info.value.save_as(str(target))
        size_mb = target.stat().st_size / 1024 / 1024
        print(f"  ✓ 已存：{target.name}（{size_mb:.1f} MB）")
        return target
    except PWTimeout:
        print(f"  ⚠ 當期下載逾時（季別資料已就緒，繼續）")
        return None


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 1200},
            locale="zh-TW",
            accept_downloads=True,
        )
        page = ctx.new_page()

        print(f"→ 開啟 {URL}")
        # 用 domcontentloaded 而非 networkidle：政府站 analytics 永不 idle
        # 60s timeout：CI runner 到台灣站較慢
        page.goto(URL, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_selector("#fileFormatId", state="visible", timeout=30_000)
        page.wait_for_timeout(1500)

        # 階段 1：季別下載（收檔舊季 skip；增補期新季刪掉重抓）
        for season in SEASONS:
            target = OUT_DIR / f"lvr_{season}.zip"
            fresh = is_fresh(season)
            if target.exists() and not fresh:
                print(f"\n=== {season}：已收檔，沿用 {target.name} ===")
                continue
            if target.exists():
                print(f"\n=== {season}：仍在增補期，刪除舊檔重抓 ===")
                target.unlink()
            try:
                download_season(page, season)
            except Exception as e:
                if fresh:
                    # 新季可能尚未開放下載（選單還沒有該季別）——警告後繼續，別讓整條管線掛掉
                    print(f"  ⚠ {season} 下載失敗（可能尚未開放），跳過：{e}")
                else:
                    raise

        # 階段 2：當期 mini-package（失敗不致命）
        try:
            download_current_period(page)
        except Exception as e:
            print(f"  ⚠ mini-package 階段失敗，繼續：{e}")

        browser.close()

    print(f"\n✅ 完成。檔案在 {OUT_DIR.relative_to(Path.cwd())}/")


if __name__ == "__main__":
    main()
