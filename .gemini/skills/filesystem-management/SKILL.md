---
name: filesystem-management
description: |
  Monitors the local filesystem for new files in the drop_zone and manages file-based task ingestion.
  It automatically moves files to the AI_Employee_Vault/Needs_Action folder and creates metadata.
---

# Filesystem Management Skill

This skill provides the "Perception" layer for local file drops, allowing the AI Employee to ingest documents, images, or data files automatically.

## Capabilities

1.  **Drop Zone Monitoring**: Watches a designated `drop_zone` folder for any new file creations.
2.  **Task Ingestion**: Automatically copies new files to `AI_Employee_Vault/Needs_Action/` with a `FILE_` prefix.
3.  **Metadata Generation**: Creates a companion `.md` file for every dropped file, containing original file details and status.

## Usage

### As a Watcher (Background Process)
Run the watcher script to start monitoring the drop zone:
```bash
python .gemini/skills/filesystem-management/scripts/filesystem_watcher.py
```

### Workflow: Ingesting a File
1.  **Drop:** Place a file (e.g., `invoice.pdf`) into the `drop_zone/` directory.
2.  **Detection:** The watcher detects the file and copies it to `AI_Employee_Vault/Needs_Action/FILE_invoice.pdf`.
3.  **Metadata:** A file named `AI_Employee_Vault/Needs_Action/FILE_invoice.pdf.md` is created automatically.
4.  **Processing:** The `ai-employee-manager` skill (Vault Audit) will then pick up this file for processing.

## Configuration
- **Drop Zone**: Located at the project root (`/drop_zone`).
- **Target**: Files are moved to `AI_Employee_Vault/Needs_Action`.

## Troubleshooting
- **Watchdog Error**: Ensure the `watchdog` Python library is installed (`pip install watchdog`).
- **Permission Denied**: Check read/write permissions for the `drop_zone` and `AI_Employee_Vault` folders.
