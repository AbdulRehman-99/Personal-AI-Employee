import os
import time
import shutil
import subprocess
import sys
import json
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
VAULT_PATH = BASE_DIR / "AI_Employee_Vault"
APPROVED_DIR = VAULT_PATH / "Approved"
DONE_DIR = VAULT_PATH / "Done"
LOGS_DIR = VAULT_PATH / "Logs"
LINKEDIN_SCRIPT = BASE_DIR / ".gemini" / "skills" / "browsing-with-playwright" / "scripts" / "linkedin-automation.py"
FACEBOOK_SCRIPT = BASE_DIR / ".gemini" / "skills" / "facebook-integration" / "scripts" / "post_facebook.py"
MCP_CLIENT = BASE_DIR / ".gemini" / "skills" / "browsing-with-playwright" / "scripts" / "mcp-client.py"
GMAIL_MCP_SERVER = f'python "{BASE_DIR}/.gemini/skills/gmail-integration/scripts/gmail_mcp_server.py"'
ODOO_MCP_SERVER = f'python "{BASE_DIR}/.gemini/skills/odoo-integration/scripts/odoo_mcp_server.py"'

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
        elif "type: facebook_post" in content:
            handle_facebook_post(task_file, content)
        elif "type: email_send" in content:
            handle_email_send(task_file, content)
        elif "type: create_invoice" in content:
            handle_odoo_invoice(task_file, content)
        else:
            print(f"Unknown task type in {task_file.name}. Skipping.")

def handle_odoo_invoice(task_file, content):
    print(f"Processing Odoo Invoice from {task_file.name}...")
    
    # Simple parsing: extract partner and lines
    # Expected format in markdown:
    # partner: Name
    # lines: [{"product": "X", "quantity": 1, "price": 10}]
    try:
        lines = content.split('\n')
        partner = next((line.split('partner:')[1].strip() for line in lines if 'partner:' in line), None)
        
        # Extract lines JSON from a code block or specific marker if possible
        # For MVP, let's assume lines are provided as a JSON string in a field called 'invoice_lines:'
        invoice_lines_str = next((line.split('invoice_lines:')[1].strip() for line in lines if 'invoice_lines:' in line), "[]")
        invoice_lines = json.loads(invoice_lines_str)

        if not partner:
            print(f"Error: No partner found in {task_file.name}")
            return

        params = json.dumps({
            "partner_name": partner,
            "lines": invoice_lines
        })

        cmd = [
            sys.executable,
            str(MCP_CLIENT),
            "call",
            "--stdio", ODOO_MCP_SERVER,
            "--tool", "create_invoice",
            "--params", params
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if "Invoice created" in result.stdout:
            print(f"Invoice created successfully for {partner}")
            shutil.move(str(task_file), str(DONE_DIR / task_file.name))
            print(f"Task moved to Done.")
        else:
            print(f"Invoice creation failed for {task_file.name}. Check output logs.")
            print(result.stdout)
            print(result.stderr)

    except Exception as e:
        print(f"Error executing invoice creation: {e}")

def handle_email_send(task_file, content):
    print(f"Processing Email Send from {task_file.name}...")
    
    # Simple extraction logic for headers and body
    try:
        lines = content.split('\n')
        to = next((line.split('to:')[1].strip() for line in lines if 'to:' in line), None)
        subject = next((line.split('subject:')[1].strip() for line in lines if 'subject:' in line), "No Subject")
        
        # Extract body (everything after the frontmatter)
        body = content.split("---")[-1].strip()
        if "# Email Content" in body:
            body = body.split("# Email Content")[-1].strip()

        if not to:
            print(f"Error: No recipient found in {task_file.name}")
            return

        params = json.dumps({
            "to": to,
            "subject": subject,
            "body": body
        })

        cmd = [
            sys.executable,
            str(MCP_CLIENT),
            "call",
            "--stdio", GMAIL_MCP_SERVER,
            "--tool", "send_email",
            "--params", params
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if "Email sent successfully" in result.stdout:
            print(f"Email sent successfully to {to}")
            # Move to Done
            shutil.move(str(task_file), str(DONE_DIR / task_file.name))
            print(f"Task moved to Done.")
        else:
            print(f"Email send failed for {task_file.name}. Check output logs.")
            print(result.stdout)
            print(result.stderr)

    except Exception as e:
        print(f"Error executing email send: {e}")

def handle_facebook_post(task_file, content):
    print(f"Processing Facebook Post from {task_file.name}...")
    
    # Extract text (everything after '---')
    body = content.split("---")[-1].strip()
    if "# Post Content" in body:
        body = body.split("# Post Content")[-1].strip()

    # Extract Page Name if present
    lines = content.split('\n')
    page_name = next((line.split('page:')[1].strip() for line in lines if 'page:' in line), None)

    timestamp = int(time.time())
    screenshot_name = f"FB_POST_CONFIRMATION_{timestamp}.png"
    screenshot_path = LOGS_DIR / screenshot_name
    
    # Execute the post
    try:
        cmd = [
            sys.executable,
            str(FACEBOOK_SCRIPT),
            "--text", body,
            "--output", str(screenshot_path)
        ]
        
        if page_name:
            cmd.extend(["--page", page_name])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120) # Increased timeout for navigation
        
        if "Post submitted successfully" in result.stdout:
            print(f"Facebook Post successful! Screenshot saved to {screenshot_path}")
            shutil.move(str(task_file), str(DONE_DIR / task_file.name))
            print(f"Task moved to Done.")
        else:
            print(f"Facebook Post failed for {task_file.name}. Check output logs.")
            print(result.stdout)
            
    except Exception as e:
        print(f"Error executing Facebook post: {e}")

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
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
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
