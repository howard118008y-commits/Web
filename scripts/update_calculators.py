#!/usr/bin/env python3
"""
地價稅試算器自動更新腳本
用法：
  python scripts/update_calculators.py                  # 用 tax-config.json 更新所有城市
  python scripts/update_calculators.py --city taipei    # 只更新台北市
  python scripts/update_calculators.py --check          # 只檢查目前各檔案的 T 值，不寫入
  python scripts/update_calculators.py --year 117-118   # 更新年度標示（搭配新 T 值）

每兩年更新流程：
  1. 在 tax-config.json 更新各城市的 T 和 year 欄位
  2. python scripts/update_calculators.py
  3. git add -A && git commit -m "Update 地價稅累進起點地價 117-118年" && git push
"""

import json
import re
import sys
import os
import argparse
from pathlib import Path

# ─── 路徑設定 ───
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
CONFIG_FILE = SCRIPT_DIR / "tax-config.json"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def read_html(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def write_html(filepath, content):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def update_T_value(content, new_T):
    """更新 const T = XXXXXX; 這一行"""
    new_content, count = re.subn(
        r'(const T = )\d+;',
        f'\\g<1>{new_T};',
        content
    )
    return new_content, count


def update_year_in_text(content, old_year, new_year, city_name):
    """更新頁面中出現的年度字串（標題、hero、級距表標題、disclaimer）"""
    if not old_year or not new_year or old_year == new_year:
        return content, 0
    count = 0
    # Replace year in hero subtitle
    new_content, n = re.subn(
        rf'({re.escape(city_name)}・){re.escape(old_year)}(年)',
        rf'\g<1>{new_year}\2',
        content
    )
    count += n
    content = new_content
    # Replace year in tier table title
    new_content, n = re.subn(
        rf'（{re.escape(old_year)}年，',
        f'（{new_year}年，',
        content
    )
    count += n
    content = new_content
    # Replace year in disclaimer
    new_content, n = re.subn(
        rf'{re.escape(old_year)}年{re.escape(city_name)}',
        f'{new_year}年{city_name}',
        content
    )
    count += n
    content = new_content
    # Replace year in meta description and title
    new_content, n = re.subn(
        rf'{re.escape(old_year)}年累進起點地價',
        f'{new_year}年累進起點地價',
        content
    )
    count += n
    content = new_content
    return content, count


def update_T_display(content, new_T):
    """更新頁面中顯示的 T 格式數字（累進起點地價顯示）"""
    T_fmt = f"{new_T:,}"
    # Update tier table title display value
    new_content, count = re.subn(
        r'（累進起點地價 [\d,]+ 元）',
        f'（累進起點地價 {T_fmt} 元）',
        content
    )
    # Update disclaimer T display
    new_content2, count2 = re.subn(
        r'累進起點地價為 [\d,]+ 元',
        f'累進起點地價為 {T_fmt} 元',
        new_content
    )
    return new_content2, count + count2


def get_current_T(content):
    """從 HTML 中讀出目前的 T 值"""
    m = re.search(r'const T = (\d+);', content)
    return int(m.group(1)) if m else None


def process_city(city_key, cfg, check_only=False, force_year=None):
    city = cfg["cities"][city_key]
    filepath = ROOT_DIR / city["file"]

    if not filepath.exists():
        print(f"  ⚠  {city['name']}: 檔案不存在 {city['file']}")
        return False

    content = read_html(filepath)
    current_T = get_current_T(content)
    new_T = city["T"]
    new_year = force_year or city.get("year", "")

    if check_only:
        status = "✓" if current_T == new_T else "⚠ 需更新"
        print(f"  {status}  {city['name']:8s}  檔案T={current_T:>12,}  設定T={new_T:>12,}  年度={city.get('year','?')}")
        return current_T != new_T

    changed = False

    # 取出目前年度（從 hero 段落）
    m_year = re.search(r'・(\d{3}-\d{3})年', content)
    old_year = m_year.group(1) if m_year else None

    # 更新 T 值
    new_content, t_count = update_T_value(content, new_T)
    if t_count > 0 and current_T != new_T:
        print(f"  ✓ {city['name']}: T  {current_T:>12,} → {new_T:>12,}")
        changed = True
    elif t_count == 0:
        print(f"  ⚠  {city['name']}: 找不到 const T = 的位置")

    # 更新年度
    if new_year and old_year and old_year != new_year:
        new_content, yr_count = update_year_in_text(new_content, old_year, new_year, city["name"])
        if yr_count > 0:
            print(f"  ✓ {city['name']}: 年度 {old_year} → {new_year}  ({yr_count} 處)")
            changed = True

    # 更新 T 格式顯示
    new_content, disp_count = update_T_display(new_content, new_T)
    if disp_count > 0 and current_T != new_T:
        print(f"  ✓ {city['name']}: 顯示數字已更新 ({disp_count} 處)")

    if changed or disp_count > 0:
        write_html(filepath, new_content)
        print(f"  ✓ {city['name']}: {city['file']} 已儲存")
    else:
        print(f"  — {city['name']}: 無需更新（T={new_T:,}，年度={new_year}）")

    return changed


def main():
    parser = argparse.ArgumentParser(description="更新地價稅試算器的累進起點地價")
    parser.add_argument("--city", help="只更新指定城市 key（如 taipei）")
    parser.add_argument("--check", action="store_true", help="只檢查，不寫入")
    parser.add_argument("--year", help="強制指定年度（如 117-118）")
    args = parser.parse_args()

    cfg = load_config()

    print(f"\n{'檢查模式' if args.check else '更新模式'} — 設定檔：{CONFIG_FILE.name}")
    print(f"上次更新：{cfg.get('_last_updated', '?')}，下次預計：{cfg.get('_next_update_due', '?')}\n")

    cities_to_process = (
        [args.city] if args.city and args.city in cfg["cities"]
        else list(cfg["cities"].keys())
    )

    needs_update = []
    for key in cities_to_process:
        changed = process_city(key, cfg, check_only=args.check, force_year=args.year)
        if changed:
            needs_update.append(key)

    print()
    if args.check:
        if needs_update:
            print(f"⚠  {len(needs_update)} 個城市需要更新：{', '.join(needs_update)}")
            print("   → 更新 scripts/tax-config.json 後執行 python scripts/update_calculators.py")
            sys.exit(1)
        else:
            print("✓ 所有檔案均與設定檔一致，無需更新")
    else:
        if needs_update:
            print(f"✓ 已更新 {len(needs_update)} 個城市：{', '.join(needs_update)}")
            print("\n下一步：")
            print("  git add .")
            print(f"  git commit -m \"Update 地價稅累進起點地價 {cfg['cities'][needs_update[0]].get('year', '')}年\"")
            print("  git push")
        else:
            print("✓ 無需更新")


if __name__ == "__main__":
    main()
