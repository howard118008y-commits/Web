#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本機設計預覽器：用 repo 內既有 lvr-data JSON 仿造資料，渲染三頁到 CX468/_preview_*.html
（不碰正式輸出；CI 重建才是正品。僅供 UI 迭代目檢。）"""
import json, sys
from pathlib import Path
from datetime import datetime

HERE = Path(__file__).resolve().parent
BASE = HERE.parent.parent          # CX468/
sys.path.insert(0, str(HERE))

import build_observatory as OBS
import build_extras as EX

rank = json.loads((BASE / 'lvr-data/排名_w180.json').read_text(encoding='utf-8'))
FOCUS = ['中和區', '永和區', '板橋區', '新店區', '土城區']
focus = {r['鄉鎮市區']: r for r in rank if r['鄉鎮市區'] in FOCUS and r['縣市'] == '新北市'}
window_data = {w: {'ranking': rank, 'focus': focus} for w in (30, 90, 180, 365)}
deep = {
    '113S1': {'n': 210, 'median': 55.0, 'median_age': 21.0},
    '115S1': {'n': 150, 'median': 52.1, 'median_age': 26.6},
    'delta': {'n': -60, 'median_pct': -5.3},
}
ai = "（預覽用示意段落）本期雙北量縮價穩，台中低總價區補漲；正式文字由 CI 端 Claude 週報產生。\n第二段示意：新店區屋齡結構改變，判讀詳見下方新店深度解析。"
now = datetime.now().strftime('%Y-%m-%d %H:%M')

(BASE / '_preview_obs.html').write_text(
    OBS.build_html(now, '115Q1', window_data, deep, ai), encoding='utf-8')

pre_rank = json.loads((BASE / 'lvr-data/presale_ranking_w180.json').read_text(encoding='utf-8'))
ren_rank = json.loads((BASE / 'lvr-data/rental_ranking_w180.json').read_text(encoding='utf-8'))
import pandas as pd
(BASE / '_preview_presale.html').write_text(
    EX.render_presale_html(pd.DataFrame(pre_rank), now), encoding='utf-8')
(BASE / '_preview_rental.html').write_text(
    EX.render_rental_html(pd.DataFrame(ren_rank), now), encoding='utf-8')
print('預覽產出：_preview_obs.html / _preview_presale.html / _preview_rental.html')
