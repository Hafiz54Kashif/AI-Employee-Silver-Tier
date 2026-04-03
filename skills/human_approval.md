# human_approval

## Purpose
Route sensitive tasks to human review before AI execution. Implements human-in-the-loop workflow for actions involving payments, passwords, emails, or other sensitive operations.

## Input
- Task files in `vault/Needs_Action/`
- Sensitive keywords list: payment, invoice, bank, password, reset, urgent, wire transfer, account, login, credential, delete, send email, reply, forward, money, transaction

## Process
1. Read task content from `vault/Needs_Action/`
2. Scan content for sensitive keywords
3. If sensitive keyword found:
   - Add approval notice to task file
   - Move task to `vault/Pending_Approval/`
   - Log: "Task requires human approval"
   - Wait for human to move file to `vault/Approved/` or `vault/Rejected/`
4. If no sensitive keyword:
   - Process task normally through standard workflow
5. Monitor `vault/Approved/` folder:
   - Generate plan and execute approved tasks
   - Move to `vault/Done/`
   - Update dashboard
6. Monitor `vault/Rejected/` folder:
   - Log rejection
   - Archive to `vault/Done/REJECTED_filename.md`

## Output
- Sensitive tasks held in `vault/Pending_Approval/` awaiting review
- Approved tasks executed and moved to `vault/Done/`
- Rejected tasks archived with rejection note
- Dashboard updated with approval status
- All actions logged in `vault/Logs/`

## Example Workflow
1. Email arrives: "Please process payment of $500 to vendor"
2. Skill detects keyword: "payment"
3. File moved to `vault/Pending_Approval/` with note: "APPROVAL REQUIRED - contains: payment"
4. Human reviews in Obsidian and moves to `vault/Approved/`
5. Approval watcher detects file in Approved folder
6. Plan generated and task executed
7. File moved to `vault/Done/`
