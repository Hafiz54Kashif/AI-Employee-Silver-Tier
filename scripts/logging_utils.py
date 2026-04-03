"""
Logging utility for the AI Employee project.
Provides consistent logging functionality across all modules.
"""

import datetime
from pathlib import Path


def log_activity(action, file_affected=None):
    """
    Log an activity to the activity log file.

    Args:
        action (str): The action that was performed
        file_affected (str, optional): The file that was affected by the action
    """
    log_file = Path("vault/Logs/activity_log.md")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if file_affected:
        log_entry = f"\n[{timestamp}]\n{action}: {file_affected}\n"
    else:
        log_entry = f"\n[{timestamp}]\n{action}\n"

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing to log: {e}")


def log_task_completion(task_name):
    """
    Log a task completion event.

    Args:
        task_name (str): The name of the completed task
    """
    log_activity("Task completed", task_name)


def log_task_moved(task_name, from_location, to_location):
    """
    Log a task movement event.

    Args:
        task_name (str): The name of the task
        from_location (str): The source location
        to_location (str): The destination location
    """
    log_activity(f"Task moved from {from_location} to {to_location}", task_name)


def log_error(error_message, file_affected=None):
    """
    Log an error event.

    Args:
        error_message (str): The error message
        file_affected (str, optional): The file associated with the error
    """
    if file_affected:
        log_activity(f"ERROR: {error_message}", file_affected)
    else:
        log_activity(f"ERROR: {error_message}")