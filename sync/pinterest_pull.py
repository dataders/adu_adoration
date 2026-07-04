#!/usr/bin/env python3
"""One-way sync: Pinterest board -> this repo's inspiration/ folder.

Reads a Pinterest board's PUBLIC RSS feed (no login, no API token) and
downloads each pin's image into `inspiration/`, tracking what it has already
pulled in `sync/manifest.json` so re-runs only fetch new pins.

Why RSS and not the API?
    Pushing pins (repo -> Pinterest) requires the Pinterest API v5 + an OAuth
    token, which means a developer app and Pinterest's approval. The RSS feed
    is read-only but needs zero setup, so this script is PULL-ONLY. See the
    README in this folder for how to upgrade to full bidirectional later.

Limits (be honest about them):
    - Read-only. Editing/deleting a pin on Pinterest is NOT reflected here, and
      nothing here is ever pushed up.
    - No delete-sync: a pin removed from the board is left in place locally
      (its manifest entry is marked `stale` so you can prune by hand).
    - RSS images are decent (we upgrade the URL to the largest size Pinterest
      serves) but not guaranteed to be the true originals.
    - Your 6 hand-curated `NN-*.jpg` files are never touched; synced pins are
      written as `pin-<id>-<slug>.jpg`.

Usage:
    python3 sync/pinterest_pull.py https://www.pinterest.com/<user>/<board>/
    python3 sync/pinterest_pull.py            # reads sync/board.txt
    python3 sync/pinterest_pull.py --dry-run  # show what would download

Honors HTTPS_PROXY/HTTP_PROXY and the CA bundle in the environment.
Standard library only — no pip install required.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INSPIRATION_DIR = REPO_ROOT / "inspiration"
MANIFEST_PATH = REPO_ROOT / "sync" / "manifest.json"
BOARD_FILE = REPO_ROOT / "sync" / "board.txt"

USER_AGENT = "adu-adoration-pinterest-pull/1.0 (+https://github.com/dataders/adu_adoration)"


def resolve_board_url(cli_url: str | None) -> str:
    """Figure out which board to sync: CLI arg wins, else sync/board.txt."""
    if cli_url:
        url = cli_url.strip()
    elif BOARD_FILE.exists():
        url = BOARD_FILE.read_text(encoding="utf-8").strip()
    else:
        sys.exit(
            "No board URL given.\n"
            "  Pass one:   python3 sync/pinterest_pull.py https://www.pinterest.com/<user>/<board>/\n"
            "  Or save it: echo 'https://www.pinterest.com/<user>/<board>/' > sync/board.txt"
        )
    if not url:
        sys.exit(f"Board URL in {BOARD_FILE} is empty.")
    return url


def rss_url_for(board_url: str) -> str:
    """Turn a board page URL into its RSS feed URL.

    Pinterest exposes a board's feed at `<board-url>.rss`, e.g.
    https://www.pinterest.com/alice/adu-ideas/  ->  .../adu-ideas.rss
    Already-.rss URLs are passed through untouched.
    """
    url = board_url.strip()
    if url.endswith(".rss"):
        return url
    url = url.rstrip("/")
    return url + ".rss"


class _ImgSrcFinder(HTMLParser):
    """Pull the first <img src=...> out of an RSS item's HTML description."""

    def __init__(self) -> None:
        super().__init__()
        self.src: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "img" and self.src is None:
            for name, value in attrs:
                if name == "src" and value:
                    self.src = value


def largest_image_url(url: str) -> str:
    """Rewrite a Pinterest CDN thumbnail URL to the largest available size.

    Pinterest CDN paths embed the size, e.g.
        https://i.pinimg.com/236x/ab/cd/ef/abcdef.jpg
    Bumping the segment to `/originals/` (falling back handled by the caller)
    gets the full-resolution image. We try originals first.
    """
    return re.sub(r"/\d+x\d*/", "/originals/", url, count=1)


def _slug(text: str, limit: int = 48) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")          # strip any stray HTML
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return (text[:limit].strip("-")) or "pin"


