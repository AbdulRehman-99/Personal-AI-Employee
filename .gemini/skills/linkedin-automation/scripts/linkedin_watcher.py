import os
import time
import argparse
import sys
from playwright.sync_api import sync_playwright

# Use the same session file location or relative to this skill
SESSION_FILE = os.path.join(os.path.dirname(__file__), '..', 'linkedin_session.json')
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

def create_task_file(vault_path, sender_name, message_text):
    safe_sender = "".join(c for c in sender_name if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
    timestamp = int(time.time())
    filename = f"LINKEDIN_MSG_{safe_sender}_{timestamp}.md"
    filepath = os.path.join(vault_path, 'Needs_Action', filename)
    
    content = f"""---
type: linkedin_message
from: {sender_name}
timestamp: {timestamp}
status: new
---

# Message Content
{message_text}

# Instructions
- [ ] Read and summarize
- [ ] Draft a reply if necessary
"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created task: {filepath}")
        return True
    except Exception as e:
        print(f"Error creating task file: {e}")
        return False

def check_messages(vault_path):
    if not os.path.exists(SESSION_FILE):
        print(f"Error: Session file not found at {SESSION_FILE}. Run post_linkedin.py --login first.")
        return

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(storage_state=SESSION_FILE, user_agent=USER_AGENT)
            page = context.new_page()
            
            # --- PHASE 1: MESSAGING ---
            print("Checking LinkedIn messaging...")
            page.goto("https://www.linkedin.com/messaging/", wait_until="load", timeout=60000)
            time.sleep(5)
            
            if "login" in page.url:
                print("CRITICAL: Session expired. Please re-run login command.")
                browser.close()
                return

            # Capture state for debugging
            debug_msg_path = os.path.join(vault_path, "Logs", "LINKEDIN_MESSAGING_DEBUG.png")
            page.screenshot(path=debug_msg_path)
            
            # Broader unread selectors
            unread_selectors = [
                ".msg-conversation-card--unread",
                ".msg-conversation-listitem--unread",
                ".msg-conversations-container__convo-item--unread",
                "span.notification-badge--show" # Badge indicator
            ]
            
            unread_items = []
            for selector in unread_selectors:
                items = page.query_selector_all(selector)
                if items:
                    unread_items.extend(items)
                    print(f"Found {len(items)} items with selector: {selector}")

            if not unread_items:
                print("No unread messages found in Messaging tab.")
            else:
                print(f"Processing {len(unread_items)} unread conversations...")
                for item in unread_items:
                    try:
                        item.click()
                        time.sleep(3)
                        
                        sender_el = page.query_selector(".msg-entity-lockup__content-title, h2.msg-entity-lockup__content-title")
                        sender = sender_el.inner_text().strip() if sender_el else "Unknown Sender"
                        
                        msgs = page.query_selector_all(".msg-s-event-listitem__body")
                        last_msg = msgs[-1].inner_text().strip() if msgs else "No content extracted"
                        
                        create_task_file(vault_path, sender, last_msg)
                    except Exception as inner_e:
                        print(f"Error reading specific message: {inner_e}")

            # --- PHASE 2: NOTIFICATIONS ---
            print("Checking LinkedIn notifications...")
            page.goto("https://www.linkedin.com/notifications/", wait_until="load", timeout=60000)
            time.sleep(5)
            
            debug_notif_path = os.path.join(vault_path, "Logs", "LINKEDIN_NOTIFICATIONS_DEBUG.png")
            page.screenshot(path=debug_notif_path)
            
            # Look for message-related notifications
            notif_items = page.query_selector_all(".nt-card")
            for notif in notif_items:
                text = notif.inner_text().lower()
                if "sent you a message" in text or "messaged you" in text:
                    print(f"Found message notification: {text[:50]}...")
                    # We usually prefer to handle actual messages in the Messaging phase, 
                    # but this confirms we are seeing them.
            
            time.sleep(2)
            browser.close()
            
        except Exception as e:
            print(f"Error checking LinkedIn: {e}")

def main():
    # Correct path calculation: script is in .gemini/skills/linkedin-automation/scripts/
    # Need to go up 4 levels to reach the project root.
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'AI_Employee_Vault'))
    
    if not os.path.exists(base_dir):
        print(f"Error: Vault directory not found at {base_dir}")
        return

    while True:
        check_messages(base_dir)
        # Sleep for 5 minutes to avoid rate limits
        print("Sleeping for 5 minutes...")
        time.sleep(300)

if __name__ == '__main__':
    main()
