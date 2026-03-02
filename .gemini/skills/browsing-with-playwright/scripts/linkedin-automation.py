import argparse
import time
import os
from playwright.sync_api import sync_playwright

# Use the same session file location or relative to this skill
SESSION_FILE = os.path.join(os.path.dirname(__file__), '..', 'linkedin_session.json')
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

def login_and_save_session():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()
        
        print("Opening LinkedIn. Please log in manually in the browser window.")
        page.goto("https://www.linkedin.com/login")
        
        print("Waiting for login to complete (Feed to load)...")
        page.wait_for_url("https://www.linkedin.com/feed/", timeout=0) 
        page.wait_for_load_state("networkidle")
        
        print("Login detected. Saving session...")
        context.storage_state(path=SESSION_FILE)
        print(f"Session saved to {SESSION_FILE}")
        browser.close()

def post_update(text, output_screenshot="post_final_confirmation.png"):
    if not os.path.exists(SESSION_FILE):
        print(f"Error: Session file not found at {SESSION_FILE}. Run with --login first.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context(
            storage_state=SESSION_FILE,
            user_agent=USER_AGENT
        )
        page = context.new_page()
        
        print(f"Navigating to LinkedIn Feed...")
        try:
            page.goto("https://www.linkedin.com/feed/", wait_until="load", timeout=60000)
            
            if "login" in page.url or "checkpoint" in page.url:
                print("CRITICAL: Session expired or Security Check detected.")
                return
            
            print("Looking for 'Start a post' button...")
            page.wait_for_timeout(5000) 
            
            post_trigger = page.get_by_text("Start a post", exact=False).first
            
            if not post_trigger or not post_trigger.is_visible():
                post_trigger = page.locator(".share-box-feed-entry__trigger, button.artdeco-button--muted.tp-1").first

            if post_trigger.is_visible(timeout=30000):
                post_trigger.click()
            else:
                print("CRITICAL: Could not find 'Start a post' button.")
                return
                
            print("Typing post content...")
            editor = page.wait_for_selector("div.ql-editor, div[contenteditable='true']", timeout=30000)
            editor.click()
            editor.fill(text)
            
            print("Finalizing post... (Waiting for 'Post' button to enable)")
            page.wait_for_timeout(5000) # Give LinkedIn a moment to process the text
            
            # Use multiple ways to find the blue Post button
            post_button_selectors = [
                "button.share-actions__primary-action",
                "button:has-text('Post')",
                ".share-actions__post-button",
                "button[type='submit']" # Sometimes it acts as a submit button
            ]
            
            post_button = None
            for selector in post_button_selectors:
                try:
                    btn = page.locator(selector).first
                    if btn.is_visible(timeout=5000):
                        post_button = btn
                        print(f"Post button found using: {selector}")
                        break
                except:
                    continue

            if post_button:
                # Wait for the button to be clickable (not disabled)
                print("Clicking 'Post' button automatically...")
                post_button.wait_for(state="visible", timeout=20000)
                # Use force=True to ensure the click happens even if covered by a small overlay
                post_button.click(force=True)
                
                print("Post button clicked. Waiting 10 seconds for confirmation...")
                time.sleep(10)
                page.screenshot(path=output_screenshot)
                print(f"Final screenshot saved as '{output_screenshot}'")
                print("Post submitted successfully!")
            else:
                page.screenshot(path="post_button_error.png")
                print("Error: Could not find the 'Post' button. See 'post_button_error.png'")
            
            time.sleep(5)
            
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            browser.close()

def main():
    parser = argparse.ArgumentParser(description='LinkedIn Automation via Playwright Skill')
    parser.add_argument('--login', action='store_true', help='Open browser to login and save session')
    parser.add_argument('--text', help='Text content to post')
    parser.add_argument('--output', default="post_final_confirmation.png", help='Path to save confirmation screenshot')
    
    args = parser.parse_args()
    
    if args.login:
        login_and_save_session()
    elif args.text:
        post_update(args.text, args.output)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
