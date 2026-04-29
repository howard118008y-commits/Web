/**
 * 鋮馨網站共用模組載入器
 * 把每頁 <div data-include="nav"></div> 替換為 nav.html 內容
 * 自動標記目前頁面對應的 menu 項目為 active
 */
(function () {
  'use strict';

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
        // 用載入的 HTML 取代 placeholder
        var temp = document.createElement('div');
        temp.innerHTML = html.trim();
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

  document.addEventListener('DOMContentLoaded', function () {
    var includes = document.querySelectorAll('[data-include]');
    Promise.all(Array.from(includes).map(loadInclude)).then(markActiveNavLink);
  });
})();
