---
name: ai-employee-manager
description: |
  Manages the AI Employee Vault, processes pending tasks, and updates the dashboard.
  It helps analyze files in /Needs_Action and organize the vault according to the Company Handbook.
---

# AI Employee Manager Skill

This skill allows the agent to autonomously manage its workspace by processing incoming files and tasks.

## Tasks & Tools

### Vault Audit
- **Goal:** Scan the `/Needs_Action` folder, analyze new files, and update the `Dashboard.md`.
- **Action:** `python scripts/vault_audit.py`

### Task Processor
- **Goal:** Move a processed file from `/Needs_Action` to `/Done`.
- **Action:** `python scripts/task_processor.py --file <filename>`

## Workflow: Processing a New File
1.  **Detect:** File system watcher drops a file into `drop_zone`.
2.  **Monitor:** Watcher moves the file to `AI_Employee_Vault/Needs_Action` and creates a metadata `.md` file.
3.  **Audit:** Use `vault_audit.py` to identify the new file and add it to the `Dashboard.md`.
4.  **Execute:** Analyze the content and perform the necessary action (e.g., summarize, flag for approval).
5.  **Complete:** Use `task_processor.py` to move the file to `AI_Employee_Vault/Done`.

## Troubleshooting
- **Missing Files:** Ensure the `AI_Employee_Vault` directory exists and has the correct permissions.
- **Watcher Inactive:** Verify `filesystem_watcher.py` is running and monitoring the `drop_zone`.
