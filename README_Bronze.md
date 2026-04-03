# Personal AI Employee — Bronze Tier
### Hackathon 0: Building Autonomous FTEs in 2026
> *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

---

## Tier Declaration
**Bronze Tier — Foundation (Minimum Viable Deliverable)** ✅
Estimated time: 8-12 hours

---

## Submission Info

| Item | Detail |
|------|--------|
| Tier | **Bronze — Foundation** |
| Demo Video | 5-10 minute walkthrough |
| Security | Credentials in `.env` — never committed |
| Submit Form | https://forms.gle/JR9T1SJq5rmQyGkGA |

---

## Bronze Tier Checklist

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Obsidian vault with `Dashboard.md` | ✅ Done | `vault/Dashboard.md` |
| `Company_Handbook.md` | ✅ Done | `vault/Company_Handbook.md` |
| One working Watcher script (Gmail) | ✅ Done | `watchers/gmail_watcher.py` |
| Claude reads/writes vault | ✅ Done | Vault files updated after every task |
| Basic folder structure | ✅ Done | `/Needs_Action`, `/Done`, `/Plans`, `/Logs` |
| All AI functionality as Agent Skills | ✅ Done | `skills/` folder |

---

## Overview

**Personal AI Employee (Bronze)** is the foundation layer of the autonomous digital worker.
It sets up the Obsidian vault as the brain's memory, a Gmail watcher as the eyes,
and Claude Code as the reasoning engine. Tasks flow from Needs_Action → Plans → Done automatically.

---

## Architecture

```
Gmail
  ↓
gmail_watcher.py (Python)
  ↓
vault/Needs_Action/email_XXXX.md
  ↓
Claude Code (reads vault → plans → executes)
  ↓
vault/Plans/task_plan.md
  ↓
vault/Done/
  ↓
vault/Dashboard.md updated
```

---

## Folder Structure

```
AI_Employee_Project/
├── vault/
│   ├── Needs_Action/        ← Claude picks tasks from here
│   ├── Plans/               ← Claude writes plans here
│   ├── Done/                ← Completed tasks go here
│   ├── Logs/                ← All activity logged here
│   ├── Dashboard.md         ← Live status board
│   └── Company_Handbook.md  ← AI rules of engagement
├── watchers/
│   └── gmail_watcher.py     ← Monitors Gmail every 2 mins
├── skills/
│   ├── process_tasks.md     ← How to process tasks
│   └── monitor_gmail.md     ← How to monitor Gmail
└── .env                     ← API credentials (never commit)
```

---

## Key Features

### 1. Obsidian Vault (Memory + GUI)
- `Dashboard.md` — live status of all tasks
- `Company_Handbook.md` — rules Claude follows before every action
- Local markdown files = no database needed

### 2. Gmail Watcher
- Checks Gmail every 2 minutes for new emails
- Saves emails as `.md` files in `vault/Needs_Action/`
- Claude picks them up and processes them

### 3. Claude Code (Reasoning Engine)
- Reads `vault/Needs_Action/` for pending tasks
- Generates `vault/Plans/task_plan.md` before acting
- Moves completed tasks to `vault/Done/`
- Updates `vault/Dashboard.md`

### 4. Agent Skills
| Skill | Purpose |
|-------|---------|
| `process_tasks.md` | How to process tasks from Needs_Action |
| `monitor_gmail.md` | How to monitor Gmail for new emails |

---

## Setup

### 1. Install Dependencies
```bash
pip install google-auth google-auth-oauthlib google-api-python-client watchdog
```

### 2. Configure Gmail API
- Create Gmail OAuth credentials at Google Cloud Console
- Save as `credentials/gmail_credentials.json`

### 3. Start Gmail Watcher
```bash
python watchers/gmail_watcher.py
```

### 4. Run Claude
```bash
claude "Check vault/Needs_Action/ and process any pending tasks"
```

---

## Security

| Concern | How We Handle It |
|---------|-----------------|
| Gmail credentials | Stored in `credentials/` folder — never in vault |
| API keys | In `.env` file only — never hardcoded |
| `.gitignore` | `.env` excluded from version control |
| Audit trail | Every action logged in `vault/Logs/` |

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Claude Code | AI reasoning engine |
| Obsidian Vault | Local memory + dashboard |
| Python 3.13+ | Gmail watcher script |
| Gmail API (OAuth2) | Email monitoring |

---

*Bronze Tier — Foundation complete. Built with Claude Code + Python + Obsidian.*
