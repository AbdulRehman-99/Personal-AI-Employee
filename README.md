# Personal AI Employee (Silver Tier)

Welcome to your Autonomous Digital FTE. This project transforms Gemini CLI from a simple chatbot into a proactive employee that manages your Gmail, LinkedIn, and files local-first.

## 🚀 Silver Tier Features
- **Proactive Watchers**: Monitors Gmail and LinkedIn every 5 minutes automatically.
- **Action Loop**: Executes approved posts and emails while you sleep.
- **Reasoning First**: Always creates a `Plan.md` before taking action.
- **Audit Trails**: Every action is logged with a timestamped screenshot in the `Vault/Logs`.

## 📂 Project Structure
```text
├── AI_Employee_Vault/         # The GUI & Memory (Obsidian)
│   ├── Needs_Action/          # Incoming Tasks
│   ├── Plans/                 # AI Reasoning Files
│   ├── Pending_Approval/      # Staging for your Review
│   ├── Approved/              # Trigger for Action Loop
│   ├── Done/                  # Completed Archive
│   └── Logs/                  # Action Screenshots
├── orchestrator.py            # The "Master On" Switch
├── task_orchestrator.py       # The "Hands" (Action Loop)
└── .gemini/skills/            # Modular Agent Skills
```

## 🛠️ Setup & Installation

### 1. Prerequisites
- Python 3.13+
- Node.js 24+
- Playwright

### 2. Install Dependencies
```powershell
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client playwright
playwright install chromium
```

### 3. Authentication
- **Gmail**: Place `credentials.json` in `.gemini/skills/gmail-integration/` and run the watcher once.
- **LinkedIn**: Run `python .gemini/skills/browsing-with-playwright/scripts/linkedin-automation.py --login` to save your session.

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
