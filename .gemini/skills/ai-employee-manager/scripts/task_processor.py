# .gemini/skills/ai-employee-manager/scripts/task_processor.py
import argparse
import os
from pathlib import Path

VAULT_PATH = Path("AI_Employee_Vault")
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
DONE = VAULT_PATH / "Done"

def process_task(file_name):
    source = NEEDS_ACTION / file_name
    dest = DONE / file_name
    
    if not source.exists():
        print(f"File {file_name} not found in {NEEDS_ACTION}.")
        return

    # Move file to Done folder
    os.rename(source, dest)
    print(f"Moved {file_name} to {DONE}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="The name of the file to move to Done.")
    args = parser.parse_args()
    
    if args.file:
        process_task(args.file)
    else:
        print("Please provide a file name using --file.")
