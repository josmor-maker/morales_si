// Fills the Automato cards (top) and the "Lately" section from data/latest.json,
// which a daily GitHub Action refreshes. Anything missing simply stays hidden.
(async () => {
  try {
    const res = await fetch('/data/latest.json', { cache: 'no-cache' });
    if (!res.ok) return;
    const data = await res.json();
    const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    const fmt = d => new Date(d).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
    const cut = (s, n) => (s && s.length > n ? s.slice(0, n).trimEnd() + '…' : s || '');

    // Automato cards in the hero
    const auto = (data.automato || []).slice(0, 3);
    if (auto.length) {
      document.getElementById('automato-cards').innerHTML = auto.map(p =>
        `<a class="post" href="${esc(p.url)}" target="_blank" rel="noopener">
           <span class="post-t">${esc(p.title)}</span>
           ${p.subtitle ? `<span class="post-d">${esc(cut(p.subtitle, 110))}</span>` : ''}
           <span class="post-m">${fmt(p.date)}</span>
         </a>`).join('');
    }

    // "Lately" section further down
    const fill = (col, id, items, render) => {
      if (!items || !items.length) return false;
      document.getElementById(id).innerHTML = items.slice(0, 3).map(it => `<li>${render(it)}</li>`).join('');
      document.getElementById(col).hidden = false;
      return true;
    };
    const a = fill('col-posts', 'latest-posts', data.posts, p =>
      `<a href="${esc(p.url)}" target="_blank" rel="noopener">${esc(p.title)}</a><small>${fmt(p.date)}</small>`);
    const b = fill('col-sky', 'latest-sky', data.bluesky, p =>
      `<a href="${esc(p.url)}" target="_blank" rel="noopener">${esc(cut(p.text, 140))}</a><small>${fmt(p.date)}</small>`);
    if (a || b) document.getElementById('latest').hidden = false;
  } catch (e) { /* keep the static fallback */ }
})();
