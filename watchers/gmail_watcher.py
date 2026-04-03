import os
import time
import base64
import json
from pathlib import Path
from datetime import datetime

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Paths — use AppData when running from .exe, project root in dev
import sys as _sys
if os.environ.get('AI_EMPLOYEE_DATA'):
    BASE_DIR = Path(os.environ['AI_EMPLOYEE_DATA'])
elif getattr(_sys, 'frozen', False):
    BASE_DIR = Path(os.environ.get('APPDATA', '')) / 'AI Employee'
else:
    BASE_DIR = Path(__file__).parent.parent
VAULT_DIR = BASE_DIR / "vault"
NEEDS_ACTION_DIR = VAULT_DIR / "Needs_Action"
DONE_DIR = VAULT_DIR / "Done"
DASHBOARD_FILE = VAULT_DIR / "Dashboard.md"
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

SETTINGS_FILE = BASE_DIR / "settings.json"
LOGS_DIR = VAULT_DIR / "Logs"


def log_action(status, message):
    """Write action to vault/Logs/YYYY-MM-DD.md"""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    entry = f"- [{datetime.now().strftime('%H:%M:%S')}] GmailWatcher | {status} | {message}\n"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(entry)

DEFAULT_EMAIL_SETTINGS = {
    "check_interval_minutes": 2,
    "sensitive_keywords": ["payment", "password", "bank", "urgent", "lawsuit"],
    "auto_reply": True,
    "reply_tone": "Professional",
}


def load_settings():
    defaults = {"email": DEFAULT_EMAIL_SETTINGS.copy(), "agent": {"status": "running"}}
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
            if "email" not in data:
                data["email"] = DEFAULT_EMAIL_SETTINGS.copy()
            else:
                for k, v in DEFAULT_EMAIL_SETTINGS.items():
                    data["email"].setdefault(k, v)
            return data
        except (json.JSONDecodeError, OSError):
            pass
    return defaults

# Check interval (seconds) — loaded from settings.json
CHECK_INTERVAL = load_settings()["email"]["check_interval_minutes"] * 60


def authenticate():
    """Authenticate with Gmail API and return service."""
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service


def get_email_body(payload):
    """Extract plain text body from email payload."""
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    break
    else:
        data = payload['body'].get('data', '')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    return body[:1000]  # Limit to 1000 chars


