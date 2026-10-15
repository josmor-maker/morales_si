// Flip-disc number boards. Reads /data/stats.json, draws each number as a 5×7 disc font
// and flips the lit discs in, column by column, the first time a board scrolls into view.
// Visitors who turn off animation get the finished number straight away (handled in CSS).
(() => {
  // 5 columns × 7 rows per character; '1' = lit disc.
  const FONT = {
    '0': ['01110','10001','10011','10101','11001','10001','01110'],
    '1': ['00100','01100','00100','00100','00100','00100','01110'],
    '2': ['01110','10001','00001','00010','00100','01000','11111'],
    '3': ['11110','00001','00001','01110','00001','00001','11110'],
    '4': ['00010','00110','01010','10010','11111','00010','00010'],
    '5': ['11111','10000','11110','00001','00001','10001','01110'],
    '6': ['00110','01000','10000','11110','10001','10001','01110'],
    '7': ['11111','00001','00010','00100','01000','01000','01000'],
    '8': ['01110','10001','10001','01110','10001','10001','01110'],
    '9': ['01110','10001','10001','01111','00001','00010','01100'],
    '-': ['00000','00000','00000','11111','00000','00000','00000'],
  };
  const NS = 'http://www.w3.org/2000/svg';
  const R = 4.2, STEP = 10;                       // disc radius and pitch (viewBox units)

  function draw(box, text, digits) {
    const chars = String(text).padStart(digits, ' ').split('');
    const cols = chars.length * 6 - 1, rows = 7;
    const svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('viewBox', `0 0 ${cols * STEP} ${rows * STEP}`);
    svg.setAttribute('aria-hidden', 'true');
    const lit = [];
    chars.forEach((ch, i) => {
      const glyph = FONT[ch] || ['00000','00000','00000','00000','00000','00000','00000'];
      for (let r = 0; r < rows; r++) for (let c = 0; c < 6; c++) {
        if (i === chars.length - 1 && c === 5) continue;          // no spacer after the last character
        const on = c < 5 && glyph[r][c] === '1';
        const x = i * 6 + c;
        const d = document.createElementNS(NS, 'circle');
        d.setAttribute('cx', x * STEP + STEP / 2);
        d.setAttribute('cy', r * STEP + STEP / 2);
        d.setAttribute('r', R);
        d.setAttribute('class', 'disc');
        if (on) { d.dataset.col = x; lit.push(d); }
        svg.appendChild(d);
      }
    });
    box.replaceChildren(svg);
    return lit;
  }

  function flipIn(lit) {
    lit.forEach(d => {
      d.style.animationDelay = `${d.dataset.col * 45 + Math.random() * 60}ms`;
      d.classList.add('on', 'flip');
    });
  }

  async function init() {
    let stats = {};
    try { const r = await fetch('/data/stats.json', { cache: 'no-cache' }); if (r.ok) stats = await r.json(); } catch (e) {}
    document.querySelectorAll('[data-stat]').forEach(tile => {
      const key = tile.dataset.stat;
      const value = key.split('.').reduce((o, k) => (o == null ? o : o[k]), stats);
      const shown = value == null ? '--' : String(value);
      const box = tile.querySelector('.disc-box');
      const lit = draw(box, shown, Number(tile.dataset.digits || shown.length));
      const sr = tile.querySelector('.sr'); if (sr && value != null) sr.textContent = shown;
      const io = new IntersectionObserver(es => {
        if (es.some(e => e.isIntersecting)) { flipIn(lit); io.disconnect(); }
      }, { threshold: 0.4 });
      io.observe(box);
    });
  }
  init();
})();
