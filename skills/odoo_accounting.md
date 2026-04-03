# odoo_accounting

## Purpose
Integrate with Odoo Community accounting system via JSON-RPC MCP server.
Enables Claude to read invoices, create draft invoices, fetch expenses,
and generate weekly financial audits for the CEO Briefing.

## Prerequisites
1. Install Odoo Community 19+: https://www.odoo.com/documentation
2. Set credentials in `.env`:
   ```
   ODOO_URL=http://localhost:8069
   ODOO_DB=my_company
   ODOO_USERNAME=admin
   ODOO_PASSWORD=admin
   ```
3. Register MCP server in Claude Code settings (see below)

## MCP Server
File: `skills/odoo_mcp_server.py`
Run: `python skills/odoo_mcp_server.py`

## Register in Claude Code
Add to your MCP config (`~/.config/claude-code/mcp.json` or project settings):
```json
{
  "servers": [
    {
      "name": "odoo",
      "command": "python",
      "args": ["skills/odoo_mcp_server.py"]
    }
  ]
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `odoo_get_invoices` | Fetch recent customer invoices |
| `odoo_create_invoice_draft` | Create draft invoice (needs approval to post) |
| `odoo_get_expenses` | Fetch vendor bills / expenses |
| `odoo_revenue_summary` | Monthly revenue summary |
| `odoo_weekly_audit` | Full weekly financial audit → saves to vault/Logs/ |

## Process for Invoice Creation
1. Claude calls `odoo_create_invoice_draft` with customer + amount
2. Invoice saved as DRAFT in Odoo (NOT posted yet)
3. Claude creates approval file in `vault/Pending_Approval/`
4. Human reviews and moves to `vault/Approved/`
5. Claude posts/sends the invoice via Odoo

## Process for Weekly Audit (CEO Briefing)
1. Scheduled task triggers every Sunday night
2. Claude calls `odoo_weekly_audit`
3. Data written to `vault/Logs/odoo_weekly_audit_YYYY-MM-DD.md`
4. CEO Briefing skill reads this data for financial section

## Security
- Odoo credentials stored in `.env` only (never in vault)
- All financial actions require human approval before posting
- Audit logs retained in `vault/Logs/` for 90 days

## Odoo API Reference
https://www.odoo.com/documentation/19.0/developer/reference/external_api.html
