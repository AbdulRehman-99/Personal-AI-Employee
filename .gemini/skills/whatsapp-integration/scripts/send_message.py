import argparse
import os
import time
import shutil
from playwright.sync_api import sync_playwright

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.path.join(SCRIPT_DIR, "whatsapp_session")

def cleanup_session_locks():
    lock_files = ["SingletonLock", "LOCK", "SingletonCookie"]
    for root, dirs, files in os.walk(USER_DATA_DIR):
        for file in files:
            if any(lock in file for lock in lock_files):
                try:
                    os.remove(os.path.join(root, file))
                except:
                    pass

def send_message(contact, message, dry_run=False):
    print(f"DEBUG: Using session path: {USER_DATA_DIR}")
    cleanup_session_locks()
    
    with sync_playwright() as p:
        browser = None
        try:
            print(f"Launching WhatsApp to send message to '{contact}'...")
            browser = p.chromium.launch_persistent_context(
                USER_DATA_DIR, 
                headless=False,
                channel="chrome",
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-blink-features=AutomationControlled"],
                viewport={'width': 1280, 'height': 800}
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto("https://web.whatsapp.com", wait_until="load", timeout=90000)
            
            try:
                page.wait_for_function("document.title.includes('WhatsApp')", timeout=60000)
            except:
                print("Timeout waiting for WhatsApp to load.")
                browser.close()
                return

            print("WhatsApp loaded. Searching for contact...")
            time.sleep(10)
            
            # 1. Find and click search box
            search_box = page.locator('[role="textbox"], div[contenteditable="true"]').first
            if search_box.count() > 0:
                search_box.click()
                search_box.fill("")
                search_box.type(contact, delay=150) # Type slower for realism
                time.sleep(5) # Wait for results to stabilize
                
                print(f"Selecting contact '{contact}' from results...")
                # 2. Robust Selection: Find the contact name in the side pane specifically
                # We look for a span or div that has the contact name as title or text
                try:
                    # Look for the chat list items
                    # Selectors for chat results can vary, so we search by text within the pane
                    contact_selector = f'span[title="{contact}"], [aria-label="Search results"] span:text("{contact}"), div[role="listitem"] span:text("{contact}")'
                    contact_element = page.locator(contact_selector).first
                    
                    if contact_element.count() > 0:
                        contact_element.click()
                        print(f"Successfully clicked contact element for '{contact}'.")
                    else:
                        print(f"Could not find specific element for '{contact}', pressing Enter as fallback...")
                        page.keyboard.press("Enter")
                except Exception as select_err:
                    print(f"Selection error: {select_err}. Pressing Enter as fallback.")
                    page.keyboard.press("Enter")
                
                time.sleep(7) # Wait longer for the chat to fully load
                
                # Diagnostic Screenshot
                page.screenshot(path="WHATSAPP_AFTER_SELECTION.png")
                print("Diagnostic screenshot saved: WHATSAPP_AFTER_SELECTION.png")
                
                # 3. Discover and Type in Message Box
                # The message box is usually the last editable div on the page, often within a footer
                message_box_selectors = [
                    'footer div[contenteditable="true"][role="textbox"]',
                    'div[contenteditable="true"][role="textbox"].copyable-text',
                    'div[contenteditable="true"][role="textbox"]'
                ]
                
                message_box = None
                for sel in message_box_selectors:
                    if page.locator(sel).last.count() > 0:
                        message_box = page.locator(sel).last
                        break
                
                if message_box and message_box.is_visible():
                    # Double check it's the message box (low on screen)
                    box = message_box.bounding_box()
                    if box and box['y'] > 400: # Lowered threshold
                        print(f"Message box verified at Y={box['y']}. Typing...")
                        message_box.click()
                        time.sleep(1)
                        message_box.fill(message)
                        time.sleep(2)
                        
                        if not dry_run:
                            message_box.press("Enter")
                            print("Message sent successfully!")
                            time.sleep(5)
                        else:
                            print("[DRY RUN] Message not sent.")
                    else:
                        print("Error: The found textbox is not in the message area.")
                else:
                    # Final Fallback: Tab navigation to find focusable input
                    print("Falling back to Tab navigation for message box...")
                    page.keyboard.press("Tab") # Try to tab into the message field
                    time.sleep(1)
                    page.keyboard.type(message)
                    if not dry_run:
                        page.keyboard.press("Enter")
                        print("Message sent via Tab fallback!")
                        time.sleep(5)
            else:
                print("Error: Could not find search box.")
                
        except Exception as e:
            print(f"Error sending message: {e}")
        finally:
            if browser:
                browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send WhatsApp Message")
    parser.add_argument("--contact", required=True, help="Contact name or phone number")
    parser.add_argument("--message", required=True, help="Message content")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without sending")
    
    args = parser.parse_args()
    
    send_message(args.contact, args.message, args.dry_run)
