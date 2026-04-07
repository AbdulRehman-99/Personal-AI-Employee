import argparse
import time
import os
from playwright.sync_api import sync_playwright

SESSION_FILE = os.path.join(os.path.dirname(__file__), '..', 'linkedin_session.json')
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

def login_and_save_session():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()
        print("Opening LinkedIn. Please log in manually.")
        page.goto("https://www.linkedin.com/login")
        page.wait_for_url("**/feed/**", timeout=0) 
        page.wait_for_load_state("networkidle")
        context.storage_state(path=SESSION_FILE)
        print(f"Session saved to {SESSION_FILE}")
        browser.close()

def post_update(text, output_screenshot="post_final_confirmation.png"):
    if not os.path.exists(SESSION_FILE):
        print(f"Error: Session file not found at {SESSION_FILE}. Run with --login first.")
        return

    with sync_playwright() as p:
        # VISIBLE MODE
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context(storage_state=SESSION_FILE, user_agent=USER_AGENT)
        page = context.new_page()
        
        print("Navigating to LinkedIn Feed...")
        try:
            page.goto("https://www.linkedin.com/feed/", wait_until="load", timeout=60000)
            time.sleep(5) # Let dynamic content load

            if "login" in page.url or "checkpoint" in page.url:
                print("CRITICAL: Session expired. Please re-run --login.")
                return
            
            # 1. Click "Start a post"
            print("Opening post dialog...")
            post_trigger = page.get_by_text("Start a post", exact=False).first
            if not post_trigger.is_visible():
                post_trigger = page.locator(".share-box-feed-entry__trigger").first
            
            post_trigger.click()
            page.screenshot(path="linkedin_step1_dialog.png")
            
            # 2. Type text
            print("Typing content...")
            editor = page.wait_for_selector("div[role='textbox'], .ql-editor", timeout=30000)
            editor.click()
            editor.fill(text)
            time.sleep(2)
            page.screenshot(path="linkedin_step2_typed.png")
            
            # 3. Submit Post
            print("Submitting post via Keyboard Shortcut (Ctrl+Enter)...")
            page.keyboard.press("Control+Enter")
            
            # Explicit click fallback
            try:
                print("Checking for explicit 'Post' button...")
                post_button = page.locator("button.share-actions__primary-action, .share-box_actions button.artdeco-button--primary").first
                if post_button.is_visible(timeout=5000):
                    print("Clicking Post button explicitly...")
                    post_button.click()
            except Exception as e:
                print(f"Post button click failed (may have already submitted): {e}")
            
            print("Waiting 10 seconds for confirmation...")
            time.sleep(10)
            page.screenshot(path=output_screenshot)
            print(f"Success! Screenshot saved to {output_screenshot}")
            print("Post submitted successfully!")
            
        except Exception as e:
            print(f"Failure: {e}")
            page.screenshot(path="linkedin_crash.png")
        finally:
            browser.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--login', action='store_true')
    parser.add_argument('--text')
    parser.add_argument('--output', default="post_final_confirmation.png")
    args = parser.parse_args()
    if args.login: login_and_save_session()
    elif args.text: post_update(args.text, args.output)

if __name__ == '__main__': main()
