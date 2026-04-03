"""
Windows Task Scheduler Setup for AI Employee
Automatically starts Gmail Watcher and Approval Watcher on Windows startup.
"""

import subprocess
import sys
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
PYTHON_PATH = sys.executable
GMAIL_WATCHER = BASE_DIR / "watchers" / "gmail_watcher.py"
APPROVAL_WATCHER = BASE_DIR / "watchers" / "approval_watcher.py"


def create_task(task_name, script_path, description):
    """Create a Windows Task Scheduler task."""
    cmd = [
        "schtasks", "/create",
        "/tn", task_name,
        "/tr", f'"{PYTHON_PATH}" "{script_path}"',
        "/sc", "ONLOGON",
        "/rl", "HIGHEST",
        "/f",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

    if result.returncode == 0:
        print(f"[OK] Task created: {task_name}")
    else:
        print(f"[ERROR] Failed to create task: {task_name}")
        print(f"       {result.stderr.strip()}")

    return result.returncode == 0


def verify_task(task_name):
    """Check if a task exists."""
    result = subprocess.run(
        ["schtasks", "/query", "/tn", task_name],
        capture_output=True, text=True, shell=True
    )
    return result.returncode == 0


def main():
    print("=" * 50)
    print("  AI Employee - Scheduler Setup")
    print("=" * 50)
    print(f"Python: {PYTHON_PATH}")
    print(f"Project: {BASE_DIR}")
    print("=" * 50)

    tasks = [
        {
            "name": "AIEmployee_GmailWatcher",
            "script": GMAIL_WATCHER,
            "description": "AI Employee - Gmail Watcher"
        },
        {
            "name": "AIEmployee_ApprovalWatcher",
            "script": APPROVAL_WATCHER,
            "description": "AI Employee - Approval Watcher"
        },
    ]

    success = 0
    for task in tasks:
        print(f"\nCreating: {task['name']}")
        if create_task(task["name"], task["script"], task["description"]):
            success += 1

    print("\n" + "=" * 50)
    print(f"Tasks created: {success}/{len(tasks)}")

    print("\nVerifying tasks...")
    for task in tasks:
        status = "EXISTS" if verify_task(task["name"]) else "MISSING"
        print(f"  [{status}] {task['name']}")

    print("\nDone! Watchers will auto-start on Windows login.")
    print("To view tasks: open Task Scheduler > Task Scheduler Library")


if __name__ == "__main__":
    main()
