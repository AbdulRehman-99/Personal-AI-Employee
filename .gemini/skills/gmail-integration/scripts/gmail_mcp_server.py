import os.path
import base64
import json
import sys
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Combined scopes for reading, modifying (marking as read), and sending.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]

def get_service():
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), '..', 'token.json')
    creds_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                return None
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def send_email(to, subject, body):
    service = get_service()
    if not service:
        return {"isError": True, "content": [{"type": "text", "text": "Failed to authenticate with Gmail."}]}
    
    try:
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body_data = {'raw': raw}
        
        sent_message = service.users().messages().send(userId='me', body=body_data).execute()
        return {"content": [{"type": "text", "text": f"Email sent successfully. Message ID: {sent_message['id']}"}]}
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": f"Error sending email: {str(e)}"}]}

def main():
    # Simple MCP stdio loop
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            req_id = request.get("id")
            method = request.get("method")
            params = request.get("params", {})

            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "gmail-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
            elif method == "notifications/initialized":
                continue # No response needed
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": [
                            {
                                "name": "send_email",
                                "description": "Send an email using Gmail API",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "to": {"type": "string", "description": "Recipient email address"},
                                        "subject": {"type": "string", "description": "Email subject"},
                                        "body": {"type": "string", "description": "Email body content"}
                                    },
                                    "required": ["to", "subject", "body"]
                                }
                            }
                        ]
                    }
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "send_email":
                    result = send_email(
                        to=arguments.get("to"),
                        subject=arguments.get("subject"),
                        body=arguments.get("body")
                    )
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": result
                    }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}
                    }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except Exception as e:
            # Fatal error in loop
            break

if __name__ == "__main__":
    main()
