# 📧 Email Automation Dashboard

A beautiful, modern web interface for automating email sending with Gmail API.

## ✨ Features

- 🎨 **Modern Dark UI** - Beautiful glassmorphism design
- 📊 **Real-time Stats** - Track sent, pending, and failed emails
- 📎 **PDF Attachments** - Automatically attach PDFs to all emails
- 👤 **Personalization** - Use {name} placeholder for personalized emails
- 🔒 **Secure** - Uses Gmail API with OAuth2 authentication
- 📈 **Progress Tracking** - Visual progress bar during sending
- 💾 **Auto-save Progress** - Resume sending from where you left off
- 🛡️ **Anti-Blocking Protection** - Smart delays and rate limiting to prevent account blocking

## 🚨 CRITICAL: Gmail Automation Safety

**⚠️ READ THIS FIRST - YOUR ACCOUNT DEPENDS ON IT**

This tool is configured with **ultra-conservative settings** to prevent Gmail from blocking you:
- ⏱️ **3-5 minute delays** between emails (NOT seconds!)
- 📧 **20 emails/day maximum** (NOT 450!)
- 📅 **Tuesday, Wednesday, Thursday ONLY**
- ⏰ **Specific time windows**:
  - 9:30 AM - 10:30 AM
  - 12:30 PM - 2:00 PM
  - 5:30 PM - 7:00 PM
- 🚫 **NO PDF attachments** (spam trigger)
- 📝 **Plain text only** (no HTML)

**DO NOT change these settings unless you want to get blocked.**

📚 **MUST READ:** 
- `GMAIL_SAFETY_CRITICAL.md` - Critical safety rules
- `CUSTOM_SCHEDULE_GUIDE.md` - Your custom schedule details

## 🚀 Quick Start

