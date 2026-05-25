# Automated Tumblr Poster 🤖

> Post to Tumblr automatically on a schedule! Set it and forget it!
> Welcome to free Tumblr automation, easy and forever.

## What is this?

This tool automatically posts your catalog of links to your Tumblr blog, once per day, on a schedule. Just fill in a spreadsheet with your posts, set it up once, and it handles the rest — forever, until the list runs out.

- Posts automatically once per day (configurable)
- Works through your list from top to bottom — no looping, no repeats
- Pulls the cover image from each link automatically and posts it as a photo
- Posts the description text and clickable link below the image
- Includes all your hashtags
- Works completely on its own after a one-time setup
- No need to open Tumblr or remember to post

## Step 0: Create your posts from links

This entire system is meant to be easy, lazy, basic but effective.

### Step One — Get Links

First, use **Web Link Collector 1000** (free PC program also by me) to collect links to every project, product, article, or page you want to promote.

**Get it here (free):**
https://reactorcore.itch.io/web-link-collector-1000

Aim for at least 90 links if posting once a day — that's 3 months of content. If you have fewer, post less often (once a week works fine too). It doesn't have to be all about you either — links to friends' work or anything cool you want to share are totally valid.

After collecting, clean up the list in Notepad++ or similar: remove duplicates, merge lists, cut anything you don't want posted.

### Step Two — Turn Links Into Posts

Use **Links Into Social Media Posts** (free PC program also by me) to convert your link list into a ready-to-use CSV automatically — it scrapes each page and generates a title and hashtags.

**Get it here (free):**
https://reactorcore.itch.io/links-into-social-media-posts

You can paste the resulting CSV into Claude or ChatGPT to improve the titles and hashtags. Just make sure the URLs don't get mangled in the process. Edit CSVs comfortably with Modern CSV or LibreOffice Calc.

---

## Step 1: Fork this repository

1. Click the **Fork** button at the top right of this page
2. Name your new repository whatever you want (like `my-tumblr-poster`)
3. Click **Create fork**

You now have your own copy of this tool.

## Step 2: Add your posts

1. In your new repository, find `posts.csv` and click on it
2. Click the **pencil icon** (Edit this file)
3. Replace the contents with your own posts in this format:
   ```
   title,url,hashtags
   My cool LEGO build,https://example.com/my-build,#lego #mecha #altbuild
   ```
4. Each row becomes one post. The title becomes the caption, the URL is the link, and hashtags become Tumblr tags (the `#` is stripped automatically).
5. Click **Commit changes**

## Step 3: Register a Tumblr app and get your credentials

See [user-setup-guide.md](user-setup-guide.md) for the full walkthrough. In short:

1. Register an app at https://www.tumblr.com/oauth/register — get your **Consumer Key** and **Consumer Secret**
2. Run `get_token.py` locally to do a one-time OAuth authorization and get your **Access Token** and **Access Token Secret**

## Step 4: Add your credentials to GitHub

1. In your repository, go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add these 5 secrets:
   - `TUMBLR_API_KEY` — your Consumer Key
   - `TUMBLR_API_SECRET` — your Consumer Secret
   - `TUMBLR_ACCESS_TOKEN` — from the `get_token.py` step
   - `TUMBLR_ACCESS_TOKEN_SECRET` — from the `get_token.py` step
   - `TUMBLR_BLOG_NAME` — just your blog subdomain, e.g. `reactorcore` (not the full URL)

## Step 5: Start the poster!

1. Click the **Actions** tab in your repository
2. Click **Tumblr Poster** in the left sidebar
3. Click **Run workflow** → **Run workflow**

Your first post will go out immediately, then it will continue once per day automatically.

---

## How to check if it's working

1. Go to the **Actions** tab
2. Look for green checkmarks ✅ next to **Tumblr Poster** runs
3. Click any run to see the log output
4. Check your Tumblr blog to see the post

## Customizing the posting schedule

Edit `.github/workflows/poster.yml` and find:
```
cron: '0 12 * * *'
```

Examples:
- Once a day at noon UTC (default): `0 12 * * *`
- Twice a day: `0 9,21 * * *`
- Once a week on Monday: `0 12 * * 1`
- Once a month on the 1st: `0 12 1 * *`

More help: https://crontab.guru/

## Important notes

- **No looping** — when all rows in your CSV are posted, the bot stops. Add more rows to resume, or reset `state.json` to `{"last_row_index": -1}` to start over.
- **Image previews** — the bot scrapes the `og:image` from each URL and posts it as a photo. This works great for itch.io and most other sites with proper open graph tags. If a page has no image, it falls back to a plain link post.
- **Tumblr API is free** — no credits, no rate limit concerns at one post per day.
- **state.json** — tracks which row was last posted. It gets committed back to your repo after each run automatically.

## Troubleshooting

**Red ❌ in Actions — "Missing Tumblr API credentials"**
One or more secrets are missing or misnamed. Check Settings → Secrets.

**Red ❌ — 401 Unauthorized**
Your access tokens are wrong or expired. Re-run `get_token.py` and update the GitHub Secrets.

**Red ❌ — 404 Not Found**
`TUMBLR_BLOG_NAME` is wrong — use just the subdomain (`reactorcore`, not `reactorcore.tumblr.com`).

**Posts stop coming**
All rows have been posted. Add new rows to the bottom of `posts.csv` or reset `state.json`.

**"Context access might be invalid" warnings in VS Code on the workflow yaml**
False alarm from the local linter — it can't see your GitHub Secrets. Works fine in GitHub Actions.

**Need to pause posting?**
Settings → Actions → General → Disable Actions.

## Tips

- Use Claude or ChatGPT to improve your CSV titles and hashtags — paste rows directly and ask for better versions
- You can manually trigger a post any time from the Actions tab
- To skip ahead in your CSV, edit `state.json` in GitHub and set `last_row_index` to the row number you want to start from (zero-indexed, so row 1 of the CSV = index 0)
- The bot commits `state.json` after every successful post, so if a run fails midway, the next run picks up from where it left off safely

## Need help?

Ask Claude, ChatGPT, or Perplexity — give them this readme as context and ask anything. Good questions to try:
- "Help me write better titles and hashtags for these CSV rows: [paste rows]"
- "How do I set the cron schedule to post every Tuesday and Thursday?"
- "The GitHub Actions run failed with this error: [paste log]"

---

## Support My Work

If this is helping you, here's how you can support me too:

Buy me an orange as a one-off gift:
https://buymeacoffee.com/reactorcoregames

Join as a Patreon member for tons of benefits:
https://www.patreon.com/ReactorcoreGames

Donate, buy, or try my other itch.io releases:
https://reactorcore.itch.io/

Share my linktree or Discord with people:
http://www.reactorcoregames.com
https://discord.gg/UdRavGhj47

Hire me or recommend me for full-time work as a Game Designer or Prompt Engineer:
reactorcoregames@gmail.com
(Advanced Game Design Plans/Consulting, Standalone Offline Web Apps, Automation Software with Python)

Enjoy! B-)
- Reactorcore
