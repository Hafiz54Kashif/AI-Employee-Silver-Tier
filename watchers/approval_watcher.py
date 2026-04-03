"""
Approval Watcher - Human-in-the-Loop Workflow
Monitors Approved and Rejected folders and acts accordingly.

HOW TO USE:
- Sensitive tasks go to vault/Pending_Approval/
- You review them in Obsidian
- Move to vault/Approved/  → AI will process them
- Move to vault/Rejected/  → AI will skip them and log
"""

import sys
import time
import shutil
from pathlib import Path
from datetime import datetime

sys.path.append('scripts')
from logging_utils import log_activity

# Paths
BASE_DIR = Path(__file__).parent.parent
VAULT_DIR = BASE_DIR / "vault"
APPROVED_DIR = VAULT_DIR / "Approved"
REJECTED_DIR = VAULT_DIR / "Rejected"
DONE_DIR = VAULT_DIR / "Done"
PLANS_DIR = VAULT_DIR / "Plans"
DASHBOARD_PATH = VAULT_DIR / "Dashboard.md"

CHECK_INTERVAL = 15  # seconds


def ensure_folders():
    for folder in [APPROVED_DIR, REJECTED_DIR, DONE_DIR, PLANS_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def generate_plan(task_content, task_filename):
    return f"""# Approved Task Plan: {task_filename}

## Task Content
{task_content}

## Execution Plan
1. Task was reviewed and approved by human
2. Analyze task requirements
3. Execute required actions
4. Validate results
5. Mark as complete

## Status: Approved & Executed
**Approved at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""


def update_dashboard(task_filename, action):
    try:
        if DASHBOARD_PATH.exists():
            content = DASHBOARD_PATH.read_text(encoding='utf-8')
        else:
            content = "# Dashboard\n\n## Recent Activity\n\n## Pending Approvals\n"

        lines = content.split('\n')
        updated = []
        added = False
        for line in lines:
            updated.append(line)
            if line.startswith("## Recent Activity") and not added:
                status = "APPROVED" if action == "approved" else "REJECTED"
                updated.append(f"- [{status}] {task_filename} ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
                added = True

        DASHBOARD_PATH.write_text('\n'.join(updated), encoding='utf-8')
    except Exception as e:
        print(f"[ERROR] Dashboard update failed: {e}")


def process_approved_task(task_path):
    """Process a task that has been approved by the human."""
    print(f"\n[APPROVED] Processing: {task_path.name}")
    log_activity("Task approved by human", task_path.name)

    try:
        task_content = task_path.read_text(encoding='utf-8')

        # Save plan
        plan_content = generate_plan(task_content, task_path.name)
        plan_path = PLANS_DIR / f"{task_path.stem}_approved_plan.md"
        plan_path.write_text(plan_content, encoding='utf-8')
        print(f"[PLAN] Saved: {plan_path.name}")

        # Move to Done
        done_path = DONE_DIR / task_path.name
        shutil.move(str(task_path), str(done_path))
        print(f"[DONE] Moved to Done: {task_path.name}")

        # Update dashboard
        update_dashboard(task_path.name, "approved")
        log_activity("Approved task completed", task_path.name)

    except Exception as e:
        print(f"[ERROR] Failed to process approved task: {e}")


def process_rejected_task(task_path):
    """Log and archive a rejected task."""
    print(f"\n[REJECTED] Skipping: {task_path.name}")
    log_activity("Task rejected by human", task_path.name)

    try:
        # Move to Done with rejected note
        content = task_path.read_text(encoding='utf-8')
        content += f"\n\n---\n**REJECTED** at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        done_path = DONE_DIR / f"REJECTED_{task_path.name}"
        done_path.write_text(content, encoding='utf-8')
        task_path.unlink()

        update_dashboard(task_path.name, "rejected")
        print(f"[DONE] Rejection logged: {done_path.name}")

    except Exception as e:
        print(f"[ERROR] Failed to process rejected task: {e}")


def main():
    print("=" * 50)
    print("  Approval Watcher - Human-in-the-Loop")
    print("=" * 50)
    print(f"Watching: {APPROVED_DIR}")
    print(f"Watching: {REJECTED_DIR}")
    print(f"Check interval: {CHECK_INTERVAL}s")
    print("=" * 50)
    print("\nWaiting for approvals... (Press Ctrl+C to stop)\n")

    ensure_folders()

    while True:
        # Check Approved folder
        approved_files = [f for f in APPROVED_DIR.iterdir() if f.is_file() and f.suffix == '.md']
        for task_file in approved_files:
            process_approved_task(task_file)

        # Check Rejected folder
        rejected_files = [f for f in REJECTED_DIR.iterdir() if f.is_file() and f.suffix == '.md']
        for task_file in rejected_files:
            process_rejected_task(task_file)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
