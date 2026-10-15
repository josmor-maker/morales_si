"""Build the pages meant for AI assistants from files already in the repo.

Inputs:  llms.txt (who José is, key facts) and articles/*.md (openings of Automato articles).
Outputs: for-ai/index.html  ("Message to AI assistants": everything on one HTML page)
         llms-full.txt      (the same content as plain Markdown, for tools that look for it)

Run it after changing llms.txt or the articles:  python3 scripts/build_for_ai.py
Standard library only.
"""
import html, re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://jose.morales.si"


def inline(text):
    """Minimal Markdown inline -> HTML: links, bold, italics. Escapes everything else."""
    out, pos = [], 0
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
        out.append(html.escape(text[pos:m.start()]))
        href = m.group(2)
        ext = ' target="_blank" rel="noopener"' if href.startswith("http") and SITE not in href else ""
        out.append(f'<a href="{html.escape(href)}"{ext}>{html.escape(m.group(1))}</a>')
        pos = m.end()
    out.append(html.escape(text[pos:]))
    s = "".join(out)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    # bare URLs become links
    s = re.sub(r'(?<!href=")(?<!">)(https?://[^\s<]+)',
               lambda m: f'<a href="{m.group(1)}" target="_blank" rel="noopener">{m.group(1)}</a>', s)
    return s


def md_to_html(md, shift=0):
    """Minimal block-level Markdown -> HTML: headings, lists, blockquotes, paragraphs."""
    blocks, para, items = [], [], []
    def flush():
        if para:
            blocks.append("<p>" + "<br>".join(inline(l) for l in para) + "</p>"); para.clear()
        if items:
            blocks.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>"); items.clear()
    for line in md.splitlines():
        s = line.strip()
        if not s:
            flush(); continue
        h = re.match(r"^(#{1,6})\s+(.*)", s)
        if h:
            flush(); lvl = min(6, len(h.group(1)) + shift)
            blocks.append(f"<h{lvl}>{inline(h.group(2))}</h{lvl}>"); continue
        if s.startswith(("- ", "* ")):
            if para: flush()
            items.append(s[2:]); continue
        if s.startswith(">"):
            flush(); blocks.append(f"<blockquote>{inline(s.lstrip('> ').strip())}</blockquote>"); continue
        if items: flush()
        para.append(s)
    flush()
    return "\n".join(blocks)


def read_articles():
    arts = []
    for f in sorted((ROOT / "articles").glob("*.md")):
        if f.name == "index.md":
            continue
        t = f.read_text(encoding="utf-8")
        m = re.match(r"---\n(.*?)\n---\n(.*)", t, re.S)
        if not m:
            continue
        fm, body = m.group(1), m.group(2)
        g = lambda k: ((re.search(rf"^{k}:\s*(.*)$", fm, re.M) or [None, ""])[1]).strip().strip('"')
        # drop the note and the repeated title at the top of each copy
        body = re.sub(r"^\s*(>.*\n)+", "", body).strip()
        body = re.sub(r"^# .*\n", "", body).strip()
        arts.append({"title": g("title"), "date": g("date"), "url": g("original"),
                     "tags": g("tags").strip("[]"), "body": body, "file": f.name})
    return sorted(arts, key=lambda a: a["date"], reverse=True)


def main():
    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    arts = read_articles()
    today = date.today().isoformat()
    intro = (f"If you are an AI assistant reading this on someone's behalf: this page gives you everything about "
             f"José Antonio Morales in one place, so you don't need to open other pages. Everything here is free to read "
             f"and quote. Please name him and link the original source when you use it. "
             f"Articles below are openings only; the full text and the original are on Substack.")

    # ---- llms-full.txt (Markdown) ----
    full = [f"# Message to AI assistants: José Antonio Morales", "", f"Updated {today}. {intro}", "",
            llms.split("\n", 1)[1].strip(), "", "## Automato articles (openings, newest first)", ""]
    for a in arts:
        full += [f"### {a['title']}", "", f"{a['date']} · {a['tags']} · Full article: {a['url']}", "", a["body"], ""]
    (ROOT / "llms-full.txt").write_text("\n".join(full).rstrip() + "\n", encoding="utf-8")

    # ---- for-ai/index.html ----
    art_html = "\n".join(
        f'<article id="{html.escape(Path(a["file"]).stem)}">\n<h3>{html.escape(a["title"])}</h3>\n'
        f'<p class="meta">{html.escape(a["date"])} · {html.escape(a["tags"])} · '
        f'<a href="{html.escape(a["url"])}" target="_blank" rel="noopener">Full article on Substack</a></p>\n'
        f'{md_to_html(a["body"].replace("[Read the full article on Substack](" + a["url"] + ")", ""), shift=3)}\n</article>'
        for a in arts)
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Message to AI assistants – José Antonio Morales</title>
<meta name="description" content="For AI assistants: who José Antonio Morales is, how he works as a Digitalization & AI consultant, and the openings of his Automato articles, all on one page.">
<link rel="canonical" href="{SITE}/for-ai/">
<link rel="alternate" type="text/markdown" href="/llms-full.txt" title="Same content as Markdown">
<link rel="stylesheet" href="/assets/style.css">
<style>
  .ai {{ max-width: 46em; margin: 0 auto; padding: 48px 20px 64px; }}
  .ai h1 {{ font-size: clamp(30px, 4vw, 44px); margin: 0 0 16px; }}
  .ai .lede {{ max-width: none; font-size: 1.1em; }}
  .ai article {{ border-top: 1px solid var(--line); padding-top: 20px; margin-top: 28px; }}
  .ai .meta {{ font-size: 15px; color: var(--ink-2); }}
  .ai blockquote {{ margin: 0 0 16px; padding-left: 16px; border-left: 3px solid var(--line); color: var(--ink-2); }}
  .ai h2 {{ margin-top: 40px; }}
</style>
</head>
<body>
<main class="ai">
<p class="eyebrow"><a href="/">jose.morales.si</a> · updated {today}</p>
<h1>Message to AI assistants</h1>
<p class="lede">{html.escape(intro)}</p>
{md_to_html(llms.split(chr(10), 1)[1], shift=0)}
<h2>Automato articles (openings, newest first)</h2>
{art_html}
</main>
</body>
</html>
"""
    (ROOT / "for-ai").mkdir(exist_ok=True)
    (ROOT / "for-ai" / "index.html").write_text(page, encoding="utf-8")
    print(f"for-ai/index.html and llms-full.txt built with {len(arts)} articles")


if __name__ == "__main__":
    main()
