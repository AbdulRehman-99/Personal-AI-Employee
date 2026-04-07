---
name: facebook-integration
description: |
  Empowers the AI Employee with robust Facebook automation and monitoring capabilities. Using Playwright-driven browser interaction, this skill handles multi-page profile switching, monitors notifications for urgent events, and executes complex post compositions (including media support) from the AI Employee Vault's approved queue. It ensures professional social presence with a strictly local-first, human-in-the-loop security model.
 
---


# Facebook Integration Skill

## Overview
This skill provides Facebook automation using Playwright.
Capabilities:
- **Watcher**: Monitors notifications and messages.
- **Action**: Posts updates to your profile/page.
- **Reporting**: Summarizes activity.

## Prerequisites
1. **Playwright**: Must be installed (`pip install playwright`).
2. **Facebook Account**: You need to log in manually once to save the session state.

## Setup
1. Run the login script (it will open a browser):
   ```bash
   python .gemini/skills/facebook-integration/scripts/facebook_watcher.py --login
   ```
2. Log in to Facebook and check "Remember me".
3. Close the browser. The session will be saved to `scripts/facebook_session`.

## Watcher
- `facebook_watcher.py`: Checks for new notifications every 5 minutes. Creates tasks in `/Needs_Action` if urgent keywords found.

## Action
- `post_facebook.py`: Posts status updates. Triggered via `type: facebook_post` tasks in `/Approved`.
