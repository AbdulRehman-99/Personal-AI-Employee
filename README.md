# Personal AI Employee: Autonomous Digital FTE (Gold Tier)

This repository contains the infrastructure for a **Local-First, Autonomous Digital Employee**. It transforms a standard AI into a Full-Time Equivalent (FTE) that can monitor your communications, plan its own tasks, and execute external actions with Human-in-the-Loop (HITL) approval.

---

## 🌟 Gold Tier Features
- **Multi-Channel Perception**: Real-time watchers for Gmail, LinkedIn, WhatsApp, Facebook, Odoo, and Filesystem.
- **Dynamic Orchestration**: Centralized `orchestrator.py` that dynamically scales watchers based on `Inbox` requirements.
- **Agentic Planning**: Every task generates a detailed `Plan.md` in the Obsidian Vault.
- **Next-Gen Facebook Automation**: Handles multi-page profile switching and complex multi-step post submissions with visual audit logs.
- **ERP Integration**: Local-first Odoo 17 integration via Docker for autonomous invoicing and financial summaries.
- **Zero-Trust Security**: No external action (POST/EMAIL) can be executed without a file presence in the `Approved/` folder.
- **Audit & Compliance**: Automated `Dashboard.md` updates via `vault_audit.py` and detailed action screenshots in `Logs/`.

---

## 🏗️ Project Structure

```text
Personal-AI-Employee/
├── orchestrator.py            # Central Nervous System (launches watchers)
├── task_orchestrator.py       # Execution Engine (processes approved tasks)
├── docker-compose.yml         # Odoo 17 & PostgreSQL infrastructure
├── drop_zone/                 # File ingestion point for FS Watcher
├── AI_Employee_Vault/         # The "Brain" (Obsidian-ready)
│   ├── Needs_Action/          # Input queue from all watchers
│   ├── Plans/                 # Strategic logic and execution steps
│   ├── Pending_Approval/      # Staging area for human review
│   ├── Approved/              # Authorization queue for execution
│   ├── Done/                  # Archive of completed work
│   ├── Logs/                  # Visual evidence (screenshots)
│   └── Dashboard.md           # Real-time performance tracking
└── .gemini/skills/            # Specialized capability modules
    ├── ai-employee-manager/   # Vault maintenance & auditing
    ├── facebook-integration/  # Multi-page social automation
    ├── odoo-integration/      # Local ERP & Accounting
    └── ...                    # Gmail, LinkedIn, WhatsApp, FS skills
```

---

## 🚀 Quickstart: Setup & Execution

### 1. Prerequisites
Ensure you have the following installed:
- **Python 3.10+**
- **Docker & Docker Compose**
- **Node.js** (for Playwright MCP)

Install core Python dependencies:
```bash
pip install playwright watchdog google-auth-oauthlib google-api-python-client
playwright install chromium
```

### 2. Infrastructure Setup (Odoo ERP)
Start the local ERP system:
```bash
docker-compose up -d
```
Access Odoo at `http://localhost:8069`. Default DB Master Password is `admin`.

### 3. Authentication (One-Time Setup)
Initialize sessions for the watchers:
| Channel | Command |
| :--- | :--- |
| **Facebook** | `python .gemini/skills/facebook-integration/scripts/facebook_watcher.py --login` |
| **LinkedIn** | `python .gemini/skills/browsing-with-playwright/scripts/linkedin-automation.py --login` |
| **WhatsApp** | `python .gemini/skills/whatsapp-integration/scripts/whatsapp_watcher.py --login` |
| **Gmail** | `python .gemini/skills/gmail-integration/scripts/gmail_watcher.py` |

### 4. Start the System
Launch the central orchestrator to begin monitoring all channels:
```bash
python orchestrator.py
```

---

## 🔄 The Lifecycle & Workflow

The **Personal AI Employee** operates on a strict, state-based workflow:

### 1. Perception & Ingestion
Watchers detect events and route them to `Needs_Action/` with standardized prefixes:
- `EMAIL_`: From Gmail Watcher.
- `FB_`: From Facebook Watcher.
- `FILE_`: From Filesystem Watcher (`drop_zone/`).
- `FIN_`: From Odoo Finance Watcher.

### 2. Autonomous Reasoning (Silent)
The Gemini CLI autonomously analyzes `Needs_Action` items and performs the following **without prompting the user**:
1. Creates a strategic `Plan.md` in `Plans/`.
2. Generates the final payload/content in `Pending_Approval/`.

### 3. The Execution Authorization (HITL)
**Mandatory:** Only once the final draft is ready will Gemini CLI proactively prompt you using its native selection system. You will see a summary of the intended action and be asked:
- **"Draft ready for execution. How should I proceed?"**
- Options: `[Approve & Execute]`, `[Edit/Redraft]`, `[Reject Task]`.

Once you select **Approve**, the agent automatically moves the file to `Approved/` and triggers the execution. This loop continues silently in the background for all other tasks until the final approval is required for each.

### 4. Task Orchestration (Action)
`task_orchestrator.py` detects files in `Approved/` and routes them by `type:` header:
- `linkedin_post`: Triggers LinkedIn automation.
- `facebook_post`: Triggers multi-page Facebook posting.
- `whatsapp_send`: Triggers WhatsApp messaging.
- `email_send`: Triggers Gmail API transmission.
- `create_invoice`: Triggers Odoo JSON-RPC invoice creation.

---

## 🛠️ Specialized Skills Deep Dive

### AI Employee Manager
- **Vault Audit**: `python .gemini/skills/ai-employee-manager/scripts/vault_audit.py` - Scans the vault and updates the `Dashboard.md`.
- **Task Processor**: Handles file movement and cleanup upon task completion.

### Odoo Integration
- **Finance Watcher**: Monitors for overdue invoices and generates financial summaries for CEO briefings.
- **MCP Server**: Provides `create_invoice` and `register_payment` tools for the agent.

### Browsing with Playwright
- **MCP Server**: A shared browser context server for complex web interactions (Navigation, Form Filling, Data Extraction).
- **LinkedIn Automation**: Standalone posting and message monitoring logic.

---

## ⚖️ Rules of Engagement
- **Zero-Trust Execution**: No file in `Approved/` = No action taken.
- **Visual Verification**: Every browser-based action captures a confirmation screenshot in `AI_Employee_Vault/Logs/`.
- **Local-First Privacy**: Sensitive session data (`.json`, `credentials.json`) and ERP data never leave your local machine.
- **Continuous Loop**: The agent remains active until the task is moved to `Done/`.

---

## 🔧 Maintenance

### Manual Session Refresh
If a session expires (e.g., Facebook login required), run the specific script with the `--login` flag as detailed in the **Authentication** section.

### System Reset
1. Stop orchestrator (`Ctrl+C`).
2. Run `vault_audit.py` to reconcile states.
3. Restart `orchestrator.py`.
