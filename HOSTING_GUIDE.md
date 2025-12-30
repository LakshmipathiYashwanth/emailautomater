# 🌐 Hosting Guide - Email Automation Dashboard

## 🎯 Hosting Options

Choose the option that best fits your needs:

---

## Option 1: Local Network Access (FREE & EASIEST)

**Best for:** Accessing from devices on the same WiFi network

### Steps:
1. Find your computer's IP address:
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., `192.168.1.100`)

2. Run the app:
   ```bash
   python app.py
   ```

3. Access from any device on the same network:
   ```
   http://YOUR_IP:5000
   ```
   Example: `http://192.168.1.100:5000`

### ✅ Pros:
- Completely free
- No setup required
- Works immediately

### ❌ Cons:
- Only works on local network
- Computer must be running

---

## Option 2: ngrok (FREE - Internet Access)

**Best for:** Quick internet access without deployment

### Steps:

1. **Download ngrok:**
   - Go to: https://ngrok.com/download
   - Sign up for free account
   - Download and extract `ngrok.exe`

2. **Authenticate ngrok:**
   ```bash
   ngrok config add-authtoken YOUR_TOKEN
   ```
   (Get token from ngrok dashboard)

3. **Run your app:**
   ```bash
   python app.py
   ```

4. **In a new terminal, run ngrok:**
   ```bash
   ngrok http 5000
   ```

5. **Copy the URL:**
   You'll see something like:
   ```
   Forwarding: https://abc123.ngrok-free.app -> http://localhost:5000
   ```

6. **Share the URL:**
   Anyone can access: `https://abc123.ngrok-free.app`

### ✅ Pros:
- Free tier available
- Instant internet access
- HTTPS included
- No deployment needed

### ❌ Cons:
- URL changes each time (unless paid plan)
- Computer must stay running
- Free tier has connection limits

---

## Option 3: Railway.app (FREE - Cloud Hosting)

**Best for:** Permanent hosting with custom domain

### Steps:

1. **Prepare files:**
   Create `Procfile` (no extension):
   ```
   web: python app.py
   ```

2. **Create `runtime.txt`:**
   ```
   python-3.11.0
   ```

3. **Update `app.py` (last line):**
   ```python
   if __name__ == '__main__':
       port = int(os.environ.get('PORT', 5000))
       app.run(debug=False, host='0.0.0.0', port=port)
   ```

4. **Sign up at Railway:**
   - Go to: https://railway.app
   - Sign up with GitHub

5. **Deploy:**
   - Click "New Project"
   - Choose "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Python and deploys

6. **Get your URL:**
   - Click "Settings" → "Generate Domain"
   - You'll get: `https://your-app.up.railway.app`

### ✅ Pros:
- Free $5/month credit (enough for small apps)
- Automatic deployments
- Custom domain support
- Always online

### ❌ Cons:
- Requires GitHub account
- Limited free tier

---

## Option 4: Render.com (FREE - Cloud Hosting)

**Best for:** Simple cloud hosting with free tier

### Steps:

1. **Create account:**
   - Go to: https://render.com
   - Sign up with GitHub

2. **Create `render.yaml`:**
   ```yaml
   services:
     - type: web
       name: email-automator
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: python app.py
   ```

3. **Update `app.py`:**
   ```python
   if __name__ == '__main__':
       port = int(os.environ.get('PORT', 5000))
       app.run(debug=False, host='0.0.0.0', port=port)
   ```

4. **Deploy:**
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Render auto-deploys

5. **Access:**
   - You'll get: `https://your-app.onrender.com`

### ✅ Pros:
- Truly free tier (no credit card)
- Auto-deploy from GitHub
- SSL included
- Always online

### ❌ Cons:
- Free tier sleeps after 15 min inactivity
- Slower cold starts

---

## Option 5: PythonAnywhere (FREE - Cloud Hosting)

**Best for:** Python-specific hosting

### Steps:

1. **Sign up:**
   - Go to: https://www.pythonanywhere.com
   - Create free account

2. **Upload files:**
   - Go to "Files" tab
   - Upload all your project files

3. **Create Web App:**
   - Go to "Web" tab
   - Click "Add a new web app"
   - Choose Flask
   - Python version: 3.10

4. **Configure:**
   - Set source code path: `/home/yourusername/Email-Automater`
   - WSGI file: Point to `app.py`

5. **Install dependencies:**
   - Open Bash console
   - Run: `pip install -r requirements.txt`

6. **Reload:**
   - Click "Reload" button
   - Access: `https://yourusername.pythonanywhere.com`

### ✅ Pros:
- Free tier available
- Python-focused
- Easy setup
- Always online

### ❌ Cons:
- Limited CPU on free tier
- No custom domain on free tier

---

## 🎯 My Recommendation

### For Testing:
**Use ngrok** - Fastest way to share with others

### For Production:
**Use Render.com** - Best free tier, no credit card needed

### For Local Use:
**Local Network** - Simplest, no external dependencies

---

## 🔒 Security Considerations

### ⚠️ IMPORTANT:
Before hosting publicly, add these security measures:

1. **Add authentication:**
   ```python
   from flask_httpauth import HTTPBasicAuth
   auth = HTTPBasicAuth()
   
   @auth.verify_password
   def verify_password(username, password):
       if username == "admin" and password == "your_secure_password":
           return username
   
   @app.route('/')
   @auth.login_required
   def index():
       return render_template('index.html')
   ```

2. **Don't commit sensitive files:**
   Create `.gitignore`:
   ```
   credentials.json
   token.json
   emails.csv
   attachment.pdf
   *.pyc
   __pycache__/
   ```

3. **Use environment variables:**
   ```python
   import os
   SECRET_KEY = os.environ.get('SECRET_KEY', 'default-key')
   ```

---

## 📞 Need Help?

Choose your hosting method and I can help you set it up step-by-step!

Which option would you like to use?
