# Tumblr Auto Poster — Setup Guide

Everything you need to do, in order, from zero to first post.

---

## Before you start

You need:
- A Tumblr account with a blog already created (the one you want to post to)
- A GitHub account
- Python installed on your PC (for the one-time token step)

---

## Step 1 — Register your Tumblr app

Go to: **https://www.tumblr.com/oauth/register**

Fill in the form exactly like this:

| Field | What to enter |
|---|---|
| **Application Name** | `Reactorcore Tumblr Poster` |
| **Application Website** | Your GitHub repo URL — create the repo first (Step 2), then come back and fill this in. Or use `https://github.com/reactorcoregames` as a placeholder. |
| **App Store URL** | Leave blank |
| **Google Play Store URL** | Leave blank |
| **Application Description** | Paste this (it's under 400 chars): `This application is used by a scheduled, single-account posting bot that publishes curated link posts to one Tumblr blog. It does not read user content, follow users, or interact with Tumblr accounts beyond creating posts. The app is used only for low-frequency automated publishing from a GitHub Actions workflow.` |
| **Administrative contact email** | `reactorcoregames@gmail.com` |
| **Default callback URL** | `https://reactorcoregames.github.io/` |
| **OAuth2 redirect URLs** | `https://reactorcoregames.github.io/` |
| **Flurry Project ID** | Leave blank |
| **All icon fields** | Leave blank |

Complete the captcha ("Are you a robot?") and submit.

After registering, Tumblr will show you your app's page with:
- **Consumer Key** → this is your `TUMBLR_API_KEY`
- **Consumer Secret** → this is your `TUMBLR_API_SECRET`

**Copy both immediately and save them somewhere safe** (like a temporary Notepad file). You'll need them shortly.

---

## Step 2 — Create your GitHub repository

1. Go to **https://github.com/new**
2. Name it something like `TumblrAutoPoster`
3. Set it to **Private** (recommended — your posts.csv and state.json will be here)
4. Click **Create repository**
5. Upload all project files into the repo (poster.py, posts.csv, state.json, get_token.py, .github/workflows/poster.yml, CLAUDE.md, this file)

The easiest way to upload if you're not using git on the command line: on the new empty repo page, click **uploading an existing file**, then drag and drop all the files from your project folder. Note: the `.github/workflows/` folder structure needs to be preserved — GitHub will handle this correctly if you drag the whole folder in.

---

## Step 3 — Get your access tokens (one-time, on your PC)

This step generates the two tokens that let the bot post on your behalf. You only do this once.

1. Open a terminal (Command Prompt or PowerShell) in the project folder
2. Run these two commands to set your credentials temporarily:
   ```
   set TUMBLR_API_KEY=paste_your_consumer_key_here
   set TUMBLR_API_SECRET=paste_your_consumer_secret_here
   ```
3. Run the helper script:
   ```
   python get_token.py
   ```
4. It will print a URL. Open that URL in your browser.
5. You'll see a Tumblr page asking you to authorize the app. Click **Allow**.
6. Tumblr will redirect your browser to your callback URL (`reactorcoregames.github.io`). The redirect URL will look like: `https://reactorcoregames.github.io/?oauth_token=...&oauth_verifier=XXXXXXXXXX` — copy the `oauth_verifier` value (the long string after `oauth_verifier=`).
7. Go back to the terminal, paste the `oauth_verifier` value, press Enter.
8. The script will print two lines:
   ```
   TUMBLR_ACCESS_TOKEN        = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TUMBLR_ACCESS_TOKEN_SECRET = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
9. Copy both values. **These are your access tokens — save them.**

---

## Step 4 — Add all secrets to GitHub

In your GitHub repository:

1. Click **Settings** (top menu of the repo)
2. In the left sidebar: **Secrets and variables** → **Actions**
3. Click **New repository secret** for each of these 5 secrets:

| Secret name | Value |
|---|---|
| `TUMBLR_API_KEY` | Your Consumer Key from Step 1 |
| `TUMBLR_API_SECRET` | Your Consumer Secret from Step 1 |
| `TUMBLR_ACCESS_TOKEN` | From Step 3 output |
| `TUMBLR_ACCESS_TOKEN_SECRET` | From Step 3 output |
| `TUMBLR_BLOG_NAME` | Just the subdomain of your blog, e.g. `reactorcore` (not the full URL) |

After adding all 5, you should see them listed on the Secrets page.

---

## Step 5 — Test it manually

1. In your repo, click the **Actions** tab
2. In the left sidebar, click **Tumblr Poster**
3. Click the **Run workflow** button (top right of the runs list)
4. Click the green **Run workflow** button in the popup
5. Wait about 30 seconds, then refresh the page
6. Click the run that just appeared — it should show a green checkmark ✅
7. Open your Tumblr blog and confirm the first post is there

If you see a red ❌, click the run → click the "post" job → read the error output. Common issues are listed in the Troubleshooting section below.

---

## How it works day-to-day

- The bot runs **automatically every day at noon UTC** (no action needed from you)
- Each run posts the next row from `posts.csv` and updates `state.json` with the index
- When all 227 rows are posted, the bot prints "All posts published." and stops — it will not loop
- You can always trigger a manual post from the Actions tab

---

## Changing the posting schedule

Edit `.github/workflows/poster.yml` and find the line:
```
cron: '0 12 * * *'
```

Examples:
- Once a day at noon UTC (default): `0 12 * * *`
- Twice a day: `0 9,21 * * *`
- Once a week on Monday: `0 12 * * 1`

Use https://crontab.guru/ to build or check any schedule.

---

## Adding more posts later

1. Open `posts.csv` in GitHub (or a CSV editor like LibreOffice Calc)
2. Add new rows at the **bottom** of the file in the same format:
   ```
   Your Post Title Here,https://your-link.com,#tag1 #tag2 #tag3
   ```
3. Commit the change — the bot will reach those rows when it gets to them

---

## Troubleshooting

**Red ❌ in Actions — "Missing Tumblr API credentials"**
→ One or more secrets are missing or misnamed. Go to Settings → Secrets and check all 5 are present with exact names.

**Red ❌ — "401 Unauthorized" from Tumblr**
→ Your access tokens are wrong or were not saved correctly. Re-run `get_token.py` to generate fresh ones and update the GitHub Secrets.

**Red ❌ — "404 Not Found" from Tumblr**
→ `TUMBLR_BLOG_NAME` is wrong. It should be just the subdomain — `reactorcore`, not `reactorcore.tumblr.com`.

**Posts stop after all rows are posted**
→ This is intentional. Add more rows to `posts.csv` or reset `state.json` to `{"last_row_index": -1}` to start over from the beginning.

**"Context access might be invalid" warning in VS Code on the workflow yaml**
→ This is a false alarm from the local linter — it can't see your GitHub Secrets. The workflow will work fine in GitHub Actions.

**Need to pause posting?**
→ Go to your repo Settings → Actions → General → scroll to the bottom and select **Disable Actions**, or simply delete the workflow schedule trigger from the yaml and commit.

---

## Support

Always feel free to ask Claude (give it this readme and CLAUDE.md as context) for help with:
- Adjusting the cron schedule
- Improving titles or hashtags in your CSV
- Troubleshooting Actions errors
- Adding new posts to the catalog
