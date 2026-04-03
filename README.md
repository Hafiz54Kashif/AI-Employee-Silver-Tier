# Personal AI Employee — Gold Tier
### Hackathon 0: Building Autonomous FTEs in 2026
> *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

---

## Tier Declaration
**Gold Tier — Autonomous Employee** ✅

| Tier | Status |
|------|--------|
| Bronze | ✅ Complete |
| Silver | ✅ Complete |
| Gold   | ✅ Complete |

---

## Submission Info

| Item | Detail |
|------|--------|
| Tier | **Gold — Autonomous Employee** |
| Demo Video | 5-10 minute walkthrough of all features |
| Security | Credentials in `.env` — never committed (see Security section) |
| Submit Form | https://forms.gle/JR9T1SJq5rmQyGkGA |

---

## Overview

**Personal AI Employee** is a fully autonomous digital worker that monitors your Gmail, processes tasks intelligently, posts on LinkedIn daily, and handles sensitive actions with human approval — all powered by **Claude Code** as the AI brain and **Obsidian Vault** as the persistent memory/dashboard.

Built for **Hackathon 0 by PIAIC**, this system demonstrates a real Digital FTE (Full-Time Equivalent) that works 24/7 without manual intervention.

---

## Gold Tier Checklist

### Bronze Requirements
| Requirement | Status | Evidence |
|-------------|--------|----------|
| Dashboard.md + Company_Handbook.md | ✅ Done | `vault/Dashboard.md`, `vault/Company_Handbook.md` |
| Folder structure (Needs_Action, Done, Plans, Logs) | ✅ Done | Full vault structure |
| Claude reads/writes vault + Plan.md generation | ✅ Done | `vault/Plans/` — 20+ plans generated |
| 1+ Watcher script | ✅ Done | Gmail + Filesystem + LinkedIn |
| Agent Skills | ✅ Done | 11 skills in `skills/` folder |

### Silver Requirements
| Requirement | Status | Evidence |
|-------------|--------|----------|
| 2+ Watcher scripts | ✅ Done | Gmail + Filesystem + LinkedIn = 3 watchers |
| LinkedIn Auto-Post for business | ✅ Done | `watchers/linkedin_watcher.py` |
| Plan.md generation loop | ✅ Done | `vault/Plans/` — 20+ plans |
| One working MCP server | ✅ Done | `skills/gmail_mcp_server.py` |
| Human-in-the-loop approval | ✅ Done | Pending_Approval → Approved/Rejected |
| Basic Scheduling | ✅ Done | Daily 9 AM cron + `scripts/setup_scheduler.bat` |

### Gold Requirements
| Requirement | Status | Evidence |
|-------------|--------|----------|
| Full cross-domain integration | ✅ Done | Email + LinkedIn + Facebook + Instagram + Twitter + Odoo |
| Odoo Community MCP (JSON-RPC) | ✅ Done | `skills/odoo_mcp_server.py` + `skills/odoo_accounting.md` |
| Facebook & Instagram integration | ✅ Done | `watchers/facebook_instagram_watcher.py` |
| Twitter (X) integration | ✅ Done | `watchers/twitter_watcher.py` |
| Multiple MCP servers | ✅ Done | Gmail MCP + Odoo MCP |
| Weekly Business + Accounting Audit | ✅ Done | `watchers/ceo_briefing_generator.py` + Odoo audit |
| Error recovery + graceful degradation | ✅ Done | `watchers/watchdog.py` with auto-restart |
| Comprehensive audit logging | ✅ Done | `vault/Logs/` — every action logged |
| Ralph Wiggum Stop Hook | ✅ Done | `.claude/hooks/ralph_wiggum_stop_hook.py` |
| Architecture documentation | ✅ Done | This README |
| All AI functionality as Agent Skills | ✅ Done | 11 skills in `skills/` folder |

---

## Gold Tier Features

