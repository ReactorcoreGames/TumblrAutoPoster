# I asked:

Is this feasible in tumblr (I attached tumblr_plan.md for the AI to read)


# Perplexity AI answered:

Yes — **Tumblr looks feasible for this exact workflow**, and in some ways it’s cleaner than Reddit for a one-post-per-run catalog bot. Your plan aligns with Tumblr’s legacy posting API: a blog-scoped API endpoint, OAuth 1.0a auth, and a `link` post type that can publish a title, URL, description, and tags. 

## Why it fits
Tumblr can support an external scheduled bot that posts from GitHub Actions, because your workflow only needs one authenticated post request per run and can store state between runs. Your plan also fits Tumblr’s blog model well: each CSV row becomes a single post, and the bot stops when the list is exhausted. 
The main thing to remember is that Tumblr’s write access uses OAuth 1.0a, so you’ll need a one-time local authorization step to get the access token and token secret before the automated workflow can run unattended.

## What you’d need
Your attached plan already identifies the core prerequisites:
- A Tumblr blog name, such as `reactorcore`.
- A Tumblr app created at the Tumblr developer portal.
- Consumer key and consumer secret from that app.
- An access token and access token secret from the one-time OAuth flow.
- GitHub Secrets for all of the above plus your bot’s state handling. 

Tumblr’s legacy API docs also show the create-post endpoint is blog-specific, which matches your “post to one blog on a schedule” use case. 

