"""
餵 ranking + spotlight + alerts 給 Claude API，產生繁體中文週報。
若 ANTHROPIC_API_KEY 未設、或 anthropic SDK 未裝，fallback 為模板化文字。

輸出：
- CX468/lvr-data/週報_最新.md      Markdown 完整版（含 metadata header）
- CX468/lvr-data/週報_最新.txt      純文字版（給 LINE/FB 貼）

執行：.venv/bin/python scripts/generate_ai_report.py
需要 env：ANTHROPIC_API_KEY（未設則 fallback）
"""

from datetime import datetime
from pathlib import Path
import json
import os

import pandas as pd

OUT_DIR = Path(__file__).resolve().parent / "_cache"
CX468_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DEST = CX468_DIR / "lvr-data"

MODEL = "claude-haiku-4-5"
MAX_TOKENS = 1500
THRESHOLD = 20.0
MIN_SAMPLE = 30


def gather_context() -> dict:
    """收集 pipeline 產物作為 AI prompt 的素材。"""
    ctx = {"generated_at": datetime.now().strftime("%Y-%m-%d")}

    # 買賣 ranking
    p = OUT_DIR / "ranking_w180.pkl"
    if p.exists():
        rk = pd.read_pickle(p)
        rk_clean = rk[rk["n"] >= MIN_SAMPLE].dropna(subset=["1年漲幅"])
        ctx["total_districts"] = len(rk)
        ctx["top_yoy_gain"] = rk_clean.nlargest(5, "1年漲幅")[["鄉鎮市區", "縣市", "n", "單價中位", "1年漲幅"]].to_dict("records")
        ctx["top_yoy_loss"] = rk_clean.nsmallest(5, "1年漲幅")[["鄉鎮市區", "縣市", "n", "單價中位", "1年漲幅"]].to_dict("records")
        ctx["top_price"] = rk.nlargest(5, "單價中位")[["鄉鎮市區", "縣市", "單價中位"]].to_dict("records")
        ctx["alerts_in"] = rk_clean[rk_clean["1年漲幅"] >= THRESHOLD][["鄉鎮市區", "縣市", "1年漲幅"]].to_dict("records")
        ctx["alerts_out"] = rk_clean[rk_clean["1年漲幅"] <= -THRESHOLD][["鄉鎮市區", "縣市", "1年漲幅"]].to_dict("records")

    # 新店深度
    sd_pkl = OUT_DIR / "shindian_deep.pkl"
    if sd_pkl.exists():
        ctx["shindian_deep"] = pd.read_pickle(sd_pkl)

    # 預售 / 租屋
    for name, key in [("presale_ranking_w180.pkl", "presale_top"),
                       ("rental_ranking_w180.pkl", "rental_top")]:
        p = OUT_DIR / name
        if p.exists():
            ctx[key] = pd.read_pickle(p).head(5).to_dict("records")
    return ctx


def build_prompt(ctx: dict) -> str:
    """組合給 Claude 的 prompt。"""
    today = ctx["generated_at"]
    parts = [
        f"請依以下資料寫一份「{today} 雙北+台中+桃園 實價登錄週報」。",
        "",
        "寫作要求：",
        "- 繁體中文、380~480 字",
        "- 結構：① 本期重點（2-3 句）② 漲幅警示 ③ 跌幅警示（或穩定）④ 結構觀察（含新店 spotlight）",
        "- 中性語氣、避免投資建議用詞（不能寫「應該買」「建議投資」「保證」「最低利率」之類）",
        "- 用「市場觀察」「值得注意」「依資料顯示」「成交品結構改變」等中立詞彙",
        "- 結尾加一行：「（資料：內政部實價登錄，已排除特殊交易與極端值）」",
        "- 不寫標題列，直接寫內文",
        "",
        "資料摘要：",
        f"- 本期涵蓋 {ctx.get('total_districts', '?')} 行政區",
        "",
        "▲ YoY 漲幅 TOP 5：",
    ]
    for r in ctx.get("top_yoy_gain", []):
        parts.append(f"  {r['鄉鎮市區']}（{r['縣市']}）+{r['1年漲幅']:.1f}%（單價中位 {r['單價中位']:.1f} 萬/坪，樣本 {int(r['n'])}）")
    parts.append("")
    parts.append("▼ YoY 跌幅 TOP 5：")
    for r in ctx.get("top_yoy_loss", []):
        parts.append(f"  {r['鄉鎮市區']}（{r['縣市']}）{r['1年漲幅']:+.1f}%（單價中位 {r['單價中位']:.1f} 萬/坪，樣本 {int(r['n'])}）")

    parts.append("")
    parts.append(f"※ 突破 ±{THRESHOLD}% 警示：上漲 {len(ctx.get('alerts_in', []))} 區、下跌 {len(ctx.get('alerts_out', []))} 區")

    sd = ctx.get("shindian_deep")
    if sd:
        parts.append("")
        parts.append("📍 新店區 113Q1 → 115Q1：")
        parts.append(f"  成交量 {sd['113S1']['n']} → {sd['115S1']['n']}（{sd['delta']['n']:+d}）")
        parts.append(f"  單價中位 {sd['113S1']['median']} → {sd['115S1']['median']} 萬/坪（{sd['delta']['median_pct']:+.1f}%）")
        parts.append(f"  屋齡中位 {sd['113S1']['median_age']} → {sd['115S1']['median_age']} 年")
        parts.append("  → 成交品結構改變（新成屋帶量消失、老屋佔比上升），單價下降為結構性而非市場性")

    if ctx.get("presale_top"):
        parts.append("")
        parts.append("🏗 預售屋 TOP 3 單價：")
        for r in ctx["presale_top"][:3]:
            parts.append(f"  {r['鄉鎮市區']}（{r['縣市']}）{r['單價中位']:.1f} 萬/坪")

    if ctx.get("rental_top"):
        parts.append("")
        parts.append("🏠 租金每坪 TOP 3：")
        for r in ctx["rental_top"][:3]:
            y = r.get("年化報酬率")
            y_str = f"，年化報酬 {y:.2f}%" if y is not None and not pd.isna(y) else ""
            parts.append(f"  {r['鄉鎮市區']}（{r['縣市']}）{r['月租每坪中位']:,.0f} 元/坪/月{y_str}")

    return "\n".join(parts)


