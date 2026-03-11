# Personal AI Employee (Silver Tier)

Welcome to your Autonomous Digital FTE. This project transforms Gemini CLI from a simple chatbot into a proactive employee that manages your Gmail, LinkedIn, and files local-first.

## 🚀 Silver Tier Features
- **Proactive Watchers**: Monitors Gmail, LinkedIn, WhatsApp, and local folders automatically.
- **Modular Skills**: Dedicated skills for Gmail, LinkedIn, WhatsApp, and Filesystem management.
- **Action Loop**: Executes approved posts, emails, and messages while you sleep.
- **Reasoning First**: Always creates a `Plan.md` before taking action.
- **Audit Trails**: Every action is logged with a timestamped screenshot in the `Vault/Logs`.

## 📂 Project Structure
```text
├── AI_Employee_Vault/         # The GUI & Memory (Obsidian)
│   ├── Needs_Action/          # Incoming Tasks (Email, LinkedIn, File Drops)
│   ├── Plans/                 # AI Reasoning & Planning Files
│   ├── Pending_Approval/      # Staging for Human Review
│   ├── Approved/              # Trigger for Action Loop
│   ├── Done/                  # Completed Cycle Archive
│   └── Logs/                  # Action Logs & Screenshots
├── orchestrator.py            # Master Process (Starts all Watchers)
├── task_orchestrator.py       # Action Execution Loop
├── drop_zone/                 # Drag & Drop folder for File Drops
└── .gemini/skills/            # Specialized Agent Skills (Gmail, LinkedIn, FS)
```

## 🛠️ Setup & Installation

### 1. Prerequisites
- Python 3.13+
- Node.js 24+
- Playwright
- Watchdog (for filesystem monitoring)

### 2. Install Dependencies
```powershell
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client playwright watchdog
playwright install chromium
```

### 3. Authentication
- **Gmail**: Place `credentials.json` in `.gemini/skills/gmail-integration/` and run the watcher once.
- **LinkedIn**: Run `python .gemini/skills/browsing-with-playwright/scripts/linkedin-automation.py --login` to save your session.
- **WhatsApp**: Run `python .gemini/skills/whatsapp-integration/scripts/whatsapp_watcher.py --login` and scan the QR code.

## 🏃 Running the AI Employee
To start all watchers and the action loop, run:
```powershell
python orchestrator.py
```

## 🔄 The Workflow
1.  **Incoming**: Check `AI_Employee_Vault/Needs_Action` for new tasks.
2.  **Plan**: Check `AI_Employee_Vault/Plans` to see how the AI intends to solve it.
3.  **Approve**: Review drafts in `Pending_Approval` and move them to `Approved`.
4.  **Confirm**: Watch the `Logs` folder for the successful execution screenshot.

## 📜 Rules of Engagement
See [Company_Handbook.md](AI_Employee_Vault/Company_Handbook.md) for detailed rules and safety thresholds.

---
*Built for the Personal AI Employee Hackathon 0 (2026).*
