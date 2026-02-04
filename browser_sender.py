import os
import time
import pandas as pd
import random
from playwright.sync_api import sync_playwright
from datetime import datetime

# --- Configuration ---
EMAILS_FILE = 'emails.csv'
PDF_FILE = 'attachment.pdf'
# The parent folder of all Chrome profiles
USER_DATA_DIR = r"C:\Users\GLB-BLR-126\AppData\Local\Google\Chrome\User Data"

# Human-Like Delays
MIN_DELAY_SECONDS = 120  # 2 minutes minimum
MAX_DELAY_SECONDS = 300  # 5 minutes maximum
MAX_EMAILS_PER_DAY = 25  # Slightly adjusted for safety

# List of templates to rotate through (Personalized)
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

def human_typing(page, selector, text):
    """Types text like a human with random delays between characters."""
    page.wait_for_selector(selector)
    page.focus(selector)
    for char in text:
        page.keyboard.type(char)
        time.sleep(random.uniform(0.05, 0.15))

def human_thinking(min_sec=2, max_sec=5):
    """Simulates a human 'thinking' or pausing."""
    time.sleep(random.uniform(min_sec, max_sec))

def move_mouse_naturally(page):
    """Simulates random mouse movements across segments of the screen."""
    width, height = 1280, 720 # Default or detected
    for _ in range(3):
        x = random.randint(100, width - 100)
        y = random.randint(100, height - 100)
        page.mouse.move(x, y, steps=10)
        time.sleep(random.uniform(0.1, 0.3))

def get_random_template():
    template = random.choice(EMAIL_TEMPLATES)
    return template["subject"], template["body"]

def run_browser_campaign():
    print("=" * 60)
    print("🚀 HUMAN-LIKE BROWSER EMAIL SENDER")
    print("=" * 60)
    print("⚠️  Using Profile 1. Ensure other Chrome instances are CLOSED.")
    
    if not os.path.exists(EMAILS_FILE):
        print(f"❌ Error: {EMAILS_FILE} not found.")
        return

    df = pd.read_csv(EMAILS_FILE)
    df.columns = [c.strip().lower().replace(' ', '_').replace('-', '_') for c in df.columns]
    
    if 'status' not in df.columns: df['status'] = 'pending'
    if 'date_sent' not in df.columns: df['date_sent'] = None
    df['date_sent'] = df['date_sent'].astype(object)

    today_str = datetime.now().strftime('%Y-%m-%d')
    emails_sent_today = len(df[df['date_sent'].astype(str) == today_str])
    
    if emails_sent_today >= MAX_EMAILS_PER_DAY:
        print(f"✅ Daily limit of {MAX_EMAILS_PER_DAY} reached for today.")
        return

    pending_emails = df[df['status'] == 'pending']
    print(f"📧 Found {len(pending_emails)} pending emails.")

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,
                channel="chrome",
                args=[
                    "--start-maximized", 
                    "--disable-blink-features=AutomationControlled",
                    "--profile-directory=Profile 1",
                    "--no-sandbox",
                    "--disable-infobars",
                    "--ignore-certificate-errors"
                ],
                ignore_default_args=["--enable-automation"],
                slow_mo=50  # Global slow down for visual cues
            )
            
            # Ensure we have a valid page
            if not browser.pages:
                page = browser.new_page()
            else:
                page = browser.pages[0]
            
            print("🌐 Navigating to Gmail...")
            page.goto("https://mail.google.com/mail/u/0/", wait_until="load", timeout=60000)
            
            # Additional check: if still on about:blank, try again
            if page.url == "about:blank":
                page.goto("https://mail.google.com/mail/u/0/", wait_until="load")
            
            # 1. Login verification (Human-like wait)
            try:
                page.wait_for_selector("a[aria-label*='Inbox']", timeout=20000)
                print("✓ Logged in as User.")
            except:
                print("❌ Not logged in. Please log in manually in the opened browser first.")
                page.wait_for_timeout(60000) # Give time for manual login
                return

            for index, row in pending_emails.iterrows():
                if emails_sent_today >= MAX_EMAILS_PER_DAY: break

                to_email = row['email']
                name = row.get('name', 'there')
                
                print(f"\n[{emails_sent_today + 1}] Processing recruiter: {to_email}")
                
                # Random segment thinking before starting
                human_thinking(3, 7)
                move_mouse_naturally(page)

                # 2. Click Compose
                page.click("div[role='button'][gh='cm']")
                page.wait_for_selector("div[role='dialog']")
                human_thinking(1, 3)

                # 3. Type 'To'
                human_typing(page, "input[peoplekit-id]", to_email)
                page.keyboard.press("Enter")
                human_thinking(1, 2)

                # 4. Type 'Subject'
                subj, body_tpl = get_random_template()
                try: body_text = body_tpl.format(name=name)
                except: body_text = body_tpl.replace("{name}", name)
                
                human_typing(page, "input[name='subjectbox']", subj)
                human_thinking(1, 2)

                # 5. Type Body
                page.click("div[aria-label='Message Body']")
                human_typing(page, "div[aria-label='Message Body']", body_text)
                human_thinking(2, 4)

                # 6. Attach File (Human behavior: checking files)
                if os.path.exists(PDF_FILE):
                    print("   📎 Attaching resume...")
                    with page.expect_file_chooser() as fc_info:
                        page.click("div[command='Files']")
                    file_chooser = fc_info.value
                    file_chooser.set_files(os.path.abspath(PDF_FILE))
                    time.sleep(random.uniform(5, 8)) # Wait for upload

                # 7. Final Check & Send
                human_thinking(2, 5)
                print("   🚀 Sending...")
                page.keyboard.down("Control")
                page.keyboard.press("Enter")
                page.keyboard.up("Control")
                
                # Check for 'Message sent' popup
                time.sleep(3)
                
                # Update CSV
                df.at[index, 'status'] = 'sent'
                df.at[index, 'date_sent'] = today_str
                df.to_csv(EMAILS_FILE, index=False)
                
                emails_sent_today += 1
                
                delay = random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
                print(f"⏳ Human rest for {delay/60:.1f} minutes...")
                time.sleep(delay)

            print("✅ Session complete.")
            browser.close()

        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_browser_campaign()
