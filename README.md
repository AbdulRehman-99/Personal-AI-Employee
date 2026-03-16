# Personal AI Employee: Autonomous Digital FTE (Gold Tier)

This repository contains the infrastructure for a **Local-First, Autonomous Digital Employee**. It transforms a standard AI into a Full-Time Equivalent (FTE) that can monitor your communications, plan its own tasks, and execute external actions with Human-in-the-Loop (HITL) approval.

---

## 🌟 Gold Tier Features
- **Multi-Channel Perception**: Watchers for Gmail, LinkedIn, WhatsApp, Facebook, Odoo, and Filesystem.
- **Agentic Planning**: Every task generates a `Plan.md` in the Obsidian Vault.
- **Next-Gen Facebook Automation**: Handles multi-page profile switching and complex multi-step post submissions.
- **ERP Integration**: Local-first Odoo 17 integration via Docker for financial and sales automation.
- **Audit & Compliance**: Automated `Dashboard.md` and detailed action screenshots in `Logs/`.

---

## 🚀 Quick Start

### 1. Prerequisite: Environment Setup
Ensure you have Python 3.10+ and Docker installed.

### 2. Launch the System
Start all watchers and the task orchestrator:
```bash
python orchestrator.py
```

### 3. ERP Services (Odoo)
Launch the local Odoo environment:
```bash
docker-compose up -d
```

---

## 🏗️ The Vault (Obsidian Ready)
The `AI_Employee_Vault/` is the brain's workspace. Connect it to **Obsidian** for a real-time view of your agent's thoughts and actions.

- **Needs_Action**: Incoming triggers from the world.
- **Plans**: How the agent intends to solve the task.
- **Pending_Approval**: Drafts awaiting your "Go Ahead".
- **Approved**: The green light for execution.
- **Done**: Historical archive of all completed work.
- **Logs**: Visual proof (screenshots) of every automated action.

---

## 🛠️ Skills & Tools
- **browsing-with-playwright**: Core browser automation.
- **facebook-integration**: Robust multi-page posting.
- **odoo-integration**: ERP data management.
- **gmail-integration**: Secure email handling.
- **whatsapp-integration**: Real-time communication.

---

## 📜 Workflow: The Reasoning Loop
1. **Perceive**: A watcher detects a new email or notification.
2. **Reason**: Gemini CLI reads the input and creates a `Plan.md`.
3. **Draft**: The agent prepares an action (e.g., a Facebook post).
4. **Approve**: You review the draft in the Vault and move it to `Approved/`.
5. **Act**: The `task_orchestrator.py` executes the action and logs proof.

---

## ⚖️ Rules of Engagement
- **No Unapproved Actions**: The agent NEVER posts or sends emails without a file in the `Approved/` folder.
- **Visual Proof**: Every browser action must capture a screenshot in `Logs/`.
- **Local First**: All sessions and ERP data stay on your machine.
