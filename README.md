# Personal AI Employee - Hackathon 0

This project implements an autonomous AI employee designed to manage tasks, process files, and perform browser automation. It leverages a structured "Vault" system for task management and specialized skills for execution.

## Project Overview

The AI Employee operates as a digital Full-Time Employee (FTE), capable of:
- **Task Management**: Automatically processing files dropped into a designated zone.
- **Vault Organization**: Managing an `AI_Employee_Vault` with `Inbox`, `Needs_Action`, and `Done` folders.
- **Browser Automation**: Using Playwright to navigate, scrape, and interact with web pages.
- **Audit & Logging**: Maintaining a dashboard of tasks and logging all actions for transparency.

## Directory Structure

```
Personal-AI-Employee/
├── AI_Employee_Vault/       # Central storage for the AI's workspace
│   ├── Company_Handbook.md  # Rules of engagement and operational guidelines
│   ├── Dashboard.md         # Real-time status of pending and completed tasks
│   ├── Inbox/               # Incoming files (manual placement)
│   ├── Needs_Action/        # Files requiring processing (auto-moved from drop_zone)
│   ├── Done/                # Completed tasks
│   └── Logs/                # JSON logs of all interactions
├── drop_zone/               # Hot folder for new tasks (watched by system)
├── .gemini/skills/          # Specialized agent capabilities
│   ├── ai-employee-manager/ # Vault management logic
│   └── browsing-with-playwright/ # Browser automation tools
└── filesystem_watcher.py    # Script to monitor drop_zone
```

## Features & Skills

### 1. AI Employee Manager
- **Vault Audit**: Scans `Needs_Action` and updates `Dashboard.md`.
- **Task Processing**: Moves completed files to `Done` and logs the action.
- **File Watcher**: Monitors `drop_zone` for new files and automatically ingests them into the workflow.

### 2. Browsing with Playwright
- **Headless Browsing**: Navigate websites, fill forms, and extract data.
- **UI Testing**: Take screenshots and verify page states.
- **MCP Integration**: Exposes browser control via a Model Context Protocol (MCP) server.

## Getting Started

1.  **Start the Watcher**: Run `python filesystem_watcher.py` to monitor the `drop_zone`.
2.  **Submit a Task**: Drop a text file or markdown file into the `drop_zone` folder.
3.  **Automatic Processing**:
    - The watcher moves the file to `AI_Employee_Vault/Needs_Action`.
    - The agent (or script) audits the vault and updates the dashboard.
    - The agent processes the file based on its content (e.g., summarizing, answering questions).
    - The file is moved to `AI_Employee_Vault/Done` upon completion.

## Rules of Engagement

Refer to `AI_Employee_Vault/Company_Handbook.md` for detailed operational rules, including:
- **Approvals**: Payments > $500 require human approval.
- **Privacy**: Sensitive data handling protocols.
- **Transparency**: All AI actions are logged.
