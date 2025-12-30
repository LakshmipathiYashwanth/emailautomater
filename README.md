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

## 🎯 Gmail Sending Limits

- **Personal Gmail**: 500 emails/day
- **Google Workspace**: 2000 emails/day

The script automatically tracks progress and can be run multiple days to send all emails.

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

Edit `send_emails.py` to customize:
- `MAX_EMAILS_PER_DAY` - Daily sending limit
- `SLEEP_BETWEEN_EMAILS` - Delay between sends (seconds)

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
