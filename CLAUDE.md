# TumblrAutoPoster — Claude Quick-Start

## What this project is
A GitHub Actions bot that posts one Tumblr link post per day from a CSV catalog, then stops when the list is exhausted (no cycling). It is a port of the TwitterAutoPoster in the sibling repo `c:\14 Repos\TwitterAutoPoster`.

Owner: Reactorcore (reactorcoregames@gmail.com)

## File map
| File | Purpose |
|---|---|
| `poster.py` | Main script — reads CSV, posts to Tumblr, updates state, commits |
| `posts.csv` | 227-row catalog: `title, url, hashtags` |
| `state.json` | `{"last_row_index": N}` — tracks next row to post |
| `get_token.py` | One-time local OAuth PIN flow to get access tokens |
| `.github/workflows/poster.yml` | Runs `poster.py` daily at noon UTC via cron |
| `user-setup-guide.md` | Human-readable setup instructions for the owner |

## Key design decisions
- **Linear, not cyclic** — `next_index = last_index + 1`. When `next_index >= len(posts)` print "All posts published." and `sys.exit(0)`. Do NOT use modulo.
- **Tumblr legacy endpoint** — `POST https://api.tumblr.com/v2/blog/{TUMBLR_BLOG_NAME}/post` (singular — the NPF `/posts` endpoint returns 8001 errors)
- **Post type** — `photo` when an `og:image` can be scraped from the URL (covers ~all itch.io pages); falls back to `link` if none found. Photo post fields: `source` (og:image URL), `caption` (CSV title + space + URL as plain text), `link` (the URL), `tags`, `state`. Form fields must be included in the OAuth signature base string or Tumblr returns 401.
- **og:image fetch** — `fetch_og_image(url)` in poster.py does a simple GET + HTMLParser scan for `<meta property="og:image">`. No extra dependencies — uses `requests` and stdlib `html.parser`.
- **Auth** — OAuth 1.0a. Functions `create_oauth_signature()` and `create_oauth_header()` are identical in structure to the Twitter version; only the env var names differ.
- **No media upload** — Tumblr auto-generates link previews from the URL.
- **CSV tags** — `hashtags` column is space-separated `#tag` strings. Strip `#` with `t.lstrip('#')` before sending.

## Environment variables (all stored as GitHub Secrets)
| Var | Description |
|---|---|
| `TUMBLR_API_KEY` | Consumer Key from Tumblr app registration |
| `TUMBLR_API_SECRET` | Consumer Secret |
| `TUMBLR_ACCESS_TOKEN` | From `get_token.py` one-time flow |
| `TUMBLR_ACCESS_TOKEN_SECRET` | From `get_token.py` one-time flow |
| `TUMBLR_BLOG_NAME` | Blog subdomain only, e.g. `reactorcore` |
| `GITHUB_TOKEN` | Auto-provided by Actions for git push |

## State file
```json
{"last_row_index": -1}
```
Start value is `-1`. After each successful post it becomes the index of the row just posted. On the next run `next_index = last_index + 1`.

## CSV format
```
title,url,hashtags
Imperial Black Halo: ...,https://reactorcore.itch.io/...,#lego #mecha #altbuild
```
227 rows. Titles can be long — no character limit on Tumblr.

## Workflow schedule
Once per day, noon UTC: `cron: '0 12 * * *'`. Also supports `workflow_dispatch` for manual runs.

## OAuth setup flow (get_token.py)
1. User sets `TUMBLR_API_KEY` and `TUMBLR_API_SECRET` in their shell
2. Script POSTs to `https://www.tumblr.com/oauth/request_token` with `oauth_callback=oob`
3. Prints authorization URL → user visits, authorizes, gets PIN
4. Script POSTs to `https://www.tumblr.com/oauth/access_token` with PIN as `oauth_verifier`
5. Prints `TUMBLR_ACCESS_TOKEN` and `TUMBLR_ACCESS_TOKEN_SECRET`

## Tumblr API response shape
Success response JSON has `response.id` as the post ID.

## Things to watch out for
- The workflow yaml will show "Context access might be invalid" warnings in VS Code for the secret names — this is normal, the linter can't see GitHub Secrets locally.
- `commit_changes()` uses `os.system()` calls for git — identical to the Twitter version, keep as-is.
- `checkout@v4` is used (not v5, which doesn't exist yet for Actions).
