from flask import Flask, render_template, request, jsonify, send_file
import os
import pandas as pd
import json
import threading
from datetime import datetime
import importlib

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '.'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

EMAILS_FILE = 'emails.csv'
PDF_FILE = 'attachment.pdf'
CREDENTIALS_FILE = 'credentials.json'

# Global state for background campaign
campaign_running = False
last_campaign_stats = {}

def run_campaign_wrapper():
    global campaign_running, last_campaign_stats
    import send_emails as se
    importlib.reload(se)
    
    try:
        print("Starting campaign thread...")
        last_campaign_stats = se.run_campaign()
    except Exception as e:
        print(f"Campaign thread error: {e}")
        last_campaign_stats = {"error": str(e), "message": f"Critical Error: {str(e)}"}
    finally:
        campaign_running = False
        print("Campaign thread finished.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    if os.path.exists(EMAILS_FILE):
        try:
            df = pd.read_csv(EMAILS_FILE)
            
            # Normalize headers
            df.columns = [c.strip().lower().replace(' ', '_').replace('-', '_') for c in df.columns]
            
            # Ensure columns exist
            if 'status' not in df.columns:
                df['status'] = 'pending'
            if 'follow_up_status' not in df.columns:
                df['follow_up_status'] = 'pending'
                
            total = len(df)
            pending = len(df[df['status'] == 'pending'])
            sent = len(df[df['status'] == 'sent'])
            failed = len(df[df['status'] == 'failed'])
            sent_followups = len(df[df['follow_up_status'] == 'sent'])
        except:
            total = 0; pending = 0; sent = 0; failed = 0; sent_followups = 0
    else:
        total = 0; pending = 0; sent = 0; failed = 0; sent_followups = 0
        
    return jsonify({
        'total': total,
        'pending': pending,
        'sent': sent,
        'failed': failed,
        'sent_followups': sent_followups,
        'has_pdf': os.path.exists(PDF_FILE),
        'has_credentials': os.path.exists(CREDENTIALS_FILE),
        'has_token': os.path.exists('token.json'),
        'is_running': campaign_running
    })

@app.route('/api/mode', methods=['GET'])
def get_mode():
    current_time = datetime.now()
    current_weekday = current_time.weekday()
    
    mode = "none"
    try:
        import send_emails as se
        # We don't reload here every time to save perf, mostly valid
        if current_weekday in se.ALLOWED_NEW_EMAIL_DAYS:
            mode = "new"
        elif current_weekday in se.ALLOWED_FOLLOWUP_DAYS:
            mode = "followup"
    except:
        mode = "error"
        
    return jsonify({
        'mode': mode,
        'day': current_time.strftime('%A'),
        'details': last_campaign_stats.get('message', '') if not campaign_running else "Running..."
    })

@app.route('/api/templates', methods=['GET'])
def get_templates():
    try:
        import send_emails as se
        importlib.reload(se)
        return jsonify({
            'new_email_templates': se.EMAIL_TEMPLATES,
            'followup_templates': se.FOLLOW_UP_TEMPLATES
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/send-emails', methods=['POST'])
def send_emails():
    global campaign_running
    
    if campaign_running:
        return jsonify({'error': 'Campaign is already running!'}), 400
        
    campaign_running = True
    
    thread = threading.Thread(target=run_campaign_wrapper)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'message': 'Campaign started in background! Check status for updates.',
        'started': True
    })

# Upload Endpoints
@app.route('/api/upload-csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files: return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'error': 'No file selected'}), 400
    if file and file.filename.endswith('.csv'):
        file.save(EMAILS_FILE)
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid file'}), 400

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files: return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'error': 'No file selected'}), 400
    if file and file.filename.endswith('.pdf'):
        file.save(PDF_FILE)
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid file'}), 400

@app.route('/api/upload-credentials', methods=['POST'])
def upload_credentials():
    if 'file' not in request.files: return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'error': 'No file selected'}), 400
    if file and file.filename.endswith('.json'):
        file.save(CREDENTIALS_FILE)
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid file'}), 400

@app.route('/api/download-template')
def download_template():
    if os.path.exists('recruiter_template.csv'):
        return send_file('recruiter_template.csv', as_attachment=True)
    else:
        # Fallback generator
        template_data = {
            'Sr No': [1],
            'Name': ['John Doe'],
            'Email': ['example1@company.com'],
            'Status': ['pending'],
            'Follow Up Status': ['pending']
        }
        df = pd.DataFrame(template_data)
        df.to_csv('template.csv', index=False)
        return send_file('template.csv', as_attachment=True)

@app.route('/api/send-test', methods=['POST'])
def send_test_email():
    data = request.json
    test_email = data.get('email')
    
    if not test_email:
        return jsonify({'error': 'Test email address required'}), 400
        
    try:
        import send_emails as se
        importlib.reload(se)
        
        # Authenticate
        service = se.authenticate_gmail()
        if not service:
            return jsonify({'error': 'Authentication failed. Check credentials/token.'}), 400
            
        # Get Sender
        profile = service.users().getProfile(userId='me').execute()
        sender_email = profile['emailAddress']
        
        # Get Template
        subject, body_template = se.get_random_template()
        body = body_template.format(name="Test User")
        
        # Create Message (No PDF for safety test, or maybe yes?)
        # Let's attach PDF if it exists to test that too
        pdf_path = se.PDF_FILE if os.path.exists(se.PDF_FILE) else None
        
        message = se.create_message(sender_email, test_email, f"[TEST] {subject}", body, pdf_path)
        success, error = se.send_message(service, 'me', message)
        
        if success:
            return jsonify({'success': True, 'message': f'Test email sent to {test_email}!'})
        else:
            return jsonify({'error': f'Failed to send: {error}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Server starting on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=port)