def create_action_file(msg_id, sender, subject, date, body):
    """Create a markdown file in Needs_Action folder."""
    safe_subject = "".join(c for c in subject if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_subject = safe_subject[:50].replace(' ', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"email_{timestamp}_{safe_subject}.md"
    filepath = NEEDS_ACTION_DIR / filename

    content = f"""---
type: email
source: gmail
from: {sender}
subject: {subject}
received: {date}
gmail_id: {msg_id}
status: pending
priority: high
---

# Email Task: {subject}

**From:** {sender}
**Received:** {date}
**Gmail ID:** {msg_id}

## Email Content

{body}

## Action Required

Please review this email and determine the appropriate response or action.
"""

    filepath.write_text(content, encoding='utf-8')
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Created: {filename}")
    return filepath


def load_processed_ids():
    """Load already processed email IDs."""
    processed_file = BASE_DIR / "processed_emails.json"
    if processed_file.exists():
        with open(processed_file, 'r') as f:
            return set(json.load(f))
    return set()


def save_processed_ids(processed_ids):
    """Save processed email IDs."""
    processed_file = BASE_DIR / "processed_emails.json"
    with open(processed_file, 'w') as f:
        json.dump(list(processed_ids), f)


def generate_reply(sender, subject, body):
    """Generate a professional auto-reply using Claude via Anthropic API."""
    env_file = BASE_DIR / ".env"
    api_key = ""
    if env_file.exists():
        for line in env_file.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line.startswith("ANTHROPIC_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip('"')
                break

    if api_key and api_key != "your_anthropic_api_key_here":
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": f"""You are a professional AI Employee assistant. Write a brief, polite auto-reply email.

From: {sender}
Subject: {subject}
Message: {body}

Write only the email body (no subject line). Keep it 2-3 sentences. Be professional and helpful.
Mention that the message has been received and will be reviewed. Sign off as 'AI Employee Assistant'."""
                }]
            )
            return message.content[0].text.strip()
        except Exception as e:
            print(f"[WARN] Claude API failed: {e}. Using default reply.")

    # Default fallback reply
    return f"""Thank you for your email regarding "{subject}".

Your message has been received and logged by our AI Employee system. A team member will review and respond to you shortly.

Best regards,
AI Employee Assistant"""


def send_reply(service, msg_id, sender, subject, reply_body):
    """Send a reply to an email."""
    try:
        import email as email_lib
        from email.mime.text import MIMEText

        # Build reply message
        reply_subject = subject if subject.startswith("Re:") else f"Re: {subject}"
        message = MIMEText(reply_body)
        message['to'] = sender
        message['subject'] = reply_subject
        message['In-Reply-To'] = msg_id
        message['References'] = msg_id

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        service.users().messages().send(
            userId='me',
            body={'raw': raw, 'threadId': msg_id}
        ).execute()

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Reply sent to: {sender}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send reply: {e}")
        return False


def check_emails(service, processed_ids):
    """Check for new unread important emails."""
    new_count = 0
    try:
        results = service.users().messages().list(
            userId='me',
            q='is:unread',
            maxResults=10
        ).execute()

        messages = results.get('messages', [])

        for msg in messages:
            msg_id = msg['id']
            if msg_id in processed_ids:
                continue

            # Mark as processing immediately to prevent duplicate replies
            processed_ids.add(msg_id)
            save_processed_ids(processed_ids)

            # Get full message
            full_msg = service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()

            headers = {h['name']: h['value'] for h in full_msg['payload']['headers']}
            sender = headers.get('From', 'Unknown')
            subject = headers.get('Subject', 'No Subject')
            date = headers.get('Date', datetime.now().isoformat())
            body = get_email_body(full_msg['payload'])

            print(f"[{datetime.now().strftime('%H:%M:%S')}] NEW EMAIL from: {sender} | Subject: {subject}")
            log_action("NEW EMAIL", f"From: {sender} | Subject: {subject}")
            filepath = create_action_file(msg_id, sender, subject, date, body)

            # Auto-reply
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Generating reply...")
            reply_body = generate_reply(sender, subject, body)
            success = send_reply(service, msg_id, sender, subject, reply_body)
            if success:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Reply SENT to: {sender}")
                log_action("REPLY SENT", f"To: {sender} | Subject: Re: {subject}")
                # Save reply text into the task file
                try:
                    file_content = filepath.read_text(encoding='utf-8')
                    reply_section = f"\n\n## Reply Sent\n\n**Sent At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{reply_body}\n"
                    filepath.write_text(file_content + reply_section, encoding='utf-8')
                except Exception:
                    pass
                # Move task file from Needs_Action to Done
                action_file = NEEDS_ACTION_DIR / filepath.name
                done_file = DONE_DIR / filepath.name
                DONE_DIR.mkdir(parents=True, exist_ok=True)
                if action_file.exists():
                    action_file.rename(done_file)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Moved to Done: {filepath.name}")
                # Update Dashboard
                if DASHBOARD_FILE.exists():
                    dashboard = DASHBOARD_FILE.read_text(encoding='utf-8')
                    entry = f"- Completed: {filepath.name} ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n"
                    dashboard = dashboard.replace("## Recent Activity\n", f"## Recent Activity\n{entry}")
                    DASHBOARD_FILE.write_text(dashboard, encoding='utf-8')

            # Mark as read
            try:
                service.users().messages().modify(
                    userId='me', id=msg_id,
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
            except Exception:
                pass

            new_count += 1

    except Exception as e:
        print(f"[ERROR] {e}")

    return new_count, processed_ids


def load_env_vars():
    """Load all variables from .env file."""
    env = {}
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding='utf-8', errors='replace').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"')
    return env


def check_emails_imap(gmail_address, app_password, processed_ids):
    """Check unread emails via IMAP (App Password method).
    Only processes emails with UID greater than the saved watermark."""
    import imaplib
    import email as email_lib
    new_count = 0
    max_uid = load_max_uid()
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(gmail_address, app_password)
        imap.select("INBOX")
        # Search ALL emails with UID > watermark (seen or unseen)
        # This ensures manually-read emails still get auto-replied
        _, msg_data = imap.uid('search', None, f'UID {max_uid + 1}:*')
        uids = msg_data[0].split()
        # Filter: only UIDs strictly greater than max_uid
        uids = [u for u in uids if int(u) > max_uid]
        for num in uids:
            _, data = imap.uid('fetch', num, "(RFC822)")
            raw = data[0][1]
            msg = email_lib.message_from_bytes(raw)
            msg_id = msg.get("Message-ID", str(num))
            if msg_id in processed_ids:
                continue
            processed_ids.add(msg_id)
            save_processed_ids(processed_ids)

            sender  = msg.get("From", "Unknown")
            subject = msg.get("Subject", "No Subject")
            date    = msg.get("Date", datetime.now().isoformat())
            body    = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')[:1000]
                        break
            else:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')[:1000]

            # Skip no-reply / automated senders — never reply to them
            NO_REPLY_KEYWORDS = [
                'noreply', 'no-reply', 'no_reply', 'donotreply', 'do-not-reply',
                'do_not_reply', 'mailer-daemon', 'postmaster', 'notifications@',
                'newsletter', 'automated@', 'system@', 'bounce@'
            ]
            sender_lower = sender.lower()
            if any(kw in sender_lower for kw in NO_REPLY_KEYWORDS):
                print(f"[{datetime.now().strftime('%H:%M:%S')}] SKIPPED (no-reply sender): {sender}")
                log_action("SKIPPED", f"No-reply sender: {sender} | Subject: {subject}")
                new_count += 1
                continue

            print(f"[{datetime.now().strftime('%H:%M:%S')}] NEW EMAIL from: {sender} | {subject}")
            log_action("NEW EMAIL", f"From: {sender} | Subject: {subject}")
            filepath = create_action_file(msg_id, sender, subject, date, body)

            reply_body = generate_reply(sender, subject, body)
            success = send_reply_smtp(gmail_address, app_password, sender, subject, reply_body)
            if success:
                log_action("REPLY SENT", f"To: {sender} | Subject: Re: {subject}")
                try:
                    content = filepath.read_text(encoding='utf-8')
                    filepath.write_text(content + f"\n\n## Reply Sent\n\n**Sent At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{reply_body}\n", encoding='utf-8')
                except Exception:
                    pass
                done_file = DONE_DIR / filepath.name
                DONE_DIR.mkdir(parents=True, exist_ok=True)
                if filepath.exists():
                    filepath.rename(done_file)
            new_count += 1
        imap.logout()
    except Exception as e:
        print(f"[ERROR IMAP] {e}")
        log_action("ERROR", str(e))
    return new_count, processed_ids


def send_reply_smtp(gmail_address, app_password, to, subject, body):
    """Send email reply via SMTP (App Password method)."""
    import smtplib
    from email.mime.text import MIMEText
    try:
        reply_subject = subject if subject.startswith("Re:") else f"Re: {subject}"
        msg = MIMEText(body)
        msg['From']    = gmail_address
        msg['To']      = to
        msg['Subject'] = reply_subject
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(gmail_address, app_password)
            smtp.send_message(msg)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Reply SENT (SMTP) to: {to}")
        return True
    except Exception as e:
        print(f"[ERROR SMTP] {e}")
        return False


def get_and_save_max_uid(gmail_address, app_password):
    """Get the highest UID currently in inbox and save it to a file.
    On next check, only emails with UID > this value will be processed."""
    import imaplib
    max_uid_file = BASE_DIR / "last_uid.txt"
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(gmail_address, app_password)
        imap.select("INBOX")
        # Get the highest UID in the entire inbox (not just unread)
        _, data = imap.uid('search', None, 'ALL')
        all_uids = data[0].split()
        if all_uids:
            max_uid = int(all_uids[-1])
        else:
            max_uid = 0
        imap.logout()
        max_uid_file.write_text(str(max_uid), encoding='utf-8')
        print(f"[INIT] Inbox snapshot taken. Max UID = {max_uid}. Only NEW emails (UID > {max_uid}) will get auto-reply.")
        log_action("INIT", f"Inbox snapshot: max UID={max_uid}. Watching for new emails only.")
        return max_uid
    except Exception as e:
        print(f"[INIT ERROR] {e}")
        return 0


def load_max_uid():
    """Load the saved max UID (watermark)."""
    max_uid_file = BASE_DIR / "last_uid.txt"
    if max_uid_file.exists():
        try:
            return int(max_uid_file.read_text(encoding='utf-8').strip())
        except Exception:
            return 0
    return None  # None means not initialized yet


def mark_existing_unread_as_seen_api(service, processed_ids):
    """On first run via Gmail API: mark all existing unread as seen."""
    try:
        results = service.users().messages().list(
            userId='me', q='is:unread', maxResults=500
        ).execute()
        messages = results.get('messages', [])
        if not messages:
            return processed_ids
        print(f"[INIT] Found {len(messages)} existing unread email(s). Marking as seen...")
        for msg in messages:
            processed_ids.add(msg['id'])
        save_processed_ids(processed_ids)
        print(f"[INIT] Done — {len(messages)} old email(s) skipped.")
        log_action("INIT", f"Skipped {len(messages)} existing unread emails.")
    except Exception as e:
        print(f"[INIT ERROR] {e}")
    return processed_ids


def main():
    print("=" * 50)
    print("  Gmail Watcher - Personal AI Employee")
    print("=" * 50)

    NEEDS_ACTION_DIR.mkdir(parents=True, exist_ok=True)

    # Detect which method to use
    env = load_env_vars()
    gmail_address  = env.get("GMAIL_ADDRESS", "")
    app_password   = env.get("GMAIL_APP_PASSWORD", "")

    use_imap = bool(gmail_address and app_password)

    if use_imap:
        print(f"  Mode: IMAP/SMTP (App Password)")
        print(f"  Account: {gmail_address}")
        service = None
    else:
        print(f"  Mode: Gmail API (OAuth)")
        print("\nAuthenticating with Gmail API...")
        service = authenticate()
        print("Gmail authenticated successfully!")

    print("=" * 50)
    processed_ids = load_processed_ids()
    print(f"Previously processed: {len(processed_ids)} emails")

    # On first run (no UID watermark saved), take inbox snapshot instantly
    # This is instant — no need to fetch 1000s of email headers
    if use_imap and load_max_uid() is None:
        print("[INIT] First run — taking inbox snapshot (instant)...")
        get_and_save_max_uid(gmail_address, app_password)

    print("\nStarting... (Press Ctrl+C to stop)\n")

    while True:
        settings = load_settings()
        if settings.get("agent", {}).get("status") == "stopped":
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Agent paused. Waiting...")
            time.sleep(30)
            continue

        interval = settings["email"]["check_interval_minutes"] * 60
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking Gmail...")

        if use_imap:
            new_count, processed_ids = check_emails_imap(gmail_address, app_password, processed_ids)
        else:
            new_count, processed_ids = check_emails(service, processed_ids)

        if new_count > 0:
            save_processed_ids(processed_ids)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {new_count} new email(s) processed")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] No new emails.")

        time.sleep(interval)


if __name__ == "__main__":
    # Prevent multiple instances running simultaneously
    lock_file = BASE_DIR / "watcher.lock"
    if lock_file.exists():
        try:
            pid = int(lock_file.read_text().strip())
            import psutil
            if psutil.pid_exists(pid):
                print(f"[ERROR] Watcher already running (PID {pid}). Exiting.")
                exit(0)
        except Exception:
            pass
    lock_file.write_text(str(os.getpid()))
    try:
        main()
    finally:
        if lock_file.exists():
            lock_file.unlink()
