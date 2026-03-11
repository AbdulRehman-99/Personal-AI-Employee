---
name: whatsapp-integration
description: |
  Integration with WhatsApp Web for monitoring messages and sending replies.
  Use this skill to check for new WhatsApp messages or send a WhatsApp message to a contact.
  It relies on a local Playwright session for authentication.
---

# WhatsApp Integration

This skill allows the agent to interact with WhatsApp Web.

## Capabilities
1.  **Monitor Messages**: Watch for unread messages and create task files in `AI_Employee_Vault/Needs_Action/`.
2.  **Send Message**: Send a text message to a specific contact or phone number.

## Setup
1.  **Login**: Run the watcher with the `--login` flag to authenticate manually via QR code.
    ```bash
    python .gemini/skills/whatsapp-integration/scripts/whatsapp_watcher.py --login
    ```

## Usage

### Watcher
Run the watcher to monitor for messages:
```bash
python .gemini/skills/whatsapp-integration/scripts/whatsapp_watcher.py
```

### Sending Messages
Send a message to a contact:
```bash
python .gemini/skills/whatsapp-integration/scripts/send_message.py --contact "Contact Name" --message "Hello world"
```
