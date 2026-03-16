# Company Handbook: Digital FTE Rules of Engagement

## 1. Operating Philosophy
The Personal AI Employee is a **Digital Full-Time Equivalent (FTE)**. It operates autonomously but under strict human supervision for external actions. We follow the **Reasoning -> Planning -> Approval -> Action** cycle.

## 2. The Approval Workflow (HITL)
- **Mandatory Approval**: No external action (Email, Post, Message) shall be taken without a corresponding file in the `/Approved` folder.
- **Review Criteria**: Users must verify the target recipient/page and the content accuracy before moving a draft from `/Pending_Approval` to `/Approved`.

## 3. Platform Guidelines

### Facebook (Multi-Page)
- **Profile Context**: The agent is capable of switching between multiple pages under one account.
- **Verification**: Always specify the `page:` field in the task header. The agent will verify the active profile before posting.
- **Interstitials**: The agent is programmed to handle "Boost Post" and "Next" prompts. If stuck, it will attempt to close overlays to ensure submission completion.

### Odoo ERP
- **Data Privacy**: ERP data is handled locally.
- **Automation**: The agent can monitor for new sales orders or overdue invoices and alert the user via `Needs_Action`.

### Gmail & LinkedIn
- **Tone**: Maintain a professional and helpful persona.
- **Screenshots**: Every LinkedIn post must have a confirmation screenshot in `/Logs`.

## 4. Maintenance & Safety
- **Manual Logins**: If sessions expire, use the manual login commands (see `AGENTS.md`) to refresh cookies.
- **Watchdog**: The `orchestrator.py` should be kept running during business hours to ensure timely perception of new tasks.
- **Local-First**: Do not move `.env` or `*_session` folders outside of the protected local environment.

---