def call_claude(prompt: str, api_key: str) -> str:
    """呼叫 Claude Messages API（用 urllib 避免 SDK 依賴）。"""
    import urllib.request
    body = json.dumps({
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body, method="POST",
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    # response: {"content": [{"type": "text", "text": "..."}], ...}
    return "".join(b["text"] for b in data["content"] if b.get("type") == "text")


def fallback_template(ctx: dict) -> str:
    """無 API 時用模板。"""
    today = ctx["generated_at"]
    parts = [f"【{today} 雙北+台中+桃園 實價登錄週報】", ""]
    parts.append(f"本期涵蓋 {ctx.get('total_districts', '?')} 行政區。")
    gains = ctx.get("alerts_in", [])
    losses = ctx.get("alerts_out", [])
    if gains:
        names = "、".join(f"{r['鄉鎮市區']}（{r['縣市']}）+{r['1年漲幅']:.1f}%" for r in gains[:5])
        parts.append(f"\n▲ YoY 突破 +20% 警示（{len(gains)} 區）：{names}")
    if losses:
        names = "、".join(f"{r['鄉鎮市區']}（{r['縣市']}）{r['1年漲幅']:+.1f}%" for r in losses[:5])
        parts.append(f"\n▼ YoY 突破 -20% 警示（{len(losses)} 區）：{names}")
    sd = ctx.get("shindian_deep")
    if sd:
        parts.append(f"\n📍 新店：成交量 {sd['113S1']['n']} → {sd['115S1']['n']}、屋齡中位 {sd['113S1']['median_age']} → {sd['115S1']['median_age']} 年，成交品結構改變。")
    parts.append("\n（資料：內政部實價登錄，已排除特殊交易與極端值）")
    return "\n".join(parts)


def main() -> int:
    DATA_DEST.mkdir(exist_ok=True)
    ctx = gather_context()
    if "total_districts" not in ctx:
        print("✗ 找不到 ranking_w180.pkl，先跑 analyze_lvr.py")
        return 1

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    used_ai = False
    if api_key:
        try:
            prompt = build_prompt(ctx)
            print(f"→ 呼叫 Claude API（{MODEL}）")
            body = call_claude(prompt, api_key)
            used_ai = True
            print(f"  ✓ AI 回應 {len(body)} 字")
        except Exception as e:
            print(f"  ⚠ API 失敗 ({e})，fallback 模板")
            body = fallback_template(ctx)
    else:
        print("⚠ ANTHROPIC_API_KEY 未設，使用模板版本")
        body = fallback_template(ctx)

    # 寫 markdown
    md_path = DATA_DEST / "週報_最新.md"
    md = (
        f"---\n"
        f"generated_at: {ctx['generated_at']}\n"
        f"model: {MODEL if used_ai else 'template-fallback'}\n"
        f"total_districts: {ctx.get('total_districts')}\n"
        f"alerts_gain: {len(ctx.get('alerts_in', []))}\n"
        f"alerts_loss: {len(ctx.get('alerts_out', []))}\n"
        f"---\n\n"
        f"{body}\n"
    )
    md_path.write_text(md, encoding="utf-8")

    # 純文字版本（去 markdown frontmatter）
    txt_path = DATA_DEST / "週報_最新.txt"
    txt_path.write_text(body, encoding="utf-8")

    print(f"✓ 已存：{md_path.name}（{md_path.stat().st_size // 1024} KB）")
    print(f"✓ 已存：{txt_path.name}")
    print(f"\n----- 預覽 -----\n{body[:300]}{'...' if len(body) > 300 else ''}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
