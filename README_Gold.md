# Personal AI Employee — Gold Tier
### Hackathon 0: Building Autonomous FTEs in 2026
> *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

---

## Tier Declaration
**Gold Tier — Autonomous Employee** ✅
Estimated time: 40+ hours

---

## Submission Info

| Item | Detail |
|------|--------|
| Tier | **Gold — Autonomous Employee** |
| Demo Video | 5-10 minute walkthrough |
| Security | Credentials in `.env` — never committed |
| Submit Form | https://forms.gle/JR9T1SJq5rmQyGkGA |

---

## Gold Tier Checklist

### Bronze Requirements (All Complete)
| Requirement | Status | Evidence |
|-------------|--------|----------|
| Dashboard.md + Company_Handbook.md | ✅ Done | `vault/Dashboard.md`, `vault/Company_Handbook.md` |
| Basic folder structure | ✅ Done | All vault folders |
| One working Watcher (Gmail) | ✅ Done | `watchers/gmail_watcher.py` |
| Claude reads/writes vault | ✅ Done | 20+ plans in `vault/Plans/` |
| Agent Skills | ✅ Done | 12 skills in `skills/` |

### Silver Requirements (All Complete)
| Requirement | Status | Evidence |
|-------------|--------|----------|
| 2+ Watcher scripts | ✅ Done | Gmail + Filesystem + LinkedIn |
| LinkedIn Auto-Post | ✅ Done | `watchers/linkedin_watcher.py` |
| Plan.md generation | ✅ Done | `vault/Plans/` |
| Gmail MCP server | ✅ Done | `skills/gmail_mcp_server.py` |
| Human-in-the-loop approval | ✅ Done | Pending_Approval → Approved/Rejected |
| Basic scheduling | ✅ Done | `scripts/setup_scheduler.bat` |

### Gold Requirements
| Requirement | Status | Evidence |
|-------------|--------|----------|
| Full cross-domain integration | ✅ Done | Email + LinkedIn + Facebook + Instagram + Twitter + Odoo |
| Odoo Community accounting MCP | ✅ Done | `skills/odoo_mcp_server.py` |
| Facebook & Instagram integration | ✅ Done | `watchers/facebook_instagram_watcher.py` |
| Twitter (X) integration | ✅ Done | `watchers/twitter_watcher.py` |
| Multiple MCP servers | ✅ Done | Gmail MCP + Odoo MCP |
| Weekly Business + Accounting Audit | ✅ Done | `watchers/ceo_briefing_generator.py` |
| Error recovery + graceful degradation | ✅ Done | `watchers/watchdog.py` with auto-restart |
| Comprehensive audit logging | ✅ Done | `vault/Logs/` — every action logged |
| Ralph Wiggum Stop Hook | ✅ Done | `.claude/hooks/ralph_wiggum_stop_hook.py` |
| Architecture documentation | ✅ Done | This README |
| All AI functionality as Agent Skills | ✅ Done | 12 skills |

---

## Overview

**Personal AI Employee (Gold)** is a fully autonomous digital worker. It monitors Gmail,
processes tasks, posts to 4 social platforms (LinkedIn, Facebook, Instagram, Twitter),
manages Odoo accounting, generates weekly CEO briefings, and keeps itself running 24/7
via watchdog and Ralph Wiggum loop — all with human-in-the-loop safety for sensitive actions.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                  EXTERNAL SOURCES                            │
│  Gmail │ Files │ LinkedIn │ Facebook │ Instagram │ Twitter   │
└───┬────┴───┬───┴────┬─────┴────┬─────┴─────┬─────┴────┬──────┘
    ↓        ↓        ↓          ↓            ↓          ↓