### 1. Ralph Wiggum Stop Hook (Autonomous Loop)
Keeps Claude working until ALL tasks in `vault/Needs_Action/` are complete.
- **File:** `.claude/hooks/ralph_wiggum_stop_hook.py`
- **How:** Registered as Claude Code Stop hook — intercepts every exit attempt
- **Loop:** Checks Needs_Action → tasks remain? re-inject prompt → tasks done? allow exit
- **Safety:** Max 20 iterations (configurable via `RALPH_MAX_ITERATIONS` env var)

### 2. Odoo Community Accounting MCP
Full accounting integration via Odoo JSON-RPC API.
- **File:** `skills/odoo_mcp_server.py`
- **Tools:** Get invoices, create draft invoices, get expenses, revenue summary, weekly audit
- **Safety:** ALL financial actions create draft only — require human approval to post
- **Audit:** Weekly financial reports saved to `vault/Logs/odoo_weekly_audit_*.md`

### 3. Facebook & Instagram Auto-Posting
Post business content via Meta Graph API.
- **File:** `watchers/facebook_instagram_watcher.py`
- **Facebook:** Drop `.md` file in `vault/Social_Posts/Facebook/`
- **Instagram:** Drop `.md` file with `image_url:` frontmatter in `vault/Social_Posts/Instagram/`
- **Summary:** Page insights + engagement stats fetched weekly

### 4. Twitter (X) Auto-Posting
Post tweets via Twitter API v2 + Tweepy.
- **File:** `watchers/twitter_watcher.py`
- **Usage:** Drop `.md` file in `vault/Social_Posts/Twitter/`
- **Auto-truncation:** Text truncated to 280 chars automatically
- **Summary:** Weekly engagement report every Sunday → `vault/Logs/twitter_weekly_summary_*.md`

### 5. Watchdog + Error Recovery
- Auto-restarts any crashed watcher process
- Max 5 restarts per session before alerting human
- Logs all restart events with timestamps
- Updates Dashboard health status every 60 seconds

### 6. Weekly CEO Briefing (Monday Morning)
Every Monday at 8 AM, Claude generates a briefing:
- Revenue vs targets (from Odoo)
- Tasks completed this week
- Social media post summary (LinkedIn + Facebook + Twitter)
- Bottlenecks and proactive suggestions
- Saved to `vault/Briefings/YYYY-MM-DD_Monday_Briefing.md`

---

## Innovation Highlights

This project goes beyond basic automation — here's what makes it stand out:

| Innovation | Description |
|------------|-------------|
| **5-Watcher Perception Layer** | Gmail + Filesystem + LinkedIn + Facebook/Instagram + Twitter — AI has eyes on all inputs |
| **File-Based HITL Approval** | No UI needed — drag file to `/Approved` folder = approval. Simple, reliable, auditable |
| **AI Content Generation** | Claude reads Business Goals and generates unique LinkedIn posts daily — not templates |
| **Rotating Topic Schedule** | 7 different daily topics auto-rotate — AI Employee builds your brand automatically |
| **Sensitivity Auto-Detection** | 15+ keywords trigger human approval — AI knows its own limits |
| **Zero-Config Memory** | Obsidian vault = persistent memory — no database, no backend, fully local |
| **Plan-Before-Act Pattern** | Every task gets a Plan.md before execution — full audit trail of AI reasoning |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  PERSONAL AI EMPLOYEE                   │
│                   (Silver Tier)                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  EXTERNAL SOURCES                       │
│       Gmail          │      Files       │   LinkedIn    │
└────────┬─────────────┴────────┬─────────┴──────┬────────┘
         │                      │                │
         ▼                      ▼                ▼
┌─────────────────────────────────────────────────────────┐
│                  PERCEPTION LAYER (Watchers)            │
│  gmail_watcher.py │ filesystem_watcher.py │ linkedin_   │
│                   │                       │ watcher.py  │
└─────────┬─────────┴───────────┬───────────┴──────┬──────┘
          │                     │                  │
          ▼                     ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│               OBSIDIAN VAULT (Local Memory)             │
