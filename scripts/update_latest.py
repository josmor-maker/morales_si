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
    req = urllib.request.Request(url, headers={"User-Agent": "jose.morales.si updater"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def substack():
    posts = []
    for source, url in FEEDS.items():
        try:
            root = ET.fromstring(get(url))
            for item in root.iter("item"):
                posts.append({
                    "source": source,
                    "title": item.findtext("title", "").strip(),
                    "url": item.findtext("link", "").strip(),
                    "date": parsedate_to_datetime(item.findtext("pubDate")).isoformat(),
                })
        except Exception as e:
            print(f"skip {source}: {e}")
    return sorted(posts, key=lambda p: p["date"], reverse=True)[:5]


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
    data = {"posts": substack(), "bluesky": bluesky()}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(data['posts'])} posts, {len(data['bluesky'])} bluesky")
