# jose.morales.si

Source of [jose.morales.si](https://jose.morales.si). First site in the move away from Carrd, and the template for the others.

## The standard

- **Plain files, no CMS.** `index.html` + `assets/style.css`. Edit the text directly.
- **Readable by people and by their AI.** Every page has a Markdown twin (`index.md`) and the site has an `llms.txt`. Keep all three saying the same thing.
- **Nothing from third parties.** No external fonts, trackers or cookies, so no cookie banner.
- **Self-updating parts run on GitHub, not in the browser.** `.github/workflows/update-latest.yml` runs `scripts/update_latest.py` daily and writes `data/latest.json` (latest Substack and Bluesky posts).
- **Hosting:** GitHub Pages from the `main` branch root. `CNAME` holds the domain; DNS is a CNAME at FreeDNS pointing to `josmor-maker.github.io`.

## Files

| File | What it is |
|---|---|
| `index.html` | The page |
| `index.md` | Same content as Markdown |
| `llms.txt` | Short summary for AI assistants |
| `assets/` | Stylesheet, script, photo (`jose.jpg`), social card (`card.jpg`) |
| `data/latest.json` | Latest posts, written by the daily workflow |
