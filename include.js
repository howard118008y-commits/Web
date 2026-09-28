
(function () {
  'use strict';
  var DEFERRED = ['anti-fraud-modal', 'chat-widget'];
  function loadInclude(el) {
    var src = el.dataset.include;
    if (!src) return Promise.resolve();
    var file = src + '.html';
    return fetch(file)
      .then(function (r) {
        if (!r.ok) throw new Error('無法載入 ' + file);
        return r.text();
      })
      .then(function (html) {
        var temp = document.createElement('div');
        temp.innerHTML = html.trim();
        temp.querySelectorAll('meta[name]').forEach(function (meta) {
          var name = (meta.getAttribute('name') || '').trim().toLowerCase();
          if (['robots', 'googlebot', 'googlebot-news', 'bingbot'].indexOf(name) !== -1) {
            meta.remove();
          }
        });
        temp.querySelectorAll('script').forEach(function (oldScript) {
          var newScript = document.createElement('script');
          Array.from(oldScript.attributes).forEach(function (attr) {
            newScript.setAttribute(attr.name, attr.value);
          });
          newScript.text = oldScript.textContent;
          oldScript.parentNode.replaceChild(newScript, oldScript);
        });
        while (temp.firstChild) {
          el.parentNode.insertBefore(temp.firstChild, el);
        }
        el.parentNode.removeChild(el);
      })
      .catch(function (err) {
        console.error('include.js:', err);
      });
  }
  function markActiveNavLink() {
    var path = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
    var pageKey = path.replace('.html', '');
    document.querySelectorAll('nav a[data-page]').forEach(function (a) {
      if (a.dataset.page === pageKey) {
        a.classList.add('active');
      }
    });
  }
  function showPageUpdated() {
    if (document.querySelector('[data-page-updated]')) return;
    if (/最後更新|更新日期|更新於/.test(document.body.innerText || '')) return;
    var latest = '';
    document.querySelectorAll('script[type="application/ld+json"]').forEach(function (s) {
      (s.textContent.match(/"dateModified"\s*:\s*"(\d{4}-\d{2}-\d{2})/g) || []).forEach(function (m) {
        var d = m.slice(-10);
        if (d > latest) latest = d;
      });
    });
    if (!latest) return;
    var p = document.createElement('p');
    p.setAttribute('data-page-updated', '');
    p.style.cssText = 'max-width:1100px;margin:32px auto 12px;padding:0 20px;font-size:13px;line-height:1.6;text-align:center;color:inherit;opacity:.6';
    var t = latest.split('-');
    p.innerHTML = '本頁最後更新：<time datetime="' + latest + '">' + t[0] + ' 年 ' + (+t[1]) + ' 月 ' + (+t[2]) + ' 日</time>';
    var footer = document.querySelector('footer');
    if (footer) footer.parentNode.insertBefore(p, footer);
    else document.body.appendChild(p);
  }
  function enhanceTables() {
    var mq = window.matchMedia ? window.matchMedia('(max-width:480px)') : null;
    var boxes = [];
    function opaqueBg(el) {
      while (el && el.nodeType === 1) {
        var c = getComputedStyle(el).backgroundColor;
        var m = c && c.match(/[\d.]+/g);
        if (m && (m.length < 4 || +m[3] > 0.9)) return c;
        el = el.parentElement;
      }
      return 'rgb(255, 255, 255)';
    }
    function update(box) {
      var sc = box.__cxScroller;
      var more = sc.scrollWidth - sc.clientWidth - sc.scrollLeft > 2;
      if (more) box.setAttribute('data-cx-more', ''); else box.removeAttribute('data-cx-more');
      if (sc.scrollLeft > 24) box.setAttribute('data-cx-scrolled', '');
      if (more && !box.__cxRoom) {
        box.__cxRoom = true;
        var prev = box.previousElementSibling;
        var gap = prev ? sc.getBoundingClientRect().top - prev.getBoundingClientRect().bottom : parseFloat(getComputedStyle(sc).marginTop) || 0;
        if (gap < 28) box.style.marginTop = '28px';
      }
    }
    function freeze(box) {
      var t = box.__cxTable, sc = box.__cxScroller;
      var ok = mq && mq.matches && !box.__cxSpan && !box.hasAttribute('data-cx-form') && box.__cxCols >= 3 && sc.scrollWidth > sc.clientWidth + 2;
      if (ok) {
        var first = t.rows[0] && t.rows[0].cells[0];
        ok = !!first && first.getBoundingClientRect().width <= sc.clientWidth * 0.45;
      }
      if (!ok) { box.removeAttribute('data-cx-freeze'); return; }
      box.setAttribute('data-cx-freeze', '');
      if (!box.__cxMo && 'MutationObserver' in window) {
        box.__cxMo = new MutationObserver(function () { if (box.hasAttribute('data-cx-freeze')) freeze(box); });
        box.__cxMo.observe(t, { childList: true, subtree: true });
      }
      Array.prototype.forEach.call(t.rows, function (r) {
        var c = r.cells[0];
        if (!c || c.getAttribute('data-cx-bg')) return;
        c.setAttribute('data-cx-bg', '1');
        var bg = getComputedStyle(c).backgroundColor;
        if (/rgba\(.*,\s*0(\.\d+)?\)$|transparent/.test(bg)) c.style.backgroundColor = opaqueBg(c.parentElement);
      });
    }
    Array.prototype.forEach.call(document.querySelectorAll('table'), function (t) {
      if (t.closest('.cx-tbox') || t.closest('[class^="cw-"],[class*=" cw-"]')) return;
      var sc = null;
      [t.parentElement, t.parentElement && t.parentElement.parentElement].some(function (el) {
        if (el && el !== document.body && /(auto|scroll)/.test(getComputedStyle(el).overflowX)) { sc = el; return true; }
        return false;
      });
      if (!sc) {
        sc = document.createElement('div');
        sc.className = 'cx-tscroll';
        t.parentNode.insertBefore(sc, t);
        sc.appendChild(t);
      }
      var box = document.createElement('div');
      box.className = 'cx-tbox';
      sc.parentNode.insertBefore(box, sc);
      box.appendChild(sc);
      var hint = document.createElement('span');
      hint.className = 'cx-thint';
      hint.setAttribute('aria-hidden', 'true');
      hint.textContent = '左右滑動看更多';
      box.appendChild(hint);
      box.__cxScroller = sc;
      box.__cxTable = t;
      box.__cxSpan = !!t.querySelector('[rowspan]:not([rowspan="1"]),[colspan]:not([colspan="1"])');
      if (t.querySelector('input,select,textarea')) box.setAttribute('data-cx-form', '');
      box.__cxCols = Math.max.apply(null, Array.prototype.map.call(t.rows, function (r) { return r.cells.length; }).concat(0));
      sc.addEventListener('scroll', function () { update(box); }, { passive: true });
      boxes.push(box);
    });
    if (!boxes.length) return;
    function all() { boxes.forEach(function (b) { freeze(b); update(b); }); }
    all();
    if ('ResizeObserver' in window) {
      var ro = new ResizeObserver(function (entries) {
        entries.forEach(function (e) { var b = e.target.closest('.cx-tbox'); if (b) { freeze(b); update(b); } });
      });
      boxes.forEach(function (b) { ro.observe(b.__cxScroller); ro.observe(b.__cxTable); });
    } else {
      window.addEventListener('resize', all);
    }
  }
  function loadDeferred(deferredEls) {
    if (!deferredEls.length) return;
    var run = function () {
      Promise.all(deferredEls.map(loadInclude));
    };
    if ('requestIdleCallback' in window) {
      requestIdleCallback(run, { timeout: 2500 });
    } else {
      setTimeout(run, 300);
    }
  }
  function loadMotion() {
    if (window.__cxMotionLoaded) return;
    window.__cxMotionLoaded = true;
    function add(src, cb) {
      var s = document.createElement('script');
      s.src = src;
      s.onload = cb || null;
      document.body.appendChild(s);
    }
    add('/js/gsap.min.js', function () {
      add('/js/ScrollTrigger.min.js', function () {
        add('/js/cx-motion.js');
      });
    });
  }
  document.addEventListener('DOMContentLoaded', function () {
    var runTables = function () { try { enhanceTables(); } catch (e) {  } };
    if ('requestIdleCallback' in window) requestIdleCallback(runTables, { timeout: 1500 }); else setTimeout(runTables, 300);
    if (!document.querySelector('[data-include="chat-widget"]')) {
      var cw = document.createElement('div');
      cw.dataset.include = 'chat-widget';
      document.body.appendChild(cw);
    }
    var all = Array.from(document.querySelectorAll('[data-include]'));
    var immediate = [];
    var deferred = [];
    all.forEach(function (el) {
      if (DEFERRED.indexOf(el.dataset.include) >= 0) {
        deferred.push(el);
      } else {
        immediate.push(el);
      }
    });
    if (immediate.some(function (el) { return el.dataset.include === 'footer'; })) {
      var early = function (src, tokensOnly) {
        var s = document.createElement('script');
        s.src = src;
        s.fetchPriority = 'high';
        if (tokensOnly) s.setAttribute('data-cx-tokens-only', '');
        document.head.appendChild(s);
      };
      if (!window.__cxHours && !document.querySelector('script[src$="cx-hours.js"]')) early('/cx-hours.js');
      if (!document.getElementById('cx-brand') && !document.querySelector('script[src$="nav.js"]')) early('/nav.js', true);
    }
    Promise.all(immediate.map(loadInclude)).then(function () {
      markActiveNavLink();
      showPageUpdated();
    });
    if (document.readyState === 'complete') {
      loadDeferred(deferred);
      loadMotion();
    } else {
      window.addEventListener('load', function () {
        loadDeferred(deferred);
        loadMotion();
      }, { once: true });
    }
  });
  (function trackIntentSignals() {
    if (typeof window === 'undefined') return;
    var sentViewContent = false;
    function fireViewContent(reason) {
      if (sentViewContent || typeof window.fbq !== 'function') return;
      sentViewContent = true;
      try {
        window.fbq('track', 'ViewContent', {
          content_name: document.title.slice(0, 100),
          content_category: location.pathname,
          trigger: reason
        });
      } catch (e) {  }
    }
    var scrollBound = function () {
      if (sentViewContent) { window.removeEventListener('scroll', scrollBound); return; }
      var doc = document.documentElement;
      var scrollable = doc.scrollHeight - window.innerHeight;
      if (scrollable <= 0) return;
      if ((window.scrollY || doc.scrollTop) / scrollable >= 0.5) fireViewContent('scroll50');
    };
    window.addEventListener('scroll', scrollBound, { passive: true });
    var stayed = 0;
    var timer = setInterval(function () {
      if (document.visibilityState === 'visible') stayed += 1;
      if (stayed >= 30) {
        clearInterval(timer);
        fireViewContent('dwell30s');
      }
    }, 1000);
    var sentContact = false;
    document.addEventListener('click', function (e) {
      if (sentContact || typeof window.fbq !== 'function') return;
      var a = e.target && e.target.closest && e.target.closest('a');
      if (!a || !a.href) return;
      var isLine = a.href.indexOf('lin.ee') > -1 || a.href.indexOf('line.me') > -1;
      var isTel = a.href.indexOf('tel:') === 0;
      if (!isLine && !isTel) return;
      sentContact = true;
      try {
        window.fbq('track', 'Contact', {
          content_category: location.pathname,
          method: isLine ? 'line' : 'phone'
        });
      } catch (err) {  }
    }, true);
  })();
})();
