"""
抓 5 精選區的地標形象照（Wikimedia Commons，CC 授權）→ img/area/<slug>.jpg
並把出處／作者／授權寫進 img/area/credits.json，供 build_area_pages.py 標註。

執行：python3 scripts/fetch_area_photos.py
來源皆為 Wikimedia Commons，使用時於頁面標註作者與授權。
"""

import json
import urllib.parse
import urllib.request
from pathlib import Path

CX468_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = CX468_DIR / "img" / "area"
UA = "CX468-area-bot/1.0 (https://cx468.com.tw; contact cx468468@gmail.com)"

# slug -> 依序嘗試的地標條目（取第一個有照片的）
CANDIDATES = {
    "zhonghe": ["烘爐地", "南山福德宮", "國立臺灣圖書館"],
    "yonghe": ["樂華夜市", "福和橋", "永和區"],
    "banqiao": ["林本源園邸", "新板特區", "板橋區 (臺灣)"],
    "xindian": ["碧潭", "和美山", "新店區"],
    "tucheng": ["承天禪寺", "土城桐花公園", "土城區 (新北市)"],
}


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def get_json(url: str) -> dict:
    return json.loads(_get(url).decode("utf-8"))


def pageimage(title: str):
    """回傳 (thumb_url_1280, file_title) 或 None。"""
    api = ("https://zh.wikipedia.org/w/api.php?action=query&format=json&redirects=1"
           "&prop=pageimages&piprop=thumbnail|name&pithumbsize=1280&titles="
           + urllib.parse.quote(title))
    data = get_json(api)
    pages = data.get("query", {}).get("pages", {})
    for _, p in pages.items():
        thumb = p.get("thumbnail", {}).get("source")
        name = p.get("pageimage")
        if thumb and name:
            return thumb, name
    return None


def commons_credit(file_title: str) -> dict:
    """取 Commons 檔案的作者 / 授權 / 描述。"""
    api = ("https://commons.wikimedia.org/w/api.php?action=query&format=json"
           "&prop=imageinfo&iiprop=extmetadata|url&titles="
           + urllib.parse.quote("File:" + file_title))
    try:
        data = get_json(api)
        pages = data.get("query", {}).get("pages", {})
        for _, p in pages.items():
            ii = (p.get("imageinfo") or [{}])[0]
            em = ii.get("extmetadata", {})

            def val(k):
                import re
                v = em.get(k, {}).get("value", "")
                return re.sub(r"<[^>]+>", "", v).strip()
            return {
                "author": val("Artist") or "Wikimedia Commons 貢獻者",
                "license": val("LicenseShortName") or "見 Wikimedia Commons",
                "descurl": ii.get("descriptionurl", ""),
            }
    except Exception as e:
        print(f"    ⚠ 取授權失敗：{e}")
    return {"author": "Wikimedia Commons 貢獻者", "license": "見 Wikimedia Commons", "descurl": ""}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    credits = {}
    for slug, titles in CANDIDATES.items():
        got = None
        for t in titles:
            try:
                r = pageimage(t)
            except Exception as e:
                print(f"  ⚠ {slug} 查 {t} 失敗：{e}")
                r = None
            if r:
                got = (t,) + r
                break
        if not got:
            print(f"  ✗ {slug}：找不到可用照片")
            continue
        landmark, thumb, fname = got
        dest = OUT_DIR / f"{slug}.jpg"
        try:
            dest.write_bytes(_get(thumb))
        except Exception as e:
            print(f"  ✗ {slug} 下載失敗：{e}")
            continue
        cred = commons_credit(fname)
        cred.update({"landmark": landmark, "file": fname})
        credits[slug] = cred
        print(f"  ✓ {slug}.jpg ← {landmark}（{dest.stat().st_size // 1024} KB）／{cred['author']}｜{cred['license']}")

    (OUT_DIR / "credits.json").write_text(
        json.dumps(credits, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ 完成，credits.json 已寫入 {OUT_DIR.relative_to(CX468_DIR)}/")


if __name__ == "__main__":
    main()
