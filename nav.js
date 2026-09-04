/* 鋮馨全站導覽列
 * 用法:每頁 <body> 開頭放 <div id="nav"></div>,並引入 <script src="/nav.js"></script>
 * 頁面要留 padding-top 給固定導覽列(桌機 64px,手機 58px)
 */
(function () {
  var css = [
    '.cx-nav{position:fixed;top:0;left:0;right:0;z-index:100;background:rgba(18,33,58,.92);',
    'backdrop-filter:blur(14px);border-bottom:1px solid #2C4A6B;font-family:"Noto Sans TC",-apple-system,"PingFang TC","Microsoft JhengHei",sans-serif;color:#F2EFE8}',
    '.cx-nav *{box-sizing:border-box}',
    '.cx-nav a{color:inherit;text-decoration:none}',
    '.cx-in{max-width:1180px;margin:0 auto;padding:0 24px;height:64px;display:flex;align-items:center;gap:28px}',
    '.cx-logo{display:flex;align-items:center;gap:10px;font-family:"Noto Serif TC",serif;font-weight:900;font-size:17px;letter-spacing:.04em;white-space:nowrap}',
    '.cx-mark{width:30px;height:30px;border-radius:7px;background:#C8945A;color:#12213A;display:grid;place-items:center;font-size:16px;flex:none}',
    '.cx-menu{display:flex;gap:4px;list-style:none;margin:0;padding:0;margin-left:8px}',
    '.cx-menu>li{position:relative}',
    '.cx-menu>li>button{background:none;border:0;color:rgba(242,239,232,.7);font:inherit;font-size:14.5px;padding:10px 12px;border-radius:8px;cursor:pointer;transition:.15s}',
    '.cx-menu>li>button:hover,.cx-menu>li.open>button{color:#F2EFE8;background:rgba(242,239,232,.06)}',
    '.cx-dd{position:absolute;top:calc(100% + 6px);left:0;min-width:240px;background:#F7F5F0;border:1px solid #E2DED4;border-radius:12px;',
    'padding:8px;box-shadow:0 14px 36px rgba(0,0,0,.28);opacity:0;transform:translateY(-4px);pointer-events:none;transition:.15s}',
    '.cx-menu>li.open .cx-dd{opacity:1;transform:none;pointer-events:auto}',
    '.cx-dd a{display:block;padding:10px 12px;border-radius:8px;font-size:14px;color:#1B2F4A}',
    '.cx-dd a:hover{background:rgba(200,148,90,.1)}',
    '.cx-dd a.go{font-weight:700;color:#12213A;background:#C8945A;margin-bottom:6px}',
    '.cx-dd a.go:hover{background:#E0B685}',
    '.cx-dd a.go::after{content:" →"}',
    '.cx-badge{display:inline-block;background:#FAC775;color:#633806;font-size:11px;font-weight:500;padding:2px 9px;border-radius:999px;margin-left:8px;vertical-align:1px}',
    '.cx-right{margin-left:auto;display:flex;align-items:center;gap:10px}',
    '.cx-phone{width:40px;height:40px;border-radius:50%;border:1px solid #2C4A6B;display:grid;place-items:center;font-size:15px;color:rgba(242,239,232,.8)}',
    '.cx-phone:hover{border-color:#C8945A;color:#F2EFE8}',
    '.cx-resume{font-size:14px;color:rgba(242,239,232,.75);padding:8px 12px;border-radius:999px;border:1px solid transparent}',
    '.cx-resume:hover{color:#F2EFE8;border-color:#2C4A6B}',
    '.cx-cta{background:#C8945A;color:#12213A;font-weight:700;font-size:14.5px;padding:10px 22px;border-radius:999px;white-space:nowrap}',
    '.cx-cta:hover{background:#E0B685}',
    '.cx-burger{display:none;background:none;border:0;color:#F2EFE8;font-size:24px;cursor:pointer;padding:4px 6px}',
    '.cx-sheet{display:none;position:fixed;top:58px;left:0;right:0;bottom:0;background:#12213A;overflow:auto;padding:16px 20px 40px;z-index:99}',
    '.cx-sheet.open{display:block}',
    '.cx-sheet details{border-bottom:1px solid #2C4A6B}',
    '.cx-sheet summary{list-style:none;padding:16px 4px;font-size:16px;font-weight:500;cursor:pointer;display:flex;justify-content:space-between}',
    '.cx-sheet summary::-webkit-details-marker{display:none}',
    '.cx-sheet summary::after{content:"+";color:#C8945A;font-size:20px}',
    '.cx-sheet details[open] summary::after{content:"−"}',
    '.cx-sheet a{display:block;padding:11px 4px 11px 14px;font-size:15px;color:rgba(242,239,232,.8)}',
    '.cx-sheet a.go{color:#C8945A;font-weight:700}',
    '.cx-sheet .cx-sheet-foot{display:flex;flex-direction:column;gap:10px;margin-top:20px}',
    '.cx-sheet .cx-sheet-foot a{padding:14px;border-radius:10px;border:1px solid #2C4A6B;text-align:center;font-size:15px}',
    '.cx-sheet .cx-sheet-foot a.cta{background:#C8945A;color:#12213A;border-color:#C8945A;font-weight:700}',
    '@media(max-width:900px){.cx-in{height:58px;gap:14px}.cx-menu,.cx-resume,.cx-phone{display:none}.cx-burger{display:block}.cx-cta{padding:9px 16px;font-size:14px}}',
    '@media(max-width:400px){.cx-in{padding:0 14px;gap:8px}.cx-logo{font-size:15px;gap:7px}.cx-right{gap:6px}.cx-cta{padding:8px 12px;font-size:13.5px}}'
  ].join('');

  var MENU = [
    { label: '企業健檢', items: [
      ['開始企業評估', '/intake.html?topic=corporate', 1],
      ['企業相關文章', '/knowledge.html']
    ]},
    { label: '民間轉銀行', items: [
      ['開始評估', '/intake.html?topic=private-to-bank', 1],
      ['民間轉銀行怎麼運作', '/private-to-bank.html'],
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
      ['二胎增貸試算', '/zhonghe-second-mortgage.html'],
      ['新北房屋稅試算', '/new-taipei-house-tax.html'],
      ['全部小工具', '/tools.html']
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

  var html =
    '<nav class="cx-nav" aria-label="主導覽">' +
      '<div class="cx-in">' +
        '<a class="cx-logo" href="/"><span class="cx-mark">鋮</span>鋮馨租賃有限公司</a>' +
        '<ul class="cx-menu">' + desktop + '</ul>' +
        '<div class="cx-right">' +
          '<a class="cx-phone" href="tel:0222490517" aria-label="撥打 02-2249-0517">☎</a>' +
          '<a class="cx-resume" id="cxResume" href="/intake.html" hidden>回到我的評估</a>' +
          '<a class="cx-cta" href="/intake.html">免費評估</a>' +
          '<button class="cx-burger" type="button" aria-label="開啟選單" aria-expanded="false">☰</button>' +
        '</div>' +
      '</div>' +
    '</nav>' +
    '<div class="cx-sheet" id="cxSheet">' + mobile +
      '<div class="cx-sheet-foot">' +
        '<a class="cta" href="/intake.html">免費評估</a>' +
        '<a href="https://lin.ee/PHIfSoY">LINE 線上諮詢</a>' +
        '<a href="tel:0222490517">撥打 02-2249-0517</a>' +
      '</div>' +
    '</div>';

  document.head.insertAdjacentHTML('beforeend', '<style>' + css + '</style>');
  var mount = document.getElementById('nav');
  if (mount) mount.innerHTML = html;
  else document.body.insertAdjacentHTML('afterbegin', html);

  /* 桌機下拉:hover 開、點擊切換、點外面關、Esc 關 */
  var lis = document.querySelectorAll('.cx-menu>li');
  function closeAll() {
    lis.forEach(function (li) { li.classList.remove('open'); li.querySelector('button').setAttribute('aria-expanded', 'false'); });
  }
  lis.forEach(function (li) {
    var btn = li.querySelector('button');
    li.addEventListener('mouseenter', function () { closeAll(); li.classList.add('open'); btn.setAttribute('aria-expanded', 'true'); });
    li.addEventListener('mouseleave', function () { li.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); });
    btn.addEventListener('click', function () {
      var on = li.classList.contains('open'); closeAll();
      if (!on) { li.classList.add('open'); btn.setAttribute('aria-expanded', 'true'); }
    });
  });
  document.addEventListener('click', function (e) { if (!e.target.closest('.cx-menu')) closeAll(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { closeAll(); sheet.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); } });

  /* 手機:漢堡開全螢幕選單 */
  var burger = document.querySelector('.cx-burger');
  var sheet = document.getElementById('cxSheet');
  burger.addEventListener('click', function () {
    var open = sheet.classList.toggle('open');
    burger.setAttribute('aria-expanded', String(open));
    burger.textContent = open ? '✕' : '☰';
    document.body.style.overflow = open ? 'hidden' : '';
  });

  /* 有填過的進度才顯示「回到我的評估」(對應 Better 的 Sign in) */
  try {
    var s = JSON.parse(localStorage.getItem('cx_intake_v1') || '{}');
    if (s.topic && s.stepName && s.stepName !== 'topic' && !s.done) {
      var r = document.getElementById('cxResume');
      r.hidden = false;
      r.href = '/intake.html?topic=' + encodeURIComponent(s.topic);
      r.textContent = '回到我的評估';
    }
  } catch (e) {}

  /* 標記目前所在的產品線 */
  var path = location.pathname + location.search;
  MENU.forEach(function (m, i) {
    if (m.items.some(function (it) { return it[1] === path; })) lis[i].querySelector('button').style.color = '#C8945A';
  });
})();
