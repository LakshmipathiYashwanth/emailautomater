import os
import time
import base64
import pandas as pd
import random
from datetime import datetime, timedelta
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
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'
SENDER_NAME = "Yashwanth L"  # Name to appear in the "From" field

# --- Anti-Blocking Configuration (GMAIL-SAFE) ---
# ⚠️ CRITICAL: These settings prevent Gmail from detecting automation
# DO NOT increase these values unless you want to get blocked!

MAX_EMAILS_PER_DAY = 20  # Ultra-conservative for Gmail automation safety
MAX_EMAILS_PER_HOUR = 5  # Maximum 4-5 emails per hour (Gmail-safe)
MIN_DELAY_SECONDS = 180  # Minimum 3 minutes between emails (human-like)
MAX_DELAY_SECONDS = 300  # Maximum 5 minutes between emails
BATCH_SIZE = 5  # Small batches to avoid detection
BATCH_BREAK_MINUTES = 15  # Longer breaks between batches (15 minutes)
MAX_RETRIES = 2  # Reduced retries to avoid spam flags
EXPONENTIAL_BACKOFF_BASE = 3  # Longer backoff (3s, 9s, 27s)

# --- Specific Day Configuration ---
# New Emails: Tuesday(1), Wednesday(2), Thursday(3)
ALLOWED_NEW_EMAIL_DAYS = [1, 2, 3]

# Follow-ups: Monday(0), Friday(4)
ALLOWED_FOLLOWUP_DAYS = [0, 4]

# Time windows stay the same (Morning/Afternoon/Evening)
TIME_WINDOWS = [
    (9, 30, 10, 30),   # 9:30 AM - 10:30 AM
    (12, 30, 14, 0),   # 12:30 PM - 2:00 PM
    (17, 30, 19, 0),   # 5:30 PM - 7:00 PM
]

def get_next_allowed_time():
    """Get the next allowed sending time window."""
    # (Simplified logic for display)
    return "Check schedule guide"

# ... (Templates code remains same) ...