## What is a little awkward
The annoying part is the OAuth setup. Unlike Reddit’s simple script-app password flow, Tumblr’s access tokens generally come from the request-token/authorize/access-token OAuth 1.0a dance, which is easiest to complete once locally and then reuse in automation. [gist.github](https://gist.github.com/ann4belle/20e92e92116852abb683b3200f75f4ea)
So the project is feasible, but you should expect a bit more setup friction than Reddit. After that, the runtime side is straightforward: one API call to create the post, plus your state update. 

## Practical limitations
Your plan is best suited for **one blog, one posting account, and low-frequency automation**. Tumblr is a better fit if you want a public archive or catalog on a single blog rather than a multi-user community moderation tool.  
Tags should be cleaned up before sending because Tumblr expects bare tag strings rather than a hashtag-style field. Media upload is not required if the post is just a link, since Tumblr can generate the link preview from the URL. 

## Verdict
So yes, Tumblr can work for this. Compared with Reddit, the setup is still manageable, but the key difference is that Tumblr will require the one-time OAuth 1.0a token grant before your GitHub Actions bot can run unattended. 
If you want, I can turn your Tumblr plan into a **same-style checklist** like I did for Reddit, including exactly what to register, what secrets to store, and what to put in the app description.

===

# Question 2:

Got it. Ok, so I'm looking at the register to access tumblr API thing and it has this form for me to fill:

Register your application
* Application Name:
* Application Website:
App Store URL:
Google Play Store URL:
* Application Description:
400 characters max
* Administrative contact email:
This won't be made public
* Default callback URL:
* OAuth2 redirect URLs (space separate):
Flurry Project ID:
(for [Tumblr In-App Sharing](https://developer.yahoo.com/flurry/docs/tumblrsharing/))
Icon:
Must be a 128x128 PNG.

Application Page Icon:
Must be a 64x64 opaque square PNG. Users will see this on your app's page.

Mobile Dashboard Icon (Retina):
Must be a 44x44 PNG. Users will see this in the post footer with a 6px border radius.

Web Dashboard Icon (Retina):
Must be a 32x32 PNG. Users will see this in the post footer with a 6px border radius.

Web Dashboard Icon (Normal):
Must be a 16x16 PNG. Users will see this in the post footer with a 2px border radius.
Are you a robot?:
Rate Limits
Newly registered applications are rate limited to 1,000 requests per hour, and 5,000 requests per day. If your application requires more requests for either of these periods, you will be able to request a rate limit removal after completing the registration process.

(is this the right place and how do I fill this up? Seems a bunch of links and elements make no sense to what I'm making?)

---

# Answer 2:

Yes — this is the right Tumblr app registration page, but for your project you only need to fill in a small subset of the fields. The rest are mostly for apps that do user login, mobile apps, or in-app sharing, and they are not important for a simple external posting bot. [requests-oauthlib.readthedocs](https://requests-oauthlib.readthedocs.io/en/v1.3.0-docs/examples/tumblr.html)

## What to fill
Use something straightforward and descriptive for the bot itself. A good set of values would be:

- **Application Name:** `Reactorcore Tumblr Poster`.
- **Application Website:** your GitHub repo, or a simple project page if you have one.
- **Application Description:** a short description of the scheduled bot that posts curated link entries to your Tumblr blog.
- **Administrative contact email:** your email.
- **Default callback URL:** a valid HTTPS URL, even if your bot won’t use it directly.
- **OAuth2 redirect URLs:** usually the same URL as the default callback, or a localhost callback if you are only doing one-time auth locally. [socialoomph](https://www.socialoomph.com/help/view/help_tumblr_application_how/)

A safe callback value for a bot like yours is something like `https://example.com/tumblr/callback` if you have a project page, or `http://localhost:8080/callback` if Tumblr accepts it for the auth flow you are using. Several Tumblr OAuth examples use a dashboard or callback URL mainly to satisfy the app registration and token exchange flow rather than because the bot is a web app. [requests-oauthlib.readthedocs](https://requests-oauthlib.readthedocs.io/en/v1.3.0-docs/examples/tumblr.html)

## What you can ignore
You can leave these blank unless Tumblr forces you to provide them:
- **App Store URL.**
- **Google Play Store URL.**
- **Flurry Project ID.**
- **Icon fields**, unless the form requires them to be uploaded before submission.
- **Are you a robot?**, obviously complete that one. [support.appreciationengine](https://support.appreciationengine.com/support/solutions/articles/47001211728-creating-a-tumblr-app)

Those icon slots are for the app’s public presentation on Tumblr’s side, not for the API itself. For a private automation bot, they are not functionally important. [support.appreciationengine](https://support.appreciationengine.com/support/solutions/articles/47001211728-creating-a-tumblr-app)

## Best callback choice
For your use case, the callback URL does not need to correspond to a real public app page. It mainly needs to be a stable URL that matches what you later use during OAuth, and Tumblr’s OAuth docs/examples commonly register a single callback URL for the app. [stackoverflow](https://stackoverflow.com/questions/7786644/tumblr-oauth-callback-url)
If you’re doing the one-time token grant locally, you can keep the callback simple and use the same value consistently throughout registration and authorization. [requests-oauthlib.readthedocs](https://requests-oauthlib.readthedocs.io/en/v1.3.0-docs/examples/tumblr.html)

## Suggested application description
You can paste something like this, which is under 400 characters:

This application is used by a scheduled, single-account posting bot that publishes curated link posts to one Tumblr blog. It does not read user content, follow users, or interact with Tumblr accounts beyond creating posts. The app is used only for low-frequency automated publishing and state tracking from an external GitHub Actions workflow.

That is honest, specific, and aligned with the kind of automation you described. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/5228458/3fc5bc5c-4712-485c-a3dd-6dbb4517666a/tumblr_plan.md)

## Why the form looks unrelated
The page is designed for the broad Tumblr developer ecosystem, including interactive login apps and mobile integrations, so it includes fields that do not matter for your workflow. Your project is much simpler: one blog, one app, scheduled posting, and a one-time OAuth setup. [socialoomph](https://www.socialoomph.com/help/view/help_tumblr_application_how/)
So yes, it is the correct place to register, but you should treat most of the extra fields as generic metadata rather than requirements for your bot’s core function. [support.appreciationengine](https://support.appreciationengine.com/support/solutions/articles/47001211728-creating-a-tumblr-app)

## Practical rule of thumb
If a field is about **sign-in, app-store distribution, or visual branding**, it is probably optional for your bot. If a field is about **callback/redirect URLs** or **app credentials**, you should fill it carefully because those are the ones that affect OAuth and token generation. [stackoverflow](https://stackoverflow.com/questions/7786644/tumblr-oauth-callback-url)