import argparse
import time
import os
import re
import shutil
from playwright.sync_api import sync_playwright
from datetime import datetime

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..', '..'))
VAULT_PATH = os.path.join(PROJECT_ROOT, "AI_Employee_Vault")
LOGS_PATH = os.path.join(VAULT_PATH, "Logs")
NEEDS_ACTION_PATH = os.path.join(VAULT_PATH, "Needs_Action")
USER_DATA_DIR = os.path.join(SCRIPT_DIR, "whatsapp_session")

def setup_directories():
    for p in [NEEDS_ACTION_PATH, LOGS_PATH]:
        if not os.path.exists(p):
            os.makedirs(p)

def cleanup_session_locks():
    lock_files = ["SingletonLock", "LOCK", "SingletonCookie"]
    for root, dirs, files in os.walk(USER_DATA_DIR):
        for file in files:
            if any(lock in file for lock in lock_files):
                try:
                    os.remove(os.path.join(root, file))
                except:
                    pass

def is_duplicate_task(contact_name):
    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', contact_name)[:50]
    pattern = f"WHATSAPP_{safe_name}_"
    for filename in os.listdir(NEEDS_ACTION_PATH):
        if filename.startswith(pattern):
            return True
    return False

def check_messages(headless=True):
    setup_directories()
    cleanup_session_locks()
    
    with sync_playwright() as p:
        browser = None
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking WhatsApp (Headless: {headless})...")
            browser = p.chromium.launch_persistent_context(
                USER_DATA_DIR, 
                headless=headless, 
                channel="chrome",
                args=["--no-sandbox", "--disable-setuid-sandbox"],
                viewport={'width': 1280, 'height': 800} # FIXED RESOLUTION
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto("https://web.whatsapp.com", wait_until="load", timeout=90000)
            
            try:
                page.wait_for_function("document.title.includes('WhatsApp')", timeout=60000)
            except:
                print("Timeout: Page title didn't update.")
                return

            print("Waiting for WhatsApp to initialize...")
            
            # Wait for either the chat list or the QR code
            try:
                page.wait_for_selector("#pane-side, canvas[aria-label='Scan me!']", timeout=60000)
            except:
                print("Timeout: Neither chat list nor QR code appeared.")
                return

            if page.locator("canvas[aria-label='Scan me!']").count() > 0:
                print("!!! ACTION REQUIRED: WhatsApp is asking for a QR code login.")
                print("Please run the watcher with the --login flag to authenticate.")
                return

            print("WhatsApp loaded. Waiting for chats to render...")
            page.wait_for_selector("#pane-side", timeout=30000)
            time.sleep(5) # Final buffer for messages to sync

            # COORDINATE STRATEGY (1280x800)
            # Side pane is roughly left 30% of screen.
            # First chat starts around Y=180 (below header/search)
            # Each chat is approx 72px high.
            
            print("Executing Coordinate Clicks...")
            start_y = 180
            chat_height = 72
            x_pos = 200 # Middle of side pane
            
            for i in range(5): # Check top 5 chats
                y_pos = start_y + (i * chat_height)
                
                print(f"[{i+1}] Clicking at ({x_pos}, {y_pos})...")
                page.mouse.click(x_pos, y_pos)
                time.sleep(3) # Wait for load
                
                # EXTRACT INFO
                try:
                    # Header
                    header_selectors = ['header span[title]', '#main header span[title]']
                    contact_name = "Unknown"
                    for selector in header_selectors:
                        if page.locator(selector).first.count() > 0:
                            contact_name = page.locator(selector).first.get_attribute('title')
                            break
                    
                    if contact_name == "Unknown":
                        print("    Failed to read name. Skipping.")
                        continue

                    # Message
                    messages = page.locator('div.message-in')
                    if messages.count() > 0:
                        last_msg = messages.last
                        text_elem = last_msg.locator('.copyable-text').first
                        message_text = text_elem.inner_text().strip() if text_elem.count() > 0 else last_msg.inner_text().strip()
                    else:
                        message_text = ""

                    # SAVE
                    if message_text and not is_duplicate_task(contact_name):
                        print(f"    Processing: {contact_name}")
                        print(f"    Msg: {message_text[:60]}...")
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', contact_name)[:50]
                        filename = f"WHATSAPP_{safe_name}_{timestamp}.md"
                        
                        with open(os.path.join(NEEDS_ACTION_PATH, filename), "w", encoding="utf-8") as f:
                            f.write(f"---\ntype: whatsapp_message\nfrom: {contact_name}\nreceived: {datetime.now().isoformat()}\nstatus: pending\n---\n\n{message_text}")
                        print(f"    Saved: {filename}")
                    elif is_duplicate_task(contact_name):
                        print(f"    Skipping: Already processed {contact_name}")

                except Exception as inner_e:
                    print(f"    Error reading chat: {inner_e}")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            if browser:
                browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WhatsApp Watcher")
    parser.add_argument("--headless", action="store_true", default=False, help="Run in headless mode")
    parser.add_argument("--login", action="store_true", help="Login mode (stay open)")
    args = parser.parse_args()

    if args.login:
        print("Login mode activated. Opening browser...")
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                USER_DATA_DIR, 
                headless=False, 
                channel="chrome",
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto("https://web.whatsapp.com")
            print("Please log in and wait for chats to load. Close the window when done.")
            page.wait_for_timeout(300000) # 5 mins
            browser.close()
        exit()

    print(f"Starting WhatsApp Watcher (Headless: {args.headless})...")
    while True:
        check_messages(headless=args.headless)
        print("Waiting 60s...")
        time.sleep(60)
