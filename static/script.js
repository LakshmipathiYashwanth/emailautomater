// Load status on page load
document.addEventListener('DOMContentLoaded', function () {
    loadStatus();
    setupFileUploads();
});

// Setup file upload handlers
function setupFileUploads() {
    document.getElementById('csvFile').addEventListener('change', function (e) {
        uploadFile(e.target.files[0], '/api/upload-csv', 'CSV');
    });

    document.getElementById('pdfFile').addEventListener('change', function (e) {
        uploadFile(e.target.files[0], '/api/upload-pdf', 'PDF');
    });

    document.getElementById('credentialsFile').addEventListener('change', function (e) {
        uploadFile(e.target.files[0], '/api/upload-credentials', 'Credentials');
    });
}

// Load current status
async function loadStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        document.getElementById('totalEmails').textContent = data.total;
        document.getElementById('pendingEmails').textContent = data.pending;
        document.getElementById('sentEmails').textContent = data.sent;
        document.getElementById('failedEmails').textContent = data.failed;

        // Update file status indicators
        if (data.has_pdf) {
            document.getElementById('pdfStatus').textContent = '✓ Uploaded';
            document.getElementById('pdfStatus').style.color = '#10b981';
        }

        if (data.has_credentials) {
            document.getElementById('credentialsStatus').textContent = '✓ Uploaded';
            document.getElementById('credentialsStatus').style.color = '#10b981';
        }
    } catch (error) {
        console.error('Error loading status:', error);
    }
}

// Upload file
async function uploadFile(file, endpoint, type) {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showNotification(`${type} uploaded successfully!`, 'success');
            loadStatus();
        } else {
            showNotification(data.error || `Failed to upload ${type}`, 'error');
        }
    } catch (error) {
        showNotification(`Error uploading ${type}: ${error.message}`, 'error');
    }
}

// Update email content
async function updateContent() {
    const subject = document.getElementById('emailSubject').value;
    const body = document.getElementById('emailBody').value;

    if (!subject || !body) {
        showNotification('Please fill in both subject and body', 'error');
        return;
    }

    try {
        const response = await fetch('/api/update-content', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ subject, body })
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('Email content updated successfully!', 'success');
        } else {
            showNotification(data.error || 'Failed to update content', 'error');
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'error');
    }
}

// Send emails
async function sendEmails() {
    const maxEmails = parseInt(document.getElementById('maxEmails').value);
    const sendButton = document.getElementById('sendButton');
    const progressContainer = document.getElementById('progressContainer');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');

    // Disable button
    sendButton.disabled = true;
    sendButton.textContent = 'Sending...';

    // Show progress
    progressContainer.style.display = 'block';
    progressFill.style.width = '0%';

    try {
        const response = await fetch('/api/send-emails', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ max_emails: maxEmails })
        });

        const data = await response.json();

        if (response.ok) {
            // Animate progress
            progressFill.style.width = '100%';
            progressText.textContent = `Successfully sent ${data.sent} emails!`;

            showNotification(data.message, 'success');

            // Reload status after 2 seconds
            setTimeout(() => {
                loadStatus();
                progressContainer.style.display = 'none';
            }, 2000);
        } else {
            showNotification(data.error || 'Failed to send emails', 'error');
            progressContainer.style.display = 'none';
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'error');
        progressContainer.style.display = 'none';
    } finally {
        sendButton.disabled = false;
        sendButton.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="22" y1="2" x2="11" y2="13"/>
                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
            Start Sending
        `;
    }
}

// Download template
async function downloadTemplate() {
    try {
        const response = await fetch('/api/download-template');
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'template.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        showNotification('Template downloaded!', 'success');
    } catch (error) {
        showNotification(`Error downloading template: ${error.message}`, 'error');
    }
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type} show`;

    setTimeout(() => {
        notification.classList.remove('show');
    }, 4000);
}
