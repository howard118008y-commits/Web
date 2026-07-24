(function () {
  'use strict';

  var CSS = `
#cx-line-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 9000;
  background: rgba(0, 0, 0, 0);
  backdrop-filter: blur(0px);
  -webkit-backdrop-filter: blur(0px);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background .28s ease, backdrop-filter .28s ease;
  pointer-events: none;
}
#cx-line-modal-backdrop.cx-open {
  background: rgba(0, 0, 0, 0.72);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  pointer-events: auto;
}

#cx-line-modal {
  background: linear-gradient(160deg, #111726 0%, #0d1020 100%);
  border: 1px solid rgba(201, 169, 97, 0.32);
  border-radius: 20px;
  padding: 40px 36px 32px;
  width: min(92vw, 360px);
  text-align: center;
  position: relative;
  box-shadow:
    0 0 0 1px rgba(201,169,97,0.08),
    0 24px 80px rgba(0,0,0,0.65),
    0 0 60px rgba(201,169,97,0.08) inset;
  opacity: 0;
  transform: translateY(22px) scale(0.96);
  transition: opacity .32s cubic-bezier(.22,.68,0,1.2), transform .32s cubic-bezier(.22,.68,0,1.2);
}
#cx-line-modal-backdrop.cx-open #cx-line-modal {
  opacity: 1;
  transform: translateY(0) scale(1);
}

#cx-line-modal .cxm-close {
  position: absolute;
  top: 14px;
  right: 16px;
  background: none;
  border: none;
  color: rgba(201,169,97,0.45);
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: color .18s, background .18s;
}
#cx-line-modal .cxm-close:hover {
  color: rgba(201,169,97,0.9);
  background: rgba(201,169,97,0.08);
}

#cx-line-modal .cxm-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  letter-spacing: 0.28em;
  color: rgba(201,169,97,0.5);
  text-transform: uppercase;
  margin-bottom: 12px;
}

#cx-line-modal .cxm-title {
  font-size: 20px;
  font-weight: 700;
  color: #E8E3D5;
  letter-spacing: -.01em;
  margin-bottom: 6px;
  font-family: 'Noto Sans TC', sans-serif;
}

#cx-line-modal .cxm-sub {
  font-size: 13px;
  color: rgba(201,169,97,0.6);
  margin-bottom: 24px;
  line-height: 1.6;
}

#cx-line-modal .cxm-qr-wrap {
  width: 180px;
  height: 180px;
  margin: 0 auto 20px;
  background: #fff;
  border-radius: 14px;
  padding: 10px;
  box-shadow: 0 0 0 1px rgba(201,169,97,0.22), 0 0 28px rgba(201,169,97,0.12);
  display: flex;
  align-items: center;
  justify-content: center;
}
#cx-line-modal .cxm-qr-wrap img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 6px;
  display: block;
}

#cx-line-modal .cxm-name {
  font-size: 13px;
  font-weight: 600;
  color: #E8E3D5;
  margin-bottom: 2px;
}
#cx-line-modal .cxm-id {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px;
  color: #06C755;
  margin-bottom: 22px;
  letter-spacing: 0.04em;
}

#cx-line-modal .cxm-btn {
  display: inline-block;
  background: #048456;
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  padding: 13px 36px;
  border-radius: 28px;
  text-decoration: none;
  letter-spacing: .01em;
  transition: filter .18s, transform .18s;
  margin-bottom: 14px;
}
#cx-line-modal .cxm-btn:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
}

#cx-line-modal .cxm-phone {
  font-size: 12px;
  color: rgba(232,227,213,0.4);
}
#cx-line-modal .cxm-phone a {
  color: rgba(232,227,213,0.65);
  text-decoration: none;
  font-weight: 500;
}
#cx-line-modal .cxm-phone a:hover {
  color: #E8E3D5;
}
`;

  var HTML = `
<div id="cx-line-modal-backdrop">
  <div id="cx-line-modal" role="dialog" aria-modal="true" aria-label="LINE 免費諮詢">
    <button class="cxm-close" id="cx-modal-close-btn" aria-label="關閉">✕</button>
    <div class="cxm-label">Free Consultation · LINE</div>
    <div class="cxm-title">掃碼加入，免費諮詢</div>
    <div class="cxm-sub">手機掃描 QR Code 加好友<br>初步評估完全免費・不申請不收費</div>
    <div class="cxm-qr-wrap">
      <img src="img/line-qr.png" alt="鋮馨租賃 LINE 官方帳號 QR Code">
    </div>
    <div class="cxm-name">鋮馨租賃有限公司</div>
    <div class="cxm-id">LINE 官方帳號</div>
    <a href="https://lin.ee/PHIfSoY" target="_blank" rel="noopener" class="cxm-btn">點此加入 LINE</a>
    <div class="cxm-phone">或來電 <a href="tel:0222490517">02-2249-0517</a> ／ <a href="tel:0931087996">0931-087-996</a></div>
  </div>
</div>
`;

  function init() {
    var style = document.createElement('style');
    style.textContent = CSS;
    document.head.appendChild(style);

    var wrapper = document.createElement('div');
    wrapper.innerHTML = HTML.trim();
    document.body.appendChild(wrapper.firstElementChild);

    var backdrop = document.getElementById('cx-line-modal-backdrop');
    var modal = document.getElementById('cx-line-modal');

    function openModal(e) {
      if (e) { e.preventDefault(); e.stopPropagation(); }
      backdrop.classList.add('cx-open');
      document.body.style.overflow = 'hidden';
      var closeBtn = document.getElementById('cx-modal-close-btn');
      if (closeBtn) closeBtn.focus();
    }

    function closeModal() {
      backdrop.classList.remove('cx-open');
      document.body.style.overflow = '';
    }

    document.addEventListener('click', function (e) {
      if (e.target.closest('.cta-strip-btn')) {
        openModal(e);
        return;
      }
      if (backdrop.classList.contains('cx-open')) {
        if (e.target === backdrop || e.target.id === 'cx-modal-close-btn') {
          closeModal();
        }
      }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && backdrop.classList.contains('cx-open')) {
        closeModal();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
