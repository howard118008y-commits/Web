/* A phone_click means a click on our business number, never a connected call.
 * One delegated listener, guarded against duplicate loading. No form data, query
 * string, link text, phone number or financial narrative is sent to analytics.
 */
(function () {
  'use strict';
  if (window.__cxConsultationTracking) return;
  window.__cxConsultationTracking = true;
  var pageNeeds = {
    '/debt-consolidation.html': 'private_debt',
    '/article-loan-integration.html': 'private_debt',
    '/private-to-bank.html': 'private_to_bank',
    '/article-private-loan-to-bank.html': 'private_to_bank',
    '/second-mortgage.html': 'second_mortgage',
    '/article-second-mortgage-scam.html': 'second_mortgage',
    '/corporate-loan.html': 'corporate_loan',
    '/corporate-checkup.html': 'corporate_loan',
    '/article-self-employed-loan.html': 'corporate_loan'
  };
  // Confirmed 2026-09-11: 02 main line, 0931 work phone, 0958 owner Ms. Zheng.
  var phoneLinks = ['tel:0222490517', 'tel:02-2249-0517', 'tel:+886222490517', 'tel:+886-2-2249-0517', 'tel:+886 2 2249 0517',
    'tel:0931087996', 'tel:0931-087-996', 'tel:+886931087996', 'tel:+886-931-087-996', 'tel:+886 931 087 996',
    'tel:0958139786', 'tel:0958-139-786', 'tel:+886958139786', 'tel:+886-958-139-786', 'tel:+886 958 139 786'];
  var needs = ['general', 'private_debt', 'private_to_bank', 'second_mortgage', 'corporate_loan'];
  var positions = ['hero', 'after_ai', 'nav', 'mobile_menu', 'sticky_bar', 'footer', 'article_bottom', 'service_bottom', 'page'];
  document.addEventListener('click', function (event) {
    var a = event.target && event.target.closest && event.target.closest('a');
    if (!a || typeof window.gtag !== 'function') return;
    var href = a.getAttribute('href') || '';
    var isPhone = phoneLinks.indexOf(href) !== -1;
    var isLine = /^https:\/\/lin\.ee\/PHIfSoY(?:[?#]|$)/.test(href);
    if (!isPhone && !isLine) return;
    var context = a.closest('[data-consultation-need]');
    var need = context ? context.getAttribute('data-consultation-need') : pageNeeds[location.pathname];
    if (needs.indexOf(need) === -1) need = 'general';
    var positioned = a.closest('[data-link-location]');
    var position = positioned && positioned.getAttribute('data-link-location');
    if (positions.indexOf(position) === -1) {
      position = a.closest('.cx-sticky-cta') ? 'sticky_bar' :
        a.closest('.cx-sheet') ? 'mobile_menu' :
        a.closest('nav') ? 'nav' : a.closest('footer') ? 'footer' : 'page';
    }
    window.gtag('event', isPhone ? 'phone_click' : 'line_click', {
      page_path: location.pathname,
      consultation_need: need,
      link_location: position
    });
  });
})();
