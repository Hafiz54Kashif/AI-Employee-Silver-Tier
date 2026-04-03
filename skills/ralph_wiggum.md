# ralph_wiggum

## Purpose
Keep Claude working autonomously until ALL tasks in vault/Needs_Action/ are complete.
Prevents Claude from stopping mid-way when multiple tasks exist.

## How It Works
When Claude tries to stop/exit, the Stop hook automatically:
1. Checks `vault/Needs_Action/` for pending `.md` files
2. If tasks remain → blocks exit + re-injects processing prompt
3. If no tasks → allows clean exit
4. Tracks iterations (max 20 by default) to prevent infinite loops

## Hook Location
`.claude/hooks/ralph_wiggum_stop_hook.py`

## Configuration
Registered in `.claude/settings.local.json` under `hooks.Stop`.

## Iteration Control
Set environment variable to change max iterations:
```bash
set RALPH_MAX_ITERATIONS=10
```
Default: 20 iterations

## State Tracking
- State file: `.claude/ralph_state.json` (auto-created, auto-deleted)
- Logs each iteration in `vault/Logs/YYYY-MM-DD.md`

## Completion Conditions
Claude exits cleanly when ANY of these is true:
- `vault/Needs_Action/` is empty
- Max iterations reached (safety limit)

## Usage
Simply run Claude on any task — the hook activates automatically on every stop attempt:
```
claude "Process all tasks in vault/Needs_Action/"
```
Claude will keep looping until Needs_Action is empty.

## Example Log Output
```
- [10:30:01] RalphWiggum | Iteration 1/20 — 3 tasks pending. Re-injecting prompt.
- [10:31:45] RalphWiggum | Iteration 2/20 — 1 tasks pending. Re-injecting prompt.
- [10:32:30] RalphWiggum | All tasks complete. Allowing Claude to exit.
```
