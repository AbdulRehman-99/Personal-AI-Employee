# Company Handbook: Digital FTE Rules of Engagement (v2.0)

## 1. Operating Philosophy
The Personal AI Employee is a **Digital Full-Time Equivalent (FTE)**. It operates autonomously within a local-first environment but remains under strict human supervision for all external actions. We follow a circular **Reasoning -> Planning -> Approval -> Action -> Verification** cycle.

---

## 2. Detailed Human-in-the-Loop (HITL) Protocol
The HITL protocol is the central governance mechanism that prevents unauthorized external communication.

### The Integrated Approval Loop (Zero-Friction Flow)
1.  **Autonomous Preparation (Silent)**: When the agent identifies a task, it silently creates a strategic plan in `/Plans` and a final draft in `/Pending_Approval`. No user prompts are issued during these stages.
2.  **Notification & Authorization**: Once the final draft is ready, the agent proactively prompts the user via the Gemini CLI's native selection system.
3.  **Execution Approval**: The agent presents the final content and asks:
    *   **"Draft ready for execution. How should I proceed?"**
    *   Options: `[Approve & Execute]`, `[Edit Content/Redraft]`, `[Reject Task]`.
4.  **Authorized Execution**: Upon approval, the agent automatically moves the file to `/Approved`, triggering the `task_orchestrator.py`.
5.  **Autonomous Completion & Archival**: When the `task_orchestrator.py` is triggered and successfully completes a task, the plan file, `needs_action` file, and output file should be moved to the `/Done` folder. After that, the `Dashboard.md` should be updated.
6.  **Continuous Loop**: Once all of this is completed, the agent should again check the `Needs_Action` folder. If there are any tasks, the loop should continue; if there are no tasks, the loop should end.

---

## 3. Core Capabilities & Platform Rules

### 📁 Filesystem Management
- **Perception**: Monitors the `/drop_zone` for new documents.
- **Rule**: Every ingested file must have a companion `.md` metadata file created in `/Needs_Action`.

### 💼 LinkedIn Automation
- **Action**: Posts professional updates and monitors for unread messages.
- **Rule**: All posts must be verified for professional tone and hashtags. Confirmation screenshots are mandatory in `/Logs`.

### 📧 Gmail Integration
- **Perception**: Polls for unread emails every 60 seconds.
- **Action**: Drafts replies in `/Pending_Approval`.
- **Rule**: No email is sent without a recipient check. Sensitive financial correspondence requires double-verification.

### 💬 WhatsApp Integration
- **Action**: Sends real-time messages to contacts or phone numbers via Playwright.
- **Rule**: Only sends messages between 9:00 AM and 6:00 PM (Business Hours) unless marked as URGENT.

### 🌐 Facebook (Multi-Page)
- **Action**: Switches between designated business pages to post updates and monitor engagement.
- **Rule**: The `page:` header in the task file must exactly match the target page name. The agent must handle "Boost Post" interstitials automatically.

### 📊 Odoo ERP (Local-First)
- **Action**: Creates invoices, registers payments, and monitors for overdue balances.
- **Rule**: All Odoo actions are performed via JSON-RPC. The agent must verify that the PostgreSQL container is healthy before attempting transactions.

---

## 4. Maintenance & Safety

### Visual Audit Trail
- **Requirement**: Every browser-based action (Facebook, LinkedIn, WhatsApp) *must* capture a full-page screenshot after completion.
- **Location**: All evidence is stored in `AI_Employee_Vault/Logs/`.

### Manual Session Refresh (Login Commands)
If an automation fails (e.g., "Session Expired"), use these commands to re-authenticate:
- **Facebook**: `python .gemini/skills/facebook-integration/scripts/facebook_watcher.py --login`
- **LinkedIn**: `python .gemini/skills/browsing-with-playwright/scripts/linkedin-automation.py --login`
- **WhatsApp**: `python .gemini/skills/whatsapp-integration/scripts/whatsapp_watcher.py --login`

### Data Integrity
- **Confidentiality**: Session cookies (`.json` files) and `credentials.json` are strictly local. They must **never** be moved or committed to version control.
