"""
LinkedIn Watcher - AI Employee Silver Tier
Monitors vault/LinkedIn_Posts/ folder for new post files
and automatically publishes them to LinkedIn.

HOW IT WORKS:
1. Create a .md file in vault/LinkedIn_Posts/
2. Watcher detects it and posts to LinkedIn
3. File moves to vault/Done/linkedin_posted/

SETUP REQUIRED:
- LinkedIn Developer App at https://www.linkedin.com/developers/
- Set LINKEDIN_ACCESS_TOKEN in .env file
"""

import os
import time
import json
import shutil
import requests
from pathlib import Path
from datetime import datetime

# Paths — use AppData when running from .exe, project root in dev
import sys as _sys
if os.environ.get('AI_EMPLOYEE_DATA'):
    BASE_DIR = Path(os.environ['AI_EMPLOYEE_DATA'])
elif getattr(_sys, 'frozen', False):
    BASE_DIR = Path(os.environ.get('APPDATA', '')) / 'AI Employee'
else:
    BASE_DIR = Path(__file__).parent.parent
VAULT_DIR = BASE_DIR / "vault"
POSTS_DIR = VAULT_DIR / "LinkedIn_Posts"
DONE_DIR = VAULT_DIR / "Done" / "linkedin_posted"
LOGS_DIR = VAULT_DIR / "Logs"
ENV_FILE = BASE_DIR / ".env"

CHECK_INTERVAL = 30  # seconds


def load_env():
    """Load environment variables from .env file."""
    env_vars = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip().strip('"')
    return env_vars


