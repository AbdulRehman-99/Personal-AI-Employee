import argparse
import time
import os
import re
from playwright.sync_api import sync_playwright
from datetime import datetime

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR))))
VAULT_PATH = os.path.join(PROJECT_ROOT, "AI_Employee_Vault")
NEEDS_ACTION_PATH = os.path.join(VAULT_PATH, "Needs_Action")
USER_DATA_DIR = os.path.join(SCRIPT_DIR, "whatsapp_session")

def setup_directories():
    if not os.path.exists(NEEDS_ACTION_PATH):
        os.makedirs(NEEDS_ACTION_PATH)

def login():
    print(f"DEBUG: Using session path: {USER_DATA_DIR}")
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(USER_DATA_DIR, headless=False)
        page = browser.pages[0]
        page.goto("https://web.whatsapp.com")
        print("Please scan the QR code to log in.")
        print("Press Enter here once you are logged in and the chats are visible.")
        input()
        print("Saving session... (Do not close the browser manually)")
        time.sleep(5)
        browser.close()
        print("Session saved!")

def check_messages():
    setup_directories()
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch_persistent_context(USER_DATA_DIR, headless=True)
            page = browser.pages[0]
            page.goto("https://web.whatsapp.com")
            
            # Wait for the chat list to load
            try:
                page.wait_for_selector('div[aria-label="Chat list"]', timeout=60000)
            except:
                print("Timeout waiting for WhatsApp to load. Ensure you are logged in.")
                return

            print("Checking for unread messages...")
            
            # Look for unread badges
            unread_chats = page.locator('span[aria-label*="unread message"]')
            count = unread_chats.count()
            
            if count > 0:
                print(f"Found {count} chats with unread messages.")
                
                for i in range(count):
                    # Get the chat element
                    badge = unread_chats.nth(i)
                    chat_row = badge.locator("xpath=../../../../..") # Navigate up to the chat row
                    
                    # Click to open chat
                    chat_row.click()
                    time.sleep(2) # Wait for chat to load

                    # Get contact name
                    contact_name = page.locator('header span[title]').first.inner_text()
                    
                    # Get last message
                    messages = page.locator('div[data-testid="msg-container"]')
                    last_message = messages.last.inner_text()
                    
                    # Create a task file
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', contact_name)
                    filename = f"WHATSAPP_{safe_name}_{timestamp}.md"
                    filepath = os.path.join(NEEDS_ACTION_PATH, filename)
                    
                    content = f"""---
type: whatsapp_message
from: {contact_name}
received: {datetime.now().isoformat()}
status: pending
---

## Message Content
{last_message}

## Suggested Actions
- [ ] Reply to {contact_name}
"""
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    print(f"Created task: {filename}")
                    
            else:
                print("No unread messages found.")
                
            browser.close()
            
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WhatsApp Watcher")
    parser.add_argument("--login", action="store_true", help="Launch browser for initial login")
    args = parser.parse_args()

    if args.login:
        login()
    else:
        while True:
            check_messages()
            time.sleep(60) # Check every minute
