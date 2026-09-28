/* 接聽時段（週一至五 10:00–17:00）改動時，index.html 開頭的 inline 要同步改 */
(function () {
  'use strict';
  if (window.__cxHours) { window.__cxHours.apply(); return; }
  var OPEN_MIN = 10 * 60, CLOSE_MIN = 17 * 60;
  function taipeiNow() {
    var host = location.hostname;
    var fake = window.__CX_NOW;
    if ((host === 'localhost' || host === '127.0.0.1') && typeof fake === 'string' &&
        /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(fake)) {
      var p = fake.split(/[-T:]/).map(Number);
      return { day: new Date(Date.UTC(p[0], p[1] - 1, p[2])).getUTCDay(), min: p[3] * 60 + p[4] };
    }
    var t = new Date(Date.now() + 8 * 60 * 60 * 1000);
    return { day: t.getUTCDay(), min: t.getUTCHours() * 60 + t.getUTCMinutes() };
  }
  function isOpen() {
    var n = taipeiNow();
    return n.day >= 1 && n.day <= 5 && n.min >= OPEN_MIN && n.min < CLOSE_MIN;
  }
  function apply() {
    var v = isOpen() ? '1' : '0';
    if (document.documentElement.getAttribute('data-cx-open') !== v) document.documentElement.setAttribute('data-cx-open', v);
    document.querySelectorAll('[data-cx-hours], .cx-sticky-cta').forEach(function (el) {
      if (el.getAttribute('data-cx-open') !== v) el.setAttribute('data-cx-open', v);
    });
  }
  function watchPrimaryCta() {
    var targets = document.querySelectorAll('[data-cx-hours] .cx-hours-actions, .cx-tool-go');
    if (!targets.length || !('IntersectionObserver' in window)) {
      document.documentElement.removeAttribute('data-cx-cta-inview');
      return;
    }
    var vh = window.innerHeight;
    document.documentElement.setAttribute('data-cx-cta-inview', Array.prototype.some.call(targets, function (t) {
      var r = t.getBoundingClientRect(); return r.width > 0 && r.bottom > 58 && r.top < vh;
    }) ? '1' : '0');
    var inView = new Set();
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) inView.add(e.target); else inView.delete(e.target); });
      document.documentElement.setAttribute('data-cx-cta-inview', inView.size ? '1' : '0');
    }, { rootMargin: '-58px 0px 0px 0px' });
    targets.forEach(function (t) { io.observe(t); });
  }
  window.__cxHours = { apply: apply, isOpen: isOpen };
  apply();
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { apply(); watchPrimaryCta(); });
  else watchPrimaryCta();
  setInterval(apply, 60 * 1000);
  document.addEventListener('visibilitychange', function () { if (!document.hidden) apply(); });
})();