def main():
    """Main execution function."""
    print("\n" + "=" * 60)
    print("🚀 Gmail Bulk Email Sender with Anti-Blocking Protection")
    print("=" * 60)
    
    # 1. Load Data
    if not os.path.exists(EMAILS_FILE):
        print(f"❌ Error: {EMAILS_FILE} not found.")
        print("Please create the CSV file with 'email' and 'name' columns.")
        return
    
    df = pd.read_csv(EMAILS_FILE)
    
    # Normalize headers to support "Name", "Email", "Status", "Follow Up Status"
    df.columns = [c.strip().lower().replace(' ', '_').replace('-', '_') for c in df.columns]
    
    if 'status' not in df.columns:
        df['status'] = 'pending'
    if 'date_sent' not in df.columns:
        df['date_sent'] = None
    df['date_sent'] = df['date_sent'].astype(object)

    if 'follow_up_status' not in df.columns:
        df['follow_up_status'] = 'pending'

    if 'follow_up_date' not in df.columns:
        df['follow_up_date'] = None
    df['follow_up_date'] = df['follow_up_date'].astype(object)
    
    pending_emails = df[df['status'] == 'pending']
    
    # Check for PDF
    pdf_path = PDF_FILE if os.path.exists(PDF_FILE) else None
    if pdf_path:
        print(f"📎 PDF Attachment found: {os.path.basename(pdf_path)}")
    else:
        print("ℹ️  No PDF attachment found (sending plain text only).")
    
    # 2. Authenticate
    print("\n🔐 Authenticating with Gmail...")
    service = authenticate_gmail()
    if not service:
        print("❌ Authentication failed.")
        return
    
    # Get user profile
    profile = service.users().getProfile(userId='me').execute()
    sender_email = profile['emailAddress']
    print(f"✓ Authenticated as: {sender_email}")

    # 3. Display Configuration
    print("\n⚙️  Anti-Blocking Configuration:")
    print(f"   • Daily limit: {MAX_EMAILS_PER_DAY} emails")
    print(f"   • New Emails: Tuesday, Wednesday, Thursday")
    print(f"   • Follow-ups: Monday, Friday")
    
    current_time = datetime.now()
    current_weekday = current_time.weekday()
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    current_day_name = day_names[current_weekday]
    
    print(f"\n📅 Today is: {current_day_name}")
    
    # Determine Mode
    mode = "none"
    if current_weekday in ALLOWED_NEW_EMAIL_DAYS:
        mode = "new"
        print("✅ Mode: Sending NEW EMAILS today")
    elif current_weekday in ALLOWED_FOLLOWUP_DAYS:
        mode = "followup"
        print("✅ Mode: Sending FOLLOW-UPS today")
    else:
        print("⏸ No sending allowed today (Weekend).")
        return

    # 4. Execute based on Day
    total_sent = 0
    total_failed = 0
    
    # Check time window first
    in_window, window_time = is_in_allowed_time_window()
    if not in_window:
        print(f"\n⏸ Outside allowed time windows.")
        print(f"⏰ Current time: {current_time.strftime('%I:%M %p')}")
        print(f"💡 Allowed time windows:")
        for start_h, start_m, end_h, end_m in TIME_WINDOWS:
            print(f"   - {start_h}:{start_m:02d} - {end_h}:{end_m:02d}")
        return

    hour_start_time = datetime.now()
    hourly_count = 0
    batch_count = 0

    if mode == "new":
        print("\n📧 Starting NEW Email Loop...")
        for index, row in pending_emails.iterrows():
            # (Loop logic for new emails - mostly same as before)
            if total_sent >= MAX_EMAILS_PER_DAY:
                print(f"\n⏸ Daily limit of {MAX_EMAILS_PER_DAY} reached.")
                break
            
            if hourly_count >= MAX_EMAILS_PER_HOUR:
                wait_time = 3600 - (datetime.now() - hour_start_time).seconds
                print(f"\n⏸ Hourly limit reached. Waiting...")
                time.sleep(wait_time)
                hourly_count = 0
                hour_start_time = datetime.now()

            # Batch break
            if total_sent > 0 and total_sent % BATCH_SIZE == 0:
                print(f"⏸ Taking {BATCH_BREAK_MINUTES} min break...")
                time.sleep(BATCH_BREAK_MINUTES * 60)

            to_email = row['email']
            name = row.get('name', 'there')
            print(f"\n[{total_sent + 1}] Sending to: {to_email}")
            
            current_subject, current_body_template = get_random_template()
            try:
                body = current_body_template.format(name=name)
            except:
                body = current_body_template.replace("{name}", name)
            
            # NO PDF for first email (Safety)
            message = create_message(sender_email, to_email, current_subject, body, None)
            success, error_type = send_message(service, 'me', message)
            
            if success:
                df.at[index, 'status'] = 'sent'
                df.at[index, 'date_sent'] = datetime.now().strftime('%Y-%m-%d')
                df.to_csv(EMAILS_FILE, index=False)  # Save immediately
                total_sent += 1
                hourly_count += 1
                delay = random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
                print(f"⏳ Waiting {delay:.1f} seconds...")
                time.sleep(delay)
            else:
                total_failed += 1
                if error_type in ['quota_exceeded', 'auth_error']:
                    break
        
        # Save after new loop
        df.to_csv(EMAILS_FILE, index=False)

    elif mode == "followup":
        # Run follow-up logic ONLY
        if FOLLOW_UP_ENABLED:
            total_sent = send_follow_ups(service, df) 
            # Note: send_follow_ups needs to return count to update total_sent
            # I will need to update send_follow_ups to be standalone or handle the counting
        
        # Save after followups
        df.to_csv(EMAILS_FILE, index=False)

    print("\n" + "=" * 60)
    print("📊 Daily Summary")
    print(f"✓ Total Activities: {total_sent}")
    print("=" * 60)

# --- PDF Attachment ---
PDF_FILE = 'attachment.pdf'  # Name of the PDF file to attach (place in same folder)

