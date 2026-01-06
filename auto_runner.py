import time
import schedule
import send_emails as se
from datetime import datetime
import logging

# Setup Logging
logging.basicConfig(
    filename='automation.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

print("=" * 60)
print("🤖 AUTO-PILOT ACTIVATED: Email Automation")
print("=" * 60)
print("✓ This script will run seamlessly in the background.")
print("✓ It checks the schedule every day at 10:00 AM.")
print("✓ Keep this terminal OPEN (minimized is fine).")
print("=" * 60)

def job():
    print(f"\n⏰ Checking schedule for {datetime.now().strftime('%A, %Y-%m-%d')}...")
    logging.info("Checking schedule...")
    
    # Reload config to ensure latest templates/settings
    import importlib
    importlib.reload(se)
    
    # Run the campaign
    # The run_campaign function handles all logic (Day checks, Time windows, Limits)
    try:
        stats = se.run_campaign()
        
        # Log result
        if stats.get('mode') != 'none':
            log_msg = f"Campaign Completed. Sent: {stats.get('sent_new', 0)} new, {stats.get('sent_followup', 0)} follow-ups."
            print(f"✅ {log_msg}")
            logging.info(log_msg)
        else:
            print("⏸ No sending scheduled for today.")
            logging.info("No sending scheduled.")
            
    except Exception as e:
        err_msg = f"CRITICAL ERROR: {str(e)}"
        print(f"❌ {err_msg}")
        logging.error(err_msg)

# Schedule the job to run every day at 10:01 AM (Just inside the 9:30-10:30 window)
schedule.every().day.at("10:01").do(job)

# Also run once immediately on startup if it's within a window? 
# Better to be safe and just wait for the schedule, or ask the user.
# We will run a quick check on startup to show status.

def check_status_on_start():
    print("ℹ️  Current System Status:")
    today = datetime.now().weekday()
    if today in se.ALLOWED_NEW_EMAIL_DAYS:
        print("   • Today is a New Email Day.")
    elif today in se.ALLOWED_FOLLOWUP_DAYS:
        print("   • Today is a Follow-up Day.")
    else:
        print("   • Today is a Rest Day.")
    print(f"   • Next run scheduled for 10:01 AM.")

# Run the job immediately on startup to catch any current valid windows
job()

while True:
    try:
        schedule.run_pending()
        time.sleep(60) # Check every minute
    except KeyboardInterrupt:
        print("\n🛑 Auto-pilot stopped by user.")
        break
    except Exception as e:
        print(f"Error in main loop: {e}")
        logging.error(f"Loop error: {e}")