def _pin_id(guid: str, link: str) -> str:
    """Stable short id for a pin, derived from its Pinterest pin URL."""
    m = re.search(r"/pin/(\d+)", guid or "") or re.search(r"/pin/(\d+)", link or "")
    if m:
        return m.group(1)
    # Fall back to a hash of whatever unique string we have.
    import hashlib

    return "x" + hashlib.sha1((guid or link).encode("utf-8")).hexdigest()[:12]


def fetch(url: str, binary: bool = False):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    return data if binary else data.decode("utf-8", errors="replace")


def parse_feed(xml_text: str) -> list[dict]:
    """Return a list of {id, title, link, image} for each pin in the feed."""
    root = ET.fromstring(xml_text)
    items = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        guid = (item.findtext("guid") or "").strip()
        description = item.findtext("description") or ""
        finder = _ImgSrcFinder()
        finder.feed(description)
        image = finder.src
        if not image:
            continue  # no image in this item; skip
        items.append(
            {
                "id": _pin_id(guid, link),
                "title": title,
                "link": link,
                "image": image,
            }
        )
    return items


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {"board_url": None, "pins": {}}


def save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def download_image(image_url: str, dest: Path) -> None:
    """Download an image, preferring the original size, falling back to the
    RSS-provided thumbnail URL if the upscaled URL 404s."""
    candidates = [largest_image_url(image_url), image_url]
    last_err: Exception | None = None
    for candidate in dict.fromkeys(candidates):  # de-dup, preserve order
        try:
            data = fetch(candidate, binary=True)
            dest.write_bytes(data)
            return
        except Exception as err:  # noqa: BLE001 - try next candidate
            last_err = err
    raise RuntimeError(f"could not download {image_url}: {last_err}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("board_url", nargs="?", help="Pinterest board URL (or .rss)")
    ap.add_argument("--dry-run", action="store_true", help="list new pins, download nothing")
    args = ap.parse_args()

    board_url = resolve_board_url(args.board_url)
    feed_url = rss_url_for(board_url)
    print(f"Board: {board_url}")
    print(f"Feed:  {feed_url}")

    try:
        xml_text = fetch(feed_url)
    except Exception as err:  # noqa: BLE001
        sys.exit(
            f"Could not fetch the RSS feed ({err}).\n"
            "Check that the board is PUBLIC and the URL is right. Private/secret "
            "boards do not expose an RSS feed."
        )

    try:
        pins = parse_feed(xml_text)
    except ET.ParseError as err:
        sys.exit(f"Feed did not parse as RSS/XML ({err}). Is the URL a board page?")

    print(f"Found {len(pins)} pin(s) in the feed.")
    manifest = load_manifest()
    manifest["board_url"] = board_url
    known = manifest.setdefault("pins", {})

    # Mark everything stale; un-mark whatever is still in the feed.
    for entry in known.values():
        entry["present_in_feed"] = False

    INSPIRATION_DIR.mkdir(parents=True, exist_ok=True)
    added = 0
    for pin in pins:
        pid = pin["id"]
        if pid in known and (INSPIRATION_DIR / known[pid]["file"]).exists():
            known[pid]["present_in_feed"] = True
            continue

        filename = f"pin-{pid}-{_slug(pin['title'])}.jpg"
        dest = INSPIRATION_DIR / filename
        if args.dry_run:
            print(f"  + would add {filename}  <- {pin['link'] or pin['image']}")
            added += 1
            continue
        try:
            download_image(pin["image"], dest)
        except Exception as err:  # noqa: BLE001
            print(f"  ! skipped {pid}: {err}")
            continue
        known[pid] = {
            "file": filename,
            "title": pin["title"],
            "link": pin["link"],
            "source_image": pin["image"],
            "present_in_feed": True,
        }
        print(f"  + added {filename}")
        added += 1

    stale = [e["file"] for e in known.values() if not e.get("present_in_feed", True)]

    if not args.dry_run:
        save_manifest(manifest)

    print(f"\nDone. {added} new pin(s) {'to add' if args.dry_run else 'added'}.")
    if stale:
        print(
            f"{len(stale)} tracked pin(s) are no longer in the feed (removed on "
            "Pinterest). Left in place — prune by hand if you like:"
        )
        for f in stale:
            print(f"    inspiration/{f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
