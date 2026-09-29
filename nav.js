
(function () {
  var TOKENS = ':root{--cx-cream:#FCF6EA;--cx-orange:#F5621C;--cx-orange-deep:#B8440C;--cx-gold:#C8945A;--cx-ink:#3C1E0E;' +
    '--cx-cream-2:#F7ECDC;--cx-card:#FEFBF6;--cx-cream-glass:rgba(252,246,234,.9);--cx-line:#E5CAA9;' +
    '--cx-ink-2:#6C5445;--cx-ink-3:#796354;--cx-cream-dim:#CCC0B3;--cx-ink-line:#5B4131;' +
    '--cx-orange-soft:#F6783B;--cx-orange-deep-hover:#A53E0C;--cx-ink-shadow:rgba(60,30,14,.4);--cx-ink-hero:#4B2F20}';
  if (!document.getElementById('cx-brand')) document.head.insertAdjacentHTML('beforeend', '<style id="cx-brand">' + TOKENS + '</style>');
  if (document.currentScript && document.currentScript.hasAttribute('data-cx-tokens-only')) return;
  /* 接聽狀態首繪前先標在 <html>（規則同 cx-hours.js，改時段要一起改）：導覽電話鈕一出現就是正確主次，不閃舊樣式 */
  (function () {
    var de = document.documentElement, h = location.hostname, f = window.__CX_NOW, d, m, t;
    if (de.hasAttribute('data-cx-open')) return;
    if ((h === 'localhost' || h === '127.0.0.1') && typeof f === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(f)) {
      f = f.split(/[-T:]/).map(Number); d = new Date(Date.UTC(f[0], f[1] - 1, f[2])).getUTCDay(); m = f[3] * 60 + f[4];
    } else { t = new Date(Date.now() + 288e5); d = t.getUTCDay(); m = t.getUTCHours() * 60 + t.getUTCMinutes(); }
    de.setAttribute('data-cx-open', d >= 1 && d <= 5 && m >= 600 && m < 1020 ? '1' : '0');
  })();
  var css = [
    '.cx-nav{position:fixed;top:0;left:0;right:0;z-index:100;display:block;height:auto;padding:0;background:var(--cx-cream-glass);',
    'backdrop-filter:blur(14px);border-bottom:1px solid var(--cx-line);font-family:"Noto Sans TC",-apple-system,"PingFang TC","Microsoft JhengHei",sans-serif;color:var(--cx-ink)}',
    '.cx-nav *{box-sizing:border-box}',
    '.cx-nav a{text-decoration:none}.cx-nav a:where(:not(.cx-cta)){color:inherit}',
    '.cx-in{max-width:1180px;margin:0 auto;padding:0 24px;height:64px;display:flex;align-items:center;gap:28px}',
    '.cx-logo{display:flex;align-items:center;gap:10px;font-family:"Noto Serif TC",serif;font-weight:900;font-size:17px;letter-spacing:.04em;white-space:nowrap}',
    '.cx-mark{width:30px;height:30px;border-radius:7px;background:var(--cx-ink);color:var(--cx-orange);box-shadow:0 0 0 1px var(--cx-cream-dim);display:grid;place-items:center;font-size:16px;flex:none}',
    '.cx-menu{display:flex;gap:4px;list-style:none;margin:0;padding:0;margin-left:8px}',
    '.cx-menu>li{position:relative}',
    '.cx-menu>li::after{content:"";position:absolute;left:0;right:0;top:100%;height:10px}',
    '.cx-menu>li>button{background:none;border:0;color:var(--cx-ink-2);font:inherit;font-size:14.5px;padding:10px 12px;border-radius:8px;cursor:pointer;transition:.15s}',
    '.cx-menu>li>button:hover,.cx-menu>li.open>button{color:var(--cx-ink);background:var(--cx-cream-2)}',
    '.cx-dd{position:absolute;top:calc(100% + 6px);left:0;min-width:240px;background:var(--cx-card);border:1px solid var(--cx-line);border-radius:12px;',
    'padding:8px;box-shadow:0 14px 36px rgba(0,0,0,.28);opacity:0;visibility:hidden;transform:translateY(-4px);pointer-events:none;transition:.15s}',
    '.cx-menu>li.open .cx-dd{opacity:1;visibility:visible;transform:none;pointer-events:auto}',
    '.cx-dd a{display:block;padding:10px 12px;border-radius:8px;font-size:14px;color:var(--cx-ink)}',
    '.cx-dd a:hover{background:var(--cx-cream-2)}',
    '.cx-dd a.go{font-weight:700;color:var(--cx-ink);background:var(--cx-orange);margin-bottom:6px}',
    '.cx-dd a.go:hover{background:var(--cx-orange-soft)}',
    '.cx-dd a.go::after{content:" →"}',
    '.cx-badge{display:inline-block;background:#FAC775;color:#633806;font-size:11px;font-weight:500;padding:2px 9px;border-radius:999px;margin-left:8px;vertical-align:1px}',
    '.cx-right{margin-left:auto;display:flex;align-items:center;gap:10px}',
    '.cx-phone{width:44px;height:44px;border-radius:50%;border:1px solid var(--cx-line);display:grid;place-items:center;font-size:15px;color:var(--cx-ink-2)}',
    '.cx-phone:hover{border-color:var(--cx-orange-deep);color:var(--cx-ink)}',
    '.cx-resume{font-size:14px;color:var(--cx-ink-2);padding:8px 12px;border-radius:999px;border:1px solid transparent}',
    '.cx-resume:hover{color:var(--cx-ink);border-color:var(--cx-line)}',
    '.cx-cta{display:inline-flex;align-items:center;min-height:44px;background:var(--cx-orange);color:var(--cx-ink);font-weight:700;font-size:14.5px;padding:10px 22px;border-radius:999px;white-space:nowrap}',
    '.cx-cta:hover{background:var(--cx-orange-soft)}',
    '.cx-cta-n{font-variant-numeric:tabular-nums;letter-spacing:.02em}.cx-cta-s{display:none}',
    /* 非接聽時段電話鈕降成次鈕（老闆 2026-09-29 拍板）：米白底＋墨框＋墨字，不換 LINE、不改字；框用 inset 陰影，尺寸不變 */
    'html[data-cx-open="0"] .cx-cta{background:var(--cx-cream);box-shadow:inset 0 0 0 1.5px var(--cx-ink)}',
    'html[data-cx-open="0"] .cx-cta:hover{background:var(--cx-cream-2)}',
    '.cx-burger{display:none;background:none;border:0;color:var(--cx-ink);font-size:24px;cursor:pointer;padding:4px 6px}',
    '.cx-sheet{display:none;position:fixed;top:58px;left:0;right:0;bottom:0;background:var(--cx-cream);color:var(--cx-ink);overflow:auto;padding:16px 20px 40px;z-index:99}',
    '.cx-sheet.open{display:block}',
    'body:has(.cx-sheet.open) :is(.cx-sticky-cta,.cw-launch,.cw-teaser,.cw-panel,.cw-full-backdrop,#float){display:none!important}',
    '.cx-sheet details{border-bottom:1px solid var(--cx-line)}',
    '.cx-sheet summary{list-style:none;padding:16px 4px;font-size:16px;font-weight:500;cursor:pointer;display:flex;justify-content:space-between;color:var(--cx-ink)}',
    '.cx-sheet summary::-webkit-details-marker{display:none}',
    '.cx-sheet summary::after{content:"+";color:var(--cx-orange-deep);font-size:20px}',
    '.cx-sheet details[open] summary::after{content:"−"}',
    '.cx-sheet a{display:block;padding:11px 4px 11px 14px;font-size:15px;color:var(--cx-ink-2)}',
    '.cx-sheet a.go{color:var(--cx-orange-deep);font-weight:700}',
    '.cx-sheet .cx-sheet-foot{display:flex;flex-direction:column;gap:10px;margin-top:20px}',
    '.cx-sheet .cx-sheet-foot a{padding:14px;border-radius:10px;border:1px solid var(--cx-ink);color:var(--cx-ink);text-align:center;font-size:15px}',
    '.cx-sheet .cx-sheet-foot a.cta{background:var(--cx-orange);color:var(--cx-ink);border-color:var(--cx-orange);font-weight:700}',
    'html[data-cx-open="0"] .cx-sheet .cx-sheet-foot a.cta{background:var(--cx-cream);border-color:var(--cx-ink)}',
    '@media(max-width:900px){.cx-in{height:58px;gap:14px}.cx-menu,.cx-resume,.cx-phone{display:none}.cx-burger{display:block}.cx-cta{padding:9px 16px;font-size:14px}.cx-cta-n{display:none}.cx-cta-s{display:inline}}',
    '@media(max-width:400px){.cx-in{padding:0 14px;gap:8px}.cx-logo{font-size:15px;gap:7px}.cx-right{gap:6px}.cx-cta{padding:8px 12px;font-size:13.5px}}',
    '.cx-nav.cx-light{background:var(--cx-card);backdrop-filter:none;color:var(--cx-ink)}',
    '.cx-light .cx-menu>li>button{color:var(--cx-ink);border-radius:999px}',
    '.cx-light .cx-phone{color:var(--cx-ink)}',
    '.cx-sheet.cx-light{background:var(--cx-card)}',
    '.cx-sheet.cx-light a{color:var(--cx-ink)}',
    '.cx-sheet.cx-light a.go{color:var(--cx-orange-deep)}',
    '.cx-right{position:relative}.cx-nc{display:none;position:absolute;top:0;right:calc(100% + 10px)}',
    '@media(min-width:1100px){html[data-cx-dcard="none"] .cx-nc{display:block}}',
    '.cx-right:has(.cx-resume:not([hidden])) .cx-nc{display:none}',
    '.cx-nc-btn{display:inline-flex;align-items:center;min-height:44px;white-space:nowrap;padding:0 16px;border:1px solid var(--cx-line);border-radius:999px;background:transparent;color:var(--cx-ink);font:inherit;font-size:14.5px;font-weight:600;cursor:pointer;transition:background-color .15s,border-color .15s}',
    '.cx-nc-btn:hover,.cx-nc-btn[aria-expanded="true"]{background:var(--cx-cream-2);border-color:var(--cx-orange-deep)}',
    '.cx-nc-btn:focus-visible,.cx-nc-panel :focus-visible{outline:2px solid var(--cx-orange-deep);outline-offset:2px}',
    '.cx-nc-panel{position:absolute;top:calc(100% + 10px);right:0;width:272px;padding:16px 16px 14px;background:var(--cx-card);color:var(--cx-ink);border:1px solid var(--cx-line);border-radius:14px;',
    'box-shadow:0 18px 40px -16px var(--cx-ink-shadow);opacity:0;visibility:hidden;transform:translateY(-4px);transition:opacity .15s ease,transform .15s ease,visibility 0s linear .15s}',
    '.cx-nc.open .cx-nc-panel{opacity:1;visibility:visible;transform:none;transition:opacity .15s ease,transform .15s ease,visibility 0s}',
    '.cx-nc-panel p{margin:0;font-size:14px;line-height:1.5;color:var(--cx-ink-2)}',
    '.cx-nc-panel .cx-nc-k{font-weight:600}',
    '.cx-nc-tel{display:flex;align-items:center;min-height:44px;font-size:24px;font-weight:800;letter-spacing:.01em;font-variant-numeric:tabular-nums}',
    '.cx-nc-tel:hover{text-decoration:underline!important;text-decoration-color:var(--cx-gold)!important;text-underline-offset:4px}',
    '.cx-nc-panel .cx-nc-closed{display:none}',
    '.cx-nc-panel[data-cx-open="0"] .cx-nc-closed{display:block}',
    '.cx-nc-panel[data-cx-open="0"] .cx-nc-open{display:none}',
    '.cx-nc-line{display:flex;align-items:center;justify-content:center;min-height:44px;margin-top:12px;border-radius:999px;font-size:15px;font-weight:700;box-shadow:inset 0 0 0 1.5px var(--cx-ink);transition:background-color .15s}',
    '.cx-nc-line:hover{background:var(--cx-cream-2)}',
    '.cx-nc-panel[data-cx-open="0"] .cx-nc-line{background:var(--cx-orange);box-shadow:none}',
    '.cx-nc-panel[data-cx-open="0"] .cx-nc-line:hover{background:var(--cx-orange-soft)}'
  ].join('');
  var MENU = [
    { label: '企業貸款', items: [
      ['公司財務健檢', '/corporate-checkup.html'],
      ['企業貸款諮詢', '/corporate-loan.html'],
      ['開始企業評估', '/intake.html?topic=corporate', 1],
      ['企業相關文章', '/knowledge.html']
    ]},
    { label: '民間轉銀行', items: [
      ['開始評估', '/intake.html?topic=private-to-bank', 1],
      ['民間轉銀行怎麼運作', '/private-to-bank.html'],
      ['民間借款整理', '/debt-consolidation.html'],
      ['二胎房貸諮詢', '/second-mortgage.html'],
      ['多筆負債整合', '/xinbei-debt-consolidation.html'],
      ['轉貸相關文章', '/knowledge.html']
    ]},
    { label: '繼承房貸', items: [
      ['開始評估', '/intake.html?topic=inherited', 1],
      ['繼承的房子怎麼處理', '/inherited-property.html'],
      ['共有持分可以辦嗎?', '/article-inherited-co-owned-house-stuck.html'],
      ['產權相關文章', '/knowledge.html']
    ]},
    { label: '售後回租', items: [
      ['開始評估', '/intake.html?topic=leaseback', 1],
      ['售後回租怎麼運作', '/sale-leaseback.html'],
      ['回租相關文章', '/knowledge.html']
    ]},
    { label: '小工具', items: [
      ['謄本解析', '/tools-lab/deed-reader.html'],
      ['二胎增貸試算', '/second-mortgage-calculator.html'],
      ['新北房屋稅試算', '/new-taipei-house-tax.html'],
      ['全部小工具', '/tools.html']
    ]},
    { label: '案例分享', items: [
      ['X 先生的民間換約(四天走完)', '/case-private-refinance.html'],
      ['中和屋主的貸款整合(匿名)', '/case-zhonghe-consolidation.html'],
      ['核可案例:自營業者民間轉銀行(匿名)', '/case-private-to-bank.html'],
      ['被朋友拖下水,三個月走出來', '/case-friend-debt.html'],
      ['月收入 6 萬、多筆負債怎麼整理(情境試算)', '/case-income-60k.html']
    ]}
  ];
  function links(items, cls) {
    return items.map(function (it) {
      var badge = it[3] ? '<span class="cx-badge">' + it[3] + '</span>' : '';
      return '<a href="' + it[1] + '"' + (it[2] ? ' class="' + cls + '"' : '') + '>' + it[0] + badge + '</a>';
    }).join('');
  }
  var desktop = MENU.map(function (m) {
    return '<li><button type="button" aria-haspopup="true" aria-expanded="false">' + m.label + '</button>' +
           '<div class="cx-dd">' + links(m.items, 'go') + '</div></li>';
  }).join('');
  var mobile = MENU.map(function (m) {
    return '<details><summary>' + m.label + '</summary>' + links(m.items, 'go') + '</details>';
  }).join('');
  var mount = document.getElementById('nav');
  var ctaHtml = '<a class="cx-cta" href="tel:0222490517" data-link-location="nav" aria-label="電話諮詢 02-2249-0517"><span class="cx-cta-n">02-2249-0517</span><span class="cx-cta-s">電話諮詢</span></a>';
  var ncHtml = '<div class="cx-nc"><button type="button" class="cx-nc-btn" aria-expanded="false" aria-controls="cxNc">聯絡</button>' +
    '<div class="cx-nc-panel" id="cxNc" data-cx-hours><p class="cx-nc-k">電話諮詢</p>' +
    '<a class="cx-nc-tel" href="tel:0222490517" data-link-location="nav_contact">02-2249-0517</a>' +
    '<p class="cx-nc-open">接聽時間：週一至週五 10:00–17:00</p><p class="cx-nc-closed">現在是非接聽時間。<br>先用 LINE 留言，我們上班後回覆您。</p>' +
    '<a class="cx-nc-line" href="https://lin.ee/PHIfSoY" target="_blank" rel="noopener" data-link-location="nav_contact">LINE 留言</a></div></div>';
  var sheetCtaHtml = '<a class="cta" href="tel:0222490517" data-link-location="mobile_menu">電話諮詢 02-2249-0517</a><a href="https://lin.ee/PHIfSoY" data-link-location="mobile_menu">未接通？LINE 留言</a><p>接聽：週一至週五 10:00–17:00</p>';
  var html =
    '<nav class="cx-nav" aria-label="主導覽">' +
      '<div class="cx-in">' +
        '<a class="cx-logo" href="/"><span class="cx-mark">鋮</span>鋮馨租賃有限公司</a>' +
        '<ul class="cx-menu">' + desktop + '</ul>' +
        '<div class="cx-right">' + ncHtml +
          '<a class="cx-phone" href="tel:0222490517" aria-label="撥打 02-2249-0517">☎</a>' +
          '<a class="cx-resume" id="cxResume" href="/intake.html" hidden>回到我的評估</a>' +
          ctaHtml +
          '<button class="cx-burger" type="button" aria-label="開啟選單" aria-controls="cxSheet" aria-expanded="false">☰</button>' +
        '</div>' +
      '</div>' +
    '</nav>' +
    '<div class="cx-sheet" id="cxSheet">' + mobile +
      '<div class="cx-sheet-foot">' +
        sheetCtaHtml +
        '<a href="tel:0222490517">撥打 02-2249-0517</a>' +
      '</div>' +
    '</div>';
  document.head.insertAdjacentHTML('beforeend', '<style>' + css + '</style>');
  if (mount) mount.innerHTML = html;
  else document.body.insertAdjacentHTML('afterbegin', html);
  if (mount && mount.getAttribute('data-theme') === 'light') {
    document.querySelector('.cx-nav').classList.add('cx-light');
    document.getElementById('cxSheet').classList.add('cx-light');
  }
  var lis = document.querySelectorAll('.cx-menu>li');
  function closeAll() {
    lis.forEach(function (li) { li.classList.remove('open'); li.querySelector('button').setAttribute('aria-expanded', 'false'); });
  }
  lis.forEach(function (li) {
    var btn = li.querySelector('button');
    var leaveT = null;
    li.addEventListener('mouseenter', function () { clearTimeout(leaveT); closeAll(); li.classList.add('open'); btn.setAttribute('aria-expanded', 'true'); });
    li.addEventListener('mouseleave', function () { leaveT = setTimeout(function () { li.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); }, 180); });
    btn.addEventListener('click', function () {
      var on = li.classList.contains('open'); closeAll();
      if (!on) { li.classList.add('open'); btn.setAttribute('aria-expanded', 'true'); }
    });
  });
  document.addEventListener('click', function (e) { if (!e.target.closest('.cx-menu')) closeAll(); });
  var nc = document.querySelector('.cx-nc'), ncBtn = nc.querySelector('.cx-nc-btn');
  function closeNc(focus) {
    if (!nc.classList.contains('open')) return;
    nc.classList.remove('open'); ncBtn.setAttribute('aria-expanded', 'false');
    if (focus) ncBtn.focus();
  }
  ncBtn.addEventListener('click', function () {
    if (nc.classList.contains('open')) { closeNc(false); return; }
    closeAll(); nc.classList.add('open'); ncBtn.setAttribute('aria-expanded', 'true');
  });
  nc.addEventListener('focusout', function (e) { if (!nc.contains(e.relatedTarget)) closeNc(false); });
  document.addEventListener('click', function (e) { if (!e.target.closest('.cx-nc')) closeNc(false); });
  document.querySelector('.cx-menu').addEventListener('mouseenter', function () { closeNc(false); });
  if (window.__cxHours) window.__cxHours.apply();
  function noCard() {
    if (!document.documentElement.hasAttribute('data-cx-dcard') && !document.querySelector('[data-include="footer"],.cx-site-footer')) document.documentElement.setAttribute('data-cx-dcard', 'none');
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', noCard); else noCard();
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (nc.classList.contains('open')) { closeNc(true); return; }
    var active = document.querySelector('.cx-menu>li.open>button');
    closeAll();
    if (sheet.classList.contains('open')) closeSheet(true);
    else if (active) active.focus();
  });
  var burger = document.querySelector('.cx-burger');
  var sheet = document.getElementById('cxSheet');
  var previousOverflow = '';
  function closeSheet(restoreFocus) {
    var wasOpen = sheet.classList.contains('open');
    sheet.classList.remove('open');
    burger.setAttribute('aria-expanded', 'false');
    burger.setAttribute('aria-label', '開啟選單');
    burger.textContent = '☰';
    if (wasOpen) document.body.style.overflow = previousOverflow;
    if (wasOpen && restoreFocus) burger.focus();
  }
  burger.addEventListener('click', function () {
    if (sheet.classList.contains('open')) { closeSheet(true); return; }
    previousOverflow = document.body.style.overflow;
    sheet.classList.add('open');
    burger.setAttribute('aria-expanded', 'true');
    burger.setAttribute('aria-label', '關閉選單');
    burger.textContent = '✕';
    document.body.style.overflow = 'hidden';
  });
  sheet.addEventListener('click', function (e) {
    if (e.target.closest('a')) closeSheet(false);
  });
  window.addEventListener('resize', function () {
    if (window.innerWidth > 900) closeSheet(false);
  });
  try {
    var s = JSON.parse(localStorage.getItem('cx_intake_v1') || '{}');
    if (!Number.isFinite(s.updatedAt) || Date.now() - s.updatedAt >= 24 * 60 * 60 * 1000 || s.updatedAt > Date.now() || s.done) {
      localStorage.removeItem('cx_intake_v1');
      s = {};
    }
    if (s.topic && s.stepName && s.stepName !== 'topic' && !s.done) {
      var r = document.getElementById('cxResume');
      r.hidden = false;
      r.href = '/intake.html?topic=' + encodeURIComponent(s.topic);
      r.textContent = '回到我的評估';
    }
  } catch (e) {}
  var path = location.pathname + location.search;
  var hit = [];
  MENU.forEach(function (m, i) {
    if (m.items.some(function (it) { return it[1] === path; })) hit.push(i);
  });
  if (hit.length === 1) lis[hit[0]].querySelector('button').style.color = 'var(--cx-orange-deep)';
})();
