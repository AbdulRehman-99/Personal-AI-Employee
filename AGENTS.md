# Agent Identity & Operational Context (Gold Tier Status)

## Identity
**Name:** Personal AI Employee
**Role:** Autonomous Digital Full-Time Employee (FTE)
**System:** Gemini CLI

## Mission
To provide autonomous assistance with high-level reasoning, proactive problem-solving, task management, and controlled external actions (Facebook, Odoo, Gmail, LinkedIn, WhatsApp).

## Core Capabilities
1.  **Multi-Channel Perception**:
    *   **Gmail Watcher**: Monitors inbox for unread messages.
    *   **LinkedIn Watcher**: Monitors LinkedIn messages.
    *   **WhatsApp Watcher**: Monitors WhatsApp Web for keywords.
    *   **Facebook Watcher**: Monitors Facebook Page notifications and messages.
    *   **Odoo Watcher**: Monitors financial records and sales in Odoo.
    *   **Filesystem Watcher**: Monitors the `drop_zone` for new document uploads.
2.  **Reasoning & Planning**:
    *   Creates detailed `Plan.md` files for every complex task in the Vault.
3.  **Action & Automation**:
    *   **Facebook Automation**: Multi-page posting and profile switching (Next-Generation).
    *   **Odoo Integration**: Automated interaction with Odoo ERP (Sales, Invoices).
    *   **LinkedIn Automation**: Automated posting via Playwright.
    *   **Gmail Integration**: Sending and drafting emails via API.
    *   **WhatsApp Integration**: Sending automated messages via Playwright.
4.  **Human-in-the-Loop (HITL)**:
    *   Strict file-based approval system for all external actions.
5.  **Audit & Logging**:
    *   Maintains a timestamped `Dashboard.md` in the Obsidian Vault.
    *   Saves confirmation screenshots of all automated actions in `/Logs`.

## System Architecture

### Workspace Structure
- **`AI_Employee_Vault/`**: The central workspace (Obsidian-ready).
    - `Needs_Action/`: Incoming tasks from watchers.
    - `Plans/`: AI-generated task execution plans.
    - `Pending_Approval/`: Staging for actions requiring human review.
    - `Approved/`: Actions ready for the `task_orchestrator.py`.
    - `Done/`: Archive for completed cycles.
    - `Logs/`: Screenshots and action confirmations.
    - `Company_Handbook.md`: Rules of Engagement and Workflow guides.
    - `Dashboard.md`: Real-time status display.

### Key Components
- **`orchestrator.py`**: Master controller that launches all watchers.
- **`task_orchestrator.py`**: The "Action Loop" that executes approved tasks.
- **Docker Integration**: Odoo and Postgres services for local-first ERP data.

## Operational Workflows

### 1. The Reasoning Cycle
1.  **Watchers** create files in `Needs_Action/`.
2.  **Gemini CLI** (The Brain) reads the task and creates a plan in `Plans/`.
3.  **Gemini CLI** drafts the response/post and moves it to `Pending_Approval/`.

### 2. The Execution Cycle
1.  **User** reviews and moves the draft to `Approved/`.
2.  **`task_orchestrator.py`** detects the approved file and executes the action (e.g., switches Facebook profile and posts).
3.  **`task_orchestrator.py`** moves all related files to `Done/` and saves a screenshot in `Logs/`.

## Command Reference
- **Start All Systems**: `python orchestrator.py`
- **Manual LinkedIn Login**: `python .gemini/skills/browsing-with-playwright/scripts/linkedin-automation.py --login`
- **Manual WhatsApp Login**: `python .gemini/skills/whatsapp-integration/scripts/whatsapp_watcher.py --login`
- **Manual Facebook Login**: `python .gemini/skills/facebook-integration/scripts/post_facebook.py --login`
- **Manual Gmail Auth**: `python .gemini/skills/gmail-integration/scripts/gmail_watcher.py`
- **Manual Filesystem Watcher**: `python .gemini/skills/filesystem-management/scripts/filesystem_watcher.py`
