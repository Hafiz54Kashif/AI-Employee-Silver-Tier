"""
Twitter (X) Watcher - AI Employee Gold Tier
=============================================
Monitors vault/Social_Posts/Twitter/ for new .md files
and posts them via Twitter API v2. Also generates weekly
engagement summaries for the CEO Briefing.

SETUP:
1. Create a Twitter Developer App: https://developer.twitter.com/
2. Enable OAuth 2.0 with Read & Write permissions
3. Generate Bearer Token and OAuth tokens
4. Add to .env:
   TWITTER_BEARER_TOKEN=your_bearer_token
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_SECRET=your_access_token_secret

INSTALL DEPENDENCY:
  pip install tweepy

HOW TO RUN:
  python watchers/twitter_watcher.py

VAULT FOLDER WATCHED:
  vault/Social_Posts/Twitter/   → posts to Twitter/X
  vault/Done/social_posted/     → archived after posting
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# ── Load .env ─────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
env_file = BASE_DIR / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

# ── Config ────────────────────────────────────────────────────────────────────
BEARER_TOKEN    = os.getenv("TWITTER_BEARER_TOKEN", "")
API_KEY         = os.getenv("TWITTER_API_KEY", "")
API_SECRET      = os.getenv("TWITTER_API_SECRET", "")
ACCESS_TOKEN    = os.getenv("TWITTER_ACCESS_TOKEN", "")
ACCESS_SECRET   = os.getenv("TWITTER_ACCESS_SECRET", "")
CHECK_INTERVAL  = 60  # seconds
MAX_TWEET_LEN   = 280

VAULT_DIR    = BASE_DIR / "vault"
TWITTER_POSTS = VAULT_DIR / "Social_Posts" / "Twitter"
DONE_DIR     = VAULT_DIR / "Done" / "social_posted"
LOGS_DIR     = VAULT_DIR / "Logs"
DASHBOARD    = VAULT_DIR / "Dashboard.md"


# ── Helpers ───────────────────────────────────────────────────────────────────

def log(status, message):
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    entry = f"- [{datetime.now().strftime('%H:%M:%S')}] Twitter | {status} | {message}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Twitter {status}: {message}")


def extract_content(filepath):
    """Extract tweet text from .md file (skip YAML frontmatter)."""
    text = filepath.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        end = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), None)
        if end:
            return "\n".join(lines[end + 1:]).strip()
    return text.strip()


def truncate_tweet(text):
    """Truncate text to 280 characters if needed."""
    if len(text) <= MAX_TWEET_LEN:
        return text
    return text[:MAX_TWEET_LEN - 3] + "..."


def archive_post(filepath, tweet_id):
    DONE_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = DONE_DIR / f"twitter_{ts}_{filepath.name}"
    filepath.rename(dest)
    log("ARCHIVED", f"{filepath.name} → {dest.name} (tweet_id: {tweet_id})")


def update_dashboard(tweet_id):
    if not DASHBOARD.exists():
        return
    content = DASHBOARD.read_text(encoding="utf-8")
    entry = f"- [Twitter POSTED] tweet_id:{tweet_id} ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n"
    if "## Recent Activity" in content:
        content = content.replace("## Recent Activity\n", f"## Recent Activity\n{entry}")
    DASHBOARD.write_text(content, encoding="utf-8")


# ── Twitter API ───────────────────────────────────────────────────────────────

def get_tweepy_client():
    """Return authenticated Tweepy v2 client."""
    try:
        import tweepy
    except ImportError:
        raise ImportError("tweepy not installed. Run: pip install tweepy")

    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
        raise ValueError("Twitter credentials not set in .env")

    return tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET,
        wait_on_rate_limit=True
    )


def post_tweet(text):
    """Post a tweet via Twitter API v2."""
    client = get_tweepy_client()
    tweet_text = truncate_tweet(text)
    response = client.create_tweet(text=tweet_text)
    if response.data:
        return {"status": "success", "tweet_id": response.data["id"]}
    return {"error": "No data in response"}


def get_twitter_summary():
    """Get recent tweets and engagement stats."""
    try:
        client = get_tweepy_client()
        import tweepy

        # Get authenticated user info
        me = client.get_me(user_fields=["public_metrics"])
        if not me.data:
            return {}

        user_id = me.data.id
        metrics = me.data.public_metrics or {}

        # Get recent tweets
        tweets = client.get_users_tweets(
            id=user_id,
            max_results=10,
            tweet_fields=["public_metrics", "created_at"]
        )

        tweet_data = []
        if tweets.data:
            for t in tweets.data:
                m = t.public_metrics or {}
                tweet_data.append({
                    "id": t.id,
                    "text": t.text[:80] + "..." if len(t.text) > 80 else t.text,
                    "likes": m.get("like_count", 0),
                    "retweets": m.get("retweet_count", 0),
                    "replies": m.get("reply_count", 0),
                    "created_at": str(t.created_at)
                })

        return {
            "followers": metrics.get("followers_count", 0),
            "following": metrics.get("following_count", 0),
            "tweet_count": metrics.get("tweet_count", 0),
            "recent_tweets": tweet_data
        }
    except Exception as e:
        return {"error": str(e)}


def save_weekly_summary():
    """Save Twitter engagement summary to vault/Logs/."""
    summary = get_twitter_summary()
    if not summary or "error" in summary:
        log("WARN", f"Could not fetch summary: {summary.get('error', 'unknown')}")
        return

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    summary_file = LOGS_DIR / f"twitter_weekly_summary_{datetime.now().strftime('%Y-%m-%d')}.md"
    content = f"""# Twitter Weekly Summary — {datetime.now().strftime('%Y-%m-%d')}

