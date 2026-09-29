/* 接聽時段（週一至五 10:00–17:00）改動時，index.html 開頭的 inline 與 nav.js 開頭的首繪判斷要同步改 */
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
  /* 固定條讓位的主鈕：聯絡區、工具鈕，加上各模板 hero 內的電話／LINE／按鈕型連結／表單（HERO 清單同 cx-dcard.js） */
  var PRIMARY = '[data-cx-hours] .cx-hours-actions, .cx-tool-go, ' +
    ':is(.bt-hero,.tp-hero,.art-hero,.hub-hero,.page-hero,.policy-hero,.ct-hero,.rv4-hero,.hero) :is(a[href^="tel:"],a[href*="lin.ee/"],a[class*="btn"],form)';
  function watchPrimaryCta() {
    var root = document.documentElement;
    if (!('IntersectionObserver' in window)) { root.removeAttribute('data-cx-cta-inview'); return; }
    var seen = new Set(), inView = new Set();
    function mark() {
      if (!seen.size) { if (root.hasAttribute('data-cx-cta-inview')) root.removeAttribute('data-cx-cta-inview'); return; }
      var v = inView.size ? '1' : '0';
      if (root.getAttribute('data-cx-cta-inview') !== v) root.setAttribute('data-cx-cta-inview', v);
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) inView.add(e.target); else inView.delete(e.target); });
      mark();
    }, { rootMargin: '-58px 0px 0px 0px' });
    function scan() {
      var vh = window.innerHeight;
      document.querySelectorAll(PRIMARY).forEach(function (t) {
        if (seen.has(t)) return;
        seen.add(t); io.observe(t);
        var r = t.getBoundingClientRect();
        if (r.width > 0 && r.bottom > 58 && r.top < vh) inView.add(t);
      });
      inView.forEach(function (t) { if (!t.isConnected) inView.delete(t); });
      mark();
    }
    scan();
    /* 主題頁 hero 表單由 include 延後注入：有元素進出 DOM 就補掃（MutationObserver 在繪製前回呼，不會先閃出固定條） */
    if ('MutationObserver' in window) new MutationObserver(function (ms) {
      for (var i = 0; i < ms.length; i++) {
        for (var j = 0; j < ms[i].addedNodes.length; j++) if (ms[i].addedNodes[j].nodeType === 1) { scan(); return; }
        if (ms[i].removedNodes.length && inView.size) { scan(); return; }
      }
    }).observe(document.body, { childList: true, subtree: true });
  }
  window.__cxHours = { apply: apply, isOpen: isOpen };
  apply();
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { apply(); watchPrimaryCta(); });
  else watchPrimaryCta();
  setInterval(apply, 60 * 1000);
  document.addEventListener('visibilitychange', function () { if (!document.hidden) apply(); });
})();
