// Fills the "Lately" section from data/latest.json, which a daily GitHub Action refreshes.
// If the file is missing or empty, the section simply stays hidden.
(async () => {
  try {
    const res = await fetch('/data/latest.json', { cache: 'no-cache' });
    if (!res.ok) return;
    const data = await res.json();
    const fmt = d => new Date(d).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
    const fill = (id, items, render) => {
      const ul = document.getElementById(id);
      (items || []).slice(0, 3).forEach(it => {
        const li = document.createElement('li');
        li.innerHTML = render(it);
        ul.appendChild(li);
      });
      return (items || []).length > 0;
    };
    const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    const a = fill('latest-posts', data.posts, p =>
      `<a href="${esc(p.url)}">${esc(p.title)}</a><small>${esc(p.source)} · ${fmt(p.date)}</small>`);
    const b = fill('latest-sky', data.bluesky, p =>
      `<a href="${esc(p.url)}">${esc(p.text.length > 140 ? p.text.slice(0, 140) + '…' : p.text)}</a><small>${fmt(p.date)}</small>`);
    if (a || b) document.getElementById('latest').hidden = false;
  } catch (e) { /* stay hidden */ }
})();
