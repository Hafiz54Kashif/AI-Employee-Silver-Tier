"""
Watchdog - AI Employee Gold Tier
Monitors all watcher processes and auto-restarts them if they crash.
Ensures the AI Employee system runs 24/7 without manual intervention.

HOW IT WORKS:
1. Checks every 60 seconds if each watcher is running
2. If crashed → restarts automatically
3. Logs everything to vault/Logs/
4. Updates Dashboard.md with health status
"""

import os
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
VAULT_DIR = BASE_DIR / "vault"
LOGS_DIR = VAULT_DIR / "Logs"
DASHBOARD_FILE = VAULT_DIR / "Dashboard.md"

# Python executable
PYTHON = sys.executable

# Processes to monitor
WATCHERS = {
    "GmailWatcher": str(BASE_DIR / "watchers" / "gmail_watcher.py"),
    "ApprovalWatcher": str(BASE_DIR / "watchers" / "approval_watcher.py"),
    "LinkedInWatcher": str(BASE_DIR / "watchers" / "linkedin_watcher.py"),
}

CHECK_INTERVAL = 60  # seconds
MAX_RESTARTS = 5     # max restarts per session

# Track running processes and restart counts
processes = {}
restart_counts = {name: 0 for name in WATCHERS}


def log(status, message):
    """Log watchdog activity."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    entry = f"- [{datetime.now().strftime('%H:%M:%S')}] Watchdog | {status} | {message}\n"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(entry)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {status}: {message}")


def update_dashboard(health_status):
    """Update dashboard with system health."""
    if not DASHBOARD_FILE.exists():
        return
    content = DASHBOARD_FILE.read_text(encoding='utf-8')

    # Remove old health status line if exists
    lines = [l for l in content.splitlines() if '🟢 System Health' not in l and '🔴 System Health' not in l]

    # Add new health line at top after title
    health_line = f"🟢 System Health: All watchers running | Last check: {datetime.now().strftime('%H:%M:%S')}"
    if not all(p.poll() is None for p in processes.values() if p):
        health_line = f"🔴 System Health: Some watchers down | Last check: {datetime.now().strftime('%H:%M:%S')}"

    # Insert after first line
    lines.insert(1, health_line)
    DASHBOARD_FILE.write_text('\n'.join(lines), encoding='utf-8')


def start_watcher(name, script_path):
    """Start a watcher process."""
    try:
        proc = subprocess.Popen(
            [PYTHON, script_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        processes[name] = proc
        log("STARTED", f"{name} (PID: {proc.pid})")
        return proc
    except Exception as e:
        log("ERROR", f"Failed to start {name}: {e}")
        return None


def check_and_restart():
    """Check all watchers and restart if needed."""
    all_healthy = True

    for name, script_path in WATCHERS.items():
        proc = processes.get(name)

        # Check if process is running
        if proc is None or proc.poll() is not None:
            all_healthy = False

            if restart_counts[name] >= MAX_RESTARTS:
                log("WARN", f"{name} exceeded max restarts ({MAX_RESTARTS}). Manual intervention needed.")
                continue

            log("RESTART", f"{name} is down. Restarting... (attempt {restart_counts[name] + 1}/{MAX_RESTARTS})")
            new_proc = start_watcher(name, script_path)
            if new_proc:
                restart_counts[name] += 1
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] OK: {name} running (PID: {proc.pid})")

    return all_healthy


def main():
    print("=" * 55)
    print("  Watchdog - AI Employee Gold Tier")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)
    print(f"Monitoring {len(WATCHERS)} processes every {CHECK_INTERVAL}s")
    print("Press Ctrl+C to stop\n")

    log("STARTED", f"Watchdog started — monitoring: {', '.join(WATCHERS.keys())}")

    # Start all watchers initially
    print("[INIT] Starting all watchers...")
    for name, script_path in WATCHERS.items():
        if Path(script_path).exists():
            start_watcher(name, script_path)
        else:
            log("WARN", f"Script not found: {script_path}")

    print(f"\n[RUNNING] Checking every {CHECK_INTERVAL} seconds...\n")

    while True:
        try:
            time.sleep(CHECK_INTERVAL)
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Health Check:")
            all_healthy = check_and_restart()
            update_dashboard(all_healthy)

        except KeyboardInterrupt:
            print("\n[STOP] Watchdog stopping...")
            log("STOPPED", "Watchdog manually stopped")
            # Stop all managed processes
            for name, proc in processes.items():
                if proc and proc.poll() is None:
                    proc.terminate()
                    log("STOPPED", f"{name} terminated")
            break
        except Exception as e:
            log("ERROR", f"Watchdog error: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
