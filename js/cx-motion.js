/* CX468 動態增強：below-fold 卡片 scroll-reveal（僅視覺、零新內容）
   三頁共用（radar-index / sale-leaseback / debt-consolidation）。
   安全設計：①每個元素只在「載入時位於 below-fold」才納入動畫，首屏可見的完全不動（保護 LCP、避免閃爍）
   ②只動 opacity/transform（走合成層，零 layout/CLS）③defer 載入、非阻斷渲染
   ④prefers-reduced-motion 自動全關 ⑤JS 未載入時內容照常顯示（不靠 CSS 藏，SEO 安全）
   ⑥once＝動完即殺，不留背景 tween ⑦選擇器在該頁不存在＝自動略過。 */
(function () {
  if (!window.gsap || !window.ScrollTrigger) return;   // 載入失敗＝優雅退場，內容照常
  gsap.registerPlugin(ScrollTrigger);

  var mm = gsap.matchMedia();
  mm.add("(prefers-reduced-motion: no-preference)", function () {

    function revealGroup(selector, stagger) {
      // 只挑「載入時確實在 below-fold」的元素，首屏可見的一律不碰
      var els = gsap.utils.toArray(selector).filter(function (el) {
        return el.getBoundingClientRect().top > window.innerHeight * 0.85;
      });
      if (!els.length) return;
      gsap.set(els, { opacity: 0, y: 26 });
      ScrollTrigger.batch(els, {
        start: "top 90%", once: true,
        onEnter: function (batch) {
          gsap.to(batch, {
            opacity: 1, y: 0, duration: 0.55, ease: "power2.out",
            stagger: stagger || 0.09
          });
        }
      });
    }

    // 各頁的成組卡片／段落（選擇器不存在的頁面自動略過）
    [
      ".tab-stack .tab-item",   // radar-index：系列卡
      "#monthly-focus",         // radar-index：本週房市焦點
      ".who-card",              // sale-leaseback：適合對象卡
      ".flow-step",             // sale-leaseback：流程步驟
      ".how-point",             // sale-leaseback：運作要點
      ".step",                  // debt-consolidation：流程步驟
      ".related-card",          // debt-consolidation：延伸閱讀卡
      ".promise-item"           // 兩頁共用：承諾清單
    ].forEach(function (sel) { revealGroup(sel); });
  });
})();
