from flask import Flask, render_template, request, jsonify, send_file
import os
import pandas as pd
import json
from send_emails import authenticate_gmail, create_message, send_message
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '.'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

EMAILS_FILE = 'emails.csv'
PDF_FILE = 'attachment.pdf'
CREDENTIALS_FILE = 'credentials.json'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get current status of emails"""
    if not os.path.exists(EMAILS_FILE):
        return jsonify({
            'total': 0,
            'pending': 0,
            'sent': 0,
            'failed': 0,
            'has_pdf': False,
            'has_credentials': False
        })
    
    df = pd.read_csv(EMAILS_FILE)
    if 'status' not in df.columns:
        df['status'] = 'pending'
    
    status_counts = df['status'].value_counts().to_dict()
    
    return jsonify({
        'total': len(df),
        'pending': status_counts.get('pending', 0),
        'sent': status_counts.get('sent', 0),
        'failed': status_counts.get('failed', 0),
        'has_pdf': os.path.exists(PDF_FILE),
        'has_credentials': os.path.exists(CREDENTIALS_FILE)
    })

@app.route('/api/upload-csv', methods=['POST'])
def upload_csv():
    """Upload CSV file with email list"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.endswith('.csv'):
        file.save(EMAILS_FILE)
        return jsonify({'success': True, 'message': 'CSV uploaded successfully'})
    
    return jsonify({'error': 'Invalid file type. Please upload a CSV file'}), 400

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """Upload PDF attachment"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.endswith('.pdf'):
        file.save(PDF_FILE)
        return jsonify({'success': True, 'message': 'PDF uploaded successfully'})
    
    return jsonify({'error': 'Invalid file type. Please upload a PDF file'}), 400

@app.route('/api/upload-credentials', methods=['POST'])
def upload_credentials():
    """Upload credentials.json"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.endswith('.json'):
        file.save(CREDENTIALS_FILE)
        return jsonify({'success': True, 'message': 'Credentials uploaded successfully'})
    
    return jsonify({'error': 'Invalid file type. Please upload a JSON file'}), 400

@app.route('/api/update-content', methods=['POST'])
def update_content():
    """Update email subject and body"""
    data = request.json
    subject = data.get('subject', '')
    body = data.get('body', '')
    
    # Read the current send_emails.py and update the content
    with open('send_emails.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple replacement for SUBJECT
    import re
    content = re.sub(
        r'SUBJECT = ".*?"',
        f'SUBJECT = "{subject}"',
        content
    )
    
    # Replace BODY_TEMPLATE
    content = re.sub(
        r'BODY_TEMPLATE = """.*?"""',
        f'BODY_TEMPLATE = """\n{body}\n"""',
        content,
        flags=re.DOTALL
    )
    
    with open('send_emails.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    return jsonify({'success': True, 'message': 'Email content updated'})

@app.route('/api/send-emails', methods=['POST'])
def send_emails():
    """Start sending emails"""
    data = request.json
    max_emails = data.get('max_emails', 450)
    
    try:
        # Load data
        if not os.path.exists(EMAILS_FILE):
            return jsonify({'error': 'No email list uploaded'}), 400
        
        df = pd.read_csv(EMAILS_FILE)
        if 'status' not in df.columns:
            df['status'] = 'pending'
        
        pending_emails = df[df['status'] == 'pending']
        
        if len(pending_emails) == 0:
            return jsonify({'error': 'No pending emails to send'}), 400
        
        # Check for PDF
        pdf_path = PDF_FILE if os.path.exists(PDF_FILE) else None
        
        # Authenticate
        service = authenticate_gmail()
        if not service:
            return jsonify({'error': 'Authentication failed. Please upload credentials.json'}), 400
        
        profile = service.users().getProfile(userId='me').execute()
        sender_email = profile['emailAddress']
        
        # Get subject and body from send_emails.py
        import send_emails as se
        # Reload the module to get updated values
        import importlib
        importlib.reload(se)
        
        subject = se.SUBJECT
        body_template = se.BODY_TEMPLATE
        
        # Send emails
        count = 0
        for index, row in pending_emails.iterrows():
            if count >= max_emails:
                break
            
            to_email = row['email']
            name = row.get('name', 'there')
            
            body = body_template.format(name=name)
            message = create_message(sender_email, to_email, subject, body, pdf_path)
            success = send_message(service, 'me', message)
            
            if success:
                df.at[index, 'status'] = 'sent'
                count += 1
                time.sleep(2)
            else:
                df.at[index, 'status'] = 'failed'
        
        df.to_csv(EMAILS_FILE, index=False)
        
        return jsonify({
            'success': True,
            'sent': count,
            'message': f'Successfully sent {count} emails'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-template')
def download_template():
    """Download CSV template"""
    template_data = {
        'email': ['example1@email.com', 'example2@email.com'],
        'name': ['John Doe', 'Jane Smith'],
        'status': ['pending', 'pending']
    }
    df = pd.DataFrame(template_data)
    template_path = 'template.csv'
    df.to_csv(template_path, index=False)
    return send_file(template_path, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
