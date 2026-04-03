# process_tasks

## Purpose
This skill enables an AI agent to systematically process tasks from the Needs_Action folder, create plans, execute them, and manage the workflow by moving completed tasks to the Done folder while updating the dashboard and maintaining logs.

## Input
- Text files containing task descriptions located in the `vault/Needs_Action` directory
- Each file should contain a clear task description that needs to be processed

## Process
1. **Scan for New Tasks**: Read all files from the `vault/Needs_Action` directory
2. **Log Detection**: Record in `vault/Logs/activity_log.md` that a new task has been detected
3. **Understand the Task**: Parse and comprehend the task requirements from each file
4. **Generate Task Plan**: Create a structured plan with clear steps to complete the task
5. **Save Plan**: Store the generated plan in the `vault/Plans` directory with a corresponding filename
6. **Log Planning**: Record in `vault/Logs/activity_log.md` that a plan has been created
7. **Execute Steps**: Logically execute each step of the plan using available tools and resources
8. **Log Execution**: Record in `vault/Logs/activity_log.md` the execution of each major step
9. **Complete Task**: Move the processed task file from `vault/Needs_Action` to `vault/Done`
10. **Log Completion**: Record in `vault/Logs/activity_log.md` that the task has been completed
11. **Update Dashboard**: Add the completed task to the Recent Activity section in `vault/Dashboard.md`

## Output
- A completed task with all required actions executed
- A saved plan in the `vault/Plans` directory
- Updated `vault/Dashboard.md` reflecting the recent activity
- The original task file moved to the `vault/Done` directory
- Comprehensive logging in `vault/Logs/activity_log.md`

## Example Workflow
1. Find a new task file in `vault/Needs_Action` titled "Prepare quarterly report"
2. Log detection: "[2026-01-10 14:20] Task detected in Needs_Action: Prepare quarterly report"
3. Read and understand the task: "Compile sales data and create a report for Q1"
4. Generate a plan with steps: collect data, analyze metrics, format report, review findings
5. Save this plan as "Prepare quarterly report_plan.md" in `vault/Plans`
6. Log planning: "[2026-01-10 14:25] Plan created for task: Prepare quarterly report"
7. Execute each step of the plan using appropriate tools
8. Log execution: "[2026-01-10 14:30] Executed data collection step for: Prepare quarterly report"
9. Once completed, move "Prepare quarterly report" from `vault/Needs_Action` to `vault/Done`
10. Log completion: "[2026-01-10 15:00] Task completed: Prepare quarterly report"
11. Update `vault/Dashboard.md` with "Completed: Prepare quarterly report" in the Recent Activity section