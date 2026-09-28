
(function () {
  if (window.__cxDcard) return;
  window.__cxDcard = true;
  var off = false;
  try { off = sessionStorage.getItem('cx_dcard_off') === '1'; } catch (e) {}
  var at = document.querySelector('.cx-sticky-cta') || document.querySelector('.cx-site-footer');
  if (off || document.querySelector('.nf-mimi') || !at) { document.documentElement.setAttribute('data-cx-dcard', 'none'); return; }
  var st = document.createElement('style');
  st.textContent = ".cx-dcard,.cx-dpill{display:none}\n@media(min-width:1024px){\n.cx-dcard{position:fixed;left:24px;bottom:24px;z-index:90;display:grid;grid-template-columns:64px minmax(0,1fr);gap:10px 14px;width:292px;padding:16px 16px 16px 18px; background:var(--cx-card);color:var(--cx-ink);border:1px solid var(--cx-line);border-radius:16px;box-shadow:0 18px 40px -16px var(--cx-ink-shadow); font-family:'Noto Sans TC',-apple-system,'PingFang TC','Microsoft JhengHei',sans-serif;line-height:1.45; opacity:0;visibility:hidden;transform:translateY(10px);transition:opacity .18s ease,transform .18s ease,visibility 0s linear .18s}\n.cx-dpill{position:fixed;left:12px;bottom:24px;z-index:90;display:inline-flex;align-items:center;gap:8px;height:48px;padding:0 16px 0 14px;border:1.5px solid var(--cx-ink);border-radius:999px; background:var(--cx-card);color:var(--cx-ink);font:700 15px/1 'Noto Sans TC',-apple-system,'PingFang TC','Microsoft JhengHei',sans-serif;letter-spacing:.04em;cursor:pointer; box-shadow:0 12px 28px -12px var(--cx-ink-shadow);opacity:0;visibility:hidden;transform:translateY(10px);transition:opacity .18s ease,transform .18s ease,visibility 0s linear .18s,background-color .18s ease}\n.cx-dpill:hover{background:var(--cx-cream-2)}\n.cx-dpill svg{fill:currentColor;flex:none}\n.cx-dcard[data-mode=\"full\"][data-show],.cx-dcard[data-open],.cx-dpill[data-show]{opacity:1;visibility:visible;transform:none;transition:opacity .18s ease,transform .18s ease,visibility 0s linear 0s}\n.cx-dcard[data-open]{left:12px;bottom:84px}\n}\n.cx-dcard p{margin:0}\n.cx-dcard-top{grid-column:1/-1}\n.cx-dcard-k{padding-right:28px;font-size:14px;font-weight:600;color:var(--cx-ink-2)}\n.cx-dcard-tel{display:inline-block;margin-top:2px;font-size:27px;line-height:1.15;font-weight:800;letter-spacing:.01em;font-variant-numeric:tabular-nums;color:var(--cx-ink);text-decoration:none;text-underline-offset:4px}\n.cx-dcard-tel:hover{text-decoration:underline;text-decoration-color:var(--cx-gold)}\n.cx-dcard-h{margin-top:4px!important;font-size:14px;color:var(--cx-ink-2)}\n.cx-dcard-qr{grid-column:1;width:64px;height:64px;padding:4px;background:#fff;border:1px solid var(--cx-line);border-radius:8px;box-sizing:content-box;image-rendering:pixelated}\n.cx-dcard-line-wrap{display:flex;flex-direction:column;justify-content:center;gap:8px;min-width:0}\n.cx-dcard-cap{font-size:14px;font-weight:600;color:var(--cx-ink)}\n.cx-dcard-line{display:inline-flex;align-items:center;justify-content:center;align-self:flex-start;min-height:40px;padding:0 16px;border-radius:999px;font-size:15px;font-weight:700;text-decoration:none;color:var(--cx-ink);box-shadow:inset 0 0 0 1.5px var(--cx-ink);transition:background-color .18s ease}\n.cx-dcard-line:hover{background:var(--cx-cream-2)}\n.cx-dcard[data-cx-open=\"0\"] .cx-dcard-line{background:var(--cx-orange);box-shadow:none}\n.cx-dcard[data-cx-open=\"0\"] .cx-dcard-line:hover{background:var(--cx-orange-soft)}\n.cx-dcard-closed{display:none}\n.cx-dcard[data-cx-open=\"0\"] .cx-dcard-closed{display:block}\n.cx-dcard[data-cx-open=\"0\"] .cx-dcard-open{display:none}\n.cx-dcard-x{position:absolute;top:8px;right:8px;width:32px;height:32px;display:grid;place-items:center;padding:0;border:0;border-radius:50%;background:transparent;color:var(--cx-ink-2);font:400 22px/1 sans-serif;cursor:pointer}\n.cx-dcard-x:hover{background:var(--cx-cream-2);color:var(--cx-ink)}\n.cx-dcard :focus-visible{outline:2px solid var(--cx-orange-deep);outline-offset:2px}\n.cx-dpill:focus-visible{outline:2px solid var(--cx-orange-deep);outline-offset:3px}\n@media print{.cx-dcard,.cx-dpill{display:none!important}}";
  var tmp = document.createElement('div');
  tmp.innerHTML = "<button type=\"button\" class=\"cx-dpill\" aria-expanded=\"false\" aria-controls=\"cxDcard\"><svg viewBox=\"0 0 24 24\" width=\"18\" height=\"18\" aria-hidden=\"true\"><path d=\"M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z\"/></svg>聯絡</button><aside class=\"cx-dcard\" id=\"cxDcard\" data-cx-hours aria-label=\"快速聯絡\"><div class=\"cx-dcard-top\"><p class=\"cx-dcard-k\">電話諮詢</p><a class=\"cx-dcard-tel\" href=\"tel:0222490517\" data-link-location=\"sticky_bar\">02-2249-0517</a><p class=\"cx-dcard-h cx-dcard-open\">接聽時間：週一至週五 10:00–17:00</p><p class=\"cx-dcard-h cx-dcard-closed\">現在是非接聽時間。<br>先用 LINE 留言，我們上班後回覆您。</p></div><img class=\"cx-dcard-qr\" src=\"/img/line-qr.png\" width=\"64\" height=\"64\" alt=\"鋮馨租賃有限公司 LINE 官方帳號 QR Code\" loading=\"lazy\" decoding=\"async\"><div class=\"cx-dcard-line-wrap\"><p class=\"cx-dcard-cap\">手機掃碼加 LINE</p><a class=\"cx-dcard-line\" href=\"https://lin.ee/PHIfSoY\" target=\"_blank\" rel=\"noopener\" data-link-location=\"sticky_bar\">LINE 留言</a></div><button type=\"button\" class=\"cx-dcard-x\" aria-label=\"收起聯絡卡\">×</button></aside>";
  var ref = at.nextSibling;
  at.parentNode.insertBefore(st, ref);
  while (tmp.firstChild) at.parentNode.insertBefore(tmp.firstChild, ref);
  if (window.__cxHours) window.__cxHours.apply();
  var card = document.querySelector('.cx-dcard'), pill = document.querySelector('.cx-dpill');
  if (!card || !pill) return;
  function drop() { [card, pill].forEach(function (el) { if (el.parentNode) el.parentNode.removeChild(el); }); document.documentElement.setAttribute('data-cx-dcard', 'none'); }
  var mq = window.matchMedia ? window.matchMedia('(min-width:1024px)') : { matches: true };
  var HERO = '.bt-hero,.tp-hero,.art-hero,.hub-hero,.page-hero,.policy-hero,.ct-hero,.rv4-hero,.hero';
  var hero = document.querySelector(HERO);
  var foot = document.querySelector('.cx-site-footer');
  var footIn = false, ticking = false, mode = 'pill';
  var MIMI = /mimi|img\/uiux\/(S0[1-8]|O0\d|K01)\//i, mimiIn = [];
  var CTA = '.cta-box,.art-cta,.cta-section,.cta-strip,.bt-cta,.bt-btns,.tl-cta,.cx-call-block,.cx-hours-actions,.lq-section,.tp-next-links,.tp-tels,.contact-card', ctaIn = [], cio = null;
  var SKIP = 'nav,.cx-sheet,footer,.cx-dcard,.cx-dpill,.cx-sticky-cta,[class^="cw-"],[class*=" cw-"],.afm-overlay,.afm-bar,[data-page-updated],' + HERO;
  var BOXY = /^(IMG|INPUT|SELECT|TEXTAREA|IFRAME|BUTTON|VIDEO|CANVAS|svg)$/;
  function measure() {
    if (!mq.matches) { mode = 'none'; card.setAttribute('data-mode', mode); document.documentElement.setAttribute('data-cx-dcard', mode); collapse(false); upd(); return; }
    watchCta();
    var min = Infinity, vw = window.innerWidth, rg = document.createRange();
    var cutoff = limit() + window.innerHeight - 24 - 224;
    var w = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT, {
      acceptNode: function (n) { return n.matches(SKIP) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT; }
    });
    for (var e = w.nextNode(); e; e = w.nextNode()) {
      var r = e.getBoundingClientRect();
      if (r.width < 2 || r.height < 2 || r.right < 0 || r.left >= min || r.bottom + window.scrollY < cutoff) continue;
      var cs = getComputedStyle(e);
      if (cs.visibility === 'hidden' || cs.position === 'fixed') continue;
      var boxy = BOXY.test(e.tagName) || (r.width < vw * 0.95 && (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' || parseFloat(cs.borderLeftWidth) > 0 || cs.boxShadow !== 'none'));
      if (boxy) { min = r.left; continue; }
      for (var c = e.firstChild; c; c = c.nextSibling) {
        if (c.nodeType !== 3 || !c.textContent.trim()) continue;
        rg.selectNodeContents(c);
        var rs = rg.getClientRects();
        for (var i = 0; i < rs.length; i++) if (rs[i].width > 0 && rs[i].left < min) min = rs[i].left;
      }
    }
    mode = min >= 328 ? 'full' : min >= 106 ? 'pill' : 'none';
    card.setAttribute('data-mode', mode);
    document.documentElement.setAttribute('data-cx-dcard', mode);
    if (mode !== 'pill') collapse(false);
    upd();
  }
  function limit() {
    if (!hero) return window.innerHeight * 0.6;
    return Math.max(0, hero.getBoundingClientRect().bottom + window.scrollY - 64);
  }
  function upd() {
    ticking = false;
    var on = mq.matches && !footIn && !mimiIn.length && !ctaIn.length && window.scrollY > limit();
    var el = mode === 'full' ? card : mode === 'pill' ? pill : null;
    if (el && on) el.setAttribute('data-show', ''); else if (el) el.removeAttribute('data-show');
    (mode === 'full' ? pill : card).removeAttribute('data-show');
    if (!el) pill.removeAttribute('data-show');
    if (!on && card.hasAttribute('data-open')) collapse(false);
  }
  function req() { if (!ticking) { ticking = true; window.requestAnimationFrame(upd); } }
  function collapse(focusPill) {
    card.removeAttribute('data-open');
    pill.setAttribute('aria-expanded', 'false');
    if (focusPill) pill.focus();
  }
  pill.addEventListener('click', function () {
    if (card.hasAttribute('data-open')) { collapse(false); return; }
    card.setAttribute('data-open', '');
    pill.setAttribute('aria-expanded', 'true');
  });
  card.querySelector('.cx-dcard-x').addEventListener('click', function () {
    if (mode === 'pill') { collapse(true); return; }
    card.removeAttribute('data-show');
    try { sessionStorage.setItem('cx_dcard_off', '1'); } catch (e) {}
    setTimeout(drop, 200);
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && card.hasAttribute('data-open')) collapse(true); });
  document.addEventListener('click', function (e) { if (card.hasAttribute('data-open') && !e.target.closest('.cx-dcard,.cx-dpill')) collapse(false); });
  window.addEventListener('scroll', req, { passive: true });
  var rt = null;
  window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(measure, 150); req(); });
  if (foot && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (es) { footIn = es[0].isIntersecting; req(); }).observe(foot);
  }
  if ('IntersectionObserver' in window) {
    var mio = new IntersectionObserver(function (es) {
      es.forEach(function (e) { var k = mimiIn.indexOf(e.target); if (e.isIntersecting && k < 0) mimiIn.push(e.target); else if (!e.isIntersecting && k >= 0) mimiIn.splice(k, 1); });
      req();
    });
    Array.prototype.forEach.call(document.images, function (i) { if (MIMI.test(i.currentSrc || i.src || '')) mio.observe(i); });
    cio = new IntersectionObserver(function (es) {
      es.forEach(function (e) { var k = ctaIn.indexOf(e.target); if (e.isIntersecting && k < 0) ctaIn.push(e.target); else if (!e.isIntersecting && k >= 0) ctaIn.splice(k, 1); });
      req();
    }, { rootMargin: '-64px 0px 0px 0px' });
    watchCta();
  }
  function watchCta() {
    if (!cio) return;
    document.querySelectorAll('a[href^="tel:"],a[href*="lin.ee/"]').forEach(function (a) {
      var b = !a.closest('nav,.cx-sheet,footer,.cx-dcard,.cx-sticky-cta,[class^="cw-"],[class*=" cw-"],.afm-overlay,.afm-bar') && a.closest(CTA);
      if (b) cio.observe(b);
    });
  }
  card.setAttribute('data-mode', mode);
  upd();
  if (document.readyState === 'complete') measure(); else window.addEventListener('load', measure, { once: true });
})();
