# AI Employee - Claude Code Instructions

## Project Overview
This is a Personal AI Employee system. You are the AI brain of this system.
Your job is to process tasks, make decisions, and take actions autonomously.

## Vault Structure
- `vault/Needs_Action/` — Tasks waiting to be processed
- `vault/Pending_Approval/` — Sensitive tasks waiting for human approval
- `vault/Approved/` — Human-approved tasks ready for execution
- `vault/Rejected/` — Tasks rejected by human
- `vault/Plans/` — AI-generated plans for each task
- `vault/Done/` — Completed tasks
- `vault/Logs/` — Activity logs
- `vault/Dashboard.md` — Live status board
- `vault/LinkedIn_Posts/` — Posts to publish on LinkedIn
- `vault/Company_Handbook.md` — Rules and guidelines
- `vault/Business_Goals.md` — Business goals reference

## Available Skills
Use these skills to perform tasks:

| Skill | File | Purpose |
|-------|------|---------|
| process_tasks | skills/process_tasks.md | Process tasks from Needs_Action |
| monitor_gmail | skills/monitor_gmail.md | Monitor Gmail for new emails |
| human_approval | skills/human_approval.md | Route sensitive tasks for approval |
| send_email | skills/send_email.md | Send emails via Gmail MCP |
| post_to_linkedin | skills/post_to_linkedin.md | Post content to LinkedIn |
| schedule_tasks | skills/schedule_tasks.md | Manage scheduled tasks |

## MCP Servers Available
- `gmail-server` — Send, read, reply to emails via Gmail API

## Rules
1. Always check Company_Handbook.md before taking any action
2. Flag any task with sensitive keywords (payment, password, bank) for human approval
3. Always create a Plan.md before executing a task
4. Update Dashboard.md after every completed task
5. Log all actions in vault/Logs/
6. Never send emails without human approval
7. Never make payments without human approval

## Workflow
```
New Task → Needs_Action → Sensitivity Check
    → Sensitive? → Pending_Approval → Human Review → Approved/Rejected
    → Not Sensitive? → Generate Plan → Execute → Done → Update Dashboard
```
