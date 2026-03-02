import argparse
import os
import shutil

VAULT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'AI_Employee_Vault'))
PENDING_DIR = os.path.join(VAULT_DIR, 'Pending_Approval')
APPROVED_DIR = os.path.join(VAULT_DIR, 'Approved')
REJECTED_DIR = os.path.join(VAULT_DIR, 'Rejected')

def list_approvals():
    if not os.path.exists(PENDING_DIR):
        print("No Pending_Approval folder found.")
        return

    files = [f for f in os.listdir(PENDING_DIR) if f.endswith('.md')]
    if not files:
        print("No pending approvals.")
    else:
        print("Pending Approvals:")
        for f in files:
            print(f" - {f}")

def move_file(filename, destination):
    src = os.path.join(PENDING_DIR, filename)
    dst = os.path.join(destination, filename)
    
    if not os.path.exists(src):
        print(f"Error: File {filename} not found in Pending_Approval.")
        return
    
    shutil.move(src, dst)
    print(f"Moved {filename} to {os.path.basename(destination)}")

def main():
    parser = argparse.ArgumentParser(description='Manage approvals')
    parser.add_argument('--list', action='store_true', help='List pending approvals')
    parser.add_argument('--approve', help='Filename to approve')
    parser.add_argument('--reject', help='Filename to reject')
    
    args = parser.parse_args()
    
    if args.list:
        list_approvals()
    elif args.approve:
        move_file(args.approve, APPROVED_DIR)
    elif args.reject:
        move_file(args.reject, REJECTED_DIR)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
