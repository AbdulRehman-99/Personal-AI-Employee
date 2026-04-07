import sys
import os
import time
import argparse
import shutil
from playwright.sync_api import sync_playwright
from datetime import datetime

# Configuration
CHECK_INTERVAL = 300 # 5 minutes
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR = os.path.join(SCRIPT_DIR, 'facebook_session')
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..', '..', 'AI_Employee_Vault'))
INBOX_DIR = os.path.join(BASE_DIR, 'Inbox')
NEEDS_ACTION_DIR = os.path.join(BASE_DIR, 'Needs_Action')

def ingest_from_inbox():
    """Checks Inbox for Facebook tasks and moves them to Needs_Action."""
    if not os.path.exists(INBOX_DIR):
        print(f"Warning: Inbox directory not found at {INBOX_DIR}")
        return

    print(f"Checking {INBOX_DIR} for Facebook tasks...")
    for filename in os.listdir(INBOX_DIR):
        if filename.endswith(".md"):
            filepath = os.path.join(INBOX_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().lower()

                # If the file mentions facebook, ingest it
                if "facebook" in content or "fb" in content:
                    print(f"Ingesting Facebook task: {filename}")
                    dest_path = os.path.join(NEEDS_ACTION_DIR, f"FB_TASK_{filename}")

                    # Ensure directory exists
                    if not os.path.exists(NEEDS_ACTION_DIR):
                        os.makedirs(NEEDS_ACTION_DIR)

                    shutil.move(filepath, dest_path)
                    print(f"Moved {filename} to Needs_Action as {os.path.basename(dest_path)}")
            except Exception as e:
                print(f"Error ingesting {filename}: {e}")

def login():
    """Runs a visible browser to allow manual login and save session."""
    print("Launching browser for login...")
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            channel="chrome",
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-infobars"]
        )
        page = browser.new_page()
        page.goto("https://www.facebook.com")
        print("Please log in to Facebook in the browser window.")
        print("Once logged in and your feed is visible, press Enter here to save and exit...")
        input()
        browser.close()
        print(f"Session saved to {SESSION_DIR}")

def check_notifications():
    """Checks Facebook notifications in visible mode as requested by user."""
    if not os.path.exists(SESSION_DIR):
        print("Error: Session not found. Run with --login first.")
        return

    print("Launching watcher to check notifications...")
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=SESSION_DIR,
                headless=False, # Visible mode as requested
                channel="chrome",
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-infobars"]
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            # Go to notifications directly
            print("Navigating to Facebook notifications...")
            page.goto("https://www.facebook.com/notifications", wait_until="networkidle", timeout=60000)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(20) # Extra time for dynamic content and title to stabilize

            # Check for unread notifications via page title
            try:
                title = page.title()
                print(f"Current page title: {title}")
                if "(" in title and ")" in title:
                    print(f"New notifications detected in title: {title}")
                    create_alert("New Facebook Notifications", f"Title: {title}. Please check Facebook for updates.")
            except Exception as e:
                print(f"Title check skipped: {e}")
            
            # Check for specific unread elements
            try:
                # This is a generic check for unread notification highlights
                unread_elements = page.locator("div[aria-label*='unread'], div[aria-label*='Unread']")
                unread_count = unread_elements.count()
                if unread_count > 0:
                    print(f"Found {unread_count} potential unread notification elements.")
                    create_alert("Unread Notifications Detected", f"Found {unread_count} unread items on the notifications page.")
            except Exception as e:
                print(f"Optional element check skipped: {e}")
            
            time.sleep(5) # Let user see the page before closing
            browser.close()
            print("Watcher check complete.")

        except Exception as e:
            print(f"Error checking Facebook: {e}")

def create_alert(title, details):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"FACEBOOK_ALERT_{timestamp}.md"
    filepath = os.path.join(NEEDS_ACTION_DIR, filename)
    
    content = f"""---
type: facebook_alert
priority: medium
status: pending
created: {datetime.now().isoformat()}
---

## {title}
{details}

### Actions
- [ ] Check Facebook
- [ ] Reply if necessary
"""
    if not os.path.exists(NEEDS_ACTION_DIR):
        os.makedirs(NEEDS_ACTION_DIR)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created alert: {filename}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", action="store_true", help="Run in login mode")
    args = parser.parse_args()

    if args.login:
        login()
    else:
        print("Starting Facebook Watcher (Visible Mode)...")
        while True:
            ingest_from_inbox()
            check_notifications()
            print(f"Sleeping for {CHECK_INTERVAL} seconds...")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
