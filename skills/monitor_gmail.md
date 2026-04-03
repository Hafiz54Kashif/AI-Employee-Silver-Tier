# monitor_gmail

## Purpose
Monitor Gmail inbox for new unread emails and create action files in the vault for processing.

## Input
- Gmail account credentials (token.json)
- Vault path for storing action files

## Process
1. Authenticate with Gmail API using stored token
2. Fetch unread emails from inbox
3. For each new email not previously processed:
   - Extract sender, subject, date, and body
   - Create a markdown file in `vault/Needs_Action/`
   - Mark email ID as processed in `processed_emails.json`
4. Log activity in `vault/Logs/`
5. Wait 120 seconds and repeat

## Output
- Markdown files in `vault/Needs_Action/` for each new email
- Updated `processed_emails.json` with processed IDs
- Log entries in `vault/Logs/`

## Example Workflow
1. Gmail has 3 new unread emails
2. Skill creates 3 files:
   - `vault/Needs_Action/email_20260322_security_alert.md`
   - `vault/Needs_Action/email_20260322_invoice_received.md`
   - `vault/Needs_Action/email_20260322_meeting_invite.md`
3. Each file contains sender, subject, body, and action required section
4. Task processor picks them up for AI processing
