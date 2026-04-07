---
name: gemail-integration
description: |
  Integrates Gmail as a core perception and communication channel for the AI Employee. This skill acts as a "Watcher" by monitoring the inbox for new client communications and as an "Action" by drafting and sending emails upon human approval. It supports the standard AI Employee workflow by standardizing email inputs into vault tasks and providing an MCP-compliant server for automated, verified email delivery.
  
---


# Gmail Integration Skill

This skill provides integration with Gmail for monitoring incoming emails and sending emails via the Gmail API. It supports the "Personal AI Employee" architecture by acting as a "Watcher" and an "Action" (MCP-like).

## Capabilities

1.  **Monitor Inbox**: Automatically checks for new unread emails and creates task files in `AI_Employee_Vault/Needs_Action/`.
2.  **Send Emails**: Allows the agent to draft and send emails via CLI command.

## Setup

1.  **Enable Gmail API**:
    *   Go to [Google Cloud Console](https://console.cloud.google.com/).
    *   Create a project and enable the **Gmail API**.
    *   Create **OAuth 2.0 Client IDs** (Desktop App).
    *   Download the `credentials.json` file and place it in this directory: `.gemini/skills/gmail-integration/credentials.json`.

2.  **Install Dependencies**:
    ```bash
    pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
    ```

3.  **Authenticate**:
    *   Run the watcher script once manually to trigger the OAuth flow:
        ```bash
        python .gemini/skills/gmail-integration/scripts/gmail_watcher.py
        ```

## Usage

### As a Watcher (Background Process)
Run the watcher script in the background to monitor for new emails:
```bash
python .gemini/skills/gmail-integration/scripts/gmail_watcher.py
```
This script will:
*   Poll for unread emails every 60 seconds.
*   Create a file in `AI_Employee_Vault/Needs_Action/EMAIL_<id>.md` for each new email.
*   Mark the email as read (optional, check script configuration).

### As an Action (Sending Email via Script)
To send an email directly, use the `send_email.py` script:
```bash
python .gemini/skills/gmail-integration/scripts/send_email.py --to "recipient@example.com" --subject "Subject" --body "Body content"
```

### As an MCP Server (Silver Tier Recommended)
This skill includes an MCP-compliant server for automated actions.

**Server Command:**
```bash
python .gemini/skills/gmail-integration/scripts/gmail_mcp_server.py
```

**Available Tools:**
*   `send_email`: Sends an email using the Gmail API.
    *   `to` (string): Recipient email address.
    *   `subject` (string): Email subject.
    *   `body` (string): Email body content.

The `task_orchestrator.py` automatically uses this MCP server to process approved email tasks.

## Security Note
*   **Credentials**: Never commit `credentials.json` or `token.json` to version control.
*   **Review**: Ensure all emails are reviewed before sending if automated.
