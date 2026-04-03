"""
Facebook & Instagram Watcher - AI Employee Gold Tier
=====================================================
Monitors vault/Social_Posts/Facebook/ and vault/Social_Posts/Instagram/
for new .md files and posts them via Meta Graph API.
Also generates weekly engagement summaries.

SETUP:
1. Create a Meta Developer App: https://developers.facebook.com/
2. Get a Page Access Token (for Facebook Pages)
3. Get an Instagram Business Account connected to your Facebook Page
4. Add to .env:
   FACEBOOK_PAGE_ID=your_page_id
   FACEBOOK_ACCESS_TOKEN=your_long_lived_page_token
   INSTAGRAM_ACCOUNT_ID=your_instagram_business_account_id

HOW TO RUN:
  python watchers/facebook_instagram_watcher.py

VAULT FOLDERS WATCHED:
  vault/Social_Posts/Facebook/    → posts to Facebook Page
  vault/Social_Posts/Instagram/   → posts to Instagram Business Account
  vault/Done/social_posted/       → archived after posting
"""

import os
import sys
import time
import json
import requests
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
FB_PAGE_ID      = os.getenv("FACEBOOK_PAGE_ID", "")
FB_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
IG_ACCOUNT_ID   = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
GRAPH_API_BASE  = "https://graph.facebook.com/v19.0"
CHECK_INTERVAL  = 60  # seconds

VAULT_DIR   = BASE_DIR / "vault"
FB_POSTS    = VAULT_DIR / "Social_Posts" / "Facebook"
IG_POSTS    = VAULT_DIR / "Social_Posts" / "Instagram"
DONE_DIR    = VAULT_DIR / "Done" / "social_posted"
LOGS_DIR    = VAULT_DIR / "Logs"
DASHBOARD   = VAULT_DIR / "Dashboard.md"


# ── Helpers ───────────────────────────────────────────────────────────────────

def log(platform, status, message):
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    entry = f"- [{datetime.now().strftime('%H:%M:%S')}] {platform} | {status} | {message}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {platform} {status}: {message}")


def extract_content(filepath):
    """Extract post text from .md file (skip YAML frontmatter)."""
    text = filepath.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        end = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), None)
        if end:
            return "\n".join(lines[end + 1:]).strip()
    return text.strip()


def archive_post(filepath, platform, post_id):
    """Move posted file to Done folder."""
    DONE_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = DONE_DIR / f"{platform}_{ts}_{filepath.name}"
    filepath.rename(dest)
    log(platform, "ARCHIVED", f"{filepath.name} → {dest.name} (post_id: {post_id})")


def update_dashboard(platform, post_id):
    if not DASHBOARD.exists():
        return
    content = DASHBOARD.read_text(encoding="utf-8")
    entry = f"- [{platform} POSTED] post_id:{post_id} ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n"
    if "## Recent Activity" in content:
        content = content.replace("## Recent Activity\n", f"## Recent Activity\n{entry}")
    DASHBOARD.write_text(content, encoding="utf-8")


# ── Facebook Posting ──────────────────────────────────────────────────────────

def post_to_facebook(message):
    """Post a text message to Facebook Page."""
    if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
        return {"error": "FACEBOOK_PAGE_ID or FACEBOOK_ACCESS_TOKEN not set in .env"}

    url = f"{GRAPH_API_BASE}/{FB_PAGE_ID}/feed"
    payload = {
        "message": message,
        "access_token": FB_ACCESS_TOKEN
    }
    resp = requests.post(url, data=payload, timeout=30)
    data = resp.json()

    if resp.status_code == 200 and "id" in data:
        return {"status": "success", "post_id": data["id"]}
    return {"error": data.get("error", {}).get("message", "Unknown error")}


def get_facebook_page_insights():
    """Get basic page engagement stats."""
    if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
        return {}
    url = f"{GRAPH_API_BASE}/{FB_PAGE_ID}/insights"
    params = {
        "metric": "page_impressions,page_engaged_users,page_fans",
        "period": "week",
        "access_token": FB_ACCESS_TOKEN
    }
    resp = requests.get(url, params=params, timeout=30)
    return resp.json() if resp.status_code == 200 else {}


# ── Instagram Posting ─────────────────────────────────────────────────────────