# --- Email Content ---
# --- Email Templates (ROTATING TO PREVENT BLOCKING) ---
import random

# Default fallback (if rotation fails)
SUBJECT = "QA Engineer - Exploring Opportunities"
BODY_TEMPLATE = """Hi {name},

I came across your profile and noticed you recruit for your company. I'm a QA Engineer with experience in manual and API testing.

I'm currently exploring new opportunities and wanted to check if you have any QA positions that might be a good fit.

Happy to share my resume if there's interest.

Best regards,
Yashwanth
"""

# List of templates to rotate through
EMAIL_TEMPLATES = [
    {
        "subject": "QA / Software Testing Opportunity",
        "body": """Dear Recruiter,

I hope you are doing well.

I am reaching out to explore Quality Assurance / Software Testing opportunities that match my experience. I have over 2 years of experience in manual testing, API testing, and QA processes across web and enterprise applications.

I would be happy to share my resume for your review. Let me know if there are any suitable openings matching my profile.

Thank you for your time.

Best regards,
Yashwanth L
+91 8792350265
yashwanthlakshmipathi3@gmail.com"""
    },
    {
        "subject": "Application for Quality Assurance Engineer",
        "body": """Dear Hiring Team,

I am writing to apply for Quality Assurance / Software Testing roles. I have 2+ years of hands-on experience in functional, regression, exploratory, and UAT testing, along with API testing using Postman and Swagger.

I have worked in Agile environments, validated backend data using SQL, and tracked defects using JIRA. I can share my resume if this aligns with your needs.

Regards,
Yashwanth L
+91 8792350265
yashwanthlakshmipathi3@gmail.com"""
    },
    {
        "subject": "QA Engineer Profile",
        "body": """Hi,

I am writing to express my interest in QA / Software Testing openings. I have experience in manual testing, API testing, backend validation, and Agile QA processes.

Please let me know if my profile suits any current or upcoming requirements. I am happy to provide my resume upon request.

Thanks & regards,
Yashwanth L
+91 8792350265
yashwanthlakshmipathi3@gmail.com"""
    },
    {
        "subject": "Exploring QA / Testing Opportunities",
        "body": """Hi {name},

I hope you are doing well.

I am reaching out to check if there are any Quality Assurance / Software Testing opportunities available. I have 2+ years of experience in manual testing, API testing, and defect tracking using JIRA in Agile environments.

I'd be glad to share my resume for your reference if there is interest.

Thank you,
Yashwanth L
+91 8792350265
yashwanthlakshmipathi3@gmail.com"""
    }
]


# --- Follow-Up Configuration ---
FOLLOW_UP_DAYS = 3  # Send follow-up after 3 days
FOLLOW_UP_ENABLED = True

# Follow-up Templates (Rotated)
FOLLOW_UP_TEMPLATES = [
    {
        "subject": "Re: QA Engineer – Exploring Opportunities", # Re: keeps thread context
        "body": """Hi {name},

I wanted to quickly follow up on my previous email.

I’m very interested in exploring QA opportunities with your team. I’ve attached my resume for your review, which details my experience in manual and API testing.

Please let me know if you have any questions or if there’s a good time to connect.

Best regards,
Yashwanth"""
    },
    {
        "subject": "Re: QA Engineer | Open to New Roles",
        "body": """Hi {name},

Following up on my note from a few days ago.

I’ve attached my resume to give you a better idea of my background in QA automation and manual testing. I'd love to see if my skills match any open roles you have.

Looking forward to hearing from you.

Thanks,
Yashwanth"""
    },
    {
        "subject": "Re: Checking on QA Opportunities",
        "body": """Hi {name},

I know you’re busy, so I’ll be brief.

I’m attaching my resume here for your reference. I really believe my experience in API and manual testing could be valuable to your clients/company.

Would love to chat if you have a moment.

Best,
Yashwanth"""
    }
]

def get_random_followup_template():
    """Select a random follow-up template."""
    template = random.choice(FOLLOW_UP_TEMPLATES)
    return template["subject"], template["body"]

