# schedule_tasks

## Purpose
Automatically start all AI Employee watchers on Windows login using Task Scheduler, ensuring the system is always running without manual intervention.

## Input
- Windows Task Scheduler (built-in Windows tool)
- Python scripts for Gmail and Approval watchers

## Scheduled Tasks
| Task Name | Script | Trigger |
|-----------|--------|---------|
| AIEmployee_GmailWatcher | watchers/gmail_watcher.py | On Windows Login |
| AIEmployee_ApprovalWatcher | watchers/approval_watcher.py | On Windows Login |

## Process
1. Run `scripts/setup_scheduler.bat` as Administrator
2. Creates two scheduled tasks in Windows Task Scheduler
3. Both tasks trigger automatically on user login
4. Tasks run with highest privileges
5. No manual startup required

## Output
- Two persistent scheduled tasks in Windows
- Watchers auto-start on every Windows login
- AI Employee always active in background

## Manual Management
- View tasks: Open Task Scheduler > Task Scheduler Library
- Disable: `schtasks /delete /tn "AIEmployee_GmailWatcher"`
- Check status: `schtasks /query /tn "AIEmployee_GmailWatcher"`
