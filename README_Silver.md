# Personal AI Employee — Silver Tier
### Hackathon 0: Building Autonomous FTEs in 2026
> *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

---

## Tier Declaration
**Silver Tier — Functional Assistant** ✅
Estimated time: 20-30 hours

---

## Submission Info

| Item | Detail |
|------|--------|
| Tier | **Silver — Functional Assistant** |
| Demo Video | 5-10 minute walkthrough |
| Security | Credentials in `.env` — never committed |
| Submit Form | https://forms.gle/JR9T1SJq5rmQyGkGA |

---

## Silver Tier Checklist

### Bronze Requirements (All Complete)
| Requirement | Status | Evidence |
|-------------|--------|----------|
| Dashboard.md + Company_Handbook.md | ✅ Done | `vault/Dashboard.md`, `vault/Company_Handbook.md` |
| Basic folder structure | ✅ Done | `/Needs_Action`, `/Done`, `/Plans`, `/Logs` |
| One working Watcher (Gmail) | ✅ Done | `watchers/gmail_watcher.py` |
| Claude reads/writes vault | ✅ Done | 20+ plans generated in `vault/Plans/` |
| Agent Skills | ✅ Done | `skills/` folder |

### Silver Requirements
| Requirement | Status | Evidence |
|-------------|--------|----------|
| 2+ Watcher scripts | ✅ Done | Gmail + Filesystem + LinkedIn = 3 watchers |
| LinkedIn Auto-Post (generate sales) | ✅ Done | `watchers/linkedin_watcher.py` + `linkedin_content_generator.py` |
| Claude reasoning loop with Plan.md | ✅ Done | `vault/Plans/` — 20+ plans auto-generated |
| One working MCP server (email sending) | ✅ Done | `skills/gmail_mcp_server.py` |
| Human-in-the-loop approval workflow | ✅ Done | Pending_Approval → Approved/Rejected flow |
| Basic scheduling (cron / Task Scheduler) | ✅ Done | Daily 9 AM + `scripts/setup_scheduler.bat` |
| All AI functionality as Agent Skills | ✅ Done | 6 skills in `skills/` folder |

---

## Overview

**Personal AI Employee (Silver)** adds a full perception layer (3 watchers), LinkedIn auto-posting,
email sending via MCP, human-in-the-loop approval for sensitive tasks, and scheduled automation.
The AI now acts proactively — it doesn't just wait for input, it monitors and responds autonomously.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│            EXTERNAL SOURCES                     │
│   Gmail       │    Files      │    LinkedIn     │
└──────┬─────────┴──────┬────────┴───────┬─────────┘
       ↓                ↓                ↓
┌─────────────────────────────────────────────────┐
│          PERCEPTION LAYER (Watchers)            │
│  gmail_watcher.py │ filesystem_watcher.py       │
│  linkedin_watcher.py + linkedin_content_gen.py  │
└──────────────────────┬──────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│          OBSIDIAN VAULT (Local Memory)          │
│  /Needs_Action/ │ /Plans/ │ /Done/ │ /Logs/     │
│  /Pending_Approval/ │ /Approved/ │ /Rejected/   │
│  Dashboard.md │ Company_Handbook.md             │
└──────────────────────┬──────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│        REASONING LAYER (Claude Code)            │
│   Read → Sensitivity Check → Plan → Execute     │
└──────────┬──────────────────────┬───────────────┘
           ↓                      ↓
