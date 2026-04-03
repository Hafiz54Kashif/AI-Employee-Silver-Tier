# post_to_facebook_instagram

## Purpose
Automatically post business content to Facebook Page and Instagram Business Account
via Meta Graph API. Generates weekly engagement summaries for CEO Briefing.

## Prerequisites
1. Create Meta Developer App: https://developers.facebook.com/
2. Connect a Facebook Page to your app
3. Connect an Instagram Business Account to that Facebook Page
4. Generate a long-lived Page Access Token
5. Add to `.env`:
   ```
   FACEBOOK_PAGE_ID=your_page_id
   FACEBOOK_ACCESS_TOKEN=your_long_lived_page_token
   INSTAGRAM_ACCOUNT_ID=your_instagram_business_account_id
   ```

## Vault Folders
| Folder | Platform |
|--------|----------|
| `vault/Social_Posts/Facebook/` | Facebook Page posts |
| `vault/Social_Posts/Instagram/` | Instagram Business posts |
| `vault/Done/social_posted/` | Archived after posting |

## Facebook Post Format
Create a `.md` file in `vault/Social_Posts/Facebook/`:
```markdown
Excited to share our latest AI project update!
Built with Claude Code + Python.
#AI #AgenticAI #Pakistan
```

## Instagram Post Format
Instagram requires an image. Add frontmatter with `image_url`:
```markdown
---
image_url: https://your-image-host.com/image.jpg
---
Check out our latest work! 🚀
#AI #Tech #Innovation
```

## Process
1. Watcher monitors vault folders every 60 seconds
2. Detects new `.md` file
3. Posts to Facebook/Instagram via Meta Graph API
4. On success: archives file to `vault/Done/social_posted/`
5. Logs post ID in `vault/Logs/`
6. Updates `vault/Dashboard.md`

## Running the Watcher
```bash
python watchers/facebook_instagram_watcher.py
```

## Weekly Summary (for CEO Briefing)
The watcher can fetch engagement stats:
- Facebook: page impressions, engaged users, fans
- Instagram: like count, comments per post

These are included in the Monday CEO Briefing automatically.

## API Reference
- Meta Graph API: https://developers.facebook.com/docs/graph-api
- Instagram Graph API: https://developers.facebook.com/docs/instagram-api
