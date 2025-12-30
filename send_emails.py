import os
import time
import base64
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# --- Configuration ---
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]
EMAILS_FILE = 'emails.csv'
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'
MAX_EMAILS_PER_DAY = 450  # Staying safely under the 500 limit for personal accounts
SLEEP_BETWEEN_EMAILS = 2  # Seconds to wait between sends to avoid rate limiting

# --- PDF Attachment ---
PDF_FILE = 'attachment.pdf'  # Name of the PDF file to attach (place in same folder)

# --- Email Content ---
SUBJECT = "hi"
BODY_TEMPLATE = """
Hi {name},

Yash testing 
"""

def authenticate_gmail():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(f"Missing {CREDENTIALS_FILE}. Please download it from Google Cloud Console.")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def create_message(sender, to, subject, message_text, pdf_path=None):
    """Create a message for an email with optional PDF attachment."""
    # Create multipart message
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    
    # Attach the email body
    message.attach(MIMEText(message_text, 'plain'))
    
    # Attach PDF if provided
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {os.path.basename(pdf_path)}',
        )
        message.attach(part)
    
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    """Send an email message."""
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print(f'Message Id: {message["id"]} sent.')
        return True
    except HttpError as error:
        print(f'An error occurred: {error}')
        return False

def main():
    print("--- Gmail Automation Script ---")
    
    # 1. Load Data
    if not os.path.exists(EMAILS_FILE):
        print(f"Error: {EMAILS_FILE} not found. Please create it with 'email' and 'name' columns.")
        return
    
    df = pd.read_csv(EMAILS_FILE)
    if 'email' not in df.columns:
        print("Error: CSV must have an 'email' column.")
        return
    
    if 'status' not in df.columns:
        df['status'] = 'pending'

    # Filter for pending emails
    pending_emails = df[df['status'] == 'pending']
    print(f"Found {len(pending_emails)} pending emails.")
    
    if len(pending_emails) == 0:
        print("No pending emails to send.")
        return
    
    # Check for PDF attachment
    pdf_path = PDF_FILE if os.path.exists(PDF_FILE) else None
    if pdf_path:
        print(f"PDF attachment found: {PDF_FILE}")
    else:
        print(f"Warning: {PDF_FILE} not found. Emails will be sent without attachment.")

    # 2. Authenticate
    print("Authenticating with Gmail...")
    service = authenticate_gmail()
    if not service:
        print("Authentication failed.")
        return
    
    # Get user profile to know the sender address
    profile = service.users().getProfile(userId='me').execute()
    sender_email = profile['emailAddress']
    print(f"Authenticated as: {sender_email}")

    # 3. Send Emails
    count = 0
    for index, row in pending_emails.iterrows():
        if count >= MAX_EMAILS_PER_DAY:
            print(f"Daily limit of {MAX_EMAILS_PER_DAY} reached. Stopping for today.")
            break
        
        to_email = row['email']
        name = row['name'] if 'name' in df.columns else "there"
        
        print(f"Sending to {to_email}...")
        
        # Personalize body
        body = BODY_TEMPLATE.format(name=name)
        
        message = create_message(sender_email, to_email, SUBJECT, body, pdf_path)
        success = send_message(service, 'me', message)
        
        if success:
            df.at[index, 'status'] = 'sent'
            count += 1
            time.sleep(SLEEP_BETWEEN_EMAILS)
        else:
            df.at[index, 'status'] = 'failed'
            print(f"Failed to send to {to_email}")

    # 4. Save Progress
    df.to_csv(EMAILS_FILE, index=False)
    print(f"Finished. Sent {count} emails. Progress saved to {EMAILS_FILE}.")

if __name__ == '__main__':
    main()
