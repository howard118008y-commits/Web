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
    } else {
      window.addEventListener('load', function () {
        loadDeferred(deferred);
      }, { once: true });
    }
  });
})();