def send_follow_ups(service, df):
    """Check for emails that need a follow-up and send them."""
    print("\n" + "=" * 60)
    print("🔄 Checking for Follow-ups...")
    print("=" * 60)
    
    count = 0
    today = datetime.now()
    
    # Ensure date_sent column exists
    if 'date_sent' not in df.columns:
        df['date_sent'] = None
    if 'follow_up_status' not in df.columns:
        df['follow_up_status'] = 'pending'
        
    for index, row in df.iterrows():
        # Check daily limit (shared with new emails)
        if count >= MAX_EMAILS_PER_DAY:
            print(f"Daily limit reached during follow-ups.")
            break

        # Criteria for follow-up:
        # 1. Status is 'sent' (initial email sent)
        # 2. Follow-up status is 'pending' (not yet followed up)
        # 3. Date sent was > FOLLOW_UP_DAYS ago
        
        status = row.get('status', '')
        f_status = row.get('follow_up_status', 'pending')
        date_sent_str = str(row.get('date_sent', ''))
        
        if status == 'sent' and f_status == 'pending' and date_sent_str and date_sent_str != 'nan':
            try:
                date_sent = datetime.strptime(date_sent_str, '%Y-%m-%d').date()
                days_diff = (today.date() - date_sent).days
                
                if days_diff >= FOLLOW_UP_DAYS:
                    # READY TO SEND FOLLOW-UP
                    to_email = row['email']
                    name = row.get('name', 'there')
                    
                    print(f"\nSending Follow-up to: {to_email} (Sent {days_diff} days ago)")
                    
                    # Select random follow-up template
                    f_subject, f_body_template = get_random_followup_template()
                    
                    # If original subject exists, maybe keep it? For now using new subject with Re:
                    # Users often prefer 'Re: Original Subject' to thread it. 
                    # But rotating subjects makes threading harder unless we saved original subject.
                    # We will use the rotated "Re: ..." subjects for simplicity and safety.
                    
                    try:
                        body = f_body_template.format(name=name)
                    except:
                        body = f_body_template.replace("{name}", name)
                        
                    # ATTACH RESUME FOR FOLLOW-UP
                    resume_path = PDF_FILE
                    if not os.path.exists(resume_path):
                        print(f"⚠️ Resume file {resume_path} not found. Skipping attachment.")
                        resume_path = None
                    
                    message = create_message(sender_email, to_email, f_subject, body, resume_path)
                    success, error_type = send_message(service, 'me', message)
                    
                    if success:
                        df.at[index, 'follow_up_status'] = 'sent'
                        df.at[index, 'follow_up_date'] = today.strftime('%Y-%m-%d')
                        df.to_csv(EMAILS_FILE, index=False)  # Save immediately
                        count += 1
                        
                        # Random delay
                        delay = random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
                        print(f"⏳ Waiting {delay:.1f} seconds before next email...")
                        time.sleep(delay)
                    else:
                        print(f"❌ Failed to send follow-up.")
                        
            except ValueError:
                continue # Skip if date format error
                
    return count

def get_random_template():
    """Select a random template from the list."""
    template = random.choice(EMAIL_TEMPLATES)
    return template["subject"], template["body"]

def is_in_allowed_time_window():
    """Check if current time is within allowed sending windows."""
    current_time = datetime.now()
    current_hour = current_time.hour
    current_minute = current_time.minute
    
    for start_hour, start_min, end_hour, end_min in TIME_WINDOWS:
        # Convert to minutes for easier comparison
        current_total_min = current_hour * 60 + current_minute
        start_total_min = start_hour * 60 + start_min
        end_total_min = end_hour * 60 + end_min
        
        if start_total_min <= current_total_min <= end_total_min:
            return True, f"{start_hour}:{start_min:02d} - {end_hour}:{end_min:02d}"
    
    return False, None

