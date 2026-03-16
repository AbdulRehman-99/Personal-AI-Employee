import argparse
import time
import os
from playwright.sync_api import sync_playwright

SESSION_FILE = os.path.join(os.path.dirname(__file__), '..', 'linkedin_session.json')

# Consistent User Agent to avoid bot detection
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

def login_and_save_session():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()
        
        print("Opening LinkedIn. Please log in manually in the browser window.")
        page.goto("https://www.linkedin.com/login")
        
        # Wait for user to log in and reach the feed
        print("Waiting for login to complete (Feed to load)...")
        try:
            # Wait for 120 seconds or until URL contains feed
            page.wait_for_url("**/feed/**", timeout=120000) 
            print("Login detected. Capturing session...")
            page.wait_for_load_state("networkidle")
            context.storage_state(path=SESSION_FILE)
            print(f"Session saved to {SESSION_FILE}")
        except Exception as e:
            print(f"Login timed out or failed: {e}")
            # Try to save whatever state we have anyway
            context.storage_state(path=SESSION_FILE)
            print(f"Attempted to save current state to {SESSION_FILE}")
        finally:
            browser.close()

def post_update(text):
    if not os.path.exists(SESSION_FILE):
        print(f"Error: Session file not found at {SESSION_FILE}. Run with --login first.")
        return

    with sync_playwright() as p:
        # Set headless=False so you can see what is happening!
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context(
            storage_state=SESSION_FILE,
            user_agent=USER_AGENT
        )
        page = context.new_page()
        
        print(f"Navigating to LinkedIn Feed...")
        try:
            # wait_until='load' is safer for state checks
            page.goto("https://www.linkedin.com/feed/", wait_until="load", timeout=60000)
            print(f"Current Page Title: {page.title()}")
            print(f"Current Page URL: {page.url}")

            # Check if we are actually on the feed or stuck on login/checkpoint
            if "login" in page.url or "checkpoint" in page.url:
                print("CRITICAL: Session expired or Security Check detected.")
                print("Please RE-RUN: python .gemini/skills/linkedin-automation/scripts/post_linkedin.py --login")
                return
            
            # Click "Start a post"
            print("Looking for 'Start a post' button...")
            page.wait_for_timeout(5000) # Wait for JS to attach listeners
            
            # This is the most robust way: Search for the text directly
            post_trigger = page.get_by_text("Start a post", exact=False).first
            
            if not post_trigger or not post_trigger.is_visible():
                print("Primary text search failed. Trying alternative selectors...")
                # Fallback to known classes
                post_trigger = page.locator(".share-box-feed-entry__trigger, button.artdeco-button--muted.tp-1").first

            if post_trigger.is_visible(timeout=10000):
                print("Clicking Start a post...")
                post_trigger.click()
            else:
                page.screenshot(path="linkedin_error.png")
                print("CRITICAL: Could not find 'Start a post' button. See 'linkedin_error.png'.")
                return
                
            # Type the text
            print("Typing post content...")
            editor = page.wait_for_selector("div.ql-editor, div[contenteditable='true']", timeout=10000)
            editor.click()
            editor.fill(text)
            
            # Click Post
            print("Clicking 'Post' button...")
            page.wait_for_timeout(2000)
            # Find the blue Post button
            post_button = page.get_by_role("button", name="Post").first
            
            if post_button.is_visible(timeout=5000):
                post_button.click()
                print("Post submitted successfully!")
            else:
                print("Error: Could not find the 'Post' button.")
            
            time.sleep(5)
            
        except Exception as e:
            print(f"An error occurred: {e}")
            page.screenshot(path="linkedin_crash.png")
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(description='LinkedIn Automation Script')
    parser.add_argument('--login', action='store_true', help='Open browser to login and save session')
    parser.add_argument('--text', help='Text content to post')
    
    args = parser.parse_args()
    
    if args.login:
        login_and_save_session()
    elif args.text:
        post_update(args.text)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
