---
name: approval-workflow
description: |
  The central governance mechanism of the AI Employee system, enforcing a "Zero-Trust" execution model. This skill manages the critical "Human-in-the-Loop" (HITL) gateway, ensuring that no external actions—such as social media posts, emails, or financial transactions—are executed without explicit human verification. it facilitates the movement of tasks from 'Pending_Approval' to 'Approved', serving as the final safety buffer for autonomous operations.
  
---


# Approval Workflow Skill

This skill manages the Human-in-the-Loop (HITL) approval process for sensitive actions.

## Workflow

1.  **Request**: When the AI needs to perform a sensitive action (e.g., sending an email, making a payment), it creates a file in `AI_Employee_Vault/Pending_Approval/`.
2.  **Review**: The user (you) reviews the file.
3.  **Approve/Reject**:
    *   **Approve**: Move the file to `AI_Employee_Vault/Approved/`.
    *   **Reject**: Move the file to `AI_Employee_Vault/Rejected/`.
4.  **Execution**: The agent (or a watcher) detects the file in `Approved` and executes the action.

## Usage

### Listing Pending Approvals
To see what requires your attention:
```bash
python .gemini/skills/approval-workflow/scripts/check_approvals.py --list
```

### Approving an Item
You can manually move the file, or use the script:
```bash
python .gemini/skills/approval-workflow/scripts/check_approvals.py --approve <filename>
```

### Rejecting an Item
```bash
python .gemini/skills/approval-workflow/scripts/check_approvals.py --reject <filename>
```

## Folder Structure
*   `AI_Employee_Vault/Pending_Approval/`: Staging area for requests.
*   `AI_Employee_Vault/Approved/`: Actionable items (watched by agent).
*   `AI_Employee_Vault/Rejected/`: Archived rejected items.