┌──────────────────────────────────────────────────────────────┐
│               PERCEPTION LAYER (5 Watchers)                  │
│  gmail_watcher │ filesystem_watcher │ linkedin_watcher        │
│  facebook_instagram_watcher │ twitter_watcher                 │
│  approval_watcher │ ceo_briefing_generator                    │
└──────────────────────────┬───────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│              OBSIDIAN VAULT (Local Memory)                   │
│  /Needs_Action/ │ /Plans/ │ /Done/ │ /Logs/ │ /Briefings/    │
│  /Pending_Approval/ │ /Approved/ │ /Rejected/                │
│  /Social_Posts/Facebook/ │ /Instagram/ │ /Twitter/           │
│  Dashboard.md │ Company_Handbook.md │ Business_Goals.md      │
└──────────────────────────┬───────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│             REASONING LAYER (Claude Code)                    │
│   Read → Sensitivity Check → Plan → Execute → Update        │
└──────┬──────────────────────────────────────┬────────────────┘
       ↓                                      ↓
┌──────────────────┐              ┌───────────────────────────┐
│ RALPH WIGGUM     │              │     ACTION LAYER          │
│ STOP HOOK        │              │  Gmail MCP → Send Email   │
│ Tasks remain?    │              │  Odoo MCP → Accounting    │
│ → re-inject      │              │  Meta API → FB + Insta    │
│ All done?        │              │  Twitter API → Tweet      │
│ → allow exit     │              │  LinkedIn API → Post      │
└──────────────────┘              └───────────────────────────┘
       ↓
┌──────────────────┐
│ HUMAN-IN-THE-    │
│ LOOP APPROVAL    │
│ Move to /Approved│
└──────────────────┘
       ↓
┌──────────────────────────────────────────────────────────────┐
│                WATCHDOG (Resilience Layer)                   │
│  Monitors all watchers → auto-restarts on crash              │
│  Max 5 restarts → alert human                                │
└──────────────────────────────────────────────────────────────┘
```

---

## Gold Tier Features (New in Gold)

### 1. Ralph Wiggum Stop Hook
Keeps Claude working autonomously until ALL tasks are done.

**How it works:**
```
Claude finishes a task → tries to exit
  → Stop hook runs (.claude/hooks/ralph_wiggum_stop_hook.py)
  → Checks vault/Needs_Action/ for pending files
  → Tasks remain? → Block exit + re-inject prompt
  → All done?     → Allow clean exit
  → Max 20 iterations (safety limit)
