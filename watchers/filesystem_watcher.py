import time
import shutil
import subprocess
from pathlib import Path
import traceback
from datetime import datetime

def log_activity(action, file_affected=None):
    """Log activity to the activity log file."""
    log_file = Path("vault/Logs/activity_log.md")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    if file_affected:
        log_entry = f"\n[{timestamp}]\n{action}: {file_affected}\n"
    else:
        log_entry = f"\n[{timestamp}]\n{action}\n"

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing to log: {e}")

def move_file_to_needs_action(file_path):
    """Move the file from drop_folder to vault/Needs_Action."""
    try:
        BASE_DIR = Path(__file__).parent.parent
        destination_dir = BASE_DIR / "vault" / "Needs_Action"
        destination_dir.mkdir(parents=True, exist_ok=True)

        destination_path = destination_dir / file_path.name
        shutil.copy2(str(file_path), str(destination_path))
        file_path.unlink()  # Explicitly delete from drop_folder

        log_activity("File moved to Needs_Action", file_path.name)
        print(f"Successfully moved {file_path.name} to Needs_Action")

        return destination_path
    except Exception as e:
        error_msg = f"Error moving file {file_path.name}: {str(e)}"
        log_activity(error_msg, file_path.name)
        print(error_msg)
        return None

def monitor_drop_folder():
    """Monitor the drop_folder for new files."""
    BASE_DIR = Path(__file__).parent.parent
    drop_folder = BASE_DIR / "drop_folder"

    # Create the drop_folder if it doesn't exist
    drop_folder.mkdir(exist_ok=True)

    # Create the vault/Needs_Action directory if it doesn't exist
    needs_action_dir = BASE_DIR / "vault" / "Needs_Action"
    needs_action_dir.mkdir(parents=True, exist_ok=True)

    # Create the vault/Logs directory if it doesn't exist
    logs_dir = BASE_DIR / "vault" / "Logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    print(f"Starting filesystem watcher...")
    print(f"Monitoring: {drop_folder.absolute()}")
    print(f"Target: {needs_action_dir.absolute()}")
    print("Press Ctrl+C to stop")

    # Keep track of files we've already seen
    known_files = set(drop_folder.iterdir()) if drop_folder.exists() else set()

    try:
        while True:
            try:
                if drop_folder.exists():
                    # Get current files in drop_folder
                    current_files = set(drop_folder.iterdir())

                    # Find new files (not in known_files)
                    new_files = current_files - known_files

                    for file_path in new_files:
                        if file_path.is_file():  # Only process files, not subdirectories
                            print("New task detected")
                            # Add to known_files immediately to prevent double detection
                            known_files.add(file_path)
                            time.sleep(1)  # Wait for file to finish writing
                            # Move the file to Needs_Action
                            result = move_file_to_needs_action(file_path)
                            if result:
                                # Auto-trigger Claude processor
                                print(f"[AUTO] Triggering Claude to process task...")
                                BASE_DIR = Path(__file__).parent.parent
                                subprocess.Popen(
                                    'claude -p "Check vault/Needs_Action/ and process any pending tasks, move completed to vault/Done/, update vault/Dashboard.md"',
                                    cwd=str(BASE_DIR),
                                    shell=True
                                )
                                print(f"[AUTO] Claude processor triggered!")

                    # Update known files (add new, don't overwrite)
                    known_files.update(current_files)

                # Wait before checking again
                time.sleep(2)

            except KeyboardInterrupt:
                print("\nFilesystem watcher stopped by user.")
                break
            except Exception as e:
                error_msg = f"Error in monitoring loop: {str(e)}"
                log_activity(error_msg)
                print(error_msg)
                traceback.print_exc()
                time.sleep(5)  # Wait longer after an error

    except KeyboardInterrupt:
        print("\nFilesystem watcher stopped by user.")

if __name__ == "__main__":
    monitor_drop_folder()