│  /Needs_Action/  │  /Plans/  │  /Done/  │  /Logs/       │
│  /Pending_Approval/  │  /Approved/  │  /Rejected/       │
│  Dashboard.md  │  Company_Handbook.md  │  Business_     │
│                                         Goals.md        │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│               REASONING LAYER (Claude Code)             │
│      Read → Sensitivity Check → Plan → Execute          │
│           → Request Approval (if sensitive)             │
└──────────────────────────┬──────────────────────────────┘
                           │
          ┌────────────────┴─────────────────┐
          ▼                                  ▼
┌──────────────────┐              ┌──────────────────────┐
│ HUMAN-IN-THE-    │              │    ACTION LAYER       │
│ LOOP APPROVAL    │──────────▶   │    Gmail MCP Server   │
│ Move to          │              │    Send Email         │
│ /Approved        │              │    Post to LinkedIn   │
└──────────────────┘              └──────────────────────┘
```

---

## Key Features

### 1. Gmail Monitoring & Auto-Reply
- `watchers/gmail_watcher.py` checks Gmail every 2 minutes
- New emails saved as `.md` files in `vault/Needs_Action/`
- Claude reads email, generates a plan, drafts reply
- Reply sent via Gmail MCP server

### 2. Human-in-the-Loop Approval
- Sensitive keywords detected: `payment`, `password`, `bank`, `invoice`, etc.
- Task moved to `vault/Pending_Approval/` automatically
- Human reviews in Obsidian and moves to `vault/Approved/` or `vault/Rejected/`
- `watchers/approval_watcher.py` monitors and executes approved tasks

### 3. LinkedIn Auto-Posting
- `watchers/linkedin_content_generator.py` runs daily at 9:00 AM
- Claude generates professional post based on `vault/Business_Goals.md`
- Post saved to `vault/LinkedIn_Posts/` as `.md` file
- `watchers/linkedin_watcher.py` detects and publishes to LinkedIn automatically
- Topics rotate daily: AI, product launch, customer success, agentic AI, etc.

### 4. Autonomous Task Processing
- Drop any `.md` file in `drop_folder/`
- Filesystem watcher detects it → moves to `vault/Needs_Action/`
- Claude generates `vault/Plans/task_plan.md`
- Task executed → moved to `vault/Done/`
- `vault/Dashboard.md` updated in real-time

### 5. Basic Scheduling
- Session cron: daily 9 AM LinkedIn post generation
- `scripts/setup_scheduler.bat`: Windows Task Scheduler setup for permanent scheduling
- Watchers auto-start on Windows login

---

## Project Structure

```
AI_Employee_Project/
│
├── watchers/
│   ├── gmail_watcher.py              # Monitors Gmail every 2 mins
│   ├── filesystem_watcher.py         # Monitors drop_folder
│   ├── approval_watcher.py           # Monitors Pending_Approval folder
│   ├── linkedin_watcher.py           # Posts .md files to LinkedIn
│   └── linkedin_content_generator.py # Generates daily LinkedIn content
│
├── skills/
│   ├── process_tasks.md              # Task processing skill
│   ├── monitor_gmail.md              # Gmail monitoring skill
│   ├── human_approval.md             # Approval workflow skill
│   ├── send_email.md                 # Email sending skill
│   ├── post_to_linkedin.md           # LinkedIn posting skill
│   └── schedule_tasks.md             # Scheduling skill
│
├── scripts/
│   ├── task_processor.py             # Core task processor
│   ├── logging_utils.py              # Logging utilities
│   ├── setup_scheduler.bat           # Windows Task Scheduler setup
│   ├── setup_scheduler.py            # Python scheduler setup
│   ├── run_linkedin_generator.bat    # Launcher for LinkedIn generator
│   └── run_linkedin_watcher.bat      # Launcher for LinkedIn watcher
│
├── vault/                            # Obsidian Vault
│   ├── Needs_Action/                 # Tasks ready for AI processing
│   ├── Pending_Approval/             # Sensitive tasks awaiting review
│   ├── Approved/                     # Human-approved tasks
│   ├── Rejected/                     # Rejected tasks
│   ├── Plans/                        # AI-generated plans (20+ plans)
│   ├── Done/                         # Completed tasks
│   │   └── linkedin_posted/          # Published LinkedIn posts
│   ├── Logs/                         # Activity logs
│   ├── LinkedIn_Posts/               # Pending LinkedIn posts
│   ├── Dashboard.md                  # Live status board
│   ├── Company_Handbook.md           # AI rules and guidelines
│   └── Business_Goals.md             # Business goals reference
│
├── drop_folder/                      # Drop task files here
├── CLAUDE.md                         # Claude Code instructions
├── LINKEDIN_SETUP.md                 # LinkedIn API setup guide
├── .env                              # API credentials (never commit)
└── README.md                         # This file
```

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Claude Code (claude-sonnet-4-6) | AI reasoning engine — plans and executes tasks |
| Obsidian Vault | Local file-based memory and dashboard |
| Python 3.14 | Watcher scripts and automation |
| Gmail API (OAuth2) | Email monitoring and sending |
| LinkedIn API (UGC Posts) | Automated LinkedIn posting |
| MCP Gmail Server | Model Context Protocol for email actions |
| Watchdog (Python) | Filesystem event monitoring |
| Windows Task Scheduler | Permanent scheduling |

---

## Installation & Setup

### Hardware Requirements
- **Minimum:** 8GB RAM, 4-core CPU, 20GB free disk space
- **Recommended:** 16GB RAM, 8-core CPU, SSD storage
- Stable internet connection (10+ Mbps)

### Prerequisites
- Python 3.10+
- Claude Code CLI installed and authenticated
- Gmail API credentials (OAuth2)
- LinkedIn Developer App + Access Token
- Obsidian (optional, for visual vault browsing)

### 1. Install Dependencies
```bash
pip install watchdog google-auth google-auth-oauthlib google-api-python-client requests anthropic
```

### 2. Configure Credentials
Create `.env` file in project root:
```
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 3. Start Watchers
```bash
# Gmail Watcher
python watchers/gmail_watcher.py

# Approval Watcher
python watchers/approval_watcher.py

# LinkedIn Watcher
python watchers/linkedin_watcher.py
```