```

**Files:**
- `.claude/hooks/ralph_wiggum_stop_hook.py` — hook script
- `skills/ralph_wiggum.md` — skill documentation
- Registered in `.claude/settings.local.json`

**Usage:**
```bash
claude "Process all tasks in vault/Needs_Action/"
# Claude will keep looping until Needs_Action is empty
```

---

### 2. Odoo Community Accounting MCP
Full accounting integration via Odoo JSON-RPC API.

**Setup:**
1. Install Odoo Community 19+: https://www.odoo.com/documentation
2. Add to `.env`:
   ```
   ODOO_URL=http://localhost:8069
   ODOO_DB=my_company
   ODOO_USERNAME=admin
   ODOO_PASSWORD=admin
   ```

**Available MCP Tools:**
| Tool | Description |
|------|-------------|
| `odoo_get_invoices` | Fetch customer invoices |
| `odoo_create_invoice_draft` | Create draft invoice (needs approval) |
| `odoo_get_expenses` | Fetch vendor bills |
| `odoo_revenue_summary` | Monthly revenue summary |
| `odoo_weekly_audit` | Full weekly financial audit |

**Safety:** All financial actions are DRAFT only — require human approval to post.

**Files:**
- `skills/odoo_mcp_server.py` — MCP server
- `skills/odoo_accounting.md` — skill documentation

---

### 3. Facebook & Instagram Auto-Posting
Post business content via Meta Graph API.

**Setup:**
1. Create Meta Developer App: https://developers.facebook.com/
2. Add to `.env`:
   ```
   FACEBOOK_PAGE_ID=your_page_id
   FACEBOOK_ACCESS_TOKEN=your_long_lived_token
   INSTAGRAM_ACCOUNT_ID=your_ig_business_account_id
   ```

**Usage:**
- **Facebook:** Drop `.md` file in `vault/Social_Posts/Facebook/`
- **Instagram:** Drop `.md` file with `image_url:` frontmatter in `vault/Social_Posts/Instagram/`

**Instagram Post Format:**
```markdown
---
image_url: https://your-image-host.com/image.jpg
---
Your caption here! #AI #Tech
```

**Files:**
- `watchers/facebook_instagram_watcher.py` — watcher
- `skills/post_to_facebook_instagram.md` — skill documentation

```bash
python watchers/facebook_instagram_watcher.py
```

---

### 4. Twitter (X) Auto-Posting
Post tweets via Twitter API v2 + Tweepy.

**Setup:**
1. Create Twitter Developer App: https://developer.twitter.com/
2. Install: `pip install tweepy`
3. Add to `.env`:
   ```
   TWITTER_BEARER_TOKEN=your_bearer_token
   TWITTER_API_KEY=your_key
   TWITTER_API_SECRET=your_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_SECRET=your_access_secret
   ```

**Usage:** Drop `.md` file in `vault/Social_Posts/Twitter/`
Auto-truncated to 280 characters if longer.

**Files:**
- `watchers/twitter_watcher.py` — watcher
- `skills/post_to_twitter.md` — skill documentation

```bash
python watchers/twitter_watcher.py
```

---

### 5. Watchdog + Error Recovery
Auto-restarts crashed watchers 24/7.

**Monitored Processes:**
- GmailWatcher
- ApprovalWatcher
- LinkedInWatcher

**Behavior:**
- Checks every 60 seconds
- Auto-restarts on crash
- Max 5 restarts per session
- Updates Dashboard health status
- Logs all events

```bash
python watchers/watchdog.py
# This starts AND monitors all other watchers
```

---

### 6. Weekly CEO Briefing (Monday Morning)
Every Monday at 8 AM, Claude generates a full briefing:
- Revenue vs targets (from Odoo audit)
- Tasks completed this week
- Social media posts summary
- Bottlenecks identified
- Proactive suggestions

Saved to: `vault/Briefings/YYYY-MM-DD_Monday_Briefing.md`

---

## Full Folder Structure

```
AI_Employee_Project/
├── vault/
│   ├── Needs_Action/
│   ├── Pending_Approval/
│   ├── Approved/
│   ├── Rejected/
│   ├── Plans/
│   ├── Done/
│   │   ├── linkedin_posted/
│   │   └── social_posted/         ← FB + Instagram + Twitter
│   ├── Logs/
│   │   ├── YYYY-MM-DD.md
│   │   ├── odoo_weekly_audit_*.md ← Gold
│   │   └── twitter_weekly_*.md    ← Gold
│   ├── Briefings/                 ← Gold
│   │   └── YYYY-MM-DD_Monday_Briefing.md
│   ├── Social_Posts/              ← Gold
│   │   ├── Facebook/
│   │   ├── Instagram/
│   │   └── Twitter/
│   ├── LinkedIn_Posts/
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   └── Business_Goals.md
├── watchers/
│   ├── gmail_watcher.py
│   ├── filesystem_watcher.py
│   ├── approval_watcher.py
│   ├── linkedin_watcher.py
│   ├── linkedin_content_generator.py
│   ├── facebook_instagram_watcher.py  ← Gold
│   ├── twitter_watcher.py             ← Gold
│   ├── ceo_briefing_generator.py
│   └── watchdog.py                    ← Gold
├── skills/
│   ├── process_tasks.md
│   ├── monitor_gmail.md
│   ├── human_approval.md
│   ├── send_email.md
│   ├── post_to_linkedin.md
│   ├── schedule_tasks.md
│   ├── ceo_briefing.md
│   ├── watchdog.md
│   ├── post_to_facebook_instagram.md  ← Gold
│   ├── post_to_twitter.md             ← Gold
│   ├── odoo_accounting.md             ← Gold
│   ├── ralph_wiggum.md                ← Gold
│   ├── gmail_mcp_server.py
│   └── odoo_mcp_server.py             ← Gold
├── scripts/
│   ├── setup_scheduler.py
│   ├── task_processor.py
│   └── logging_utils.py
├── .claude/
│   ├── settings.local.json
│   └── hooks/
│       └── ralph_wiggum_stop_hook.py  ← Gold
├── .env
├── README.md          ← Main (combined)
├── README_Bronze.md   ← Bronze only
├── README_Silver.md   ← Silver only
└── README_Gold.md     ← This file
```

---

## All Agent Skills

| Skill | Purpose | Tier |
|-------|---------|------|
| `process_tasks.md` | Process tasks from Needs_Action | Bronze |
| `monitor_gmail.md` | Monitor Gmail | Bronze |
| `human_approval.md` | HITL approval workflow | Silver |
| `send_email.md` | Send emails via Gmail MCP | Silver |
| `post_to_linkedin.md` | Post to LinkedIn | Silver |
| `schedule_tasks.md` | Task scheduling | Silver |
| `ceo_briefing.md` | Monday CEO Briefing | Silver+ |
| `watchdog.md` | Monitor + restart watchers | Gold |
| `post_to_facebook_instagram.md` | Post to FB + Instagram | Gold |
| `post_to_twitter.md` | Post to Twitter (X) | Gold |
| `odoo_accounting.md` | Odoo accounting MCP | Gold |
| `ralph_wiggum.md` | Autonomous loop Stop hook | Gold |

---

## Complete Setup Guide

### 1. Install All Dependencies
```bash
pip install watchdog google-auth google-auth-oauthlib google-api-python-client requests tweepy
```

### 2. Configure `.env`
```env
# Gmail
GMAIL_CREDENTIALS_PATH=credentials/gmail_credentials.json

