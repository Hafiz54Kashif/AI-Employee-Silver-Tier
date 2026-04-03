# watchdog

## Purpose
Monitor all AI Employee watcher processes and automatically restart them if they crash or stop. Ensures the system runs 24/7 without manual intervention.

## Input
- List of critical watcher scripts to monitor
- PID files to track running processes

## Process
1. Check every 60 seconds if each watcher process is running
2. If a process is not running:
   - Log the crash
   - Restart the process automatically
   - Send alert notification
3. Write health status to vault/Logs/watchdog.log
4. Update Dashboard.md with system health status

## Monitored Processes
| Process | Script | Restart on Crash |
|---------|--------|-----------------|
| Gmail Watcher | watchers/gmail_watcher.py | Yes |
| Approval Watcher | watchers/approval_watcher.py | Yes |
| LinkedIn Watcher | watchers/linkedin_watcher.py | Yes |

## Output
- All watchers kept alive 24/7
- Crash logs in vault/Logs/
- Dashboard updated with health status
- Email alert sent on repeated crashes