### 4. Setup Permanent Scheduling (Run as Administrator)
```bash
scripts/setup_scheduler.bat
```

---

## How It Works — Demo Flows

### Flow 1: Email Processing
```
Email arrives in Gmail
    → gmail_watcher.py detects it (every 2 mins)
    → Saved as vault/Needs_Action/email_XXXX.md
    → Claude reads + generates vault/Plans/email_plan.md
    → Reply drafted and sent via Gmail MCP
    → Moved to vault/Done/
    → Dashboard.md updated
```

### Flow 2: Sensitive Task (Human Approval)
```
Email with "payment" keyword arrives
    → Sensitivity check triggers
    → Moved to vault/Pending_Approval/
    → Human reviews in Obsidian
    → Moves file to vault/Approved/
    → approval_watcher.py detects approval
    → Claude executes the task
    → Moved to vault/Done/
```

### Flow 3: Daily LinkedIn Post (9 AM)
```
9:00 AM — Scheduler fires
    → linkedin_content_generator.py runs
    → Reads vault/Business_Goals.md
    → Claude generates professional post
    → Saved to vault/LinkedIn_Posts/daily_post_YYYY-MM-DD.md
    → linkedin_watcher.py detects file (30 sec)
    → Published to LinkedIn automatically
    → Moved to vault/Done/linkedin_posted/
    → Dashboard.md updated
```

---

## Live Activity Log (Sample)

From `vault/Dashboard.md`:
- 6 test emails processed and replied ✅
- LinkedIn post published successfully ✅
- Payment task flagged → human approved → executed ✅
- 5 task files processed via drop_folder ✅
- 20+ Plan.md files auto-generated ✅