# LinkedIn
LINKEDIN_ACCESS_TOKEN=your_token

# Facebook + Instagram
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_ACCESS_TOKEN=your_long_lived_token
INSTAGRAM_ACCOUNT_ID=your_ig_business_id

# Twitter (X)
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret

# Odoo
ODOO_URL=http://localhost:8069
ODOO_DB=my_company
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
```

### 3. Start Watchdog (starts everything automatically)
```bash
python watchers/watchdog.py
```

### 4. Run Claude with Ralph Wiggum Loop
```bash
claude "Process all tasks in vault/Needs_Action/ and update Dashboard"
# Will loop automatically until Needs_Action is empty
```

---

## Security

| Concern | How We Handle It |
|---------|-----------------|
| All credentials | `.env` only — never hardcoded or in vault |
| `.gitignore` | `.env` excluded from version control |
| Financial actions | DRAFT only in Odoo — require human approval to post |
| Sensitive tasks | 15+ keywords trigger HITL approval flow |
| Payments | Never auto-executed — always require `/Approved` file move |
| Audit trail | Every action logged in `vault/Logs/` — 90 day retention |
| Rate limiting | Max 10 emails/hour, max 3 financial actions/day |

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Claude Code (claude-sonnet-4-6) | AI reasoning engine |
| Obsidian Vault | Local memory + dashboard |
| Python 3.13+ | All watcher scripts |
| Gmail API (OAuth2) | Email monitoring + sending |
| LinkedIn API | Auto-posting |
| Meta Graph API | Facebook + Instagram posting |
| Twitter API v2 + Tweepy | Twitter (X) posting |
| Odoo Community 19+ | Accounting system |
| Odoo JSON-RPC API | Accounting MCP integration |
| Ralph Wiggum Stop Hook | Autonomous looping |
| Watchdog process | Auto-restart + resilience |
| Windows Task Scheduler | Permanent scheduling |

---

## Lessons Learned

1. **File-based state is powerful** — Obsidian vault as GUI + state machine = no database needed
2. **Stop hooks = true autonomy** — Without Ralph Wiggum, Claude exits after one task
3. **HITL is non-negotiable** — Never auto-approve payments or sensitive actions
4. **Watchdog saves hours** — Watchers crash on network blips; auto-restart is essential
5. **MCP servers are modular** — Gmail MCP and Odoo MCP are fully independent
6. **Test each watcher alone first** — Debug in isolation before running all together
7. **Log everything** — vault/Logs/ is the only audit trail when Claude makes wrong decisions

---

*Gold Tier — Autonomous Employee complete.*
*Built with Claude Code + Python + Obsidian + Odoo + Meta API + Twitter API*
*PIAIC — Agentic AI Hackathon 0*
