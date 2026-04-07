import argparse
import os
import time
from playwright.sync_api import sync_playwright

# --- CONFIGURATION ---
# Absolute path to store your login session
SESSION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'facebook_session'))
STORAGE_STATE = os.path.join(SESSION_DIR, 'storage_state.json')

def switch_profile(page, target_profile_name):
    """
    Switches the current Facebook context to the specified Page/Profile.
    """
    # Clean up quotes if passed in
    target_profile_name = target_profile_name.strip("\"'")
    print(f"Attempting to switch profile to: {target_profile_name}")
    
    try:
        # Check if we are already on the correct profile (look at top right or nav)
        account_selectors = [
            f"div[role='button'][aria-label*='{target_profile_name}']",
            f"div[role='button'][aria-label='Your profile']",
            f"div[role='button'][aria-label='Account']",
            "img[alt*='profile picture']"
        ]
        
        # Quick check: Is the name already visible in a profile link?
        if page.locator(f"a[role='link'] span:has-text('{target_profile_name}')").first.is_visible(timeout=2000):
            print(f"Target profile '{target_profile_name}' seems to be already active (found in link).")
            return True

        account_btn = None
        for sel in account_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=3000):
                    label = btn.get_attribute("aria-label") or ""
                    if target_profile_name.lower() in label.lower():
                        print(f"Target profile '{target_profile_name}' is already active (found in button label: '{label}').")
                        return True
                    account_btn = btn
                    print(f"Found Account button with: {sel}")
                    break
            except:
                continue
        
        if account_btn:
            account_btn.click()
            time.sleep(3)
        else:
            print("Error: Could not find Account menu button.")
            return False

        # 2. Check if the name is in the opened menu (as active)
        if page.locator(f"div[role='link'] span:has-text('{target_profile_name}')").first.is_visible():
            print(f"Target profile '{target_profile_name}' is already active (confirmed in menu).")
            account_btn.click() # Close menu
            return True

        # 3. Click "See all profiles" or Target directly
        target_direct = page.locator(f"div[role='button']:has-text('{target_profile_name}')").first
        if target_direct.is_visible():
            print(f"Found profile '{target_profile_name}' in initial menu. Switching...")
            target_direct.click()
        else:
            see_all = page.locator("span:has-text('See all profiles')").first
            if see_all.is_visible():
                see_all.click()
                time.sleep(3)
                target_option = page.locator(f"div[role='button'] span:has-text('{target_profile_name}')").first
                if not target_option.is_visible():
                    target_option = page.locator(f"div[role='button']:has-text('{target_profile_name}')").first
                
                if target_option.is_visible():
                    print(f"Found profile '{target_profile_name}' in list. Switching...")
                    target_option.click()
                else:
                    print(f"Error: Could not find profile '{target_profile_name}' in list.")
                    return False
            else:
                print("Error: Could not find 'See all profiles' or direct switch.")
                return False

        # 4. Wait for Switch/Reload
        try:
            page.wait_for_load_state("domcontentloaded", timeout=15000)
        except:
            pass
        print("Waiting 10 seconds for profile switch to settle...")
        time.sleep(10) 
        return True

    except Exception as e:
        print(f"Profile switch failed: {e}")
        return False

