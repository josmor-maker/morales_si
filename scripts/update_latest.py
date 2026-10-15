"""Daily update, run by .github/workflows/update-latest.yml. Standard library only.

- data/latest.json: the five latest Bluesky posts (the Automato cards come from the vault, written by the weekly task).
- data/stats.json:  bluesky.posts_30d, every post José wrote on Bluesky in the past 30 days, replies included, reposts not.

Substack is not contacted: it refuses requests from GitHub's servers."""
import json, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

FEEDS = {
    "Automato": "https://automato.substack.com/feed",
    "Growing Fearless": "https://growingfearless.substack.com/feed",
}
BLUESKY_HANDLE = "morales.si"
OUT = Path(__file__).resolve().parent.parent / "data" / "latest.json"
STATS = OUT.parent / "stats.json"


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


def bluesky_posts_30d():
    """Count own posts and replies of the last 30 days, paging back through the author feed."""
    from datetime import datetime, timedelta, timezone
    since = datetime.now(timezone.utc) - timedelta(days=30)
    count, cursor = 0, ""
    for _ in range(20):  # at most 2,000 posts back
        url = ("https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed"
               f"?actor={BLUESKY_HANDLE}&limit=100&filter=posts_with_replies" + (f"&cursor={cursor}" if cursor else ""))
        page = json.loads(get(url))
        for f in page.get("feed", []):
            if f.get("reason"):
                continue  # a repost of someone else's post
            created = f["post"]["record"].get("createdAt", "")
            when = datetime.fromisoformat(created.replace("Z", "+00:00"))
            if when < since:
                return count
            count += 1
        cursor = page.get("cursor")
        if not cursor:
            return count
    return count


if __name__ == "__main__":
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    latest = bluesky()
    if latest:  # a failed fetch keeps yesterday's posts rather than emptying the page
        old["bluesky"] = latest
    OUT.write_text(json.dumps(old, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    stats = json.loads(STATS.read_text(encoding="utf-8")) if STATS.exists() else {}
    try:
        stats.setdefault("bluesky", {})["posts_30d"] = bluesky_posts_30d()
    except Exception as e:
        print(f"skip bluesky count: {e}")
    STATS.write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("bluesky posts:", len(old.get("bluesky", [])), "| posts in 30 days:", stats.get("bluesky", {}).get("posts_30d"))