## Account Stats
- **Followers:** {summary.get('followers', 0):,}
- **Following:** {summary.get('following', 0):,}
- **Total Tweets:** {summary.get('tweet_count', 0):,}

## Recent Tweets Performance
| Tweet | Likes | Retweets | Replies |
|-------|-------|----------|---------|
"""
    for t in summary.get("recent_tweets", []):
        content += f"| {t['text'][:40]}... | {t['likes']} | {t['retweets']} | {t['replies']} |\n"

    content += f"\n*Generated by AI Employee | {datetime.now().isoformat()}*\n"
    summary_file.write_text(content, encoding="utf-8")
    log("SUMMARY", f"Weekly summary saved: {summary_file.name}")


# ── Watcher Loop ──────────────────────────────────────────────────────────────

def process_twitter_posts():
    if not TWITTER_POSTS.exists():
        TWITTER_POSTS.mkdir(parents=True, exist_ok=True)
        return

    for f in TWITTER_POSTS.glob("*.md"):
        content = extract_content(f)
        if not content:
            continue
        log("POSTING", f.name)
        try:
            result = post_tweet(content)
            if result.get("status") == "success":
                log("SUCCESS", f"Tweet ID: {result['tweet_id']}")
                archive_post(f, result["tweet_id"])
                update_dashboard(result["tweet_id"])
            else:
                log("ERROR", result.get("error", "Unknown error"))
        except ImportError as e:
            log("ERROR", str(e))
            break
        except ValueError as e:
            log("ERROR", str(e))
            break
        except Exception as e:
            log("ERROR", str(e))


def main():
    print("=" * 55)
    print("  Twitter (X) Watcher - Gold Tier")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    if not ACCESS_TOKEN:
        print("\n[WARN] Twitter credentials not set in .env")
        print("  → Twitter posting will be skipped until configured")
        print("  → See skills/post_to_twitter.md for setup guide\n")

    print(f"Watching: vault/Social_Posts/Twitter/")
    print(f"Interval: {CHECK_INTERVAL}s\n")

    log("STARTED", "Twitter Watcher running")

    iteration = 0
    while True:
        try:
            process_twitter_posts()

            # Generate weekly summary every Sunday (weekday 6)
            if datetime.now().weekday() == 6 and datetime.now().hour == 23:
                save_weekly_summary()

            iteration += 1
            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n[STOP] Twitter Watcher stopping...")
            log("STOPPED", "Twitter Watcher stopped")
            break
        except Exception as e:
            log("ERROR", str(e))
            time.sleep(30)


if __name__ == "__main__":
    main()
