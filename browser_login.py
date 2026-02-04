import os
from playwright.sync_api import sync_playwright

# Exact Profile Path provided by User
USER_DATA_DIR = r"C:\Users\GLB-BLR-126\AppData\Local\Google\Chrome\User Data\Profile 1"

def login_mode():
    print("=" * 60)
    print("🔐 CHROME PROFILE 1 SETUP")
    print("=" * 60)
    print("⚠️  CLOSE ALL CHROME WINDOWS FIRST!")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            channel="chrome",
            args=[
                "--start-maximized", 
                "--disable-blink-features=AutomationControlled"
            ]
        )
        page = browser.pages[0]
        page.goto("https://gmail.com")
        
        print("\n⏳ Waiting for you to log in and close the browser...")
        try:
            page.wait_for_event("close", timeout=0) 
        except:
            pass
            
        print("✅ Bot Profile is ready!")

if __name__ == "__main__":
    login_mode()
