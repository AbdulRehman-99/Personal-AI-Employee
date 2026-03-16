import subprocess
import time
import sys
import os

# Define paths to watcher scripts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GMAIL_WATCHER = os.path.join(BASE_DIR, '.gemini', 'skills', 'gmail-integration', 'scripts', 'gmail_watcher.py')
LINKEDIN_WATCHER = os.path.join(BASE_DIR, '.gemini/skills/browsing-with-playwright/scripts/linkedin_watcher.py')
FS_WATCHER = os.path.join(BASE_DIR, '.gemini', 'skills', 'filesystem-management', 'scripts', 'filesystem_watcher.py')
FINANCE_WATCHER = os.path.join(BASE_DIR, '.gemini', 'skills', 'odoo-integration', 'scripts', 'finance_watcher.py')
FACEBOOK_WATCHER = os.path.join(BASE_DIR, '.gemini', 'skills', 'facebook-integration', 'scripts', 'facebook_watcher.py')
TASK_ORCHESTRATOR = os.path.join(BASE_DIR, 'task_orchestrator.py')

def start_process(script_path):
    if not os.path.exists(script_path):
        print(f"Error: Script not found at {script_path}")
        return None
    
    print(f"Starting {os.path.basename(script_path)}...")
    return subprocess.Popen([sys.executable, script_path], creationflags=subprocess.CREATE_NEW_CONSOLE)

def main():
    print("Starting AI Employee Orchestrator (Gold Tier)...")
    
    processes = []
    
    # Start Gmail Watcher
    p_gmail = start_process(GMAIL_WATCHER)
    if p_gmail: processes.append(p_gmail)
    
    # Start LinkedIn Watcher
    p_linkedin = start_process(LINKEDIN_WATCHER)
    if p_linkedin: processes.append(p_linkedin)
    
    # Start Filesystem Watcher
    p_fs = start_process(FS_WATCHER)
    if p_fs: processes.append(p_fs)

    # Start Finance Watcher (Odoo)
    p_finance = start_process(FINANCE_WATCHER)
    if p_finance: processes.append(p_finance)

    # Start Facebook Watcher
    p_facebook = start_process(FACEBOOK_WATCHER)
    if p_facebook: processes.append(p_facebook)

    # Start Task Orchestrator (Action Loop)
    p_task = start_process(TASK_ORCHESTRATOR)
    if p_task: processes.append(p_task)
    
    print(f"All watchers started. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
            # Check if processes are still alive
            for p in processes:
                if p.poll() is not None:
                    print(f"Warning: A watcher process (PID {p.pid}) has exited.")
                    # Optional: Restart logic could go here
    except KeyboardInterrupt:
        print("
Stopping all watchers...")
        for p in processes:
            p.terminate()
        print("Done.")

if __name__ == '__main__':
    main()
