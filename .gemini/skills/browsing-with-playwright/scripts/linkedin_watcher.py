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
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=SESSION_FILE)
            page = context.new_page()
            
            print("Checking LinkedIn messages...")
            page.goto("https://www.linkedin.com/messaging/")
            
            # Wait for message list - increased timeout
            page.wait_for_selector(".msg-conversation-listitem", timeout=30000)
            
            # Check for unread conversations
            unread_selector = ".msg-conversation-card__unread-count" 
            # Note: Selectors change often on LinkedIn. This is a best-effort attempt.
            # A more robust way is to look for the "unread" class on the list item container
            
            unread_items = page.query_selector_all(".msg-conversation-listitem--unread")
            
            if not unread_items:
                print("No unread messages found.")
            else:
                print(f"Found {len(unread_items)} unread conversations.")
                
                for item in unread_items:
                    # Click to open conversation and get text
                    item.click()
                    time.sleep(2) # Wait for load
                    
                    # Get sender name
                    sender_el = page.query_selector(".msg-entity-lockup__content-title")
                    sender = sender_el.inner_text() if sender_el else "Unknown Sender"
                    
                    # Get last message
                    msgs = page.query_selector_all(".msg-s-event-listitem__body")
                    last_msg = msgs[-1].inner_text() if msgs else "No content"
                    
                    create_task_file(vault_path, sender, last_msg)
                    
                    # Ideally, we mark as read by clicking away or it happens automatically
            
            browser.close()
            
        except Exception as e:
            print(f"Error checking LinkedIn: {e}")

def main():
    # Assuming vault path is relative to script location
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'AI_Employee_Vault'))
    
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
