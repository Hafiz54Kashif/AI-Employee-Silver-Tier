# ceo_briefing

## Purpose
Generate a "Monday Morning CEO Briefing" every Sunday night by auditing the week's completed tasks, business goals progress, and providing proactive suggestions. Transforms the AI Employee from reactive to proactive.

## Input
- `vault/Business_Goals.md` — current goals and targets
- `vault/Done/` — all tasks completed this week
- `vault/Logs/` — activity logs for the week

## Process
1. Read `vault/Business_Goals.md` for current targets
2. Scan `vault/Done/` for files created this week
3. Read `vault/Logs/` for activity summary
4. Analyze:
   - Tasks completed vs pending
   - Email response rate
   - LinkedIn posts published
   - Any bottlenecks or errors
5. Generate CEO Briefing markdown file
6. Save to `vault/Briefings/YYYY-MM-DD_Monday_Briefing.md`
7. Update `vault/Dashboard.md`
8. Log action in `vault/Logs/`

## Output
- `vault/Briefings/YYYY-MM-DD_Monday_Briefing.md`
- Dashboard updated
- Log entry written

## Briefing Structure
- Executive Summary
- Tasks Completed This Week
- Email Activity
- LinkedIn Posts Published
- Bottlenecks Identified
- Proactive Suggestions
- Upcoming Week Preview
