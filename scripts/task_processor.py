"""
Task Processor for AI Employee
Implements the process_tasks skill workflow
"""

import os
import shutil
import time
import base64
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
sys.path.append('scripts')
from logging_utils import log_activity, log_task_completion, log_task_moved

# Gmail API imports
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

BASE_DIR = Path(__file__).resolve().parent.parent
TOKEN_FILE = BASE_DIR / "token.json"
VAULT_DIR = BASE_DIR / "vault"
SCOPES = ['https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.modify']


def get_gmail_service():
    """Get authenticated Gmail service."""
    if not GMAIL_AVAILABLE or not TOKEN_FILE.exists():
        return None
    try:
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return build('gmail', 'v1', credentials=creds)
    except Exception:
        return None


def generate_auto_reply(sender, subject, email_body):
    """Generate a professional auto-reply based on email content."""
    name = sender.split('<')[0].strip().split()[0] if sender else "there"
    return f"""Dear {name},

Thank you for your email regarding "{subject}".

I have received your message and our AI Employee system has logged it for processing.
A team member will review your request and get back to you shortly.

Summary of your inquiry:
{email_body[:200]}...

Best regards,
Hafiz Kashif
Hafiz Kashif AI Solutions

---
This email was sent by a Digital AI Employee.
Powered by Claude Code + Python + Obsidian.
"""


def send_auto_reply(task_content, task_filename):
    """Send auto-reply to email sender using Gmail API."""
    service = get_gmail_service()
    if not service:
        print(f"[REPLY] Gmail service unavailable — skipping reply")
        return False

    try:
        # Extract email details from task content
        lines = task_content.splitlines()
        sender = ""
        subject = ""
        gmail_id = ""
        body_lines = []
        in_body = False

        for line in lines:
            if line.startswith("from:"):
                sender = line.replace("from:", "").strip()
            elif line.startswith("subject:"):
                subject = line.replace("subject:", "").strip()
            elif line.startswith("gmail_id:"):
                gmail_id = line.replace("gmail_id:", "").strip()
            elif line.startswith("## Email Content"):
                in_body = True
            elif in_body and not line.startswith("## Action"):
                body_lines.append(line)

        if not sender or not subject:
            print(f"[REPLY] Could not extract sender/subject — skipping reply")
            return False

        email_body = '\n'.join(body_lines).strip()
        reply_text = generate_auto_reply(sender, subject, email_body)

        # Build reply message
        msg = MIMEMultipart()
        msg['to'] = sender
        msg['subject'] = f"Re: {subject}"
        if gmail_id:
            msg['In-Reply-To'] = gmail_id
            msg['References'] = gmail_id
        msg.attach(MIMEText(reply_text, 'plain'))

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()

        print(f"[REPLY] Auto-reply sent to: {sender}")
        log_activity("Auto-reply sent", f"To: {sender} | Subject: Re: {subject}")
        return True

    except Exception as e:
        print(f"[REPLY] Failed to send reply: {e}")
        return False


def read_task_file(file_path):
    """Read the content of a task file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content.strip()
    except Exception as e:
        print(f"Error reading task file {file_path}: {e}")
        return None


def generate_task_plan(task_content, task_filename):
    """Generate a structured plan based on the task content."""
    plan_content = f"""# Task Plan for: {task_filename}

## Original Task:
{task_content}

## Plan Steps:
1. Analyze the task requirements
2. Identify necessary resources and tools
3. Execute the required actions
4. Validate the results
5. Complete the task

## Status: In Progress
Created on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    return plan_content


def save_task_plan(plan_content, task_filename):
    """Save the generated plan to the Plans folder."""
    try:
        plans_dir = VAULT_DIR / "Plans"
        plans_dir.mkdir(parents=True, exist_ok=True)

        plan_filename = f"{task_filename}_plan.md"
        plan_path = plans_dir / plan_filename

        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)

        log_activity("Plan created", plan_filename)
        print(f"Plan saved: {plan_path}")
        return plan_path
    except Exception as e:
        print(f"Error saving plan: {e}")
        return None


def execute_task_steps(task_content, task_filename):
    """Execute the steps required for the task."""
    # This is a simplified execution - in a real system, this would contain
    # more complex logic based on the task content
    print(f"Executing task: {task_filename}")
    print(f"Task content: {task_content}")

    # Simulate task execution
    time.sleep(2)  # Simulating processing time

    log_activity("Task executed", task_filename)
    return True


def move_task_to_done(task_path):
    """Move the completed task to the Done folder."""
    try:
        done_dir = VAULT_DIR / "Done"
        done_dir.mkdir(parents=True, exist_ok=True)

        # Resolve absolute path
        task_path = Path(task_path).resolve()

        if not task_path.exists():
            print(f"Task already processed: {task_path.name}")
            return done_dir / task_path.name

        destination_path = done_dir / task_path.name
        shutil.move(str(task_path), str(destination_path))

        log_task_moved(task_path.name, "Needs_Action", "Done")
        print(f"Task moved to Done: {destination_path}")
        return destination_path
    except Exception as e:
        print(f"Error moving task to Done: {e}")
        return None


