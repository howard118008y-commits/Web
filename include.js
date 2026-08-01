/**
 * 鋮馨網站共用模組載入器
 * 把每頁 <div data-include="nav"></div> 替換為 nav.html 內容
 * 自動標記目前頁面對應的 menu 項目為 active
 *
 * 載入策略（為了 LCP）：
 * - nav / footer / line-qr：DOMContentLoaded 立即載入（影響首屏 layout）
 * - anti-fraud-modal / chat-widget：延遲到 idle / window load 後才載入（避免阻擋 hero LCP）
 * - chat-widget（小鋮 AI 助理）不必每頁加 div，由本檔自動注入全站生效
 */
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

  /**
   * 動態增強（GSAP 卡片 scroll-reveal）全站延遲載入。
   * 與 chat-widget 同策略：window load 後才載，絕不阻擋首屏 LCP。
   * onload 鏈保證順序 gsap → ScrollTrigger → cx-motion；用絕對路徑 /js/ 兼容 /en/ 等子目錄。
   * 任一環節失敗只是沒有動畫，內容照常顯示（cx-motion 內另有 gsap 存在性守衛）。
   */
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
    // 小鋮 AI 助理全站自動注入（延遲載入，不影響 LCP）
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

    Promise.all(immediate.map(loadInclude)).then(markActiveNavLink);

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

  /* ── Meta Pixel 中間層轉換訊號（2026-08-01 加）──────────────────
     背景：Pixel 原本只有 PageView(每週約 4,000) 與 Lead(每週約 4)，中間全空，
     Lead 量遠低於 Meta 轉換優化所需的每週 50 次門檻，無法用來做轉換投放。
     這裡補兩個中間訊號，讓 Meta 有足夠密度的意圖訊號可學習：

       ViewContent — 深度瀏覽（捲動 ≥50% 或停留 ≥30 秒），代表真的在看內容
       Contact     — 點 LINE 或撥電話，高意圖但量少，供日後往下切用

     兩者皆每頁只送一次；無 fbq（未載入 Pixel 的頁）時整段靜默跳過。 */
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
      } catch (e) { /* Pixel 未就緒，忽略 */ }
    }

    // 觸發條件一：捲動達 50%
    var scrollBound = function () {
      if (sentViewContent) { window.removeEventListener('scroll', scrollBound); return; }
      var doc = document.documentElement;
      var scrollable = doc.scrollHeight - window.innerHeight;
      if (scrollable <= 0) return;               // 頁面不可捲動，交給停留時間判定
      if ((window.scrollY || doc.scrollTop) / scrollable >= 0.5) fireViewContent('scroll50');
    };
    window.addEventListener('scroll', scrollBound, { passive: true });

    // 觸發條件二：停留滿 30 秒（分頁在背景時不計）
    var stayed = 0;
    var timer = setInterval(function () {
      if (document.visibilityState === 'visible') stayed += 1;
      if (stayed >= 30) {
        clearInterval(timer);
        fireViewContent('dwell30s');
      }
    }, 1000);

    // Contact：點 LINE / 電話（高意圖，量少，供日後切換用）
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
      } catch (err) { /* 忽略 */ }
    }, true);
  })();
})();
