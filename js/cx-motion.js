/* CX468 動態增強：below-fold 中性結構卡 scroll-reveal（僅視覺、零新內容）
   全站生效（由 include.js 於 window load 後延遲載入，快取共用、零 LCP 衝擊）。
   安全設計：①每個元素只在「載入時位於 below-fold」才納入動畫，首屏可見的完全不動（保護 LCP、避免閃爍）
   ②只動 opacity/transform（走合成層，零 layout/CLS）③defer/延遲載入、非阻斷渲染
   ④prefers-reduced-motion 自動全關 ⑤JS 未載入時內容照常顯示（不靠 CSS 藏，SEO 安全）
   ⑥once＝動完即殺 ⑦選擇器在該頁不存在＝自動略過。

   ⚠️ 合規策展（媽祖 2026-07-10 核）：白名單制——只淡入「中性結構卡」。敏感盒
   （warn-box / warning-box / price-box / info-box / highlight-box / cta-box / example-box /
   split-box / insight-box / def-num 三要件 / 月付案例卡）**不作為直接動畫目標**；
   若它巢狀於白名單卡內（如地價稅頁 price-box 在 step-card 內），則隨整卡「同進同出」——
   限定語/免責永不與其主張分離（合規實質標準），非「數字永不動」。
   ⚠️ 治理：白名單按 class 不按頁。新頁面若重用下列白名單 class 名，會自動被納入動畫、不經審查——
   新頁上線前的媽祖把關須包含「本頁是否有白名單 class 誤動到敏感內容」這一項檢查。 */
(function () {
  if (!window.gsap || !window.ScrollTrigger) return;   // 載入失敗＝優雅退場，內容照常
  gsap.registerPlugin(ScrollTrigger);

  var mm = gsap.matchMedia();
  mm.add("(prefers-reduced-motion: no-preference)", function () {

    /* 動畫收尾一律 clearProps：inline 的 opacity/transform 完全移除，
       元素不可能停在中途透明度（原本靠 once＝動完即殺，若 tween 未跑完就被殺會永久半透明）。 */
    function settle(els) {
      gsap.set(els, { clearProps: "opacity,transform" });
    }

    function revealGroup(selector, stagger) {
      var els = gsap.utils.toArray(selector).filter(function (el) {
        return el.getBoundingClientRect().top > window.innerHeight * 0.85;   // 只動 below-fold
      });
      if (!els.length) return;
      gsap.set(els, { opacity: 0, y: 26 });
      els.forEach(function (el) { el.setAttribute("data-cx-reveal", ""); });  // 供 failsafe 掃描
      ScrollTrigger.batch(els, {
        start: "top 90%", once: true,
        onEnter: function (batch) {
          gsap.to(batch, {
            opacity: 1, y: 0, duration: 0.55, ease: "power2.out", stagger: stagger || 0.09,
            onComplete: function () { settle(batch); }
          });
        }
      });
    }

    /* Failsafe：捲動位置被「跳著換」時（bfcache 上一頁還原／錨點落地／程式捲動），
       ScrollTrigger 的起訖值可能已過期而不再觸發 onEnter，元素會卡在 opacity 0。
       refresh() 重算後再掃一次：凡是已捲過觸發線卻仍不是全不透明的，直接還原。
       內容看得見 > 動畫演出。 */
    function failsafe() {
      var line = window.innerHeight * 0.9;
      document.querySelectorAll("[data-cx-reveal]").forEach(function (el) {
        if (el.getBoundingClientRect().top < line &&
            parseFloat(getComputedStyle(el).opacity) < 1) {
          gsap.killTweensOf(el);
          settle(el);
        }
      });
    }

    /* 全站 html{scroll-behavior:smooth}——錨點/還原的捲動要跑好幾百毫秒才到位，
       只掃一次會在元素還沒過觸發線時就掃完。故補掃多次。 */
    var timers = [];
    function sweep(delays) {
      delays.forEach(function (d) { timers.push(setTimeout(failsafe, d)); });
    }
    function resync() {
      ScrollTrigger.refresh();
      sweep([120, 600, 1500]);
    }
    window.addEventListener("pageshow", resync);      // bfcache 還原（上一頁 / 上一頁按鈕）
    window.addEventListener("hashchange", resync);    // 錨點跳轉
    // 捲動結束時再保險一次（scrollend 不支援就退回 scroll + debounce）
    var seTimer;
    if ("onscrollend" in window) {
      window.addEventListener("scrollend", failsafe);
    } else {
      window.addEventListener("scroll", function () {
        clearTimeout(seTimer); seTimer = setTimeout(failsafe, 200);
      }, { passive: true });
    }
    sweep([1200]);                                    // 首次載入後補一次（含錨點直接落地）

    // 中性結構卡白名單（選擇器不存在的頁面自動略過）。
    // 白名單制＝新頁型的卡片預設「不動」，要納入需明確加 selector＋過媽祖，避免誤 animate 到敏感盒。
    [
      ".tab-stack .tab-item",  // radar-index 系列卡
      "#monthly-focus",        // radar-index 本週焦點
      ".who-card",             // 適合對象
      ".flow-step",            // 流程步驟（售後回租）
      ".how-point",            // 運作要點
      ".step",                 // 流程步驟（貸款整合等）
      ".step-card",            // 流程卡（全站多頁）
      ".svc-card",             // 服務卡
      ".related-card",         // 延伸閱讀卡
      ".poi-card",             // 周邊機能卡
      ".loc-card",             // 地點卡
      ".live-card",            // 即時資料卡
      ".scenario-card",        // 情境卡
      ".chart-card",           // 圖表卡
      ".faq-item",             // FAQ 問答（整組 Q+A 同進同出）
      ".promise-item",         // 承諾清單
      ".proof-card",           // 首頁：信任證明卡
      ".diag-card",            // 首頁：服務導引卡
      ".proc-step"             // 首頁：流程步驟
    ].forEach(function (sel) { revealGroup(sel); });

    // 使用者中途切換成 prefers-reduced-motion 時，把本 context 掛的東西收乾淨
    return function () {
      timers.forEach(clearTimeout); clearTimeout(seTimer);
      window.removeEventListener("pageshow", resync);
      window.removeEventListener("hashchange", resync);
      window.removeEventListener("scrollend", failsafe);
      document.querySelectorAll("[data-cx-reveal]").forEach(function (el) {
        settle(el);
        el.removeAttribute("data-cx-reveal");
      });
    };
  });
})();
