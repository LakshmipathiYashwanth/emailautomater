// Load status on page load
document.addEventListener('DOMContentLoaded', function () {
    loadStatus();
    loadTemplates();
    setupFileUploads();

    // Start polling if page refresh happened during run
    setInterval(loadStatus, 5000); // Poll every 5s generally
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

    document.getElementById('tokenFile').addEventListener('change', function (e) {
        uploadFile(e.target.files[0], '/api/upload-token', 'Token');
    });
}

// Load templates
async function loadTemplates() {
    try {
        const response = await fetch('/api/templates');
        const data = await response.json();

        renderTemplates('newTemplates', data.new_email_templates);
        renderTemplates('followupTemplates', data.followup_templates);
    } catch (error) {
        console.error('Error loading templates:', error);
    }
}

function renderTemplates(containerId, templates) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    if (!templates || templates.length === 0) {
        container.innerHTML = '<div class="template-card">No templates found.</div>';
        return;
    }

    templates.forEach((t, index) => {
        const div = document.createElement('div');
        div.className = 'template-card';
        div.innerHTML = `
            <div class="template-subject">#${index + 1}: ${escapeHtml(t.subject)}</div>
            <div class="template-body">${escapeHtml(t.body)}</div>
        `;
        container.appendChild(div);
    });
}

function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.template-list').forEach(l => l.classList.remove('active'));

    if (tab === 'new') {
        document.querySelector('button[onclick="switchTab(\'new\')"]').classList.add('active');
        document.getElementById('newTemplates').classList.add('active');
    } else {
        document.querySelector('button[onclick="switchTab(\'followup\')"]').classList.add('active');
        document.getElementById('followupTemplates').classList.add('active');
    }
}

// Load current status and mode
async function loadStatus() {
    try {
        // 1. Get Mode
        const modeRes = await fetch('/api/mode');
        const modeData = await modeRes.json();
        updateModeBadge(modeData);

        // 2. Get Stats
        const statusRes = await fetch('/api/status');
        const data = await statusRes.json();

        document.getElementById('sentEmails').textContent = data.sent;
        document.getElementById('sentFollowups').textContent = data.sent_followups;
        document.getElementById('pendingEmails').textContent = data.pending;
        document.getElementById('failedEmails').textContent = data.failed;

        // Update indicators
        updateIndicator('pdfStatus', data.has_pdf, '✓ Attached', 'Missing');
        updateIndicator('credentialsStatus', data.has_credentials, '✓ Ready', 'Missing');
        updateIndicator('tokenStatus', data.has_token, '✓ Uploaded', 'Missing (Local Auth Required)');

        // Handle Running State
        const sendButton = document.getElementById('sendButton');
        const progressContainer = document.getElementById('progressContainer');
        const statusText = document.getElementById('campaignStatusText');

        if (data.is_running) {
            sendButton.disabled = true;
            sendButton.textContent = 'Running...';
            progressContainer.style.display = 'block';
            statusText.textContent = "Campaign is actively sending emails...";
            statusText.style.color = "#059669";
        } else {
            sendButton.disabled = false;
            sendButton.innerHTML = `
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="22" y1="2" x2="11" y2="13"/>
                    <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                </svg>
                Start Campaign
            `;
            progressContainer.style.display = 'none';
            if (statusText.textContent.includes("Running")) {
                statusText.textContent = "Last Run Complete. Ready for next batch.";
                statusText.style.color = "#64748b";
            }
        }

    } catch (error) {
        console.error('Error loading status:', error);
    }
}

function updateModeBadge(data) {
    const badge = document.getElementById('modeDisplay');
    const icon = document.getElementById('modeIcon');
    const text = document.getElementById('modeText');

    badge.className = 'mode-badge'; // Reset

    if (data.mode === 'new') {
        badge.classList.add('mode-new');
        icon.textContent = '📧';
        text.textContent = `New Emails Mode (${data.day})`;
    } else if (data.mode === 'followup') {
        badge.classList.add('mode-followup');
        icon.textContent = '🔄';
        text.textContent = `Follow-up Mode (${data.day})`;
    } else {
        badge.classList.add('mode-weekend');
        icon.textContent = '⏸';
        text.textContent = `Weekly Rest (${data.day})`;
    }
}

function updateIndicator(elementId, isActive, activeText, inactiveText) {
    const el = document.getElementById(elementId);
    if (isActive) {
        el.textContent = activeText;
        el.style.color = '#10b981';
    } else {
        el.textContent = inactiveText;
        el.style.color = '#ef4444';
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

        if (response.ok) {
            showNotification(`${type} uploaded successfully!`, 'success');
            loadStatus();
        } else {
            const data = await response.json();
            showNotification(data.error || `Failed to upload ${type}`, 'error');
        }
    } catch (error) {
        showNotification(`Error uploading ${type}: ${error.message}`, 'error');
    }
}

// Send emails (Start Campaign)
async function sendEmails() {
    const sendButton = document.getElementById('sendButton');
    sendButton.disabled = true;
    sendButton.textContent = 'Starting...';

    try {
        const response = await fetch('/api/send-emails', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('Campaign started! Tracking progress...', 'success');
            loadStatus(); // Will detect is_running=true
        } else {
            showNotification(data.error || 'Failed to start campaign', 'error');
            sendButton.disabled = false;
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'error');
        sendButton.disabled = false;
    }
}

// Send Test Email
async function sendTestEmail() {
    const emailInput = document.getElementById('testEmailInput');
    const btn = document.getElementById('testBtn');
    const email = emailInput.value.trim();

    if (!email) {
        showNotification('Please enter an email address', 'error');
        return;
    }

    btn.disabled = true;
    btn.textContent = 'Sending...';

    try {
        const response = await fetch('/api/send-test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email })
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('✓ Test email sent successfully!', 'success');
            emailInput.value = ''; // Clear input
        } else {
            showNotification(data.error || 'Failed to send test', 'error');
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Send';
    }
}

// Download template
async function downloadTemplate() {
    window.location.href = '/api/download-template';
}

// Helpers
function escapeHtml(text) {
    if (!text) return '';
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type} show`;

    setTimeout(() => {
        notification.classList.remove('show');
    }, 4000);
}
