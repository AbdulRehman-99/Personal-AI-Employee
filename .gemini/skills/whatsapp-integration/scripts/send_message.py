import argparse
import os
import time
from playwright.sync_api import sync_playwright

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.path.join(SCRIPT_DIR, "whatsapp_session")

def send_message(contact, message, dry_run=False):
    print(f"DEBUG: Using session path: {USER_DATA_DIR}")
    with sync_playwright() as p:
        try:
            print(f"Launching WhatsApp to send message to '{contact}'...")
            browser = p.chromium.launch_persistent_context(USER_DATA_DIR, headless=False)
            page = browser.pages[0]
            page.goto("https://web.whatsapp.com")
            
            # Wait for load
            try:
                page.wait_for_selector('div[aria-label="Chat list"]', timeout=60000)
            except:
                print("Timeout waiting for WhatsApp to load. Ensure you have logged in using the watcher script.")
                browser.close()
                return

            print("Searching for contact...")
            search_box = None
            
            # Strategy 1: Data-tab index (most reliable when stable)
            try:
                search_box = page.locator('div[contenteditable="true"][data-tab="3"]')
                if search_box.is_visible():
                    print("Debug: Found search box via data-tab=3")
            except: pass

            # Strategy 2: Title attribute
            if not search_box or not search_box.is_visible():
                try:
                    search_box = page.get_by_title("Search input textbox")
                    if search_box.is_visible():
                        print("Debug: Found search box via title")
                except: pass

            # Strategy 3: Placeholder text (sometimes "Search" or "Search or start new chat")
            if not search_box or not search_box.is_visible():
                try:
                    search_box = page.get_by_placeholder("Search", exact=False)
                    if search_box.is_visible():
                         print("Debug: Found search box via placeholder")
                except: pass

            # Strategy 4: Generic contenteditable in the side pane (dangerous but effective fallback)
            if not search_box or not search_box.is_visible():
                 try:
                    # The side pane is usually the first third of the screen, containing the first contenteditable
                    search_box = page.locator('div[contenteditable="true"]').first
                    print("Debug: Fallback to first contenteditable div")
                 except: pass

            if search_box and search_box.is_visible():
                search_box.click()
                search_box.fill(contact)
                time.sleep(3) # Wait for search results to populate
                
                print("Selecting contact from results...")
                # Use global keyboard Enter as it's more reliable
                page.keyboard.press("Enter")
                time.sleep(2)
                
                # Check if chat opened (looking for the message box)
                try:
                    message_box_check = page.locator('div[contenteditable="true"][role="textbox"]').last
                    if not message_box_check.is_visible(timeout=5000):
                        print("Enter didn't open chat, trying to click the result...")
                        # Fallback: Click the first chat result in the list
                        # Search results often have a specific class or structure
                        first_result = page.locator('div[role="listitem"]').filter(has_text=contact).first
                        if not first_result.is_visible():
                             first_result = page.locator('div[aria-label="Search results"] div[role="listitem"]').first
                        
                        if first_result.is_visible():
                            first_result.click()
                            time.sleep(2)
                except:
                    print("Selection fallback failed or chat already opened.")
            else:
                print("Error: Could not find the search box using any known selector.")
                browser.close()
                return
            
            # Wait for chat to open (check for header)
            time.sleep(3) 
            
            print(f"Typing message: {message}")
            # Message box
            try:
                # Try specific title first
                message_box = page.get_by_title("Type a message")
                if not message_box.is_visible():
                     # Fallback: the last contenteditable div is usually the message box
                    message_box = page.locator('div[contenteditable="true"][role="textbox"]').last
                
                message_box.click()
                message_box.fill(message)
                
                if not dry_run:
                    message_box.press("Enter")
                    print("Message sent!")
                    time.sleep(2) # Wait for send tick
                else:
                    print("[DRY RUN] Message not sent.")
            except Exception as msg_err:
                print(f"Could not find message box: {msg_err}")
                
            browser.close()
            
        except Exception as e:
            print(f"Error sending message: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send WhatsApp Message")
    parser.add_argument("--contact", required=True, help="Contact name or phone number")
    parser.add_argument("--message", required=True, help="Message content")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without sending")
    
    args = parser.parse_args()
    
    send_message(args.contact, args.message, args.dry_run)
