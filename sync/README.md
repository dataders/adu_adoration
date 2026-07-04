# Pinterest → `inspiration/` sync

One-way mirror of a **public** Pinterest board into this repo's
[`inspiration/`](../inspiration/) folder, using the board's RSS feed. No
Pinterest login, no API token, no signup.

## Quick start

```bash
# 1. Point it at your board (public boards only) — do this once:
echo 'https://www.pinterest.com/<user>/<board>/' > sync/board.txt

# 2. Preview what it would pull:
python3 sync/pinterest_pull.py --dry-run

# 3. Actually pull new pins into inspiration/:
python3 sync/pinterest_pull.py
```

You can also pass the URL directly instead of using `board.txt`:

```bash
python3 sync/pinterest_pull.py https://www.pinterest.com/<user>/<board>/
```

Re-run it any time — it's idempotent. Already-downloaded pins are tracked in
[`manifest.json`](manifest.json), so a re-run only fetches **new** pins.

Synced pins land as `inspiration/pin-<id>-<slug>.jpg`. Your six hand-curated
`NN-*.jpg` references are never touched.

## What this does and doesn't do

| | |
|---|---|
| ✅ Pull new pins from a public board | Reads `<board-url>.rss` |
| ✅ Full-res images when available | Rewrites the CDN URL to `/originals/`, falls back to the RSS thumbnail |
| ✅ Idempotent re-runs | `manifest.json` records every pulled pin |
| ✅ Leaves your curated files alone | Only writes `pin-*.jpg` |
| ❌ **Push** repo images up to Pinterest | Needs the API v5 + OAuth token (see below) |
| ❌ **Delete-sync** | A pin removed on Pinterest is flagged (not deleted) locally |
| ❌ Private/secret boards | RSS is only exposed for public boards |

This is **pull-only** because that's the part that needs no credentials — which
is what you asked for. Creating or editing pins on Pinterest is impossible
without the authenticated API.

## Why not a Pinterest MCP?

There is no Pinterest connector in the Claude MCP directory (checked the
registry — it has monday.com, Miro, etc., but nothing Pinterest). So there's
nothing to "flip on"; a real integration has to talk to Pinterest's own API or,
as here, its RSS feed.

## Upgrading to full bidirectional (later, if you want it)

True two-way sync (pushing local images up as new pins) requires the
[Pinterest API v5](https://developers.pinterest.com/docs/api/v5/):

1. Create a Pinterest **business account** and a developer **app** at
   <https://developers.pinterest.com/>.
2. Request **trial access** (self-serve) — enough for a personal board.
3. Generate an **OAuth access token** with the `boards:read`, `pins:read`, and
   `pins:write` scopes.
4. Swap the RSS reader here for API calls:
   - Pull: `GET /v5/boards/{board_id}/pins` (full metadata + original images).
   - Push: `POST /v5/pins` with `media_source` of type `image_base64` to upload
     a local file as a new pin.

The `manifest.json` format here already tracks the pin↔file mapping you'd need
to avoid duplicate uploads, so it carries over.
