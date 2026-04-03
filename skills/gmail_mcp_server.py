"""
Gmail MCP Server for AI Employee
Provides tools to Claude Code for sending, reading, and replying to emails.

Tools available:
- send_email: Send a new email
- read_emails: Read unread emails
- reply_to_email: Reply to an existing email
- list_emails: List recent emails
"""

import base64
import sys
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Paths
BASE_DIR = Path(__file__).parent.parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
]

# Initialize MCP server
app = Server("gmail-mcp-server")


def get_gmail_service():
    """Authenticate and return Gmail service."""
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, 'w') as f:
                f.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def get_email_body(payload):
    """Extract plain text from email payload."""
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    break
    else:
        data = payload['body'].get('data', '')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    return body[:2000]


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="send_email",
            description="Send a new email via Gmail",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body text"},
                },
                "required": ["to", "subject", "body"]
            }
        ),
        types.Tool(
            name="read_emails",
            description="Read unread emails from Gmail inbox",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of emails to fetch (default: 5)",
                        "default": 5
                    },
                    "query": {
                        "type": "string",
                        "description": "Gmail search query (default: is:unread)",
                        "default": "is:unread"
                    }
                }
            }
        ),
        types.Tool(
            name="reply_to_email",
            description="Reply to an existing email",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "Gmail message ID to reply to"},
                    "body": {"type": "string", "description": "Reply text"},
                },
                "required": ["message_id", "body"]
            }
        ),
        types.Tool(
            name="list_emails",
            description="List recent emails with subject and sender",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "integer",
                        "description": "Number of emails to list (default: 10)",
                        "default": 10
                    }
                }
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

    service = get_gmail_service()

    # --- SEND EMAIL ---
    if name == "send_email":
        to = arguments["to"]
        subject = arguments["subject"]
        body = arguments["body"]

        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        result = service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()

        return [types.TextContent(
            type="text",
            text=f"Email sent successfully!\nTo: {to}\nSubject: {subject}\nMessage ID: {result['id']}"
        )]

    # --- READ EMAILS ---
    elif name == "read_emails":
        max_results = arguments.get("max_results", 5)
        query = arguments.get("query", "is:unread")

        results = service.users().messages().list(
            userId='me', q=query, maxResults=max_results
        ).execute()

        messages = results.get('messages', [])
        if not messages:
            return [types.TextContent(type="text", text="No emails found.")]

        output = []
        for msg in messages:
            full = service.users().messages().get(
                userId='me', id=msg['id'], format='full'
            ).execute()
            headers = {h['name']: h['value'] for h in full['payload']['headers']}
            body = get_email_body(full['payload'])
            output.append(
                f"ID: {msg['id']}\n"
                f"From: {headers.get('From', 'Unknown')}\n"
                f"Subject: {headers.get('Subject', 'No Subject')}\n"
                f"Body: {body[:300]}...\n"
                f"{'-'*40}"
            )

        return [types.TextContent(type="text", text="\n".join(output))]

    # --- REPLY TO EMAIL ---
    elif name == "reply_to_email":
        message_id = arguments["message_id"]
        body = arguments["body"]

        original = service.users().messages().get(
            userId='me', id=message_id, format='full'
        ).execute()
        headers = {h['name']: h['value'] for h in original['payload']['headers']}

        reply = MIMEMultipart()
        reply['to'] = headers.get('From', '')
        reply['subject'] = "Re: " + headers.get('Subject', '')
        reply['In-Reply-To'] = headers.get('Message-ID', '')
        reply['References'] = headers.get('Message-ID', '')
        reply.attach(MIMEText(body, 'plain'))

        thread_id = original.get('threadId')
        raw = base64.urlsafe_b64encode(reply.as_bytes()).decode()
        result = service.users().messages().send(
            userId='me',
            body={'raw': raw, 'threadId': thread_id}
        ).execute()

        return [types.TextContent(
            type="text",
            text=f"Reply sent!\nTo: {reply['to']}\nSubject: {reply['subject']}\nMessage ID: {result['id']}"
        )]

    # --- LIST EMAILS ---
    elif name == "list_emails":
        max_results = arguments.get("max_results", 10)

        results = service.users().messages().list(
            userId='me', maxResults=max_results
        ).execute()

        messages = results.get('messages', [])
        if not messages:
            return [types.TextContent(type="text", text="No emails found.")]

        output = []
        for msg in messages:
            full = service.users().messages().get(
                userId='me', id=msg['id'], format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()
            headers = {h['name']: h['value'] for h in full['payload']['headers']}
            output.append(
                f"[{msg['id']}] {headers.get('Subject', 'No Subject')} "
                f"| From: {headers.get('From', 'Unknown')}"
            )

        return [types.TextContent(type="text", text="\n".join(output))]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
