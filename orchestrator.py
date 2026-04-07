import subprocess
import time
import sys
import os

# Define paths to watcher scripts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_PATH = os.path.join(BASE_DIR, "AI_Employee_Vault")

GMAIL_WATCHER = os.path.join(BASE_DIR, '.gemini', 'skills', 'gmail-integration', 'scripts', 'gmail_watcher.py')
LINKEDIN_WATCHER = os.path.join(BASE_DIR, '.gemini/skills/browsing-with-playwright/scripts', 'linkedin_watcher.py')
FS_WATCHER = os.path.join(BASE_DIR, '.gemini', 'skills', 'filesystem-management', 'scripts', 'filesystem_watcher.py')
FINANCE_WATCHER = os.path.join(BASE_DIR, '.gemini', 'skills', 'odoo-integration', 'scripts', 'finance_watcher.py')
FACEBOOK_WATCHER = os.path.join(BASE_DIR, '.gemini', 'skills', 'facebook-integration', 'scripts', 'facebook_watcher.py')
WHATSAPP_WATCHER = os.path.join(BASE_DIR, '.gemini', 'skills', 'whatsapp-integration', 'scripts', 'whatsapp_watcher.py')
TASK_ORCHESTRATOR = os.path.join(BASE_DIR, 'task_orchestrator.py')

def start_process(script_path):
    if not os.path.exists(script_path):
        print(f"Error: Script not found at {script_path}")
        return None
    
    print(f"Starting {os.path.basename(script_path)}...")
    return subprocess.Popen([sys.executable, script_path], creationflags=subprocess.CREATE_NEW_CONSOLE)

def main():
    print("Starting AI Employee Orchestrator (Full Persistence Mode)...")
    
    # Map of names to paths
    watchers = {
        'fs': FS_WATCHER,
        'task': TASK_ORCHESTRATOR,
        'gmail': GMAIL_WATCHER,
        'linkedin': LINKEDIN_WATCHER,
        'facebook': FACEBOOK_WATCHER,
        'finance': FINANCE_WATCHER,
        'whatsapp': WHATSAPP_WATCHER
    }
    
    processes = {}
    
    # Start all watchers persistently by default
    for name, path in watchers.items():
        processes[name] = start_process(path)
    
    print("All watchers active. Monitoring for system health...")
    
    try:
        while True:
            # Check for dead processes and restart them
            for name, p in list(processes.items()):
                if p and p.poll() is not None:
                    print(f"Warning: {name} process (PID {p.pid}) has exited. Restarting...")
                    processes[name] = start_process(watchers[name])
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nStopping all system components...")
        for name, p in processes.items():
            if p:
                print(f"Terminating {name}...")
                p.terminate()
        print("System shutdown complete.")

if __name__ == '__main__':
    main()