### 1. Install Python
Download and install Python from [python.org](https://www.python.org/downloads/)
**Important:** Check "Add Python to PATH" during installation

### 2. Install Dependencies
```bash
cd "C:\Email - Automater"
python -m pip install -r requirements.txt
```

### 3. Get Gmail API Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json` and place in this folder

### 4. Run the Application
```bash
python app.py
```

### 5. Open in Browser
Navigate to: `http://localhost:5000`

## 📝 How to Use

### Step 1: Upload Files
1. **Email List (CSV)** - Click "Download Template" for format
   ```csv
   email,name,status
   john@example.com,John Doe,pending
   jane@example.com,Jane Smith,pending
   ```

2. **PDF Attachment** (Optional) - Upload your PDF file

3. **Credentials** - Upload the `credentials.json` from Google Cloud

### Step 2: Configure Email
- Enter your email subject
- Write your message body
- Use `{name}` to personalize with recipient's name
- Click "Save Content"

### Step 3: Send Emails
- Set max emails per run (default: 450)
- Click "Start Sending"
- First time: Browser will open for Google authentication

## 🛡️ Anti-Blocking Protection (Gmail-Safe)

### Built-in Safety Features:
- ⏱️ **Random Delays**: 3-5 MINUTES between each email (human-like behavior)
- 🎲 **Content Rotation**: Automatically rotates 5 different subject/body templates
- 📦 **Batch Processing**: Sends 5 emails, then takes a 15-minute break
- ⏰ **Rate Limiting**: Max 5 emails/hour, 20 emails/day
- 🔄 **Smart Retries**: Exponential backoff on temporary errors
- 🚨 **Quota Detection**: Auto-stops if Gmail rate limits are hit
- 💾 **Progress Saving**: Resume safely from where you stopped
- 📅 **Custom Schedule**: Monday-Friday only
- ⏰ **Time Windows**: 9:30-10:30 AM, 12:30-2 PM, 5:30-7 PM

### Gmail Sending Limits:
- **Personal Gmail**: 500 emails/day (we use 20 for SAFETY)
- **This is NOT a bug** - Ultra-conservative = Account safety

### Expected Sending Times (REALISTIC):
- **5 emails**: ~20-25 minutes
- **10 emails**: ~45-50 minutes
- **20 emails**: ~1.5-2 hours (across 3 time windows)
- **60 emails/week**: 3 days × 20 emails
- **1500 emails**: ~25 weeks (~6 months)

**Note:** YES, it's SLOW. That's intentional. Slow = Safe = No blocking.

### 📅 Your Custom Schedule:
- **Days**: Tuesday, Wednesday, Thursday ONLY
- **Time Windows**:
  - Morning: 9:30 AM - 10:30 AM
  - Afternoon: 12:30 PM - 2:00 PM
  - Evening: 5:30 PM - 7:00 PM
- **Weekly Capacity**: 60 emails (3 days × 20)
- **Monthly Capacity**: ~240 emails

### 🚨 Why This Schedule?
This pattern is **EXCELLENT** for Gmail because:
- ✅ Irregular weekly pattern (3 days, not 5)
- ✅ Multiple short time windows (not continuous)
- ✅ Natural human behavior times
- ✅ Very hard to detect as automation

### 📚 Critical Reading:
- **`CUSTOM_SCHEDULE_GUIDE.md`** - Complete schedule details
- **`GMAIL_SAFETY_CRITICAL.md`** - MUST READ before sending
- `QUICK_START_ANTI_BLOCKING.md` - Quick reference
- `ANTI_BLOCKING_GUIDE.md` - Detailed guide

## 🌐 Hosting Options

### Local Network Access
```bash
python app.py
# Access from other devices: http://YOUR_IP:5000
```

### Deploy to Cloud

#### Option 1: Heroku
```bash
# Install Heroku CLI
heroku create your-app-name
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

#### Option 2: Railway
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repo
3. Deploy automatically

#### Option 3: PythonAnywhere
1. Upload files to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Configure web app with Flask
3. Set working directory

## 🔧 Configuration

### ⚠️ Current Gmail-Safe Settings:
```python
MIN_DELAY_SECONDS = 180         # 3 minutes (DO NOT REDUCE!)
MAX_DELAY_SECONDS = 300         # 5 minutes
BATCH_SIZE = 5                  # Small batches
BATCH_BREAK_MINUTES = 15        # Long breaks
MAX_EMAILS_PER_HOUR = 5         # Very conservative
MAX_EMAILS_PER_DAY = 20         # Ultra-safe

# Custom Schedule
ALLOWED_WEEKDAYS = [1, 2, 3]    # Tuesday, Wednesday, Thursday
TIME_WINDOWS = [
    (9, 30, 10, 30),            # 9:30 AM - 10:30 AM
    (12, 30, 14, 0),            # 12:30 PM - 2:00 PM
    (17, 30, 19, 0),            # 5:30 PM - 7:00 PM
]
```

### 🚨 WARNING:
**DO NOT change these settings!** They are optimized for Gmail safety.

If you change:
- `MIN_DELAY_SECONDS` to less than 180 → **Account blocked**
- `MAX_EMAILS_PER_DAY` to more than 20 → **Spam flagged**
- `ALLOWED_WEEKDAYS` to include more days → **Bot detected**
- `TIME_WINDOWS` to be continuous → **Automation detected**

**See `CUSTOM_SCHEDULE_GUIDE.md` and `GMAIL_SAFETY_CRITICAL.md` for details.**

## 📊 File Structure

```
Email - Automater/
├── app.py                 # Flask web server
├── send_emails.py         # Email sending logic
├── requirements.txt       # Python dependencies
├── emails.csv            # Email list (auto-generated)
├── attachment.pdf        # PDF attachment (upload via UI)
├── credentials.json      # Gmail API credentials (upload via UI)
├── templates/
│   └── index.html        # Web interface
└── static/
    ├── style.css         # Styling
    └── script.js         # Frontend logic
```

## 🛡️ Security Notes

- Never commit `credentials.json` or `token.json` to version control
- Keep your email list private
- Use environment variables for sensitive data in production

## 📞 Support

For issues or questions, check:
1. Python is installed and in PATH
2. All dependencies are installed
3. `credentials.json` is properly configured
4. Gmail API is enabled in Google Cloud Console

## 📄 License

MIT License - Feel free to use and modify!
