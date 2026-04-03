# AI Employee — Silver Tier
### Autonomous Personal AI Agent | Gmail + LinkedIn + Flask Dashboard

> *Your personal AI employee that works 24/7 — monitors your inbox, replies intelligently, and posts to LinkedIn daily. Fully autonomous. Zero manual effort.*

---

## What It Does

| Feature | Description |
|---------|-------------|
| **Gmail Auto-Reply** | Monitors your inbox every 2 minutes. Reads new emails, drafts professional replies, sends automatically |
| **LinkedIn Auto-Posting** | Posts daily content to your LinkedIn at a scheduled time — from your own pre-written queue |
| **Human-in-the-Loop** | Sensitive emails (payment, password, bank) are held for your approval before any action |
| **Flask Dashboard** | Web UI to connect accounts, manage settings, review flagged emails, and schedule LinkedIn posts |
| **Windows Installer** | Ships as a `.exe` — customers install it like any app, no coding required |

---

## System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    AI EMPLOYEE SYSTEM                    │
└──────────────────────────────────────────────────────────┘

  Gmail Inbox              LinkedIn Profile
      │                         │
      ▼                         ▼
┌─────────────┐         ┌───────────────────┐
│gmail_watcher│         │linkedin_scheduler │
│  (IMAP)     │         │  (time-based)     │
└──────┬──────┘         └────────┬──────────┘
       │                         │
       ▼                         ▼
┌──────────────────────────────────────────┐
│            VAULT (Local Memory)          │
│  Needs_Action/  Pending_Approval/  Done/ │
│  Logs/  LinkedIn_Posts/  Approved/       │
└────────────────────┬─────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
   ┌─────────────┐    ┌──────────────────┐
   │  APPROVAL   │    │  AUTO-ACTIONS    │
   │  (Human)    │    │  Reply Email     │
   │  Dashboard  │    │  Post LinkedIn   │
   └─────────────┘    └──────────────────┘
```

---

## Key Features

### 1. Gmail Auto-Reply (IMAP UID Watermark)
- Connects via IMAP with App Password — no OAuth complexity
- **UID watermark system:** saves inbox snapshot on first connect; only emails arriving *after* connection get auto-replied (no old email spam)
- No-reply filter: ignores `noreply@`, `mailer-daemon@`, newsletters
- Reply tone configurable: Professional / Friendly / Concise

### 2. LinkedIn Auto-Posting
- **Scheduler** (`linkedin_scheduler.py`) runs 24/7, triggers at your set time (default 9:00 AM)
- Reads from your pre-scheduled posts queue — pick the exact date and content
- **Watcher** (`linkedin_watcher.py`) detects new post files and publishes via LinkedIn API
- One-click OAuth login — no LinkedIn Developer App setup needed for customers

### 3. Human-in-the-Loop Approval
- Keywords: `payment`, `password`, `bank`, `urgent`, `invoice` → auto-flagged
- Flagged tasks move to `vault/Pending_Approval/` instead of being acted on
- Review and approve/reject directly from the dashboard
- `approval_watcher.py` executes approved tasks automatically

### 4. Flask Dashboard
- Connect Gmail (email + App Password) and LinkedIn (one-click OAuth)
- Set auto-reply tone, check interval, sensitive keywords
- Schedule LinkedIn posts by date with custom content
- View full activity logs with timestamp breakdown
- Toggle agent on/off without restarting

### 5. Windows .exe Installer
- Built with PyInstaller + Inno Setup
- Customer installs → opens dashboard → enters their Gmail + LinkedIn → agent starts
- All user data stored in `%APPDATA%\AI Employee` — not in the install folder
- No Python, no terminal, no technical knowledge required

---

## Project Structure

```
AI_Employee_Project/
│
├── dashboard/
│   ├── app.py                        # Flask web dashboard
│   └── templates/
│       ├── base.html                 # Shared layout + navigation
│       ├── index.html                # Home — stats + recent activity
│       ├── accounts.html             # Connect Gmail & LinkedIn
│       ├── emails.html               # Email settings + keywords
│       ├── linkedin.html             # LinkedIn schedule + topics
│       ├── approvals.html            # Review flagged emails
│       ├── logs.html                 # Full activity log viewer
│       └── settings.html             # Business name + general settings
│
├── watchers/
│   ├── gmail_watcher.py              # IMAP email monitor + auto-reply
│   ├── linkedin_watcher.py           # Publishes .md files to LinkedIn
│   ├── linkedin_scheduler.py         # Time-based scheduler (runs 24/7)
│   ├── linkedin_content_generator.py # Fallback post generator (Claude AI)
│   ├── approval_watcher.py           # Executes human-approved tasks
│   └── watchdog.py                   # Process monitor + auto-restart
│
├── skills/
│   ├── gmail_mcp_server.py           # Gmail MCP server (send/read)
│   ├── monitor_gmail.md              # Gmail monitoring skill
│   ├── human_approval.md             # Approval workflow skill
│   ├── send_email.md                 # Email sending skill
│   ├── post_to_linkedin.md           # LinkedIn posting skill
│   ├── process_tasks.md              # Task processing skill
│   └── schedule_tasks.md             # Scheduling skill
│
├── scripts/
│   ├── task_processor.py             # Core task execution logic
│   ├── logging_utils.py              # Shared logging utilities
│   ├── setup_scheduler.py            # Windows Task Scheduler setup
│   ├── setup_scheduler.bat           # One-click scheduler setup
│   └── setup_tasks_admin.ps1         # PowerShell admin scheduler setup
│
├── vault/
│   ├── Company_Handbook.md           # AI rules — edit to customize behaviour
│   ├── Business_Goals.md             # Context for AI-generated content
│   ├── Needs_Action/                 # Incoming tasks (auto-managed)
│   ├── Pending_Approval/             # Flagged tasks awaiting review
│   ├── Approved/                     # Human-approved (auto-executed)
│   ├── Rejected/                     # Rejected tasks
│   ├── Plans/                        # AI-generated task plans
│   ├── Done/                         # Completed tasks + posted content
│   │   └── linkedin_posted/          # Published LinkedIn posts archive
│   ├── Logs/                         # Daily activity logs (YYYY-MM-DD.md)
│   └── LinkedIn_Posts/               # Queue for pending LinkedIn posts
│
├── Start_Dashboard.bat               # Start dashboard + all agents
├── Start_Agents_Only.bat             # Start agents without dashboard
├── build_exe.spec                    # PyInstaller build config
├── installer.iss                     # Inno Setup installer config
├── settings.json                     # App configuration
├── CLAUDE.md                         # Claude Code agent instructions
├── LINKEDIN_SETUP.md                 # LinkedIn OAuth setup guide
└── .env                              # Credentials (gitignored)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Brain | Claude API (`claude-sonnet-4-6`) |
| Web Dashboard | Python · Flask · Jinja2 |
| Email | IMAP (Gmail App Password) · SMTP |
| LinkedIn | LinkedIn UGC API · OAuth 2.0 |
| MCP Server | Gmail MCP (`skills/gmail_mcp_server.py`) |
| Scheduling | Windows Task Scheduler · Python threading |
| Packaging | PyInstaller · Inno Setup |
| Storage | Local file system (Vault pattern) |

