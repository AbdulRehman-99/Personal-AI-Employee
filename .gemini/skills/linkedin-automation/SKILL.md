---
name: linkedin-automation
description: |
  Enables the AI Employee to autonomously manage professional networking by posting updates and engagement on LinkedIn. It uses Playwright for browser automation, supports session persistence for zero-friction execution, and integrates with the AI Employee Vault's approval workflow to ensure all professional communications are human-verified before going live.
---


# LinkedIn Automation Skill

This skill automates posting updates to LinkedIn using Playwright.

## Capabilities
1.  **Post Update**: Automatically logs in (or uses saved session) and posts a text update to your LinkedIn feed.

## Setup

1.  **Install Playwright**:
    ```bash
    pip install playwright
    playwright install chromium
    ```

2.  **Create Session (One-time Setup)**:
    *   Run the script with the `--login` flag to open a browser and log in manually.
    *   The script will save your session cookies to `linkedin_session.json`.
    ```bash
    python .gemini/skills/linkedin-automation/scripts/post_linkedin.py --login
    ```

## Usage

### Posting an Update
To post an update, use the `--text` argument:
```bash
python .gemini/skills/linkedin-automation/scripts/post_linkedin.py --text "This is an automated post from my AI Employee! #AI #Automation"
```

## Security Note
*   **Session File**: The `linkedin_session.json` file contains your session cookies. **Protect this file.** Do not commit it to version control.
*   **Rate Limiting**: Avoid posting too frequently to prevent your account from being flagged.
