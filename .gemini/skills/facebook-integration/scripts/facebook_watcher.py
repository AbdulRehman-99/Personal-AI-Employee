import sys
import os
import time
import argparse
from playwright.sync_api import sync_playwright
from datetime import datetime

# Configuration
CHECK_INTERVAL = 300 # 5 minutes
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'AI_Employee_Vault'))
NEEDS_ACTION_DIR = os.path.join(BASE_DIR, 'Needs_Action')
# Ensure absolute path for session
SESSION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'facebook_session'))

def login():
    print("Starting Facebook Login Session...")
    with sync_playwright() as p:
        # Launch persistent context
        browser = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False, # Must be visible for login
            channel="chrome" # Use installed chrome if available, or just chromium
        )
        page = browser.new_page()
        page.goto("https://www.facebook.com")
        print("Please log in to Facebook in the browser window.")
        print("Once logged in, press Enter here to save and exit...")
        input()
        browser.close()
        print("Session saved.")

def check_notifications():
    if not os.path.exists(SESSION_DIR):
        print("Error: Session not found. Run with --login first.")
        return

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=SESSION_DIR,
                headless=True
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            # Go to notifications directly
            page.goto("https://www.facebook.com/notifications")
            page.wait_for_load_state("networkidle")

            # Check for unread notifications (very rough selector, FB changes classes often)
            # Look for aria-label="New notifications" or similar indicators
            # Strategy: Get text of first few notifications
            
            # This is a heuristic. In a real scenario, we'd use robust selectors.
            # Let's try to grab notification items.
            # Facebook often uses role="article" or aria-label for notifications.
            
            notifications = page.get_by_role("link", name="unread").all()
            
            # If explicit "unread" not found, just grab the first 3 items text to see if they are interesting
            # Using a more generic selector for notification cards
            # Simplified for hackathon: Check for specific keywords in visible text
            
            content = page.content()
            
            # Simple keyword check in page content for demo purposes if selectors fail
            keywords = ["commented on your photo", "mentioned you", "sent you a request"]
            found_items = []
            
            # Try to find specific notification elements (often have data-visualcompletion)
            # We will just scrape the text of the notification area
            
            # Fallback: Check page title for (1) etc
            title = page.title()
            if "(" in title and ")" in title:
                print(f"New notifications detected in title: {title}")
                # Create a generic alert
                create_alert("New Facebook Notifications", f"Title: {title}. Please check Facebook.")
            
            browser.close()

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
        
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Created alert: {filename}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", action="store_true", help="Run in login mode")
    args = parser.parse_args()

    if args.login:
        login()
    else:
        print("Starting Facebook Watcher...")
        while True:
            check_notifications()
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
