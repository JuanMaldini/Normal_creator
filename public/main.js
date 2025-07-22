const dropArea = document.getElementById('drop-area');
const output = document.getElementById('output');
const copyBtn = document.getElementById('copy-btn');
const downloadBtn = document.getElementById('download-btn');
const statusMessage = document.getElementById('status-message');
const strengthBtn = document.getElementById('strength-btn');
const strengthDropdown = document.getElementById('strength-dropdown');
const formatBtn = document.getElementById('format-btn');
const formatDropdown = document.getElementById('format-dropdown');

let filePath = '';
let strength = 2;
let format = 'png';

// Function to show status messages
function showStatus(message, type = 'info') {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    
    if (type === 'success' || type === 'error') {
        setTimeout(() => {
            statusMessage.textContent = '';
            statusMessage.className = 'status-message';
        }, 5000);
    }
}

// Download repository functionality
downloadBtn.addEventListener('click', async () => {
    downloadBtn.disabled = true;
    downloadBtn.textContent = '⏳ Downloading...';
    showStatus('Downloading BumpToNormalMap repository...', 'info');
    
    try {
        const response = await fetch('/download-repo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showStatus(result.message, 'success');
            downloadBtn.textContent = '✅ Downloaded';
        } else {
            showStatus(`Error: ${result.error}`, 'error');
            downloadBtn.textContent = '❌ Error';
            setTimeout(() => {
                downloadBtn.textContent = 'Update';
                downloadBtn.disabled = false;
            }, 3000);
        }
    } catch (error) {
        showStatus(`Network error: ${error.message}`, 'error');
        downloadBtn.textContent = '❌ Error';
        setTimeout(() => {
            downloadBtn.textContent = 'Update';
            downloadBtn.disabled = false;
        }, 3000);
    }
});

strengthBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    strengthDropdown.classList.toggle('show');
    formatDropdown.classList.remove('show');
});

formatBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    formatDropdown.classList.toggle('show');
    strengthDropdown.classList.remove('show');
});

strengthDropdown.addEventListener('click', (e) => {
    if (e.target.dataset.strength) {
        strength = parseInt(e.target.dataset.strength);
        strengthBtn.textContent = `💪 ${strength}`;
        strengthDropdown.classList.remove('show');
    }
});

formatDropdown.addEventListener('click', (e) => {
    if (e.target.dataset.format) {
        format = e.target.dataset.format;
        formatBtn.textContent = `📁 ${format}`;
        formatDropdown.classList.remove('show');
    }
});

document.addEventListener('click', () => {
    strengthDropdown.classList.remove('show');
    formatDropdown.classList.remove('show');
});

// Drag events
['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropArea.classList.add('dragover');
    });
});
['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropArea.classList.remove('dragover');
    });
});

// Drop event
 dropArea.addEventListener('drop', async (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        // Try to get absolute path (only works in Electron or with backend)
        if (file.path) {
            filePath = file.path;
        } else {
            // Fallback: show file name only
            filePath = file.name;
        }
        output.textContent = filePath;
        copyBtn.disabled = false;
    }
});

copyBtn.addEventListener('click', () => {
    if (filePath) {
        const command = `python bumptonormalmap.py ${filePath} ${strength} ${format}`;
        navigator.clipboard.writeText(command);
        copyBtn.textContent = 'Go!';
        setTimeout(() => {
            copyBtn.textContent = 'Run';
        }, 1500);
    }
});