def update_dashboard(task_filename):
    """Update the dashboard with recent activity."""
    try:
        dashboard_path = VAULT_DIR / "Dashboard.md"

        # Read current dashboard content
        if dashboard_path.exists():
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = "# Dashboard\n\n## Pending Tasks\n\n## Recent Activity\n\n## Messages Waiting\n"

        # Find the Recent Activity section and add the completed task
        lines = content.split('\n')
        updated_lines = []
        added = False

        for line in lines:
            updated_lines.append(line)
            if line.startswith("## Recent Activity") and not added:
                updated_lines.append(f"- Completed: {task_filename} ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
                added = True

        # Write updated content back to dashboard
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated_lines))

        log_activity("Dashboard updated", "Recent Activity section")
        print("Dashboard updated with completed task")
    except Exception as e:
        print(f"Error updating dashboard: {e}")


SENSITIVE_KEYWORDS = [
    'payment', 'invoice', 'bank', 'password', 'reset', 'urgent',
    'wire transfer', 'account', 'login', 'credential', 'delete',
    'send email', 'reply', 'forward', 'money', 'transaction'
]


def is_sensitive_task(task_content):
    """Check if a task contains sensitive keywords requiring human approval."""
    content_lower = task_content.lower()
    for keyword in SENSITIVE_KEYWORDS:
        if keyword in content_lower:
            return True, keyword
    return False, None


def move_to_pending_approval(task_path, reason):
    """Move sensitive task to Pending_Approval folder."""
    try:
        pending_dir = VAULT_DIR / "Pending_Approval"
        pending_dir.mkdir(parents=True, exist_ok=True)

        # Read original content and add approval note
        content = task_path.read_text(encoding='utf-8')
        approval_note = f"""
---
## APPROVAL REQUIRED

**Reason:** Task contains sensitive keyword: `{reason}`
**Flagged at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Action needed:** Move this file to `vault/Approved/` to approve or `vault/Rejected/` to reject.

---
"""
        content = content + approval_note
        dest_path = pending_dir / task_path.name
        dest_path.write_text(content, encoding='utf-8')
        task_path.unlink()  # Remove from Needs_Action

        log_activity("Task moved to Pending_Approval", task_path.name)
        print(f"[APPROVAL NEEDED] {task_path.name} → Pending_Approval (reason: {reason})")
        return dest_path
    except Exception as e:
        print(f"Error moving to Pending_Approval: {e}")
        return None


def process_single_task(task_path):
    """Process a single task file through the complete workflow."""
    task_filename = task_path.name
    print(f"\n--- Starting processing for task: {task_filename} ---")

    log_activity("Task processing started", task_filename)

    # Step 1: Read the task file
    task_content = read_task_file(task_path)
    if not task_content:
        print(f"Could not read task content for {task_filename}")
        return False

    # Step 2: Check if task is sensitive → needs human approval
    sensitive, reason = is_sensitive_task(task_content)
    if sensitive:
        move_to_pending_approval(task_path, reason)
        return True  # Task handled — waiting for approval

    # Step 3: Generate task plan
    plan_content = generate_task_plan(task_content, task_filename)
    plan_path = save_task_plan(plan_content, task_filename)

    if not plan_path:
        print(f"Could not create plan for {task_filename}")
        return False

    # Step 4: Send auto-reply if it's an email task
    if task_filename.startswith("email_"):
        send_auto_reply(task_content, task_filename)

    # Step 5: Execute task steps
    if not execute_task_steps(task_content, task_filename):
        print(f"Could not execute task steps for {task_filename}")
        return False

    # Step 7: Move task to Done
    done_path = move_task_to_done(task_path)
    if not done_path:
        print(f"Could not move task to Done for {task_filename}")
        return False

    # Step 6: Update dashboard
    update_dashboard(task_filename)

    # Step 7: Log completion
    log_task_completion(task_filename)
    print(f"--- Completed processing for task: {task_filename} ---")

    return True


def monitor_and_process_tasks():
    """Monitor Needs_Action folder and process tasks."""
    needs_action_dir = VAULT_DIR / "Needs_Action"

    print("Starting task processor...")
    print(f"Monitoring: {needs_action_dir.absolute()}")
    print("Press Ctrl+C to stop")

    try:
        while True:
            # Look for task files in Needs_Action folder
            task_files = list(needs_action_dir.glob("*"))

            if task_files:
                for task_file in task_files:
                    if task_file.is_file():
                        # Process the task
                        process_single_task(task_file)

            # Wait before checking again
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nTask processor stopped by user.")


if __name__ == "__main__":
    monitor_and_process_tasks()