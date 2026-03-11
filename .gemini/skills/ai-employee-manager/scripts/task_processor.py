# .gemini/skills/ai-employee-manager/scripts/task_processor.py
import argparse
import os
import shutil
from pathlib import Path

# Robustly find the vault path relative to this script
# Path: <root>/.gemini/skills/ai-employee-manager/scripts/task_processor.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
VAULT_PATH = PROJECT_ROOT / "AI_Employee_Vault"
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
DONE = VAULT_PATH / "Done"

def process_task(file_name):
    # Ensure directories exist
    DONE.mkdir(parents=True, exist_ok=True)
    
    source = NEEDS_ACTION / file_name
    dest = DONE / file_name
    
    if not source.exists():
        print(f"Error: File '{file_name}' not found in {NEEDS_ACTION}")
        return

    try:
        # Move file to Done folder
        shutil.move(str(source), str(dest))
        print(f"Successfully moved '{file_name}' to {DONE}")
    except Exception as e:
        print(f"Error moving file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a task by moving it from Needs_Action to Done.")
    parser.add_argument("--file", required=True, help="The name of the file to move to Done.")
    args = parser.parse_args()
    
    process_task(args.file)
