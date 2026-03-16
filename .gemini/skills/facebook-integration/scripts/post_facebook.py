import argparse
import os
import time
from playwright.sync_api import sync_playwright

# --- CONFIGURATION ---
# Absolute path to store your login session
SESSION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'facebook_session'))

def switch_profile(page, target_profile_name):
    """
    Switches the current Facebook context to the specified Page/Profile.
    """
    print(f"Attempting to switch profile to: {target_profile_name}")
    
    try:
        # 1. Click Account/Profile Menu (Top Right - the profile picture button)
        account_selectors = [
            "div[role='button'][aria-label='Your profile']",
            "div[role='button'][aria-label='Account']",
            "div[aria-label='Account controls and settings']",
            "svg[aria-label='Your profile']",
            "img[alt*='profile picture']"
        ]
        
        account_btn = None
        for sel in account_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=3000):
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

        # 2. Check if we are already on the correct profile
        if page.locator(f"div[role='link'] span:has-text('{target_profile_name}')").first.is_visible():
            print(f"Target profile '{target_profile_name}' is already active.")
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
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=SESSION_DIR,
                headless=headless,
                channel="chrome",
                slow_mo=500,
                args=["--disable-blink-features=AutomationControlled"]
            )
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
            
            # Check if dialog is already open (unlikely but possible)
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
                    # Try to click the parent button if it exists
                    try:
                        parent_btn = trigger.locator("xpath=./ancestor::div[@role='button']").first
                        if parent_btn.is_visible(timeout=1000):
                            parent_btn.click(force=True)
                        else:
                            trigger.click(force=True)
                    except:
                        trigger.click(force=True)
                    
                    # Wait a bit for dialog
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
            # Use fill for instant entry (like pasting)
            textbox.fill(text)
            
            print("Waiting for Post button to detect content...")
            time.sleep(2) # Short buffer for UI state update
            
            print("Clicking Post/Submit...")
            # Facebook multi-step dialog handler (e.g., Next -> Post/Share)
            for step in range(4):
                print(f"Submission Step {step + 1}...")
                
                # Selectors for the primary action button
                submit_selectors = [
                    "div[role='dialog'] [role='button']:has-text('Post')",
                    "div[role='dialog'] [role='button']:has-text('Share')",
                    "div[role='dialog'] [role='button']:has-text('Publish')",
                    "div[role='dialog'] [role='button']:has-text('Next')",
                    "div[role='dialog'] [role='button']:has-text('Done')",
                    "div[role='dialog'] [aria-label='Post']",
                    "div[role='dialog'] [aria-label='Share now']",
                    "div[role='dialog'] [aria-label='Publish']",
                    "div[role='dialog'] [aria-label='Next']"
                ]
                
                btn = None
                for sel in submit_selectors:
                    try:
                        candidates = page.locator(sel)
                        count = candidates.count()
                        
                        # Iterate backwards (bottom-up) because the main Post button is usually at the bottom
                        # and "Add to your post" is often above it.
                        for i in range(count - 1, -1, -1):
                            target = candidates.nth(i)
                            if target.is_visible(timeout=1000):
                                # Validation: Ensure it's not the "Add to your post" button
                                label = target.get_attribute("aria-label") or ""
                                text_content = target.text_content() or ""
                                
                                if "Add to your post" in label or "Add to your post" in text_content:
                                    print(f"Skipping 'Add to your post' button found via {sel}")
                                    continue
                                    
                                if target.is_enabled():
                                    btn = target
                                    print(f"Found active button: '{text_content.strip()}' (Label: '{label}') using selector: {sel}")
                                    break
                                else:
                                    print(f"Found button '{text_content.strip()}' but it is DISABLED.")
                        if btn: break
                    except: continue

                if btn:
                    btn.click(force=True)
                    print("Clicked button, waiting for transition...")
                    time.sleep(5) # Wait for next step or dialog closure
                    
                    # Check if dialog is gone
                    if not page.locator("div[role='dialog']").first.is_visible(timeout=3000):
                        print("Post dialog closed. Submission appears complete.")
                        if screenshot_path:
                             page.screenshot(path=screenshot_path)
                        break
                    else:
                        print("Dialog still visible, checking for next step or close...")
                        # Check for "Not now" or "Maybe later" (Boost post prompts)
                        try:
                            not_now = page.locator("div[role='dialog'] [role='button']:has-text('Not now')").first
                            if not_now.is_visible(timeout=1000):
                                print("Found 'Not now' button, clicking...")
                                not_now.click()
                                time.sleep(2)
                        except: pass

                        if screenshot_path:
                             page.screenshot(path=screenshot_path.replace(".png", f"_step_{step+1}.png"))
                else:
                    print("No more active submission buttons found.")

                    # Final success check: Is the original textbox gone?
                    if not page.locator(textbox_selector).first.is_visible():
                         print("Original textbox is gone. Assuming post success (dialog might be an upsell).")
                         # Try to close whatever remains
                         try:
                             close_btn = page.locator("div[role='dialog'] [aria-label='Close']").first
                             if close_btn.is_visible():
                                 close_btn.click()
                         except: pass
                    elif not page.locator("div[role='dialog']").first.is_visible():
                         print("Dialog is gone. Success.")
                    else:
                         print("Error: Stuck in dialog. Trying Escape key fallback...")
                         page.keyboard.press("Escape")
                         time.sleep(2)
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
        
        print("Session saved.")

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
