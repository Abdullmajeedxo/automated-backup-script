import os
import sys
import shutil
import argparse
import subprocess
from datetime import datetime

TASK_NAME = "AutomatedBackupScript"

def create_backup(source, destination):
    """Zips the source folder and saves it to the destination with a timestamp."""
    if not os.path.exists(source):
        print(f"Error: source folder not found -> {source}")
        return None

    os.makedirs(destination, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = os.path.join(destination, f"backup_{timestamp}")

    shutil.make_archive(backup_path, "zip", source)
    print(f"Backup created: {backup_path}.zip")
    return f"{backup_path}.zip"

def cleanup_old_backups(destination, max_to_keep):
    """Deletes the oldest backups if there are more than max_to_keep."""
    backups = sorted(
        f for f in os.listdir(destination)
        if f.startswith("backup_") and f.endswith(".zip")
    )
    for old_backup in backups[: max(0, len(backups) - max_to_keep)]:
        os.remove(os.path.join(destination, old_backup))
        print(f"Removed old backup: {old_backup}")


def run_backup(source, destination, keep):
    print("Starting backup...")
    result = create_backup(source, destination)
    if result:
        cleanup_old_backups(destination, keep)
        print("Backup process finished successfully.")
    else:
        print("Backup process failed.")

def ask(question, default=None):
    suffix = f" [{default}]" if default else ""
    answer = input(f"{question}{suffix}: ").strip().strip('"')
    return answer if answer else default

SHORTCUTS = {
    "documents": "Documents",
    "desktop": "Desktop",
    "downloads": "Downloads",
    "pictures": "Pictures",
    "music": "Music",
    "videos": "Videos",
}


def resolve_path(user_input):
    """Lets the user type a short name (e.g. 'downloads') instead of a full path."""
    key = user_input.strip().lower()
    if key in SHORTCUTS:
        return os.path.join(os.path.expanduser("~"), SHORTCUTS[key])
    return user_input

def choose_frequency():
    print("\nHow often do you want backups?")
    print("  1) Daily")
    print("  2) Weekly")
    print("  3) Monthly")
    choice = input("Choose 1, 2, or 3 [1]: ").strip() or "1"
    return {"1": "DAILY", "2": "WEEKLY", "3": "MONTHLY"}.get(choice, "DAILY")

def schedule_with_task_scheduler(source, destination, keep, frequency):
    """Registers this script with Windows Task Scheduler so it runs on its own."""
    python_exe = sys.executable
    script_path = os.path.abspath(__file__)

    command = (
        f'"{python_exe}" "{script_path}" '
        f'--source "{source}" --destination "{destination}" --keep {keep}'
    )

    schtasks_args = [
        "schtasks", "/create", "/f",
        "/tn", TASK_NAME,
        "/tr", command,
        "/sc", frequency,
        "/st", "02:00",
    ]
    if frequency == "WEEKLY":
        schtasks_args += ["/d", "MON"]
    elif frequency == "MONTHLY":
        schtasks_args += ["/d", "1"]

    subprocess.run(schtasks_args, check=True)

def run_setup_wizard():
    print("=== Automated Backup Setup ===\n")

    default_source = os.path.join(os.path.expanduser("~"), "Documents")
    while True:
        raw_source = ask("What folder do you want to back up? (e.g. Documents, Downloads, or a full path)", default_source)
        source = resolve_path(raw_source)
        if os.path.exists(source):
            break
        print(f"  -> I couldn't find that folder: {source}")
        print("     Try a short name like 'Documents' or 'Downloads', or type the full path.\n")

    default_destination = os.path.join(os.path.expanduser("~"), "Backups")
    raw_destination = ask("Where should backups be saved? (e.g. Downloads, or a full path)", default_destination)
    destination = resolve_path(raw_destination)

    keep = ask("How many backups do you want to keep before old ones are deleted?", "5")
    keep = int(keep) if keep.isdigit() else 5

    frequency = choose_frequency()

    print("\nCreating your first backup now...")
    backup_file = create_backup(source, destination)

    if not backup_file:
        print("\nSetup stopped: the first backup failed, so nothing was scheduled.")
        print("Run the script again and double-check the folder paths.")
        return

    cleanup_old_backups(destination, keep)

    if os.name == "nt":
        try:
            schedule_with_task_scheduler(source, destination, keep, frequency)
            print(f"\nAll set! Backups will run automatically ({frequency.lower()}, at 2:00 AM).")
        except Exception as e:
            print(f"\nCould not schedule automatic backups: {e}")
            print("You can still run this script manually any time.")
    else:
        print("\nAutomatic scheduling via Task Scheduler is only available on Windows.")
        print("On Linux/Mac, add this command to a cron job to automate it.")

    print(f"\nYou'll find your backups here: {destination}")


def main():
    parser = argparse.ArgumentParser(description="Back up a folder into timestamped zip files.")
    parser.add_argument("--source", help="Folder to back up")
    parser.add_argument("--destination", help="Folder where backups are stored")
    parser.add_argument("--keep", type=int, default=5, help="Number of backups to keep (default: 5)")
    args = parser.parse_args()

    if args.source and args.destination:
        
        run_backup(args.source, args.destination, args.keep)
    else:
        
        run_setup_wizard()


if __name__ == "__main__":
    main()
