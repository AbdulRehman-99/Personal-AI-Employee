import os
import time
import shutil
import subprocess
import sys
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
VAULT_PATH = BASE_DIR / "AI_Employee_Vault"
APPROVED_DIR = VAULT_PATH / "Approved"
DONE_DIR = VAULT_PATH / "Done"
LOGS_DIR = VAULT_PATH / "Logs"
LINKEDIN_SCRIPT = BASE_DIR / ".gemini" / "skills" / "browsing-with-playwright" / "scripts" / "linkedin-automation.py"

def get_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def process_approved_tasks():
    if not APPROVED_DIR.exists():
        return

    for task_file in APPROVED_DIR.glob("*.md"):
        print(f"Detected approved task: {task_file.name}")
        content = get_file_content(task_file)
        
        # Check task type
        if "type: linkedin_post" in content:
            handle_linkedin_post(task_file, content)
        else:
            print(f"Unknown task type in {task_file.name}. Skipping.")

def handle_linkedin_post(task_file, content):
    print(f"Processing LinkedIn Post from {task_file.name}...")
    
    # Extract text (everything after '---')
    body = content.split("---")[-1].strip()
    if "# Post Content" in body:
        body = body.split("# Post Content")[-1].strip()

    timestamp = int(time.time())
    screenshot_name = f"POST_CONFIRMATION_{timestamp}.png"
    screenshot_path = LOGS_DIR / screenshot_name
    
    # Execute the post
    try:
        cmd = [
            sys.executable,
            str(LINKEDIN_SCRIPT),
            "--text", body,
            "--output", str(screenshot_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if "Post submitted successfully!" in result.stdout:
            print(f"Post successful! Screenshot saved to {screenshot_path}")
            # Move to Done
            shutil.move(str(task_file), str(DONE_DIR / task_file.name))
            print(f"Task moved to Done.")
        else:
            print(f"Post failed for {task_file.name}. Check output logs.")
            print(result.stdout)
            
    except Exception as e:
        print(f"Error executing LinkedIn post: {e}")

def main():
    print("AI Employee Task Orchestrator (Action Loop) Started.")
    print(f"Monitoring {APPROVED_DIR} for tasks...")
    
    # Ensure folders exist
    DONE_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

    while True:
        try:
            process_approved_tasks()
        except Exception as e:
            print(f"Error in Action Loop: {e}")
        
        time.sleep(10) # Poll every 10 seconds

if __name__ == "__main__":
    main()
