# 🚀 Deploy to Render.com - Step by Step Guide

## 📋 Prerequisites
- GitHub account
- Your code pushed to GitHub repository

---

## 🎯 Quick Deployment Steps

### Step 1: Push Code to GitHub

1. **Initialize Git (if not already done):**
   ```bash
   cd "C:\Email - Automater"
   git init
   git add .
   git commit -m "Initial commit - Email Automator"
   ```

2. **Create GitHub Repository:**
   - Go to: https://github.com/new
   - Repository name: `email-automator`
   - Make it **Private** (recommended for security)
   - Click "Create repository"

3. **Push to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/email-automator.git
   git branch -M main
   git push -u origin main
   ```

---

### Step 2: Deploy on Render

1. **Sign Up / Login:**
   - Go to: https://render.com
   - Sign up with GitHub (easiest)

2. **Create New Web Service:**
   - Click "New +" button (top right)
   - Select "Web Service"

3. **Connect Repository:**
   - Find and select your `email-automator` repository
   - Click "Connect"

4. **Configure Service:**
   
   **Name:** `email-automator` (or any name you like)
   
   **Region:** Choose closest to you
   
   **Branch:** `main`
   
   **Runtime:** `Python 3`
   
   **Build Command:**
   ```
   pip install -r requirements.txt
   ```
   
   **Start Command:**
   ```
   gunicorn app:app
   ```
   
   **Instance Type:** `Free`

5. **Click "Create Web Service"**

---

### Step 3: Wait for Deployment

- Render will automatically:
  - ✅ Install dependencies
  - ✅ Build your app
  - ✅ Deploy it
  - ✅ Give you a URL

- **Deployment takes:** ~2-5 minutes

- **Your URL will be:** `https://email-automator-xxxx.onrender.com`

---

## 🎉 You're Live!

Once deployed, you can:
- ✅ Access from anywhere
- ✅ Share the URL with others
- ✅ Upload files via the web interface
- ✅ Send emails from the cloud

---

## ⚠️ Important Notes

### **Free Tier Limitations:**
- ✅ **Pros:**
  - Completely free
  - HTTPS included
  - Auto-deploy on git push
  
- ⚠️ **Cons:**
  - Sleeps after 15 minutes of inactivity
  - Takes ~30 seconds to wake up on first request
  - 750 hours/month free (enough for personal use)

### **File Storage:**
- ⚠️ **Files are ephemeral** on free tier
- Uploaded files (CSV, PDF, credentials) will be lost on restart
- **Solution:** Re-upload files after each restart, or upgrade to paid tier

---

## 🔒 Security Recommendations

### **Before Deploying:**

1. **Add Password Protection** (Optional but recommended):
   
   I can add a simple password to your app. Want me to add this?

2. **Environment Variables** (for sensitive data):
   
   In Render dashboard:
   - Go to "Environment"
   - Add variables:
     ```
     SECRET_KEY=your-random-secret-key
     ```

3. **Update .gitignore:**
   
   Make sure these files are NOT in your GitHub repo:
   ```
   credentials.json
   token.json
   emails.csv
   attachment.pdf
   ```

---

## 🔄 Auto-Deploy

Once set up, every time you push to GitHub:
```bash
git add .
git commit -m "Update"
git push
```

Render automatically redeploys! 🚀

---

## 📊 Monitor Your App

In Render Dashboard:
- **Logs:** See real-time logs
- **Metrics:** CPU, Memory usage
- **Events:** Deployment history

---

## 🆙 Upgrade Options

### **If You Need:**

**Persistent Storage:**
- Upgrade to Starter plan ($7/month)
- Files won't be deleted

**Always Online:**
- Paid plans don't sleep
- Instant response

**Custom Domain:**
- Connect your own domain
- Available on all plans

---

## 🐛 Troubleshooting

### **Build Failed:**
- Check `requirements.txt` is correct
- Verify Python version compatibility

### **App Crashes:**
- Check logs in Render dashboard
- Look for error messages

### **Can't Upload Files:**
- Files upload to temporary storage
- Will be lost on restart (free tier)

### **Authentication Issues:**
- Gmail API requires OAuth flow
- First-time users need to authenticate via browser
- Token stored temporarily

---

## 🎯 Alternative: Railway.app

If you prefer Railway instead:

1. Go to: https://railway.app
2. Sign up with GitHub
3. "New Project" → "Deploy from GitHub"
4. Select your repo
5. Done! (Even easier than Render)

**Railway Pros:**
- $5 free credit/month
- Persistent storage on free tier
- Faster cold starts

---

## 📞 Need Help?

### **Common Issues:**

**Q: Files disappear after restart**
- A: Free tier has ephemeral storage. Re-upload or upgrade.

**Q: App is slow to load**
- A: Free tier sleeps. First request takes ~30s.

**Q: How to update the app?**
- A: Just push to GitHub, Render auto-deploys.

---

## ✅ Checklist

Before deploying:
- [ ] Code pushed to GitHub
- [ ] `.gitignore` configured
- [ ] Sensitive files excluded
- [ ] `render.yaml` in root directory
- [ ] `requirements.txt` updated
- [ ] Ready to deploy!

---

## 🚀 Ready to Deploy?

1. Push your code to GitHub
2. Go to Render.com
3. Connect repository
4. Click deploy
5. Get your URL!

**Want me to help with any specific step?** 🎉
