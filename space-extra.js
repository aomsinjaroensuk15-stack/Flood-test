/* space-extra.js — ระบบเสริมธีมอวกาศสำหรับเช็กน้ำท่วม */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* 1) แถบพลังงานสะสมด้านบน */
  const prog = document.createElement('div');
  prog.id = 'prog';
  document.body.appendChild(prog);
  addEventListener('scroll', () => {
    const h = document.documentElement;
    const p = h.scrollTop / (h.scrollHeight - h.clientHeight || 1);
    prog.style.width = (p * 100).toFixed(2) + '%';
  }, { passive: true });

  /* 2) ทางเท้าดาวตามนิ้ว (งดในโหมดประหยัดแบตเคลื่อนไหว) */
  if (!reduced && matchMedia('(pointer: fine)').matches) {
    const COLORS = ['#4DD8FF', '#8B5CF6', '#F472B6', '#FFFFFF', '#7EE7FF'];
    let last = 0;
    addEventListener('pointermove', e => {
      const now = performance.now();
      if (now - last < 55) return;
      last = now;
      const s = document.createElement('i');
      s.className = 'trail';
      const c = COLORS[Math.random() * COLORS.length | 0];
      const size = 3 + Math.random() * 5;
      s.style.cssText = `left:${e.clientX - size / 2}px;top:${e.clientY - size / 2}px;
        width:${size}px;height:${size}px;background:${c};
        box-shadow:0 0 8px ${c}`;
      document.body.appendChild(s);
      setTimeout(() => s.remove(), 750);
    }, { passive: true });
  }

  /* 3) ฝนตกบนกราฟ เมื่อฝนสะสมเกินเกณฑ์เฝ้าระวัง */
  const rainCheck = () => {
    const days = $('days');
    if (!days) return;
    const wet = !!(typeof cur !== 'undefined' && cur && cur.a &&
      (cur.a.rain24 >= T.rain24.watch || cur.a.rain48 >= T.rain48.watch));
    days.classList.toggle('raining', wet && !reduced);
  };
  setInterval(rainCheck, 15000); rainCheck();

  /* 4) ระเบิดประกาย + สั่น เมื่อการ์ดเข้าสู่ระดับอันตราย */
  const COLORS2 = ['#FF5A5A', '#F97316', '#FBBF24', '#FFFFFF'];
  const burst = r => {
    for (let i = 0; i < 22; i++) {
      const p = document.createElement('i');
      p.className = 'burst';
      const a = Math.random() * Math.PI * 2, d = 60 + Math.random() * 140;
      const c = COLORS2[Math.random() * COLORS2.length | 0];
      p.style.cssText = `left:${r.left + r.width / 2}px;top:${r.top + r.height / 2}px;
        background:${c};color:${c};--dx:${Math.cos(a) * d}px;--dy:${Math.sin(a) * d}px`;
      document.body.appendChild(p);
      setTimeout(() => p.remove(), 900);
    }
    if (navigator.vibrate) navigator.vibrate([120, 60, 120]);
  };
  let wasDanger = false;
  new MutationObserver(() => {
    const card = $('card');
    const is = card && card.classList.contains('danger');
    if (is && !wasDanger && !reduced) burst(card.getBoundingClientRect());
    wasDanger = is;
  }).observe($('card'), { attributes: true, attributeFilter: ['class'] });
})();
