# 🌐 Hosting Guide: Deploying Your Email Automator

You can host this application so it runs 24/7 without your computer being on. However, because it uses **Google OAuth** and **Local Files (CSV tracking)**, there are specific requirements.

---

## ⚠️ Critical Warning: Persistence

**DO NOT use standard "Free Tier" web hosting (like Heroku Free or Render Free) without a Disk.**

*   **Why?** Free tiers reset their filesystem every time they restart (ephemeral storage).
*   **The Risk:** You upload your list, send 10 emails, the server restarts -> **It forgets who it sent to.** Next time, it sends to them AGAIN. 🛑
*   **The Solution:** You MUST use a hosting service with **Persistent Storage (Disk)** or a **VPS**.

---

## ✅ Best Option 1: Cheap VPS (Recommended)
A Virtual Private Server (VPS) is just a remote computer you control. It's cheap, stable, and keeps your files forever.

**Providers:**
*   **DigitalOcean Droplet** ($4/mo)
*   **Hetzner Cloud** (~$4/mo)
*   **AWS Lightsail** ($3.50/mo)

### **Deployment Steps:**

1.  **Create a Ubuntu VPS**.
2.  **SSH into it** (`ssh root@your-ip`).
3.  **Install Python:**
    ```bash
    apt update && apt install python3-pip git -y
    ```
4.  **Clone your code:**
    ```bash
    git clone https://github.com/yourusername/email-automator.git
    cd email-automator
    ```
    *(Or just copy your files using SCP/FileZilla)*
5.  **Install Requirements:**
    ```bash
    pip3 install -r requirements.txt
    pip3 install gunicorn schedule
    ```
6.  **Run with Auto-Runner (Easiest):**
    ```bash
    # Run in background even if you disconnect
    nohup python3 auto_runner.py > output.log 2>&1 &
    ```
    *Now it runs forever.*

7.  **Run the Dashboard (Optional):**
    ```bash
    gunicorn --bind 0.0.0.0:80 app:app
    ```

---

## ✅ Option 2: Render.com (Easiest Web UI)

If you prefer a managed service, use Render but **you typically need the paid Starter plan ($7/mo) + Disk** for true safety. For testing, you can use Free, BUT you must manually download your `emails.csv` after every run to save progress.

### **The "Token Problem" (Auth)**
Server cannot open a browser to log in to Google.
**Solution:**
1.  Run the app **LOCALLY** on your PC first.
2.  Log in and generate `token.json`.
3.  Deploy the app content to Render.
4.  Go to your hosted URL: `https://your-app.onrender.com`.
5.  Use the **"Upload Token"** button to upload your local `token.json` to the server.

---

## 🚀 How to Deploy to Render (Free Tier Test)

1.  **GitHub**: Push your code to a generic private GitHub repo.
2.  **Render**:
    *   New -> **Web Service**.
    *   Connect your Repo.
    *   Runtime: **Python 3**.
    *   Build Command: `pip install -r requirements.txt`
    *   Start Command: `gunicorn app:app`
3.  **Deploy**.
4.  **Configure**:
    *   Open your new URL.
    *   Upload `credentials.json`.
    *   Upload `token.json` (Generated locally).
    *   Upload `emails.csv`.
5.  **Run**: Click Start.

**🛑 REMEMBER ON FREE TIER:**
Before the server "sleeps" (15 min inactivity), click the **Download CSV** (I need to add this button!) or ensure you have a backup. If the server restarts, you must re-upload `emails.csv` with the *updated status*.

---

## 🔒 Security Checklist for Hosting

1.  **Add Password Protection**: Since your dashboard controls emails, you don't want strangers finding the URL.
    *   *Simple:* Add `Flask-BasicAuth` to `app.py`.
2.  **HTTPS**: Render/VPS usually provide this automatically.
3.  **Secrets**: Never commit `token.json` or `credentials.json` to GitHub. Use the upload feature.

---

## 💡 Summary

| Feature | Local PC (Current) | VPS ($4/mo) | Render Free | Render Paid ($7+) |
| :--- | :--- | :--- | :--- | :--- |
| **Setup** | Easy | Medium | Easy | Easy |
| **24/7 Run** | No (PC Sleep) | **Yes** | No (Sleeps) | **Yes** |
| **Data Safe?** | Yes | **Yes** | **NO** (Risky) | Yes |
| **Cost** | Free | $4/mo | Free | ~$7/mo |

**Recommendation:** Stick to **Local PC** if you are okay running it daily. Switch to **VPS** if you want true "set it and forget it" without data risks.
