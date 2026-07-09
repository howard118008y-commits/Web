/* CX468 動態增強：儀表板卡片 scroll-reveal（僅視覺、零新內容）
   安全設計：①只動 below-fold 卡片，不碰首屏 hero（保護 LCP）
   ②只動 opacity/transform（走合成層，零 layout/CLS）③defer 載入、非阻斷渲染
   ④prefers-reduced-motion 自動全關 ⑤JS 未載入時內容照常顯示（不靠 CSS 藏，SEO 安全）
   ⑥once＝動完即殺，不留背景 tween。 */
(function () {
  if (!window.gsap || !window.ScrollTrigger) return;   // 載入失敗＝優雅退場，內容照常
  gsap.registerPlugin(ScrollTrigger);

  var mm = gsap.matchMedia();
  mm.add("(prefers-reduced-motion: no-preference)", function () {

    // 系列卡片：依序淡入（stagger）——「選擇系列」五張確定在 below-fold
    gsap.set(".tab-stack .tab-item", { opacity: 0, y: 28 });
    ScrollTrigger.batch(".tab-stack .tab-item", {
      start: "top 90%", once: true,
      onEnter: function (batch) {
        gsap.to(batch, { opacity: 1, y: 0, duration: 0.55, ease: "power2.out", stagger: 0.09 });
      }
    });

    // 本週房市焦點卡：進入視線淡入（位置由驗證確認在 below-fold 才納入）
    var focus = document.querySelector("#monthly-focus");
    if (focus && focus.getBoundingClientRect().top > window.innerHeight * 0.9) {
      gsap.set(focus, { opacity: 0, y: 24 });
      ScrollTrigger.create({
        trigger: focus, start: "top 90%", once: true,
        onEnter: function () { gsap.to(focus, { opacity: 1, y: 0, duration: 0.6, ease: "power2.out" }); }
      });
    }
  });
})();
