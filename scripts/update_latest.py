"""Fetch the latest Substack posts and Bluesky posts into data/latest.json.
Runs daily from .github/workflows/update-latest.yml. Standard library only."""
import json, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

FEEDS = {
    "Automato": "https://automato.substack.com/feed",
    "Growing Fearless": "https://growingfearless.substack.com/feed",
}
BLUESKY_HANDLE = "morales.si"
OUT = Path(__file__).resolve().parent.parent / "data" / "latest.json"


def get(url):
    # Substack refuses unknown clients, so identify as an ordinary feed reader.
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def substack(source, url, limit=3):
    """Latest posts from one Substack feed. Returns None if the feed can't be read,
    so the caller can keep the previous data instead of blanking the page."""
    try:
        root = ET.fromstring(get(url))
    except Exception as e:
        print(f"skip {source}: {e}")
        return None
    posts = []
    for item in root.iter("item"):
        posts.append({
            "source": source,
            "title": item.findtext("title", "").strip(),
            "subtitle": (item.findtext("description") or "").strip(),
            "url": item.findtext("link", "").strip(),
            "date": parsedate_to_datetime(item.findtext("pubDate")).isoformat(),
        })
    return sorted(posts, key=lambda p: p["date"], reverse=True)[:limit]


def bluesky():
    url = ("https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed"
           f"?actor={BLUESKY_HANDLE}&limit=10&filter=posts_no_replies")
    try:
        feed = json.loads(get(url))["feed"]
    except Exception as e:
        print(f"skip bluesky: {e}")
        return []
    out = []
    for f in feed:
        post = f["post"]
        if f.get("reason"):  # skip reposts
            continue
        rkey = post["uri"].rsplit("/", 1)[-1]
        out.append({
            "text": post["record"].get("text", ""),
            "url": f"https://bsky.app/profile/{BLUESKY_HANDLE}/post/{rkey}",
            "date": post["record"].get("createdAt", post.get("indexedAt")),
        })
    return out[:5]


if __name__ == "__main__":
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    fresh = {
        "automato": substack("Automato", FEEDS["Automato"]),
        "posts": substack("Growing Fearless", FEEDS["Growing Fearless"]),
        "bluesky": bluesky() or None,
    }
    # A feed that fails today keeps yesterday's items rather than emptying the page.
    data = {k: (v if v is not None else old.get(k, [])) for k, v in fresh.items()}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print({k: len(v) for k, v in data.items()})