def get_next_allowed_time():
    """Get the next allowed sending time window."""
    current_time = datetime.now()
    current_hour = current_time.hour
    current_minute = current_time.minute
    current_total_min = current_hour * 60 + current_minute
    
    # Check today's remaining windows
    for start_hour, start_min, end_hour, end_min in TIME_WINDOWS:
        start_total_min = start_hour * 60 + start_min
        if current_total_min < start_total_min:
            return f"Today at {start_hour}:{start_min:02d}"
    
    # Otherwise, next allowed day
    current_weekday = current_time.weekday()
    if current_weekday in ALLOWED_WEEKDAYS:
        # Check if there's a next allowed day this week
        for day in ALLOWED_WEEKDAYS:
            if day > current_weekday:
                days_ahead = day - current_weekday
                next_day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][day]
                return f"{next_day} at {TIME_WINDOWS[0][0]}:{TIME_WINDOWS[0][1]:02d}"
    
    # Next week
    next_allowed_day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][ALLOWED_WEEKDAYS[0]]
    return f"Next {next_allowed_day} at {TIME_WINDOWS[0][0]}:{TIME_WINDOWS[0][1]:02d}"

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
    message['from'] = f"{SENDER_NAME} <{sender}>"
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

def send_message(service, user_id, message, retry_count=0):
    """Send an email message with retry logic and quota detection."""
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print(f'✓ Message Id: {message["id"]} sent successfully.')
        return True, None
    except HttpError as error:
        error_details = str(error)
        
        # Check for quota exceeded errors
        if '429' in error_details or 'quotaExceeded' in error_details or 'userRateLimitExceeded' in error_details:
            print(f'⚠ QUOTA EXCEEDED: {error}')
            print(f'⏸ You have hit Gmail\'s rate limit. Waiting for extended period...')
            return False, 'quota_exceeded'
        
        # Check for authentication errors
        if '401' in error_details or 'invalid_grant' in error_details:
            print(f'⚠ AUTHENTICATION ERROR: {error}')
            return False, 'auth_error'
        
        # Retry with exponential backoff for temporary errors
        if retry_count < MAX_RETRIES and ('500' in error_details or '503' in error_details):
            wait_time = EXPONENTIAL_BACKOFF_BASE ** retry_count
            print(f'⚠ Temporary error. Retrying in {wait_time} seconds... (Attempt {retry_count + 1}/{MAX_RETRIES})')
            time.sleep(wait_time)
            return send_message(service, user_id, message, retry_count + 1)
        
        print(f'✗ An error occurred: {error}')
        return False, 'send_error'

