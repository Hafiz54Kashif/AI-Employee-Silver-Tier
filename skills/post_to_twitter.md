# post_to_twitter

## Purpose
Automatically post business updates and content to Twitter (X) via Twitter API v2.
Generates weekly engagement summaries for the CEO Briefing.

## Prerequisites
1. Create Twitter Developer Account: https://developer.twitter.com/
2. Create a project and app with Read & Write permissions
3. Enable OAuth 1.0a (for posting tweets)
4. Generate all 4 tokens
5. Install dependency: `pip install tweepy`
6. Add to `.env`:
   ```
   TWITTER_BEARER_TOKEN=your_bearer_token
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_SECRET=your_access_token_secret
   ```

## Vault Folder
| Folder | Purpose |
|--------|---------|
| `vault/Social_Posts/Twitter/` | Drop `.md` files here to post |
| `vault/Done/social_posted/` | Archived after posting |
| `vault/Logs/twitter_weekly_summary_*.md` | Engagement reports |

## Tweet Format
Create a `.md` file in `vault/Social_Posts/Twitter/`:
```markdown
Excited to share our AI Employee project!
Built with Claude Code + Python + Obsidian.
Now running 24/7 autonomously 🤖
#AI #AgenticAI #ClaudeCode
```
**Note:** Tweets are auto-truncated to 280 characters if longer.

## Process
1. Watcher monitors `vault/Social_Posts/Twitter/` every 60 seconds
2. Detects new `.md` file
3. Posts tweet via Twitter API v2
4. On success: archives to `vault/Done/social_posted/`
5. Logs tweet ID in `vault/Logs/`
6. Updates `vault/Dashboard.md`

## Running the Watcher
```bash
python watchers/twitter_watcher.py
```

## Weekly Summary (for CEO Briefing)
Every Sunday at 11 PM, the watcher auto-generates:
- Follower count
- Recent tweets performance (likes, retweets, replies)
- Saved to `vault/Logs/twitter_weekly_summary_YYYY-MM-DD.md`

## API Reference
- Twitter API v2: https://developer.twitter.com/en/docs/twitter-api
- Tweepy docs: https://docs.tweepy.org/