┌──────────────────┐   ┌─────────────────────────┐
│ HUMAN-IN-THE-    │   │     ACTION LAYER         │
│ LOOP APPROVAL    │──▶│  Gmail MCP → Send Email  │
│ Move to /Approved│   │  LinkedIn API → Post     │
└──────────────────┘   └─────────────────────────┘
```

---

## Folder Structure

```
AI_Employee_Project/
├── vault/
│   ├── Needs_Action/           ← Incoming tasks
│   ├── Pending_Approval/       ← Awaiting human review
│   ├── Approved/               ← Ready to execute
│   ├── Rejected/               ← Human-rejected tasks
│   ├── Plans/                  ← AI-generated plans
│   ├── Done/
│   │   └── linkedin_posted/    ← Published LinkedIn posts
│   ├── Logs/                   ← Activity logs
│   ├── LinkedIn_Posts/         ← Pending posts
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   └── Business_Goals.md
├── watchers/
│   ├── gmail_watcher.py
│   ├── filesystem_watcher.py
│   ├── approval_watcher.py
│   ├── linkedin_watcher.py
│   └── linkedin_content_generator.py
├── skills/
│   ├── process_tasks.md
│   ├── monitor_gmail.md
│   ├── human_approval.md
│   ├── send_email.md
│   ├── post_to_linkedin.md
│   ├── schedule_tasks.md
│   └── gmail_mcp_server.py
├── scripts/
│   ├── setup_scheduler.py
│   ├── setup_scheduler.bat
│   └── task_processor.py
└── .env
```

---

## Key Features

### 1. Gmail Monitoring + Auto-Reply
- `watchers/gmail_watcher.py` checks Gmail every 2 minutes
- Email saved as `.md` file in `vault/Needs_Action/`
- Claude generates plan → drafts reply → sends via Gmail MCP

### 2. Human-in-the-Loop Approval
- Sensitive keywords detected: `payment`, `password`, `bank`, `invoice`, etc.
- Task moved to `vault/Pending_Approval/` automatically
- Human moves to `vault/Approved/` or `vault/Rejected/`
- `watchers/approval_watcher.py` executes approved tasks

### 3. LinkedIn Auto-Posting (Daily)
- `linkedin_content_generator.py` runs every day at 9:00 AM
- Claude reads `vault/Business_Goals.md` and generates unique post
- Saved to `vault/LinkedIn_Posts/daily_post_YYYY-MM-DD.md`
- `linkedin_watcher.py` detects and publishes automatically
- Topics rotate: AI, product launch, customer success, etc.

### 4. Gmail MCP Server
- Claude can send emails directly via MCP
- No browser automation needed
- `skills/gmail_mcp_server.py`

### 5. Scheduling
- Daily 9 AM LinkedIn content generation
- Windows Task Scheduler via `scripts/setup_scheduler.bat`

---

## Agent Skills

| Skill | Purpose |
|-------|---------|
| `process_tasks.md` | Process tasks from Needs_Action |
| `monitor_gmail.md` | Monitor Gmail for new emails |
| `human_approval.md` | Route sensitive tasks for approval |
| `send_email.md` | Send emails via Gmail MCP |
| `post_to_linkedin.md` | Post content to LinkedIn |
| `schedule_tasks.md` | Manage scheduled tasks |

---

## Demo Flows

### Flow 1: Email → Auto-Reply
```
Email arrives in Gmail
  → gmail_watcher.py detects (every 2 mins)
  → vault/Needs_Action/email_XXXX.md created
  → Claude reads + creates vault/Plans/plan.md
  → Reply sent via Gmail MCP
  → Moved to vault/Done/
  → Dashboard.md updated
```

### Flow 2: Sensitive Email → Human Approval
```
Email with "payment" arrives
  → Sensitivity check triggers
  → Moved to vault/Pending_Approval/
  → Human reviews in Obsidian
  → Moves to vault/Approved/
  → approval_watcher.py detects
  → Claude executes + moves to vault/Done/
```

### Flow 3: LinkedIn Daily Post
```
9:00 AM — Scheduler fires
  → linkedin_content_generator.py runs
  → Claude generates post from Business_Goals.md
  → Saved to vault/LinkedIn_Posts/
  → linkedin_watcher.py posts to LinkedIn
  → Moved to vault/Done/linkedin_posted/
  → Dashboard.md updated
```

---

## Setup

### 1. Install Dependencies
```bash
pip install watchdog google-auth google-auth-oauthlib google-api-python-client requests
```

### 2. Configure `.env`
```env
LINKEDIN_ACCESS_TOKEN=your_linkedin_token
ANTHROPIC_API_KEY=your_anthropic_key
```

### 3. Start All Watchers
```bash
python watchers/gmail_watcher.py
python watchers/approval_watcher.py
python watchers/linkedin_watcher.py
```

### 4. Setup Permanent Scheduling (Run as Admin)
```bash
scripts/setup_scheduler.bat
```

---

## Security

| Concern | How We Handle It |
|---------|-----------------|
| API Keys | `.env` only — never hardcoded |
| `.gitignore` | `.env` excluded from git |
| Sensitive Actions | 15+ keywords trigger HITL approval |
| Payments | Always require human move to `/Approved` |
| Audit Trail | Every action logged in `vault/Logs/` |

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Claude Code | AI reasoning engine |
| Obsidian Vault | Local memory + dashboard |
| Python 3.13+ | Watcher scripts |
| Gmail API (OAuth2) | Email monitoring + sending |
| LinkedIn API | Automated posting |
| Gmail MCP Server | Claude → send emails |
| Windows Task Scheduler | Permanent scheduling |

---

*Silver Tier — Functional Assistant complete. Built with Claude Code + Python + Obsidian + MCP.*