def run_campaign():
    """Run the email campaign and return stats."""
    stats = {
        "sent_new": 0,
        "sent_followup": 0,
        "failed": 0,
        "mode": "none",
        "message": ""
    }

    print("\n" + "=" * 60)
    print("🚀 Gmail Bulk Email Sender with Anti-Blocking Protection")
    print("=" * 60)
    
    # 1. Load Data
    if not os.path.exists(EMAILS_FILE):
        print(f"❌ Error: {EMAILS_FILE} not found.")
        stats["message"] = f"Error: {EMAILS_FILE} not found."
        return stats
    
    df = pd.read_csv(EMAILS_FILE)
    
    # Normalize headers to support "Name", "Email", "Status", "Follow Up Status"
    df.columns = [c.strip().lower().replace(' ', '_').replace('-', '_') for c in df.columns]

    if 'status' not in df.columns:
        df['status'] = 'pending'
    if 'date_sent' not in df.columns:
        df['date_sent'] = None
    df['date_sent'] = df['date_sent'].astype(object)

    if 'follow_up_status' not in df.columns:
        df['follow_up_status'] = 'pending'

    if 'follow_up_date' not in df.columns:
        df['follow_up_date'] = None
    df['follow_up_date'] = df['follow_up_date'].astype(object)
    
    pending_emails = df[df['status'] == 'pending']
    
    # Check for PDF
    pdf_path = PDF_FILE if os.path.exists(PDF_FILE) else None
    if pdf_path:
        print(f"📎 PDF Attachment found: {os.path.basename(pdf_path)}")
    else:
        print("ℹ️  No PDF attachment found (sending plain text only).")
    
    # 2. Authenticate
    print("\n🔐 Authenticating with Gmail...")
    service = authenticate_gmail()
    if not service:
        print("❌ Authentication failed.")
        stats["message"] = "Authentication failed."
        return stats
    
    # Get user profile
    profile = service.users().getProfile(userId='me').execute()
    sender_email = profile['emailAddress']
    print(f"✓ Authenticated as: {sender_email}")

    # 3. Determine Mode
    current_time = datetime.now()
    current_weekday = current_time.weekday()
    
    mode = "none"
    if current_weekday in ALLOWED_NEW_EMAIL_DAYS:
        mode = "new"
        print("✅ Mode: Sending NEW EMAILS today")
    elif current_weekday in ALLOWED_FOLLOWUP_DAYS:
        mode = "followup"
        print("\n✅ Mode: Sending FOLLOW-UPS today")
    else:
        print("\n⏸ No sending allowed today (Weekend).")
        stats["message"] = "Weekend - No sending allowed."
        return stats
        
    stats["mode"] = mode

    # 4. Check Time Window
    in_window, window_time = is_in_allowed_time_window()
    if not in_window:
        print(f"\n⏸ Outside allowed time windows.")
        msg = f"Outside allowed time ({current_time.strftime('%I:%M %p')}). Next: {get_next_allowed_time()}"
        print(msg)
        stats["message"] = msg
        return stats

    # 5. Execute
    total_sent = 0
    total_failed = 0
    hour_start_time = datetime.now()
    hourly_count = 0

    if mode == "new":
        print("\n📧 Starting NEW Email Loop...")
        for index, row in pending_emails.iterrows():
            if total_sent >= MAX_EMAILS_PER_DAY:
                print(f"\n⏸ Daily limit of {MAX_EMAILS_PER_DAY} reached.")
                stats["message"] = "Daily limit reached."
                break
            
            if hourly_count >= MAX_EMAILS_PER_HOUR:
                wait_time = 3600 - (datetime.now() - hour_start_time).seconds
                if wait_time > 0:
                    print(f"\n⏸ Hourly limit reached. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                hourly_count = 0
                hour_start_time = datetime.now()

            # Batch break
            if total_sent > 0 and total_sent % BATCH_SIZE == 0:
                print(f"⏸ Taking {BATCH_BREAK_MINUTES} min break...")
                time.sleep(BATCH_BREAK_MINUTES * 60)

            to_email = row['email']
            name = row.get('name', 'there')
            print(f"\n[{total_sent + 1}] Sending to: {to_email}")
            
            current_subject, current_body_template = get_random_template()
            try:
                body = current_body_template.format(name=name)
            except:
                body = current_body_template.replace("{name}", name)
            
            message = create_message(sender_email, to_email, current_subject, body, None)
            success, error_type = send_message(service, 'me', message)
            
            if success:
                df.at[index, 'status'] = 'sent'
                df.at[index, 'date_sent'] = datetime.now().strftime('%Y-%m-%d')
                df.to_csv(EMAILS_FILE, index=False)  # Save immediately
                total_sent += 1
                hourly_count += 1
                delay = random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
                print(f"⏳ Waiting {delay:.1f} seconds...")
                time.sleep(delay)
            else:
                total_failed += 1
                if error_type in ['quota_exceeded', 'auth_error']:
                    break
        
        # Save
        df.to_csv(EMAILS_FILE, index=False)
        stats["sent_new"] = total_sent
        stats["failed"] = total_failed

    elif mode == "followup":
        if FOLLOW_UP_ENABLED:
            follow_up_count = send_follow_ups(service, df) 
            stats["sent_followup"] = follow_up_count
        
        # Save
        df.to_csv(EMAILS_FILE, index=False)

    print("\n" + "=" * 60)
    print("📊 Daily Summary")
    print(f"✓ New Emails: {stats['sent_new']}")
    print(f"✓ Follow-ups: {stats['sent_followup']}")
    print("=" * 60)
    
    return stats

def main():
    run_campaign()

if __name__ == '__main__':
    main()
