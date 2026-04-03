"""
LinkedIn Content Generator - AI Employee
Generates daily LinkedIn posts using Claude AI based on Business Goals.
Runs daily at 9:00 AM via Windows Task Scheduler.

HOW IT WORKS:
1. Reads vault/Business_Goals.md for context
2. Uses Claude API to generate a professional LinkedIn post
3. Saves post to vault/LinkedIn_Posts/daily_post_YYYY-MM-DD.md
4. linkedin_watcher.py picks it up and posts to LinkedIn automatically
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
SCHEDULED_POSTS_FILE = BASE_DIR / "vault" / "scheduled_posts.json"
VAULT_DIR = BASE_DIR / "vault"
POSTS_DIR = VAULT_DIR / "LinkedIn_Posts"
LOGS_DIR = VAULT_DIR / "Logs"
GOALS_FILE = VAULT_DIR / "Business_Goals.md"
ENV_FILE = BASE_DIR / ".env"

# Rotating topics — one per day of week
DAILY_TOPICS = {
    0: "Agentic AI systems and how autonomous agents are transforming businesses in 2026",                          # Monday
    1: "motivational post about learning, growth, and persistence — with a subtle AI and automation twist",        # Tuesday
    2: "how businesses of any size can use AI automation to save time, reduce costs, and scale faster",            # Wednesday
    3: "behind the scenes of building an AI Employee — autonomous agents that work 24/7 without human input",     # Thursday
    4: "motivational post about consistency, hard work, and how AI helps professionals focus on high-value work",  # Friday
    5: "the future of work — AI employees, digital transformation, and what it means for businesses worldwide",    # Saturday
    6: "learning Agentic AI in 2026 — what I am building, what I am discovering, and why it matters for business", # Sunday
}


def load_env():
    """Load environment variables from .env file."""
    env_vars = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip().strip('"')
    return env_vars


def load_business_goals():
    """Load business goals for context."""
    if GOALS_FILE.exists():
        return GOALS_FILE.read_text(encoding='utf-8')
    return "Focus on AI innovation, business growth, customer success, and market expansion."


def generate_post_with_claude(api_key, topic, goals_context):
    """Use Claude API to generate a LinkedIn post."""
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    today = datetime.now().strftime("%B %d, %Y")

    prompt = f"""You are a professional LinkedIn content writer for a tech company focused on AI and business automation.

Today's date: {today}
Today's topic: {topic}

Company context:
{goals_context}

Write a compelling LinkedIn post that:
- Is 150-250 words long
- Starts with a strong hook (question or bold statement)
- Shares genuine insight or value about the topic
- Connects to business growth, AI, or professional development
- Has a clear call-to-action at the end
- Ends with 5-7 relevant hashtags on a new line
- Sounds human, authentic, and professional — NOT robotic

Only output the post content. No explanations, no "Here is the post:", just the post text."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()


def generate_fallback_post(topic, goals_context):
    """Fallback rotating templates if API key not available."""
    today = datetime.now().strftime("%B %d, %Y")
    templates = [
        f"The future of work is already here — and it runs on AI.\n\nEvery day, we're building systems that handle repetitive tasks, monitor emails, generate content, and make smart decisions autonomously.\n\nAt our core, we believe that {topic} is the key to unlocking the next level of business growth.\n\nOur Q2 2026 roadmap is packed with milestones:\n- Automated customer onboarding\n- AI-powered market expansion\n- Real-time operational intelligence\n\nThe companies winning tomorrow are building their AI foundation today.\n\nWhat AI process have you automated recently? Share below.\n\n#AI #AgenticAI #BusinessGrowth #Automation #Pakistan #FutureOfWork #ProductLaunch",
        f"What if your best employee never slept, never forgot, and always followed the rules?\n\nThat's what we're building — an AI Employee that processes tasks, manages communications, and takes action 24/7.\n\nFocused on {topic}, our team is pushing boundaries in {today}.\n\nThe result? Faster decisions. Lower costs. Happier customers.\n\nThis is not the future. This is now.\n\n#AI #AgenticAI #AIEmployee #Automation #Pakistan #Innovation #Tech",
    ]
    day_index = datetime.now().weekday() % len(templates)
    return templates[day_index]


def log_action(status, message):
    """Log the generator activity."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    entry = f"- [{datetime.now().strftime('%H:%M:%S')}] ContentGenerator | {status} | {message}\n"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(entry)


def update_dashboard(filename, status):
    """Update dashboard with generator status."""
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
                    f"- [LinkedIn Content {status}] {filename} "
                    f"({datetime.now().strftime('%Y-%m-%d %H:%M')})"
                )
                added = True
        dashboard.write_text('\n'.join(updated), encoding='utf-8')


def main():
    print("=" * 50)
    print("  LinkedIn Content Generator - AI Employee")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # Check if today's post already exists
    today_str = datetime.now().strftime('%Y-%m-%d')
    output_file = POSTS_DIR / f"daily_post_{today_str}.md"

    if output_file.exists():
        print(f"[SKIP] Today's post already exists: {output_file.name}")
        log_action("SKIPPED", f"Post already exists: {output_file.name}")
        return

    # Check scheduled posts first
    POSTS_DIR.mkdir(parents=True, exist_ok=True)

    if SCHEDULED_POSTS_FILE.exists():
        with open(SCHEDULED_POSTS_FILE, 'r', encoding='utf-8') as f:
            scheduled = json.load(f)
        if today_str in scheduled:
            post_content = scheduled[today_str]
            print(f"[SCHEDULED] Using pre-written post for {today_str}")
            log_action("SCHEDULED", f"Used pre-written post for {today_str}")
        else:
            # Fallback if no scheduled post for today
            goals_context = load_business_goals()
            today_topic = DAILY_TOPICS[datetime.now().weekday()]
            print(f"[TOPIC] {today_topic}")
            post_content = generate_fallback_post(today_topic, goals_context)
            log_action("FALLBACK", f"No scheduled post for {today_str}, used template")
    else:
        goals_context = load_business_goals()
        today_topic = DAILY_TOPICS[datetime.now().weekday()]
        post_content = generate_fallback_post(today_topic, goals_context)
        log_action("FALLBACK", "scheduled_posts.json not found, used template")

    # Save post file
    output_file.write_text(post_content, encoding='utf-8')
    print(f"[SAVED] {output_file.name}")
    print(f"\n--- POST PREVIEW ---\n{post_content[:200]}...\n---")

    update_dashboard(output_file.name, "GENERATED")
    log_action("SAVED", f"Post saved to {output_file.name} — linkedin_watcher will publish it")

    print("\n[DONE] linkedin_watcher.py will detect and publish this post automatically.")
    print("=" * 50)


if __name__ == "__main__":
    main()