def get_linkedin_profile(access_token):
    """Get LinkedIn user profile (person URN)."""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    # Try userinfo endpoint first (needs openid scope)
    response = requests.get(
        'https://api.linkedin.com/v2/userinfo',
        headers=headers
    )
    if response.status_code == 200:
        return response.json().get('sub')

    # Fallback: try /v2/me endpoint
    response = requests.get(
        'https://api.linkedin.com/v2/me',
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        return data.get('id')

    # Fallback: read from .env
    env = load_env()
    return env.get('LINKEDIN_PERSON_ID', None)


def post_to_linkedin(access_token, person_id, content):
    """Post content to LinkedIn."""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    post_data = {
        "author": f"urn:li:person:{person_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    response = requests.post(
        'https://api.linkedin.com/v2/ugcPosts',
        headers=headers,
        json=post_data
    )

    return response.status_code, response.json() if response.text else {}


def extract_post_content(file_path):
    """Extract post content from markdown file."""
    content = file_path.read_text(encoding='utf-8')
    lines = content.strip().splitlines()
    post_lines = []

    # Skip frontmatter (--- ... ---)
    in_frontmatter = False
    started = False
    for line in lines:
        if line.strip() == '---':
            if not started:
                in_frontmatter = True
                started = True
                continue
            elif in_frontmatter:
                in_frontmatter = False
                continue
        if not in_frontmatter:
            post_lines.append(line)

    return '\n'.join(post_lines).strip()


def log_post(filename, status, message):
    """Log LinkedIn post activity."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    entry = f"- [{datetime.now().strftime('%H:%M:%S')}] LinkedIn | {status} | {filename} | {message}\n"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(entry)


def update_dashboard(filename, status):
    """Update dashboard with LinkedIn post status."""
    dashboard = VAULT_DIR / "Dashboard.md"
    if dashboard.exists():
        content = dashboard.read_text(encoding='utf-8')
        lines = content.splitlines()
        updated = []
        added = False
        for line in lines:
            updated.append(line)
            if line.startswith("## Recent Activity") and not added:
                updated.append(
                    f"- [LinkedIn {status}] {filename} "
                    f"({datetime.now().strftime('%Y-%m-%d %H:%M')})"
                )
                added = True
        dashboard.write_text('\n'.join(updated), encoding='utf-8')


def process_post_file(file_path, access_token, person_id):
    """Process a LinkedIn post file."""
    print(f"\n[POST] Processing: {file_path.name}")

    content = extract_post_content(file_path)
    if not content:
        print(f"[SKIP] Empty content in {file_path.name}")
        return

    print(f"[CONTENT] {content[:100]}...")

    status_code, response = post_to_linkedin(access_token, person_id, content)

    if status_code == 201:
        print(f"[SUCCESS] Posted to LinkedIn!")
        post_id = response.get('id', 'unknown')
        log_post(file_path.name, "POSTED", f"Post ID: {post_id}")
        update_dashboard(file_path.name, "POSTED")

        # Move to Done
        DONE_DIR.mkdir(parents=True, exist_ok=True)
        done_path = DONE_DIR / file_path.name
        shutil.move(str(file_path), str(done_path))
        print(f"[DONE] Moved to: {done_path}")
    else:
        print(f"[ERROR] Failed to post. Status: {status_code}")
        print(f"        Response: {response}")
        log_post(file_path.name, "FAILED", f"Status {status_code}: {response}")


def load_settings():
    """Load settings from settings.json."""
    settings_file = BASE_DIR / "settings.json"
    if settings_file.exists():
        with open(settings_file, 'r') as f:
            return json.load(f)
    return {"linkedin": {"post_time": "09:00"}}


def already_posted_today():
    """Check if LinkedIn post already happened today."""
    today = datetime.now().strftime('%Y-%m-%d')
    # Check Done/linkedin_posted folder
    if DONE_DIR.exists():
        for f in DONE_DIR.iterdir():
            if today in f.name:
                return True
    # Check today's log file for POSTED entry
    log_file = LOGS_DIR / f"{today}.md"
    if log_file.exists():
        content = log_file.read_text(encoding='utf-8', errors='replace')
        if 'LinkedIn | POSTED' in content:
            return True
    return False


def run_content_generator():
    """Run linkedin_content_generator.py to create today's post."""
    import subprocess, sys
    generator = BASE_DIR / "watchers" / "linkedin_content_generator.py"
    if generator.exists():
        print(f"[AUTO] Generating today's LinkedIn post...")
        result = subprocess.run(
            [sys.executable, str(generator)],
            capture_output=True, text=True, timeout=60
        )
        print(f"[AUTO] Generator done.")
        time.sleep(3)
    else:
        print(f"[WARN] Generator not found: {generator}")


def main():
    print("=" * 50)
    print("  LinkedIn Watcher - AI Employee")
    print("=" * 50)

    # Load credentials
    env = load_env()
    access_token = env.get('LINKEDIN_ACCESS_TOKEN', '')

    if not access_token:
        print("[ERROR] LINKEDIN_ACCESS_TOKEN not found in .env file")
        print(f"        Create: {ENV_FILE}")
        print("        Add: LINKEDIN_ACCESS_TOKEN=your_token_here")
        print("\nSee LINKEDIN_SETUP.md for instructions.")
        return

    # Get LinkedIn profile
    print("Connecting to LinkedIn...")
    person_id = get_linkedin_profile(access_token)
    if not person_id:
        print("[ERROR] Could not get LinkedIn profile. Check your access token.")
        return

    print(f"[OK] Connected! Person ID: {person_id}")
    print(f"[OK] Watching: {POSTS_DIR}")
    print(f"Check interval: {CHECK_INTERVAL}s")
    print("=" * 50)
    print("\nWaiting for posts... (Press Ctrl+C to stop)\n")

    # Ensure folders exist
    POSTS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Missed Post Check (startup) ──
    settings = load_settings()
    post_time_str = settings.get("linkedin", {}).get("post_time", "09:00")
    post_hour, post_min = map(int, post_time_str.split(":"))
    now = datetime.now()
    post_time_today = now.replace(hour=post_hour, minute=post_min, second=0, microsecond=0)

    if now >= post_time_today and not already_posted_today():
        print(f"[MISSED] No LinkedIn post today yet (scheduled {post_time_str}). Generating now...")
        run_content_generator()

    while True:
        post_files = [f for f in POSTS_DIR.iterdir() if f.is_file() and f.suffix == '.md']
        for post_file in post_files:
            process_post_file(post_file, access_token, person_id)

        if not post_files:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] No new posts.")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