---

## Quick Start (Development)

### Prerequisites
- Python 3.10+
- Gmail account with **App Password** enabled (2FA required)
- LinkedIn account (OAuth handled by the app)

### Install
```bash
git clone https://github.com/Hafiz54Kashif/AI-Employee-Silver-Tier.git
cd AI-Employee-Silver-Tier
pip install flask requests anthropic
```

### Configure
Create a `.env` file in the project root:
```
GMAIL_ADDRESS=your@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
ANTHROPIC_API_KEY=sk-ant-...
```

### Run
```bash
python dashboard/app.py
```
Open `http://localhost:5000` — connect your LinkedIn account from the Accounts page.

---

## How It Works — Core Flows

### Flow 1: New Email → Auto-Reply
```
Email arrives in Gmail
  → gmail_watcher.py detects it (every 2 mins via IMAP)
  → Saved as vault/Needs_Action/email_XXXX.md
  → Sensitive keyword? → vault/Pending_Approval/ (wait for human)
  → Safe? → Reply drafted and sent via SMTP
  → Moved to vault/Done/
  → Logged in vault/Logs/YYYY-MM-DD.md
```

### Flow 2: LinkedIn Post at Scheduled Time
```
9:00 AM (configurable)
  → linkedin_scheduler.py fires
  → Reads from scheduled posts queue
  → Saves post to vault/LinkedIn_Posts/daily_post_YYYY-MM-DD.md
  → linkedin_watcher.py detects file (polls every 30s)
  → Published to LinkedIn via UGC API
  → Moved to vault/Done/linkedin_posted/
```

### Flow 3: Sensitive Email → Human Approval
```
Email with "payment" keyword
  → Moved to vault/Pending_Approval/
  → Appears in Dashboard → Approvals tab
  → Human clicks Approve or Reject
  → approval_watcher.py picks up approved file
  → Task executed → vault/Done/
```

---

## Security

| Concern | How Handled |
|---------|-------------|
| API keys & passwords | Stored in `.env` only — gitignored, never committed |
| LinkedIn credentials | OAuth token in `.env` — customer's own account |
| Sensitive actions | 5+ keywords auto-flag for human review before any action |
| Payments / legal | Never auto-executed — require explicit human approval |
| Audit trail | Every action logged with timestamp in `vault/Logs/` |
| Path traversal | All file operations use `Path(filename).name` safe sanitization |

---

## Agent Skills

| Skill | Purpose |
|-------|---------|
| `monitor_gmail.md` | Gmail monitoring workflow |
| `human_approval.md` | Sensitivity check + approval routing |
| `send_email.md` | Email sending via SMTP |
| `post_to_linkedin.md` | LinkedIn UGC API posting |
| `process_tasks.md` | Task processing loop |
| `schedule_tasks.md` | Scheduling and time-based triggers |
| `gmail_mcp_server.py` | Gmail MCP server for Claude Code integration |

---

## Silver Tier Requirements ✅

| Requirement | Implementation |
|-------------|---------------|
| 2+ watcher scripts | `gmail_watcher.py` + `linkedin_watcher.py` + `linkedin_scheduler.py` |
| LinkedIn auto-post | Scheduled daily via `linkedin_scheduler.py` + `linkedin_watcher.py` |
| Plan.md generation | Every email task generates a plan before execution |
| One working MCP server | `skills/gmail_mcp_server.py` |
| Human-in-the-loop | `Pending_Approval/` → Dashboard review → `approval_watcher.py` |
| Basic scheduling | Daily 9 AM trigger · `scripts/setup_scheduler.bat` for Windows Task Scheduler |

---

## Author

Built for **Hackathon 0 — PIAIC Agentic AI Batch**
Stack: Python · Flask · Claude API · IMAP · LinkedIn OAuth · PyInstaller