---

## Security Disclosure

| Concern | How We Handle It |
|---------|-----------------|
| API Keys | Stored in `.env` file only — never hardcoded |
| .gitignore | `.env` is in `.gitignore` — never committed to GitHub |
| Sensitive Actions | 15+ keywords trigger HITL approval before any action |
| Payments | Never auto-executed — always require human move to `/Approved` |
| Audit Trail | Every action logged in `vault/Logs/YYYY-MM-DD.md` |
| LinkedIn Token | Stored in `.env` only — not in vault or any tracked file |
| Gmail OAuth | Credentials file excluded from version control |

**The Human Remains Accountable:** All actions run under your credentials, on your machine, in your name.

---

## Agent Skills

All AI functionality is implemented as Agent Skills in `skills/` folder:

| Skill | Purpose | Tier |
|-------|---------|------|
| `process_tasks.md` | Process tasks from Needs_Action | Bronze |
| `monitor_gmail.md` | Monitor Gmail for new emails | Bronze |
| `human_approval.md` | Route sensitive tasks for approval | Silver |
| `send_email.md` | Send emails via Gmail MCP | Silver |
| `post_to_linkedin.md` | Post content to LinkedIn | Silver |
| `schedule_tasks.md` | Manage scheduled tasks | Silver |
| `ceo_briefing.md` | Generate Monday CEO Briefing | Silver+ |
| `watchdog.md` | Monitor + restart watcher processes | Gold |
| `post_to_facebook_instagram.md` | Post to Facebook & Instagram | Gold |
| `post_to_twitter.md` | Post to Twitter (X) | Gold |
| `odoo_accounting.md` | Odoo accounting via JSON-RPC MCP | Gold |
| `ralph_wiggum.md` | Autonomous loop via Stop hook | Gold |

---

## Demo Video

The demo video (5-10 minutes) covers:
1. System overview and architecture walkthrough
2. Live Gmail monitoring — email arrives → AI processes → reply sent
3. Human-in-the-loop approval — sensitive task flagged → human approves → executed
4. LinkedIn auto-posting — content generated → published automatically
5. Dashboard.md and Logs live update demonstration
6. Scheduling setup via Windows Task Scheduler

---

## Judging Criteria Coverage

| Criterion | Weight | How We Address It |
|-----------|--------|-------------------|
| Functionality | 30% | All 9 Silver requirements complete with live evidence |
| Innovation | 25% | AI content generation, file-based HITL, 3-watcher perception layer |
| Practicality | 20% | Gmail auto-reply + LinkedIn posting = real daily business value |
| Security | 15% | .env credentials, .gitignore, HITL for all sensitive actions |
| Documentation | 10% | This README + Plan.md for every task + activity logs |

---

## Lessons Learned

1. **File-based state is powerful** — Obsidian vault as both GUI and state machine eliminates need for a database
2. **Stop hooks = true autonomy** — Without Ralph Wiggum, Claude stops after one task regardless of remaining work
3. **HITL is non-negotiable for payments** — Never auto-approve financial actions; always require human file-move
4. **Watchdog saves hours** — Watchers crash on network blips; process managers restart them silently
5. **MCP servers are modular** — Each integration (Gmail, Odoo, Social) is fully independent and swappable
6. **Test each watcher in isolation** — Complexity adds up fast; one broken watcher shouldn't kill the system
7. **Log everything** — When Claude makes a wrong decision, vault/Logs/ is the only audit trail

---

## Author

**Hackathon 0 — Personal AI Employee (Gold Tier)**
Built with Claude Code + Obsidian + Python + MCP
PIAIC — Agentic AI Batch

---

*This AI Employee never sleeps, never forgets, and always logs its work.*

---

*Gold Tier — 40+ hours | Claude Code + Python + Obsidian + Odoo + Meta API + Twitter API*
