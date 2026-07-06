/* 房貸儀表板 v4 完整版 — 真實歷史序列圖表引擎
   資料：cx_data.json（現值/狀態/註記，每日 CI 更新）＋ cx_history.json（歷史序列，深歷史＋每日累積）
   行為：
   1) #all18 網格：18 張精簡卡（現值＋狀態燈＋sparkline＋註記）
   2) 大卡（[data-cx-code] 的 .chart-container svg）：該指標歷史 ≥8 點時，以真實序列重繪（取代建置示意圖）
   誠實原則：畫的都是公開統計的歷史值；點數不足就不畫、不補假線。 */
(function () {
  var STATUS_COLOR = { green: '#34c759', yellow: '#ffd166', red: '#ff6b6b' };

  function svgPath(pts, w, h, pad) {
    var xs = pts.map(function (p) { return p[0]; });
    var ys = pts.map(function (p) { return p[1]; });
    var minY = Math.min.apply(null, ys), maxY = Math.max.apply(null, ys);
    if (maxY - minY < 1e-9) { minY -= 1; maxY += 1; }
    var n = pts.length;
    function X(i) { return pad + (w - 2 * pad) * (n === 1 ? 0.5 : i / (n - 1)); }
    function Y(v) { return h - pad - (h - 2 * pad) * ((v - minY) / (maxY - minY)); }
    var d = pts.map(function (p, i) { return (i ? 'L' : 'M') + X(i).toFixed(1) + ' ' + Y(p[1]).toFixed(1); }).join('');
    return { d: d, X: X, Y: Y, minY: minY, maxY: maxY };
  }

  function fmt(v) {
    if (Math.abs(v) >= 10000) return (v / 10000).toFixed(1) + '萬';
    if (Math.abs(v) >= 1000) return v.toLocaleString('en-US', { maximumFractionDigits: 0 });
    return String(Math.round(v * 100) / 100);
  }

  function sparkline(points, color) {
    var w = 300, h = 72, pad = 6;
    var g = svgPath(points, w, h, pad);
    var last = points[points.length - 1];
    return '<svg viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none" style="width:100%;height:44px;display:block">'
      + '<path d="' + g.d + '" fill="none" stroke="' + color + '" stroke-width="2" vector-effect="non-scaling-stroke"/>'
      + '<circle cx="' + g.X(points.length - 1) + '" cy="' + g.Y(last[1]) + '" r="3" fill="' + color + '"/>'
      + '</svg>';
  }

  function bigChart(points, unit) {
    var w = 1200, h = 320, pad = 34;
    var g = svgPath(points, w, h, pad);
    var first = points[0], last = points[points.length - 1];
    var mid = points[Math.floor(points.length / 2)];
    var area = g.d + 'L' + g.X(points.length - 1).toFixed(1) + ' ' + (h - pad)
      + 'L' + g.X(0).toFixed(1) + ' ' + (h - pad) + 'Z';
    return '<svg viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none">'
      + '<defs><linearGradient id="gArea" x1="0" y1="0" x2="0" y2="1">'
      + '<stop offset="0%" stop-color="rgba(212,175,55,.28)"/><stop offset="100%" stop-color="rgba(212,175,55,0)"/>'
      + '</linearGradient></defs>'
      + '<line x1="' + pad + '" y1="' + (h - pad) + '" x2="' + (w - pad) + '" y2="' + (h - pad) + '" stroke="rgba(255,255,255,.14)"/>'
      + '<path d="' + area + '" fill="url(#gArea)"/>'
      + '<path d="' + g.d + '" fill="none" stroke="#D4AF37" stroke-width="2.5" vector-effect="non-scaling-stroke"/>'
      + '<circle cx="' + g.X(points.length - 1) + '" cy="' + g.Y(last[1]) + '" r="4" fill="#D4AF37"/>'
      + '<g font-family="IBM Plex Mono,monospace" font-size="12" fill="#7A7565">'
      + '<text x="' + pad + '" y="' + (h - 10) + '">' + first[0] + '</text>'
      + '<text x="' + (w / 2) + '" y="' + (h - 10) + '" text-anchor="middle">' + mid[0] + '</text>'
      + '<text x="' + (w - pad) + '" y="' + (h - 10) + '" text-anchor="end">' + last[0] + '</text>'
      + '<text x="' + (w - pad) + '" y="' + 20 + '" text-anchor="end">高 ' + fmt(g.maxY) + unit + '</text>'
      + '<text x="' + pad + '" y="' + 20 + '">低 ' + fmt(g.minY) + unit + '</text>'
      + '</g></svg>';
  }

  Promise.all([
    fetch('cx_data.json').then(function (r) { return r.json(); }),
    fetch('cx_history.json').then(function (r) { return r.json(); }).catch(function () { return {}; })
  ]).then(function (res) {
    var data = res[0], hist = res[1];
    var map = {};
    data.indicators.forEach(function (d) { map[d.code] = d; });

    /* ── 18 卡總覽網格 ── */
    var grid = document.getElementById('all18-grid');
    if (grid) {
      data.indicators.forEach(function (ind) {
        var h = hist[ind.code];
        var pts = h && h.points ? h.points : [];
        var color = STATUS_COLOR[ind.status] || '#ffd166';
        var card = document.createElement('div');
        card.className = 'a18-card';
        card.innerHTML =
          '<div class="a18-top"><span class="a18-code">' + ind.code + '</span>'
          + '<span class="a18-dot" style="background:' + color + '"></span></div>'
          + '<div class="a18-name">' + ind.name + '</div>'
          + '<div class="a18-value">' + ind.value + '</div>'
          + (pts.length >= 2 ? sparkline(pts, color)
             : '<div class="a18-nochart">歷史累積中（' + pts.length + ' 點）</div>')
          + '<div class="a18-note">' + (ind.note || '') + '</div>'
          + '<div class="a18-upd">資料至 ' + (ind.updated || '—') + '</div>';
        grid.appendChild(card);
      });
    }

    /* ── 大卡真實走勢替換 ── */
    document.querySelectorAll('[data-cx-code]').forEach(function (el) {
      var code = el.getAttribute('data-cx-code');
      var h = hist[code];
      if (!h || !h.points || h.points.length < 8) return;
      var box = el.querySelector('.chart-container');
      if (!box) return;
      box.innerHTML = bigChart(h.points, h.unit || '');
      var t = el.querySelector('.chart-section-zh');
      if (t) t.textContent = '歷史走勢（公開統計實值）';
      var te = el.querySelector('.chart-section-en');
      if (te) te.textContent = h.points[0][0] + ' — ' + h.points[h.points.length - 1][0] + ' · ' + h.points.length + ' obs';
    });
  }).catch(function (e) { console.warn('radar charts:', e); });
})();
