# Tumblr Auto Poster — Implementation Plan

## Overview
Port of TwitterAutoPoster targeting Tumblr. Posts one link post per run to a Tumblr blog,
using GitHub Actions on a schedule. Posts are treated as a permanent catalog — each CSV row
is posted once (no looping). State tracks the last posted index to resume on next run; when
all rows are exhausted the workflow stops gracefully.

## CSV Format (shared with TwitterAutoPoster)
```
title, url, hashtags
```
- `hashtags` field contains space-separated tags prefixed with `#` (e.g. `#lego #mecha`)
- Strip `#` when passing to Tumblr API (it expects bare tag strings in an array)

## Tumblr API
- **Endpoint:** `POST https://api.tumblr.com/v2/blog/{blog-identifier}/posts`
- **Auth:** OAuth 1.0a — same pattern as TwitterAutoPoster (reuse `create_oauth_header` / `create_oauth_signature`)
- **Post type:** `link` — includes `title`, `url`, `description`, and `tags[]`
- **Free:** Yes, no credits system. Rate limit is generous for one post per 12–24 hours.
- **Docs:** https://www.tumblr.com/docs/en/api/v2#posts--create-a-new-blog-post-legacy

### Request body (JSON)
```json
{
  "content": [
    {
      "type": "link",
      "url": "<url from csv>",
      "title": "<title from csv>",
      "description": "<title from csv>"
    }
  ],
  "tags": ["lego", "mecha", "altbuild"],
  "state": "published"
}
```
Note: Tumblr NPF (Neue Post Format) v2 endpoint. Tags are bare strings (no `#`).

## Credentials needed (GitHub Secrets)
| Secret name | Where to get it |
|---|---|
| `TUMBLR_API_KEY` | https://www.tumblr.com/oauth/apps → register app → Consumer Key |
| `TUMBLR_API_SECRET` | Same app registration → Consumer Secret |
| `TUMBLR_ACCESS_TOKEN` | OAuth 1.0a PIN flow (run once locally, save the token) |
| `TUMBLR_ACCESS_TOKEN_SECRET` | Same PIN flow |
| `TUMBLR_BLOG_NAME` | Your blog identifier, e.g. `reactorcore` (just the subdomain part) |

## State file (state.json)
Same structure as TwitterAutoPoster:
```json
{ "last_row_index": 42, "last_post_time": "2026-05-20T12:00:00+00:00" }
```
When `last_row_index` >= len(posts) - 1, print "All posts published." and exit 0 (no loop).

## poster.py — structure
Reuse from TwitterAutoPoster with these changes:
- Replace `post_to_twitter()` with `post_to_tumblr(content, url, tags)`
- Add `TUMBLR_BLOG_NAME` env var
- Change API endpoint and request body shape (see above)
- Remove `extract_first_url` — URL is already a dedicated CSV column, pass it directly
- Tags: split `hashtags` string on whitespace, strip `#` from each token → list of strings
- No media upload needed — Tumblr generates its own link preview from the URL automatically
- `commit_changes()` is identical — reuse as-is

## GitHub Actions workflow (.github/workflows/poster.yml)
```yaml
name: Tumblr Poster
on:
  schedule:
    - cron: '0 */24 * * *'   # once per day; change to */12 for twice daily
  workflow_dispatch:
jobs:
  post:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - run: pip install requests
      - name: Run poster
        env:
          TUMBLR_API_KEY: ${{ secrets.TUMBLR_API_KEY }}
          TUMBLR_API_SECRET: ${{ secrets.TUMBLR_API_SECRET }}
          TUMBLR_ACCESS_TOKEN: ${{ secrets.TUMBLR_ACCESS_TOKEN }}
          TUMBLR_ACCESS_TOKEN_SECRET: ${{ secrets.TUMBLR_ACCESS_TOKEN_SECRET }}
          TUMBLR_BLOG_NAME: ${{ secrets.TUMBLR_BLOG_NAME }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python poster.py
```

## Files to create
- `poster.py` — main script (port from TwitterAutoPoster)
- `posts.csv` — copy from TwitterAutoPoster (shared content)
- `state.json` — initial: `{"last_row_index": -1}`
- `.github/workflows/poster.yml` — as above
- `readme.md` — brief description

## One-time OAuth setup (local, before first deploy)
Tumblr's OAuth 1.0a requires a PIN-based authorization step that can't happen inside
GitHub Actions. Run a small helper script once locally to get your access token and secret,
then save them as GitHub Secrets. A `get_token.py` helper should be included in the repo
for this purpose.
