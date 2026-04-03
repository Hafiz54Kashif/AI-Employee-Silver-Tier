"""
Odoo MCP Server - AI Employee Gold Tier
========================================
MCP server that connects to Odoo Community via JSON-RPC API.
Exposes accounting tools that Claude can call for:
- Creating/reading invoices
- Logging expenses
- Generating financial summaries
- Weekly accounting audit

SETUP:
1. Install Odoo Community 19+ locally: https://www.odoo.com/documentation
2. Copy .env.example → .env and fill in your Odoo credentials
3. Run this server: python skills/odoo_mcp_server.py

ENVIRONMENT VARIABLES (.env):
  ODOO_URL=http://localhost:8069
  ODOO_DB=my_company
  ODOO_USERNAME=admin
  ODOO_PASSWORD=admin

ODOO API REFERENCE:
  https://www.odoo.com/documentation/19.0/developer/reference/external_api.html
"""

import json
import os
import sys
import xmlrpc.client
from datetime import datetime, date
from pathlib import Path

# ── Load .env ─────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
env_file = BASE_DIR / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

ODOO_URL      = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB       = os.getenv("ODOO_DB", "odoo")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")

VAULT_DIR = BASE_DIR / "vault"
LOGS_DIR  = VAULT_DIR / "Logs"


# ── Odoo Connection ───────────────────────────────────────────────────────────

def get_odoo_uid():
    """Authenticate with Odoo and return user ID."""
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    if not uid:
        raise ConnectionError(f"Odoo authentication failed for user '{ODOO_USERNAME}'")
    return uid


def odoo_call(model, method, args=None, kwargs=None):
    """Make an authenticated Odoo JSON-RPC call."""
    uid = get_odoo_uid()
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    return models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        model, method,
        args or [],
        kwargs or {}
    )


# ── Tools ─────────────────────────────────────────────────────────────────────

def get_invoices(state="posted", limit=10):
    """Fetch recent invoices from Odoo."""
    domain = [["move_type", "=", "out_invoice"]]
    if state:
        domain.append(["state", "=", state])
    records = odoo_call(
        "account.move", "search_read",
        [domain],
        {
            "fields": ["name", "partner_id", "amount_total", "invoice_date", "state", "payment_state"],
            "limit": limit,
            "order": "invoice_date desc"
        }
    )
    return records


def create_invoice_draft(partner_name, amount, description, currency="USD"):
    """Create a draft invoice in Odoo (requires human approval to post)."""
    # Find or create partner
    partners = odoo_call("res.partner", "search_read",
                         [[["name", "ilike", partner_name]]],
                         {"fields": ["id", "name"], "limit": 1})

    if not partners:
        return {"error": f"Partner '{partner_name}' not found in Odoo. Please create them first."}

    partner_id = partners[0]["id"]

    # Find product/account
    accounts = odoo_call("account.account", "search_read",
                         [[["account_type", "=", "income"]]],
                         {"fields": ["id", "name"], "limit": 1})

    if not accounts:
        return {"error": "No income account found in Odoo chart of accounts."}

    invoice_vals = {
        "move_type": "out_invoice",
        "partner_id": partner_id,
        "invoice_date": date.today().isoformat(),
        "invoice_line_ids": [(0, 0, {
            "name": description,
            "quantity": 1,
            "price_unit": amount,
            "account_id": accounts[0]["id"],
        })],
    }

    invoice_id = odoo_call("account.move", "create", [[invoice_vals]])
    return {
        "status": "draft_created",
        "invoice_id": invoice_id,
        "partner": partner_name,
        "amount": amount,
        "note": "Invoice is in DRAFT state. Requires human approval to post/send."
    }


def get_expenses(limit=20):
    """Fetch recent expenses from Odoo."""
    records = odoo_call(
        "account.move", "search_read",
        [[["move_type", "=", "in_invoice"]]],
        {
            "fields": ["name", "partner_id", "amount_total", "invoice_date", "state"],
            "limit": limit,
            "order": "invoice_date desc"
        }
    )
    return records


def get_revenue_summary(month=None, year=None):
    """Get revenue summary for a given month/year."""
    today = date.today()
    month = month or today.month
    year  = year  or today.year

    domain = [
        ["move_type", "=", "out_invoice"],
        ["state", "=", "posted"],
        ["invoice_date", ">=", f"{year}-{month:02d}-01"],
        ["invoice_date", "<=", f"{year}-{month:02d}-28"],
    ]

    invoices = odoo_call(
        "account.move", "search_read",
        [domain],
        {"fields": ["amount_total", "payment_state", "partner_id"]}
    )

    total_invoiced = sum(i["amount_total"] for i in invoices)
    total_paid     = sum(i["amount_total"] for i in invoices if i["payment_state"] == "paid")
    total_pending  = total_invoiced - total_paid

    return {
        "period": f"{year}-{month:02d}",
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "total_pending": total_pending,
        "invoice_count": len(invoices),
        "invoices": invoices[:5]
    }


