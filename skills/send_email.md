# send_email

## Purpose
Send emails via Gmail using the Gmail MCP Server. Allows Claude Code to compose and send emails as part of task execution.

## Input
- Recipient email address
- Email subject
- Email body text

## Process
1. Connect to Gmail MCP Server (gmail-server)
2. Compose email with provided details
3. Send via Gmail API using stored OAuth token
4. Log sent email details in `vault/Logs/`
5. **Move original task file from `vault/Needs_Action/` to `vault/Done/`**
6. Update dashboard with email sent status and task completion

## Output
- Email delivered to recipient
- Confirmation with Gmail Message ID
- Log entry: "[timestamp] Email sent to: recipient | Subject: subject"

## Example Usage
Claude Code can use this skill to:
- Reply to customer inquiries automatically
- Send task completion notifications
- Forward important information to team members
- Send scheduled reports

## MCP Tool
Uses: `send_email` tool from `gmail-server` MCP
```
to: recipient@example.com
subject: Re: Your inquiry
body: Thank you for reaching out...
```
