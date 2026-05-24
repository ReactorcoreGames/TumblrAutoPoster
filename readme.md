# 🐦 Automated Twitter Poster 🤖

> Post to Twitter/X automatically on a schedule! Set it and forget it! 
Welcome to free twitter automation, easy and forever.

## ✨ What is this?

This is a simple tool that automatically posts content to your Twitter/X account on a schedule. Just fill in a spreadsheet with your posts, set it up once, and it will handle the rest!

- 🕒 Posts automatically every 12 hours (configurable)
- 📝 Cycles through your list of prepared posts
- 🔄 Works completely on its own after setup
- 🔗 Automatically creates Twitter cards for your links
- 🖼️ Includes images from your links when available
- 📱 No need to open Twitter or remember to post

## 🚀 Quick Setup Guide

### Step 0: Create your posts from links 🖇️

This entire system is meant to be easy, lazy, basic but effective.

#### 1. Step One - Get Links

First, use 'Web Link Collector 1000' (free PC program also by me) to acquire a list of links to every distinct piece you've contributed to, worked on by yourself or anything else you want to promote. This can be any web page for any particular project, item, article, gallery, store, service, commission, or whatever else you worked on that can has a link towards.

**Get 'Web Link Collector 1000' here:** (free)
https://reactorcore.itch.io/web-link-collector-1000

Ideally, you'd want atleast 3 months worth of links. If you post something once a day, every 24 hours, then that'd mean 90 links. 90 pages, products, items, services, articles, releases, etc. Do NOT to post more often than twice a day (every 12 hours), otherwise you may be flagged for spamming by the platform.

If you have less links, then either post less often (once a week/month) or have links that promote things your friends are making, or anything cool that you want to highlight and share for the love of it. It doesn't have to be all about you.

After you use the Web Link Collector to get all the links you need, edit the .txt list in notepad++ or similar to remove unnecessary links, remove duplicates or to merge other lists so you'll have one big true final list of links.

#### 2. Step Two - Turn Links Into Social Media Posts

Next, turn that big list of links into social media posts using another program I made that'll automate the whole thing for you, aptly named 'Links Into Social Media Posts' PC program. 

**Get 'Links Into Social Media Posts' here:** (free)
https://reactorcore.itch.io/links-into-social-media-posts

This will take your TXT file list of links and turn it into ready-to-use CSV list of social media posts. It'll automatically web scrape every link and extract title+metadata and create some suitable hashtags from it too. In most cases it'll do a good job, but you can always paste the resulting CSV into chatgpt or claude to have it improve the title and hashtags for better ones. Just make sure the original links aren't messed up in the process when you enhance the post entries with AI. You can edit CSV files easier with programs like 'Modern CSV' or 'Libre Office Calc'.

Now you're finally ready to use the Auto Poster program. You can always go and update your lists later when you release new stuff, but try to make the initial list as big, clean and quality as you can.

### Step 1: Copy this repository 📋

1. Click the **Fork** button at the top right of this page
2. Name your new repository whatever you want (like "my-twitter-poster")
3. Click **Create fork**

Congrats! Now you have your own copy of this tool! 🎉

### Step 2: Prepare your posts 📝

1. In your new repository, find the `posts.csv` file and click on it
2. Click the **pencil icon** (Edit this file)
3. Add your posts in the format: 
   ```
   title,url,hashtags
   Check out my cool project!,https://example.com,#cool #project #awesome
   ```
4. Each row will become one tweet
5. Click **Commit changes** when done

### Step 3: Get your Twitter API Credentials 🔑

**Important:** You need Twitter API access (which requires approval) to use this tool.

