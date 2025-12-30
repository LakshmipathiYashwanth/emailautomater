# 🔐 How to Get credentials.json - Step by Step Guide

## Quick Overview
You need to create a Google Cloud Project and enable Gmail API to get the `credentials.json` file.

---

## 📋 Detailed Steps:

### Step 1: Go to Google Cloud Console
🔗 **Link:** https://console.cloud.google.com/

### Step 2: Create a New Project
1. Click on the project dropdown (top left, next to "Google Cloud")
2. Click **"NEW PROJECT"**
3. Enter project name: `EmailAutomation` (or any name you like)
4. Click **"CREATE"**
5. Wait for the project to be created (takes ~10 seconds)
6. Select your new project from the dropdown

### Step 3: Enable Gmail API
1. In the search bar at the top, type: **"Gmail API"**
2. Click on **"Gmail API"** from the results
3. Click the **"ENABLE"** button
4. Wait for it to enable (~5 seconds)

### Step 4: Configure OAuth Consent Screen
1. Go to: **APIs & Services** → **OAuth consent screen** (left sidebar)
2. Select **"External"** user type
3. Click **"CREATE"**
4. Fill in the required fields:
   - **App name:** Email Automator
   - **User support email:** Your email address
   - **Developer contact:** Your email address
5. Click **"SAVE AND CONTINUE"**
6. On the "Scopes" page, click **"SAVE AND CONTINUE"** (no changes needed)
7. On "Test users" page:
   - Click **"ADD USERS"**
   - Enter your Gmail address
   - Click **"ADD"**
   - Click **"SAVE AND CONTINUE"**
8. Click **"BACK TO DASHBOARD"**

### Step 5: Create OAuth 2.0 Credentials
1. Go to: **APIs & Services** → **Credentials** (left sidebar)
2. Click **"+ CREATE CREDENTIALS"** (top)
3. Select **"OAuth client ID"**
4. For "Application type", select **"Desktop app"**
5. Name: `Email Automator Desktop`
6. Click **"CREATE"**
7. A popup will appear with your credentials

### Step 6: Download credentials.json
1. In the popup, click **"DOWNLOAD JSON"**
2. Save the file
3. **IMPORTANT:** Rename it to exactly `credentials.json`
4. Move it to: `C:\Email - Automater\credentials.json`

---

## ✅ Verification

After placing `credentials.json` in the folder, you should have:
```
C:\Email - Automater\
├── credentials.json  ← This file
├── app.py
├── send_emails.py
└── ...
```

---

## 🎯 What Happens Next?

When you run the application for the first time:
1. A browser window will open
2. You'll be asked to log in to your Google account
3. Click **"Allow"** to grant permissions
4. The app will save a `token.json` file for future use
5. You won't need to login again unless you revoke access

---

## ⚠️ Important Notes

- **Keep `credentials.json` private** - Don't share it with anyone
- **Test users:** Only the email you added as a test user can authenticate
- **Publishing:** The app will show "unverified" warning - this is normal for personal use
- **Scopes:** The app only requests permission to send emails (not read)

---

## 🔗 Quick Links

- **Google Cloud Console:** https://console.cloud.google.com/
- **Gmail API Documentation:** https://developers.google.com/gmail/api
- **OAuth 2.0 Setup:** https://console.cloud.google.com/apis/credentials

---

## 🆘 Troubleshooting

**Problem:** Can't find "Gmail API"
- **Solution:** Make sure you've selected your project from the dropdown

**Problem:** OAuth consent screen asks for verification
- **Solution:** Choose "External" and add yourself as a test user

**Problem:** Downloaded file has a different name
- **Solution:** Rename it to exactly `credentials.json` (case-sensitive)

**Problem:** "Access blocked" error
- **Solution:** Add your email to test users in OAuth consent screen

---

## 🎉 You're Done!

Once you have `credentials.json` in place, you can:
1. Run `python app.py`
2. Open `http://localhost:5000`
3. Upload your files and start sending emails!