def get_weekly_audit():
    """Generate weekly financial audit data for CEO Briefing."""
    from datetime import timedelta
    today   = date.today()
    week_start = today - timedelta(days=today.weekday())

    # Revenue this week
    invoices = odoo_call(
        "account.move", "search_read",
        [[
            ["move_type", "=", "out_invoice"],
            ["state", "=", "posted"],
            ["invoice_date", ">=", week_start.isoformat()]
        ]],
        {"fields": ["name", "amount_total", "payment_state", "partner_id"]}
    )

    # Expenses this week
    expenses = odoo_call(
        "account.move", "search_read",
        [[
            ["move_type", "=", "in_invoice"],
            ["state", "=", "posted"],
            ["invoice_date", ">=", week_start.isoformat()]
        ]],
        {"fields": ["name", "amount_total", "partner_id"]}
    )

    revenue  = sum(i["amount_total"] for i in invoices)
    expenses_total = sum(e["amount_total"] for e in expenses)

    audit = {
        "week_start": week_start.isoformat(),
        "week_end": today.isoformat(),
        "revenue": revenue,
        "expenses": expenses_total,
        "net_profit": revenue - expenses_total,
        "invoices_issued": len(invoices),
        "unpaid_invoices": [i for i in invoices if i["payment_state"] != "paid"],
    }

    # Save audit to vault
    log_weekly_audit(audit)
    return audit


def log_weekly_audit(audit):
    """Save weekly audit to vault/Logs/."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    audit_file = LOGS_DIR / f"odoo_weekly_audit_{date.today().isoformat()}.md"
    content = f"""# Odoo Weekly Audit — {audit['week_start']} to {audit['week_end']}

## Financial Summary
- **Revenue:** ${audit['revenue']:,.2f}
- **Expenses:** ${audit['expenses']:,.2f}
- **Net Profit:** ${audit['net_profit']:,.2f}
- **Invoices Issued:** {audit['invoices_issued']}

## Unpaid Invoices
"""
    for inv in audit.get("unpaid_invoices", []):
        partner = inv["partner_id"][1] if inv.get("partner_id") else "Unknown"
        content += f"- {inv['name']} | {partner} | ${inv['amount_total']:,.2f}\n"

    content += f"\n*Generated by AI Employee Odoo MCP | {datetime.now().isoformat()}*\n"
    audit_file.write_text(content, encoding="utf-8")


# ── MCP Tool Dispatcher ───────────────────────────────────────────────────────

TOOLS = {
    "odoo_get_invoices": {
        "description": "Fetch recent invoices from Odoo accounting system",
        "parameters": {
            "state": {"type": "string", "description": "Invoice state: posted, draft, cancel (default: posted)"},
            "limit": {"type": "integer", "description": "Max number of invoices to return (default: 10)"}
        },
        "handler": lambda p: get_invoices(p.get("state", "posted"), p.get("limit", 10))
    },
    "odoo_create_invoice_draft": {
        "description": "Create a DRAFT invoice in Odoo (requires human approval to post)",
        "parameters": {
            "partner_name": {"type": "string", "description": "Customer name"},
            "amount": {"type": "number", "description": "Invoice amount"},
            "description": {"type": "string", "description": "Invoice line description"}
        },
        "handler": lambda p: create_invoice_draft(p["partner_name"], p["amount"], p["description"])
    },
    "odoo_get_expenses": {
        "description": "Fetch recent expenses/vendor bills from Odoo",
        "parameters": {
            "limit": {"type": "integer", "description": "Max number of records (default: 20)"}
        },
        "handler": lambda p: get_expenses(p.get("limit", 20))
    },
    "odoo_revenue_summary": {
        "description": "Get monthly revenue summary from Odoo",
        "parameters": {
            "month": {"type": "integer", "description": "Month number 1-12 (default: current month)"},
            "year": {"type": "integer", "description": "Year (default: current year)"}
        },
        "handler": lambda p: get_revenue_summary(p.get("month"), p.get("year"))
    },
    "odoo_weekly_audit": {
        "description": "Generate weekly financial audit for CEO Briefing",
        "parameters": {},
        "handler": lambda p: get_weekly_audit()
    },
}


def handle_request(request):
    """Process an MCP tool call request."""
    method = request.get("method")
    params = request.get("params", {})

    if method == "tools/list":
        tools_list = []
        for name, tool in TOOLS.items():
            tools_list.append({
                "name": name,
                "description": tool["description"],
                "inputSchema": {
                    "type": "object",
                    "properties": tool["parameters"]
                }
            })
        return {"tools": tools_list}

    elif method == "tools/call":
        tool_name = params.get("name")
        tool_params = params.get("arguments", {})

        if tool_name not in TOOLS:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            result = TOOLS[tool_name]["handler"](tool_params)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2, default=str)}]}
        except ConnectionError as e:
            return {"error": f"Odoo connection failed: {e}. Is Odoo running at {ODOO_URL}?"}
        except Exception as e:
            return {"error": f"Tool execution failed: {e}"}

    return {"error": f"Unknown method: {method}"}


def main():
    """Run MCP server on stdio."""
    print(f"Odoo MCP Server started | Odoo: {ODOO_URL} | DB: {ODOO_DB}", file=sys.stderr)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON: {e}"}), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)


if __name__ == "__main__":
    main()
