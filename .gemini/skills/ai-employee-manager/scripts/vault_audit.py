# .gemini/skills/ai-employee-manager/scripts/vault_audit.py
import os
import sys
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path("AI_Employee_Vault").resolve()
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
DASHBOARD = VAULT_PATH / "Dashboard.md"

def audit():
    if not NEEDS_ACTION.exists():
        print(f"Directory {NEEDS_ACTION} does not exist.")
        return

    # Find all .md files in Needs_Action (excluding the Dashboard)
    files = list(NEEDS_ACTION.glob("*.md"))
    
    print(f"Found {len(files)} pending task(s).")
    
    # Update Dashboard.md
    with open(DASHBOARD, "r") as f:
        lines = f.readlines()
    
    # Update Pending Tasks section
    new_lines = []
    in_pending = False
    for line in lines:
        if line.startswith("## Pending Tasks"):
            in_pending = True
            new_lines.append(line)
            if not files:
                new_lines.append("No pending tasks found.\n")
            else:
                for f in files:
                    new_lines.append(f"- [ ] {f.name}\n")
            continue
        
        if in_pending and line.startswith("##"):
            in_pending = False
            new_lines.append(line)
            continue
        
        if not in_pending:
            new_lines.append(line)
            
    with open(DASHBOARD, "w") as f:
        f.writelines(new_lines)
    
    print(f"Updated {DASHBOARD}.")

if __name__ == "__main__":
    audit()