def run_home_post(text, url=None, page_name=None, screenshot_path=None, headless=True):
    """
    Directly posts to the Facebook Home Page or a specified Page URL.
    """
    with sync_playwright() as p:
        print(f"Launching browser (Session: {SESSION_DIR})")
        
        launch_args = {
            "user_data_dir": SESSION_DIR,
            "headless": headless,
            "channel": "chrome",
            "slow_mo": 500,
            "args": ["--disable-blink-features=AutomationControlled"]
        }
        
        if os.path.exists(STORAGE_STATE):
            print(f"Loading storage state from {STORAGE_STATE}")
            launch_args["storage_state"] = STORAGE_STATE

        try:
            context = p.chromium.launch_persistent_context(**launch_args)
        except Exception as e:
            print(f"Error: Ensure all other Chrome windows are closed. {e}")
            return

        page = context.pages[0] if context.pages else context.new_page()
        page.set_default_timeout(60000)

        try:
            print("Navigating to Facebook...")
            page.goto("https://www.facebook.com", wait_until="domcontentloaded")
            time.sleep(5)

            if "login" in page.url or page.get_by_test_id("royal_login_button").is_visible():
                print("[!] NOT LOGGED IN.")
                context.close()
                return

            if page_name:
                if not switch_profile(page, page_name):
                    print("Aborting post due to switch failure.")
                    context.close()
                    return

            # Post Detection
            print("Locating post field...")
            
            textbox_selector = "div[role='dialog'] div[role='textbox']"
            if page.locator(textbox_selector).first.is_visible():
                print("Post dialog already open.")
            else:
                post_selectors = [
                    "div[role='button'] span:has-text(\"What's on your mind\")",
                    "div[role='button'] span:has-text(\"Write something\")",
                    "div[role='button'] span:has-text(\"Create post\")",
                    "text=What's on your mind",
                    "text=Write something...",
                    "text=Create post",
                    "text=Write a post"
                ]
                
                trigger = None
                for sel in post_selectors:
                    try:
                        btn = page.locator(sel).first
                        if btn.is_visible(timeout=3000):
                            trigger = btn
                            print(f"Found trigger: {sel}")
                            break
                    except: continue

                if trigger:
                    print(f"Clicking trigger...")
                    try:
                        parent_btn = trigger.locator("xpath=./ancestor::div[@role='button']").first
                        if parent_btn.is_visible(timeout=1000):
                            parent_btn.click(force=True)
                        else:
                            trigger.click(force=True)
                    except:
                        trigger.click(force=True)
                    
                    try:
                        page.wait_for_selector(textbox_selector, state="visible", timeout=5000)
                    except:
                        print("Dialog didn't appear after click, trying 'P' shortcut...")
                        page.keyboard.press("p")
                else:
                    print("No trigger found, trying 'P' shortcut...")
                    page.keyboard.press("p")
            
            print("Waiting for post dialog...")
            try:
                page.wait_for_selector(textbox_selector, state="visible", timeout=10000)
            except:
                print("Still no dialog. Forcing 'P' one last time...")
                page.keyboard.press("p")
                page.wait_for_selector(textbox_selector, state="visible", timeout=10000)

            print("Pasting message content...")
            textbox = page.locator(textbox_selector).first
            textbox.focus()
            textbox.fill(text)
            time.sleep(2)
            
            print("Clicking Post/Submit...")
            for step in range(5):
                print(f"Submission Step {step + 1}...")
                
                # Priority: Post/Share/Publish, then Next/Done
                submit_selectors = [
                    "div[role='dialog'] div[aria-label='Post']",
                    "div[role='dialog'] [role='button']:has-text('Post')",
                    "div[role='dialog'] [role='button']:has-text('Share')",
                    "div[role='dialog'] [role='button']:has-text('Publish')",
                    "div[role='dialog'] [aria-label='Share now']",
                    "div[role='dialog'] [aria-label='Publish']",
                    "div[role='dialog'] [role='button']:has-text('Next')",
                    "div[role='dialog'] [role='button']:has-text('Done')",
                    "div[role='dialog'] [aria-label='Next']"
                ]
                
                btn = None
                for sel in submit_selectors:
                    try:
                        candidates = page.locator(sel)
                        count = candidates.count()
                        for i in range(count - 1, -1, -1):
                            target = candidates.nth(i)
                            if target.is_visible(timeout=3000):
                                label = (target.get_attribute("aria-label") or "").strip()
                                text_content = (target.text_content() or "").strip()
                                
                                # CRITICAL: Don't skip if the label is just "Post"
                                if label == "Post" or text_content == "Post":
                                    btn = target
                                    print(f"Found EXACT Post button: '{text_content}' (Label: '{label}')")
                                    break

                                # Skip the "Add to your post" widget buttons
                                if "Add to your post" in label or "Add to your post" in text_content:
                                    continue
                                
                                if target.is_enabled():
                                    btn = target
                                    btn_text = text_content or label
                                    print(f"Found active button: '{btn_text}'")
                                    break
                        if btn: break
                    except: continue

                if btn:
                    clicked_text = (btn.text_content() or btn.get_attribute("aria-label") or "").strip()
                    print(f"Clicking '{clicked_text}'...")
                    btn.click(force=True)
                    
                    if screenshot_path:
                         step_screenshot = screenshot_path.replace(".png", f"_after_{clicked_text.replace(' ', '_')}.png")
                         page.screenshot(path=step_screenshot)
                         print(f"Step screenshot saved to {step_screenshot}")

                    print(f"Waiting 10 seconds for transition...")
                    time.sleep(10) 
                    
                    # Log visible buttons for debugging
                    try:
                        all_btns = page.locator("div[role='dialog'] [role='button']").all()
                        labels = [ (b.get_attribute("aria-label") or b.text_content() or "").strip() for b in all_btns ]
                        print(f"Current buttons in dialog: {labels}")
                    except: pass

                    # Check if dialog is gone
                    dialog = page.locator("div[role='dialog']").first
                    if not dialog.is_visible(timeout=5000):
                        print("Post dialog closed. Verification...")
                        time.sleep(3)
                        if not page.locator("div[role='dialog']").first.is_visible():
                            print("Post submitted successfully")
                            if screenshot_path:
                                page.screenshot(path=screenshot_path)
                            break
                    else:
                        print("Dialog still visible. Checking for prompts (Not now, etc)...")
                        try:
                            # Try to close any follow-up dialogs (Boost, etc)
                            not_now = page.locator("div[role='dialog'] [role='button']:has-text('Not now'), div[role='dialog'] [aria-label='Close']").first
                            if not_now.is_visible(timeout=2000):
                                print(f"Found prompt '{not_now.text_content()}', clicking...")
                                not_now.click()
                                time.sleep(3)
                        except: pass
                else:
                    print("No explicit button found. Trying Ctrl+Enter fallback...")
                    page.keyboard.press("Control+Enter")
                    time.sleep(15)
                    if not page.locator("div[role='dialog']").first.is_visible(timeout=5000):
                         print("Dialog closed via Ctrl+Enter. Success.")
                         print("Post submitted successfully")
                         if screenshot_path:
                             page.screenshot(path=screenshot_path)
                    break

            context.close()

        except Exception as e:
            print(f"Automation failed: {e}")
            if screenshot_path:
                page.screenshot(path=screenshot_path)
            context.close()

def login_mode():
    """Manual login to save session."""
    print("\n" + "="*50)
    print("MANUAL LOGIN MODE")
    print("1. Log in to Facebook.")
    print("2. Check 'Remember Password'.")
    print("3. Close the browser window manually when finished.")
    print("="*50 + "\n")
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(user_data_dir=SESSION_DIR, headless=False, channel="chrome")
        page = context.new_page()
        page.goto("https://www.facebook.com")
        while True:
            try:
                if page.is_closed(): break
                time.sleep(1)
            except: break
        context.storage_state(path=STORAGE_STATE)
        print(f"Session and Storage State saved to {SESSION_DIR}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", action="store_true")
    parser.add_argument("--text", help="Post content")
    parser.add_argument("--url", help="The URL of your Facebook Page or Profile")
    parser.add_argument("--page", help="The specific Page Name to switch to before posting")
    parser.add_argument("--output", help="Path to save the confirmation screenshot")
    parser.add_argument("--visible", action="store_true")
    args = parser.parse_args()

    if args.login:
        login_mode()
    elif args.text:
        run_home_post(args.text, url=args.url, page_name=args.page, screenshot_path=args.output, headless=not args.visible)
    else:
        parser.print_help()
