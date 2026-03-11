import os.path
import base64
import json
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import sys

# Combined scopes for reading, modifying (marking as read), and sending.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]

def get_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_path = os.path.join(os.path.dirname(__file__), '..', 'token.json')
    creds_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                print(f"Error: credentials.json not found at {creds_path}")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def create_task_file(service, message_id, vault_path):
    try:
        message = service.users().messages().get(userId='me', id=message_id).execute()
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        snippet = message.get('snippet', '')
        
        file_content = f"""---
type: email
from: {sender}
subject: {subject}
status: new
id: {message_id}
---

# Email Content
{snippet}

# Instructions
- [ ] Read and summarize
- [ ] Draft a reply if necessary
"""
        filename = f"EMAIL_{message_id}.md"
        filepath = os.path.join(vault_path, 'Needs_Action', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        print(f"Created task: {filepath}")
        
        # Mark as read (remove UNREAD label)
        service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()

    except Exception as e:
        print(f"Error processing message {message_id}: {e}")

def main():
    service = get_service()
    if not service:
        return

    # Assuming vault path is relative to script location or hardcoded
    # Adjust this path as necessary
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'AI_Employee_Vault'))
    
    if not os.path.exists(base_dir):
        print(f"Error: Vault directory not found at {base_dir}")
        return

    print(f"Monitoring Gmail for new messages... Writing to {base_dir}")

    while True:
        try:
            print("Checking for unread messages...")
            # Use q='is:unread' to be more broad than just labelIds=['UNREAD']
            results = service.users().messages().list(userId='me', q='is:unread', maxResults=10).execute()
            messages = results.get('messages', [])

            if not messages:
                print('No unread messages found.')
            else:
                print(f"Found {len(messages)} unread messages. Processing...")
                for message in messages:
                    create_task_file(service, message['id'], base_dir)
            
            print("Done checking. Sleeping for 60 seconds...")
            time.sleep(60) # Check every minute

        except Exception as e:
            print(f"An error occurred during Gmail scan: {e}")
            time.sleep(60)

if __name__ == '__main__':
    main()
