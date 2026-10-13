Automated Backup Script

A simple backup tool that walks you through setup with a few plain questions — what to back up, where to save it, and how often — then schedules itself to run automatically using Windows Task Scheduler. No need to touch it again after the first run.

What it does
- Asks for the folder to back up and where to save backups (accepts shortcuts like "Documents" or "Downloads", or a full path)
- Creates a timestamped zip backup right away
- Automatically deletes the oldest backups once you pass a limit you set
- Schedules itself (daily/weekly/monthly) using Windows Task Scheduler, so it keeps running in the background without you opening anything again

Built with
Python — using only built-in libraries (`os`, `shutil`, `argparse`, `subprocess`) plus Windows' own Task Scheduler for automation.


How to run it
1. Make sure Python is installed ([python.org](https://www.python.org/downloads/))
2. Download or clone this repository
3. Open a terminal in the project folder and run:
4. Answer the prompts — no need to edit any code.

Note: automatic scheduling (Task Scheduler) only works on Windows.
