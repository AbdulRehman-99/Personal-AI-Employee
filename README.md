# Personal AI Employee: Autonomous Digital FTE

An advanced, autonomous digital employee built on the **Gemini CLI** system. This agent is designed for high-level reasoning, proactive task management, and sophisticated browser automation, operating within a structured "Vault" environment optimized for **Obsidian**.

---

## 🚀 Overview

The **Personal AI Employee** functions as a full-time digital assistant (FTE) that manages its own workspace, monitors incoming tasks via a file-system watcher, and executes complex workflows using specialized skills.

### Key Features
- 📂 **Automated Task Ingestion**: Real-time monitoring of a `drop_zone` folder.
- 🏛️ **Structured Vault Management**: Organized workflow through `Inbox`, `Needs_Action`, and `Done` states.
- 🌐 **Browser Automation**: Full web interaction capabilities via Playwright MCP.
- 📊 **Dynamic Dashboard**: Real-time status tracking in `Dashboard.md`.
- 📝 **Obsidian Integration**: Specialized Markdown logging for seamless visualization.

---

## 🏗️ System Architecture

### Workspace Structure
- **`AI_Employee_Vault/`**: The central command center (Obsidian Vault).
    - `Inbox/`: Landing zone for manual task entry.
    - `Needs_Action/`: Active queue for the AI to process.
    - `Done/`: Permanent archive for completed work.
    - `Logs/`: Detailed activity records (Markdown-formatted for Obsidian).
    - `Company_Handbook.md`: The "Constitution" governing AI behavior.
    - `Dashboard.md`: High-level overview of system status and recent activity.
- **`drop_zone/`**: Hot-folder for external file submissions.
- **`.gemini/skills/`**: Modular capabilities (Vault Management, Playwright).

### Core Components
| Component | Responsibility |
| :--- | :--- |
| `filesystem_watcher.py` | Monitors `drop_zone` and ingests files into the Vault. |
| `vault_audit.py` | Scans the queue and updates the `Dashboard.md`. |
| `task_processor.py` | Handles the transition of tasks from active to completed. |
| `browsing-with-playwright` | Enables web scraping, form submission, and UI navigation. |

---

## 🛠️ Getting Started

### Prerequisites
- Python 3.10+
- Node.js (for Playwright MCP)
- Gemini CLI Environment

### Installation & Setup
1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd Personal-AI-Employee
   ```

2. **Start the File System Watcher**:
   ```bash
   python filesystem_watcher.py
   ```

3. **Open the Vault**:
   Open the `AI_Employee_Vault` folder in **Obsidian** to monitor the AI's progress in real-time via the `Dashboard.md`.

---

## 🔄 Operational Workflows

### 1. Task Submission
- **Auto**: Drop any file into the `drop_zone/`. The system will automatically move it to `Needs_Action` and create a metadata file.
- **Manual**: Place a markdown file directly into `AI_Employee_Vault/Inbox`.

### 2. The Processing Cycle
1. **Audit**: The AI runs `vault_audit.py` to recognize new work.
2. **Execute**: The AI analyzes the task, applies the necessary skills, and generates an output.
3. **Log**: A Markdown log is created in the `Logs/` folder, containing a JSON manifest for technical tracking.
4. **Complete**: `task_processor.py` moves the files to `Done/` and updates the `Dashboard.md`.

---

## ⚖️ Rules of Engagement (Handbook Summary)

The AI Employee operates under a strict ethical and operational framework:
- **Politeness**: All communications must be professional.
- **Financial Safety**: Transactions > $500 require human approval (HITL).
- **Transparency**: Every AI-generated action is clearly labeled.
- **Auditability**: Detailed logs are mandatory for every operation.

---

## 📂 Logs & Visibility
Logs are stored in `AI_Employee_Vault/Logs/` with the `.md` extension. This ensures they are immediately visible in the Obsidian file explorer while maintaining structured data within code blocks for system parsing.

---
*Created by the Personal AI Employee System*
