/* 房貸儀表板 v4 — 輕主題動態引擎
   讀 cx_data.json（現值/狀態/註記）＋ cx_history.json（歷史序列）：
   1) 覆蓋現值/註記/更新月（比靜態生成更即時）
   2) 走勢圖：十年歷史實值（紅線＋淡紅面積，紙色格線）；點數 <8 顯示累積中
   3) 變化列：依序列頻率自動標「月變/季變」＋「一年變化」（歷史實值相減，非預測）
   4) 統計列：十年高／低／平均（歷史實值計算）
   誠實原則：畫的、算的都是公開統計歷史值；不足就不顯示，不補假線。 */
(function () {
  function fmt(v) {
    if (Math.abs(v) >= 10000) return (v / 10000).toFixed(1) + '萬';
    if (Math.abs(v) >= 1000) return v.toLocaleString('en-US', { maximumFractionDigits: 0 });
    return String(Math.round(v * 100) / 100);
  }

  function chart(points, unit) {
    var w = 520, h = 150, pad = 10, padB = 22;
    var ys = points.map(function (p) { return p[1]; });
    var minY = Math.min.apply(null, ys), maxY = Math.max.apply(null, ys);
    if (maxY - minY < 1e-9) { minY -= 1; maxY += 1; }
    var n = points.length;
    function X(i) { return pad + (w - 2 * pad) * (n === 1 ? 0.5 : i / (n - 1)); }
    function Y(v) { return (h - padB) - (h - padB - pad) * ((v - minY) / (maxY - minY)); }
    var d = points.map(function (p, i) { return (i ? 'L' : 'M') + X(i).toFixed(1) + ' ' + Y(p[1]).toFixed(1); }).join('');
    var area = d + 'L' + X(n - 1).toFixed(1) + ' ' + (h - padB) + 'L' + X(0).toFixed(1) + ' ' + (h - padB) + 'Z';
    var last = points[n - 1], first = points[0];
    return '<svg viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none" style="width:100%;height:132px;display:block">'
      + '<defs><linearGradient id="rvA" x1="0" y1="0" x2="0" y2="1">'
      + '<stop offset="0%" stop-color="rgba(27,47,74,.16)"/><stop offset="100%" stop-color="rgba(27,47,74,0)"/></linearGradient></defs>'
      + '<line x1="' + pad + '" y1="' + (h - padB) + '" x2="' + (w - pad) + '" y2="' + (h - padB) + '" stroke="rgba(0,0,0,.12)"/>'
      + '<line x1="' + pad + '" y1="' + pad + '" x2="' + (w - pad) + '" y2="' + pad + '" stroke="rgba(0,0,0,.05)" stroke-dasharray="3 4"/>'
      + '<path d="' + area + '" fill="url(#rvA)"/>'
      + '<path d="' + d + '" fill="none" stroke="#1B2F4A" stroke-width="2" vector-effect="non-scaling-stroke"/>'
      + '<circle cx="' + X(n - 1) + '" cy="' + Y(last[1]) + '" r="3.5" fill="#1B2F4A"/>'
      + '<g font-family="IBM Plex Mono,monospace" font-size="10.5" fill="#a1a1a6">'
      + '<text x="' + pad + '" y="' + (h - 7) + '">' + first[0] + '</text>'
      + '<text x="' + (w - pad) + '" y="' + (h - 7) + '" text-anchor="end">' + last[0] + '</text>'
      + '<text x="' + (w - pad) + '" y="' + (pad + 4) + '" text-anchor="end" fill="#8a6d1a">高 ' + fmt(maxY) + unit + '</text>'
      + '</g></svg>';
  }

  function monthsBetween(a, b) {
    var ay = +a.slice(0, 4), am = +a.slice(5, 7), by = +b.slice(0, 4), bm = +b.slice(5, 7);
    return (by - ay) * 12 + (bm - am);
  }

  function chgSpan(label, cur, prev, unit) {
    if (prev === undefined || prev === null) return '';
    var d = cur - prev;
    if (Math.abs(d) < 1e-9) return '<span class="rv4-chg">' + label + ' <b>持平</b></span>';
    var cls = d > 0 ? 'up' : 'down';
    var arrow = d > 0 ? '▲' : '▼';
    return '<span class="rv4-chg">' + label + ' <b class="' + cls + '">' + arrow + ' '
      + fmt(Math.abs(d)) + unit + '</b></span>';
  }

  Promise.all([
    fetch('cx_data.json').then(function (r) { return r.json(); }),
    fetch('cx_history.json').then(function (r) { return r.json(); }).catch(function () { return {}; })
  ]).then(function (res) {
    var data = res[0], hist = res[1];
    var lu = document.getElementById('last-update');
    if (lu && data.generated) lu.textContent = String(data.generated).replace(/-/g, '.');
    var map = {};
    data.indicators.forEach(function (d) { map[d.code] = d; });

    document.querySelectorAll('.rv4-card').forEach(function (el) {
      var code = el.getAttribute('data-cx-code');
      var ind = map[code];
      if (ind) {
        el.querySelector('.rv4-value').textContent = ind.value;
        el.querySelector('.rv4-note').textContent = ind.note || '';
        el.querySelector('.rv4-upd').textContent = '資料至 ' + (ind.updated || '—');
        var dot = el.querySelector('.rv4-dot');
        dot.className = 'rv4-dot ' + (ind.status || 'yellow');
      }
      var h = hist[code];
      var pts = h && h.points ? h.points : [];
      if (pts.length >= 8) {
        el.querySelector('[data-role=chart]').innerHTML = chart(pts, h.unit || '');
        var vals = pts.map(function (p) { return p[1]; });
        var hi = Math.max.apply(null, vals), lo = Math.min.apply(null, vals);
        var mean = vals.reduce(function (a, b) { return a + b; }, 0) / vals.length;
        el.querySelector('[data-role=stats]').innerHTML =
          '<div class="rv4-stat"><div class="k">十年高</div><div class="v">' + fmt(hi) + '</div></div>'
          + '<div class="rv4-stat"><div class="k">十年低</div><div class="v">' + fmt(lo) + '</div></div>'
          + '<div class="rv4-stat"><div class="k">十年均</div><div class="v">' + fmt(mean) + '</div></div>'
          + '<div class="rv4-stat"><div class="k">現值</div><div class="v">' + fmt(vals[vals.length - 1]) + '</div></div>';
        // 變化列：偵測頻率（月/季），算近一期與近一年（歷史實值）
        var gap = pts.length >= 3 ? monthsBetween(pts[pts.length - 3][0], pts[pts.length - 2][0]) : 1;
        var freqLabel = gap >= 3 ? '季變' : '月變';
        var cur = pts[pts.length - 1][1], prev = pts[pts.length - 2][1];
        var perYear = gap >= 3 ? 4 : 12;
        var yearIdx = pts.length - 1 - perYear;
        var yearPrev = yearIdx >= 0 ? pts[yearIdx][1] : null;
        var htmlChg = chgSpan(freqLabel, cur, prev, h.unit || '')
          + chgSpan('一年', cur, yearPrev, h.unit || '');
        if (htmlChg) el.querySelector('[data-role=changes]').innerHTML = htmlChg;
      }
    });
  }).catch(function (e) { console.warn('radar v4:', e); });

  function tick() {
    var el = document.getElementById('now');
    if (el) {
      var d = new Date();
      function p(x) { return x < 10 ? '0' + x : x; }
      el.textContent = d.getFullYear() + '.' + p(d.getMonth() + 1) + '.' + p(d.getDate())
        + ' ' + p(d.getHours()) + ':' + p(d.getMinutes()) + ':' + p(d.getSeconds());
    }
  }
  tick(); setInterval(tick, 1000);
})();
