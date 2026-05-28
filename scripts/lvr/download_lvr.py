"""
從內政部「不動產成交案件實際資訊資料供應系統」下載指定季別的全國 CSV ZIP。

下載 115年第1季 (2026 Q1) + 114年第4季 (2025 Q4)，
共涵蓋 2025-10 到 2026-03 之實價登錄資料。

下載完存到 output/lvr_115S1.zip / output/lvr_114S4.zip。
"""

from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

OUT_DIR = Path(__file__).resolve().parent / "_cache"
OUT_DIR.mkdir(exist_ok=True)

URL = "https://plvr.land.moi.gov.tw/DownloadOpenData"
SEASONS = [
    "115S1",
    "114S4", "114S3", "114S2", "114S1",
    "113S4", "113S3", "113S2", "113S1",
]


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
        page.goto(URL, wait_until="networkidle", timeout=30_000)
        page.wait_for_timeout(1500)

        for season in SEASONS:
            target = OUT_DIR / f"lvr_{season}.zip"
            if target.exists():
                print(f"\n=== {season}：已存在 {target.name}，跳過 ===")
                continue
            download_season(page, season)

        browser.close()

    print(f"\n✅ 完成。檔案在 {OUT_DIR.relative_to(Path.cwd())}/")


if __name__ == "__main__":
    main()