1. Go to [developer.twitter.com](https://developer.twitter.com)
2. Apply for a developer account (if you don't have one)
3. Create a new App in your developer dashboard
4. Go to your App's "Keys and tokens" section
5. Generate and copy these **4 credentials**:
   - **API Key** (Consumer Key)
   - **API Key Secret** (Consumer Secret)
   - **Access Token** 
   - **Access Token Secret**
6. Copy all credentials immediately (you won't see the secrets again!)

**Note:** Twitter's API access requires approval and may take some time. Make sure you have a legitimate use case when applying.

### Step 4: Add your Twitter API credentials to GitHub 🔒

1. In your GitHub repository, click on **Settings**
2. In the left sidebar, click on **Secrets and variables** → **Actions**
3. Click **New repository secret** and create these **4 secrets**:
   - `TWITTER_API_KEY` - paste your API Key
   - `TWITTER_API_SECRET` - paste your API Key Secret
   - `TWITTER_ACCESS_TOKEN` - paste your Access Token
   - `TWITTER_ACCESS_TOKEN_SECRET` - paste your Access Token Secret

### Step 5: Create initial state file 📄

1. In your repository, click **Add file** → **Create new file**
2. Name it `state.json`
3. Add this content:
   ```json
   {
     "last_row_index": -1,
     "last_post_time": null
   }
   ```
4. Click **Commit changes**

### Step 6: Start the poster! 🎬

1. Click on the **Actions** tab in your repository
2. Click on **Twitter Poster** in the left sidebar
3. Click the **Run workflow** button
4. Click the green **Run workflow** button in the popup

Woohoo! 🎉 Your first tweet will be sent immediately, and then it will continue posting every 12 hours!

## 📊 How to check if it's working

1. Go to the **Actions** tab in your repository
2. Look for green checkmarks ✅ next to "Twitter Poster" runs
3. Click on any run to see the details
4. Check your Twitter profile to see your tweets!

## 🛠️ Customizing your posting schedule

Want to post more or less frequently? You can change the schedule by editing the `.github/workflows/poster.yml` file:

1. Click on the file and then the edit (pencil) icon
2. Find the line that says `cron: '0 */12 * * *'`
3. Change it to:
   - Every 6 hours: `0 */6 * * *`
   - Once a day: `0 12 * * *` (posts at 12:00 UTC)
   - Twice a day on weekdays only: `0 9,17 * * 1-5`
   
### More info on cron scheduling to make sense of it:
https://crontab.guru/examples.html
https://crontab.guru/
https://docs.oracle.com/cd/E12058_01/doc/doc.1014/e12030/cron_expressions.htm
https://en.wikipedia.org/wiki/Cron

## ⚠️ Important Notes

- **Twitter API Limits**: Twitter has strict rate limits. Don't post too frequently or your API access might be suspended.
- **Content Guidelines**: Make sure your posts comply with Twitter's terms of service.
- **Character Limit**: Tweets are limited to 280 characters. The script will automatically trim hashtags if needed.
- **API Costs**: Twitter's API may have usage costs depending on your plan.

## 🤔 Troubleshooting

**Tweets not showing up?**
- Check the Actions tab for any red ❌ errors
- Verify your Twitter Bearer Token is correct and has necessary permissions
- Make sure your posts.csv file has the correct format
- Check that your Twitter developer account is in good standing

**Getting API errors?**
- Ensure your Twitter app has the correct permissions (Read and Write)
- Check if you've hit any rate limits
- Verify all 4 Twitter API credentials are correct and haven't expired
- Make sure your Access Token has write permissions

**Need to pause posting?**
- Go to Settings → Actions → General
- Scroll down and select "Disable Actions"

## 🌟 Tips and Tricks

- 💡 Keep URLs short to leave more room for your message
- 💡 Use hashtags strategically to reach more people
- 💡 Mix up your content to keep followers engaged
- 💡 You can manually trigger posts anytime from the Actions tab
- 💡 Twitter automatically creates link previews, so you don't need to describe the link

## 🔐 Security Best Practices

- Never share your Bearer Token publicly
- Use GitHub Secrets to store sensitive information
- Regularly review your Twitter app's permissions
- Monitor your API usage to avoid unexpected charges

## 📞 Need help?

Always ask AI like ChatGPT, Perplexity or Claude. They can help you in almost everything.
You can give them this readme.md as context and ask literally anything, like how to set up the cron schedule timing syntax, which hashtags/title would be better (copy paste the line(s) from your CSV into the AI), ideas for more things to add to your list of links or troubleshooting issues with github actions and so on.

---

Happy tweeting! 🐦✨

## 🔄 Differences from Bluesky Poster

If you're coming from the Bluesky version:
- Uses Twitter's Bearer Token instead of handle/password authentication
- Different character limit (280 vs 300)
- Different image upload process
- Automatic Twitter card generation for links
- Requires Twitter Developer Account approval

---

## Support My Work

If my work is helping you, here's how you can support me too:

Buy me an orange as a one-off gift:
https://buymeacoffee.com/reactorcoregames

Join as a Patreon memeber for tons of benefits: 
https://www.patreon.com/ReactorcoreGames

Donate, buy, try my other itch.io releases: 
https://reactorcore.itch.io/

Share my linktree or discord with people:
http://www.reactorcoregames.com
https://discord.gg/UdRavGhj47

Hire me or recommend me for full-time work as a Game Designer or Prompt Engineer:
mailto:reactorcoregames@gmail.com
(I can do Advanced Game Design Plans/Consulting, Build Standalone Offline Web Apps or Automation Software With Python)


Enjoy! B-)
- Reactorcore