"""
LinkedIn Scheduler - AI Employee
Runs 24/7 in background.
At post_time (from settings.json), picks today's post from
scheduled_posts.json and saves it to LinkedIn_Posts/ folder.
linkedin_watcher.py then publishes it automatically.
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Paths — use AppData when running from .exe, project root in dev
if os.environ.get('AI_EMPLOYEE_DATA'):
    BASE_DIR = Path(os.environ['AI_EMPLOYEE_DATA'])
elif getattr(sys, 'frozen', False):
    BASE_DIR = Path(os.environ.get('APPDATA', '')) / 'AI Employee'
else:
    BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / "vault" / "Logs"
SETTINGS_FILE = BASE_DIR / "settings.json"
POSTS_DIR = BASE_DIR / "vault" / "LinkedIn_Posts"
SCHEDULED_FILE = BASE_DIR / "vault" / "scheduled_posts.json"


def log(msg):
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"- [{datetime.now().strftime('%H:%M:%S')}] LinkedInScheduler | INFO | {msg}\n")


def load_settings():
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {"linkedin": {"post_time": "09:00"}, "agent": {"status": "running"}}


def main():
    print("=" * 50)
    print("  LinkedIn Scheduler - AI Employee")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    log("Scheduler started")

    posted_today = False
    last_date = ""

    while True:
        try:
            now = datetime.now()
            today_str = now.strftime('%Y-%m-%d')

            # Reset at midnight
            if today_str != last_date:
                posted_today = False
                last_date = today_str

            settings = load_settings()

            # Respect agent pause
            if settings.get("agent", {}).get("status") == "stopped":
                time.sleep(60)
                continue

            post_time = settings.get("linkedin", {}).get("post_time", "09:00")
            ph, pm = map(int, post_time.split(":"))
            is_post_time = (now.hour == ph and now.minute == pm)

            # Check if already posted today
            done_file = BASE_DIR / "vault" / "Done" / "linkedin_posted" / f"daily_post_{today_str}.md"
            post_file = POSTS_DIR / f"daily_post_{today_str}.md"
            already_done = done_file.exists() or post_file.exists()

            if is_post_time and not posted_today and not already_done:
                print(f"[{now.strftime('%H:%M:%S')}] Post time! Picking today's post...")

                if not SCHEDULED_FILE.exists():
                    log("ERROR: scheduled_posts.json not found")
                    posted_today = True
                    time.sleep(60)
                    continue

                try:
                    with open(SCHEDULED_FILE, encoding='utf-8') as f:
                        scheduled = json.load(f)
                except (json.JSONDecodeError, OSError) as e:
                    log(f"ERROR reading scheduled_posts.json: {e}")
                    posted_today = True
                    time.sleep(60)
                    continue

                if today_str not in scheduled:
                    log(f"No post scheduled for {today_str}")
                    posted_today = True
                    time.sleep(60)
                    continue

                # Save today's post to LinkedIn_Posts folder
                POSTS_DIR.mkdir(parents=True, exist_ok=True)
                post_content = scheduled[today_str]
                post_file.write_text(post_content, encoding='utf-8')
                print(f"[{now.strftime('%H:%M:%S')}] Post file created — linkedin_watcher will publish it")
                log(f"Post file created for {today_str} — waiting for watcher to publish")
                posted_today = True

            time.sleep(60)  # Check every minute

        except Exception as e:
            log(f"ERROR: {e}")
            time.sleep(60)


if __name__ == "__main__":
    main()
