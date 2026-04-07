# .gemini/skills/ai-employee-manager/scripts/vault_audit.py
import os
import sys
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path("AI_Employee_Vault").resolve()
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
DASHBOARD = VAULT_PATH / "Dashboard.md"

def audit():
    if not DASHBOARD.exists():
        print(f"Dashboard not found at {DASHBOARD}")
        return

    # Find all .md files in Needs_Action
    files = list(NEEDS_ACTION.glob("*.md")) if NEEDS_ACTION.exists() else []
    
    print(f"Found {len(files)} pending task(s).")
    
    # Update Dashboard.md with UTF-8
    with open(DASHBOARD, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Update Status and Recent Tasks
    new_lines = []
    found_last_update = False
    for line in lines:
        if "**Last Update:**" in line:
            new_lines.append(f"**Last Update:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            found_last_update = True
        else:
            new_lines.append(line)
            
    with open(DASHBOARD, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    
    print(f"Updated {DASHBOARD}.")

if __name__ == "__main__":
    audit()