def post_to_instagram(caption, image_url=None):
    """
    Post to Instagram Business Account via Graph API.
    Requires an image URL (Instagram does not support text-only posts via API).
    If no image provided, logs a warning and skips.
    """
    if not IG_ACCOUNT_ID or not FB_ACCESS_TOKEN:
        return {"error": "INSTAGRAM_ACCOUNT_ID or FACEBOOK_ACCESS_TOKEN not set in .env"}

    if not image_url:
        return {"error": "Instagram requires an image_url. Add 'image_url: https://...' to your post frontmatter."}

    # Step 1: Create media container
    container_url = f"{GRAPH_API_BASE}/{IG_ACCOUNT_ID}/media"
    container_payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": FB_ACCESS_TOKEN
    }
    resp = requests.post(container_url, data=container_payload, timeout=30)
    container = resp.json()

    if "id" not in container:
        return {"error": container.get("error", {}).get("message", "Failed to create media container")}

    # Step 2: Publish container
    publish_url = f"{GRAPH_API_BASE}/{IG_ACCOUNT_ID}/media_publish"
    publish_payload = {
        "creation_id": container["id"],
        "access_token": FB_ACCESS_TOKEN
    }
    pub_resp = requests.post(publish_url, data=publish_payload, timeout=30)
    pub_data = pub_resp.json()

    if "id" in pub_data:
        return {"status": "success", "post_id": pub_data["id"]}
    return {"error": pub_data.get("error", {}).get("message", "Publish failed")}


def get_instagram_summary():
    """Get Instagram account media stats."""
    if not IG_ACCOUNT_ID or not FB_ACCESS_TOKEN:
        return {}
    url = f"{GRAPH_API_BASE}/{IG_ACCOUNT_ID}/media"
    params = {
        "fields": "id,caption,like_count,comments_count,timestamp",
        "limit": 10,
        "access_token": FB_ACCESS_TOKEN
    }
    resp = requests.get(url, params=params, timeout=30)
    return resp.json() if resp.status_code == 200 else {}


# ── Watcher Loop ──────────────────────────────────────────────────────────────

def parse_frontmatter(filepath):
    """Parse simple YAML frontmatter for image_url etc."""
    text = filepath.read_text(encoding="utf-8")
    meta = {}
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            for line in text[3:end].splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    meta[k.strip()] = v.strip()
    return meta


def process_facebook_posts():
    if not FB_POSTS.exists():
        FB_POSTS.mkdir(parents=True, exist_ok=True)
        return
    for f in FB_POSTS.glob("*.md"):
        content = extract_content(f)
        if not content:
            continue
        log("Facebook", "POSTING", f.name)
        result = post_to_facebook(content)
        if "post_id" in result:
            log("Facebook", "SUCCESS", f"Post ID: {result['post_id']}")
            archive_post(f, "facebook", result["post_id"])
            update_dashboard("Facebook", result["post_id"])
        else:
            log("Facebook", "ERROR", result.get("error", "Unknown"))


def process_instagram_posts():
    if not IG_POSTS.exists():
        IG_POSTS.mkdir(parents=True, exist_ok=True)
        return
    for f in IG_POSTS.glob("*.md"):
        meta    = parse_frontmatter(f)
        content = extract_content(f)
        image_url = meta.get("image_url", "")
        if not content:
            continue
        log("Instagram", "POSTING", f.name)
        result = post_to_instagram(content, image_url)
        if "post_id" in result:
            log("Instagram", "SUCCESS", f"Post ID: {result['post_id']}")
            archive_post(f, "instagram", result["post_id"])
            update_dashboard("Instagram", result["post_id"])
        else:
            log("Instagram", "ERROR", result.get("error", "Unknown"))


def main():
    print("=" * 55)
    print("  Facebook & Instagram Watcher - Gold Tier")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    if not FB_ACCESS_TOKEN:
        print("\n[WARN] FACEBOOK_ACCESS_TOKEN not set in .env")
        print("  → Facebook/Instagram posting will be skipped")
        print("  → Add credentials to .env to enable\n")

    print(f"Watching:")
    print(f"  Facebook:  vault/Social_Posts/Facebook/")
    print(f"  Instagram: vault/Social_Posts/Instagram/")
    print(f"  Interval:  {CHECK_INTERVAL}s\n")

    log("System", "STARTED", "Facebook & Instagram Watcher running")

    while True:
        try:
            process_facebook_posts()
            process_instagram_posts()
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\n[STOP] Watcher stopping...")
            log("System", "STOPPED", "Facebook & Instagram Watcher stopped")
            break
        except Exception as e:
            log("System", "ERROR", str(e))
            time.sleep(30)


if __name__ == "__main__":
    main()
