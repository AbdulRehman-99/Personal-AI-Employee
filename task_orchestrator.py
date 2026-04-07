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
LINKEDIN_SCRIPT = BASE_DIR / ".gemini" / "skills" / "linkedin-automation" / "scripts" / "post_linkedin.py"
FACEBOOK_SCRIPT = BASE_DIR / ".gemini" / "skills" / "facebook-integration" / "scripts" / "post_facebook.py"
WHATSAPP_SCRIPT = BASE_DIR / ".gemini" / "skills" / "whatsapp-integration" / "scripts" / "send_message.py"
MCP_CLIENT = BASE_DIR / ".gemini" / "skills" / "browsing-with-playwright" / "scripts" / "mcp-client.py"
GMAIL_MCP_SERVER = f'python "{BASE_DIR}/.gemini/skills/gmail-integration/scripts/gmail_mcp_server.py"'
ODOO_MCP_SERVER = f'python "{BASE_DIR}/.gemini/skills/odoo-integration/scripts/odoo_mcp_server.py"'

def get_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def parse_task_file(content):
    """
    Robustly parses frontmatter and body.
    Returns (headers_dict, body_text)
    """
    parts = content.split("---")
    if len(parts) >= 3:
        header_str = parts[1]
        # Join the rest in case content contains '---'
        body_text = "---".join(parts[2:]).strip()
        
        headers = {}
        for line in header_str.strip().split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                value = val.strip()
                # Remove literal quotes if present
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1].strip()
                headers[key.strip().lower()] = value
        return headers, body_text
    return {}, content.strip()

def process_approved_tasks():
    if not APPROVED_DIR.exists():
        return

    for task_file in APPROVED_DIR.glob("*.md"):
        print(f"Detected approved task: {task_file.name}")
        content = get_file_content(task_file)
        headers, body = parse_task_file(content)
        
        task_type = headers.get('type', '')
        
        # Routing based on type
        if "linkedin_post" in task_type:
            handle_linkedin_post(task_file, headers, body)
        elif "facebook_post" in task_type:
            handle_facebook_post(task_file, headers, body)
        elif "whatsapp_send" in task_type:
            handle_whatsapp_send(task_file, headers, body)
        elif "email_send" in task_type:
            handle_email_send(task_file, headers, body)
        elif "create_invoice" in task_type:
            handle_odoo_invoice(task_file, headers, body)
        else:
            print(f"Unknown task type '{task_type}' in {task_file.name}. Skipping.")

def handle_whatsapp_send(task_file, headers, body):
    print(f"Processing WhatsApp Message from {task_file.name}...")
    
    if "# Message Content" in body:
        body = body.split("# Message Content")[-1].strip()

    contact = headers.get('contact')
    if not contact:
        print(f"Error: No contact specified in {task_file.name}")
        return

    try:
        cmd = [
            sys.executable,
            str(WHATSAPP_SCRIPT),
            "--contact", contact,
            "--message", body
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if "Message sent" in result.stdout:
            print(f"WhatsApp message sent successfully to {contact}")
            shutil.move(str(task_file), str(DONE_DIR / task_file.name))
        else:
            print(f"WhatsApp send failed for {task_file.name}.")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
    except Exception as e:
        print(f"Error executing WhatsApp send: {e}")

def handle_odoo_invoice(task_file, headers, body):
    print(f"Processing Odoo Invoice from {task_file.name}...")
    try:
        partner = headers.get('partner')
        invoice_lines_str = headers.get('invoice_lines', '[]')
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
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if "Invoice created" in result.stdout:
            print(f"Invoice created successfully for {partner}")
            shutil.move(str(task_file), str(DONE_DIR / task_file.name))
        else:
            print(f"Invoice creation failed for {task_file.name}.")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)

    except Exception as e:
        print(f"Error executing invoice creation: {e}")

def handle_email_send(task_file, headers, body):
    print(f"Processing Email Send from {task_file.name}...")
    try:
        to = headers.get('to')
        subject = headers.get('subject', 'No Subject')
        
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
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if "Email sent successfully" in result.stdout:
            print(f"Email sent successfully to {to}")
            shutil.move(str(task_file), str(DONE_DIR / task_file.name))
        else:
            print(f"Email send failed for {task_file.name}.")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)

    except Exception as e:
        print(f"Error executing email send: {e}")

def handle_facebook_post(task_file, headers, body):
    print(f"Processing Facebook Post from {task_file.name}...")
    
    if "# Post Content" in body:
        body = body.split("# Post Content")[-1].strip()

    page_name = headers.get('page')
    is_visible = headers.get('visible', 'false').lower() == 'true'

    timestamp = int(time.time())
    screenshot_name = f"FB_POST_CONFIRMATION_{timestamp}.png"
    screenshot_path = LOGS_DIR / screenshot_name
    
    try:
        cmd = [
            sys.executable,
            str(FACEBOOK_SCRIPT),
            "--text", body,
            "--output", str(screenshot_path),
            "--visible"
        ]
        
        if page_name:
            cmd.extend(["--page", page_name])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if "Post submitted successfully" in result.stdout:
            print(f"Facebook Post successful! Screenshot saved to {screenshot_path}")
            shutil.move(str(task_file), str(DONE_DIR / task_file.name))
        else:
            print(f"Facebook Post failed for {task_file.name}.")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
    except Exception as e:
        print(f"Error executing Facebook post: {e}")

def handle_linkedin_post(task_file, headers, body):
    print(f"Processing LinkedIn Post from {task_file.name}...")
    
    if "# Post Content" in body:
        body = body.split("# Post Content")[-1].strip()

    timestamp = int(time.time())
    screenshot_name = f"POST_CONFIRMATION_{timestamp}.png"
    screenshot_path = LOGS_DIR / screenshot_name
    
    try:
        cmd = [
            sys.executable,
            str(LINKEDIN_SCRIPT),
            "--text", body,
            "--output", str(screenshot_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if "Post submitted successfully!" in result.stdout:
            print(f"Post successful! Screenshot saved to {screenshot_path}")
            shutil.move(str(task_file), str(DONE_DIR / task_file.name))
        else:
            print(f"Post failed for {task_file.name}.")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
    except Exception as e:
        print(f"Error executing LinkedIn post: {e}")

def main():
    print("AI Employee Task Orchestrator (Action Loop) Started.")
    print(f"Monitoring {APPROVED_DIR} for tasks for the next 60 seconds...")
    
    # Ensure folders exist
    DONE_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

    start_time = time.time()
    execution_limit = 60 # Run for 60 seconds
    
    while (time.time() - start_time) < execution_limit:
        try:
            process_approved_tasks()
        except Exception as e:
            print(f"Error in Action Loop: {e}")
        
        time.sleep(10) # Poll every 10 seconds

    print(f"Execution window ({execution_limit}s) complete. Updating Dashboard...")
    
    # Automatically update Dashboard before exiting
    audit_script = BASE_DIR / ".gemini" / "skills" / "ai-employee-manager" / "scripts" / "vault_audit.py"
    if audit_script.exists():
        subprocess.run([sys.executable, str(audit_script)], capture_output=True)
        print("Dashboard updated successfully.")
    else:
        print("Warning: vault_audit.py not found. Dashboard not updated.")
    
    print("Action Phase complete. Task Orchestrator closing automatically.")

if __name__ == "__main__":
    main()
