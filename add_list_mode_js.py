"""
Script to add List Mode JavaScript functionality to app.js
"""

# JavaScript code to add
list_mode_js = '''
// List Mode Variables
let currentCrawlMode = 'standard';
let currentListTab = 'paste';
let validUrlList = [];
let invalidUrlList = [];

// Switch between Standard and List Mode
function switchCrawlMode(mode) {
    currentCrawlMode = mode;
    const standardInput = document.getElementById('standardModeInput');
    const listInput = document.getElementById('listModeInput');
    
    if (mode === 'standard') {
        standardInput.style.display = 'block';
        listInput.style.display = 'none';
    } else {
        standardInput.style.display = 'none';
        listInput.style.display = 'block';
    }
}

// Switch between Paste and Upload tabs in List Mode
function switchListTab(tab) {
    currentListTab = tab;
    const pasteTab = document.getElementById('pasteTab');
    const uploadTab = document.getElementById('uploadTab');
    const pasteContent = document.getElementById('pasteUrlsContent');
    const uploadContent = document.getElementById('uploadFileContent');
    
    if (tab === 'paste') {
        pasteTab.classList.add('active');
        uploadTab.classList.remove('active');
        pasteContent.style.display = 'block';
        uploadContent.style.display = 'none';
    } else {
        pasteTab.classList.remove('active');
        uploadTab.classList.add('active');
        pasteContent.style.display = 'none';
        uploadContent.style.display = 'block';
    }
}

// Validate URL list from textarea
async function validateUrlList() {
    const textarea = document.getElementById('urlListText');
    const urlText = textarea.value.trim();
    
    if (!urlText) {
        document.getElementById('urlListStats').style.display = 'none';
        return;
    }
    
    try {
        const response = await fetch('/api/parse_url_list', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ urlText: urlText })
        });
        
        const data = await response.json();
        
        if (data.success) {
            validUrlList = data.validUrls;
            invalidUrlList = data.invalidUrls;
            
            // Update stats display
            document.getElementById('validUrlCount').textContent = validUrlList.length;
            document.getElementById('invalidUrlCount').textContent = invalidUrlList.length;
            document.getElementById('uniqueDomainCount').textContent = data.stats.unique_domains;
            
            document.getElementById('urlListStats').style.display = 'flex';
            
            if (invalidUrlList.length > 0) {
                document.getElementById('invalidUrlBadge').style.display = 'inline-flex';
            } else {
                document.getElementById('invalidUrlBadge').style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Error validating URL list:', error);
    }
}

// Handle file upload
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload_url_list', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            validUrlList = data.validUrls;
            invalidUrlList = data.invalidUrls;
            
            // Show file info
            document.getElementById('fileName').textContent = file.name;
            document.getElementById('fileInfo').style.display = 'flex';
            
            // Update textarea with the content
            const textarea = document.getElementById('urlListText');
            textarea.value = validUrlList.join('\\n');
            
            // Switch to paste tab to show results
            switchListTab('paste');
            
            // Validate to show stats
            await validateUrlList();
            
            showNotification(`Loaded ${validUrlList.length} valid URLs from ${file.name}`, 'success');
        } else {
            showNotification(data.error || 'Failed to upload file', 'error');
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        showNotification('Error uploading file', 'error');
    }
}

// Clear uploaded file
function clearFile() {
    document.getElementById('urlListFile').value = '';
    document.getElementById('fileInfo').style.display = 'none';
    validUrlList = [];
    invalidUrlList = [];
}

// Show notification (helper function)
function showNotification(message, type = 'info') {
    // Simple notification - can be enhanced
    const statusText = document.getElementById('statusText');
    if (statusText) {
        statusText.textContent = message;
        setTimeout(() => {
            statusText.textContent = 'Ready';
        }, 3000);
    }
}

'''

# Read app.js
with open('web/static/js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find a good place to insert - after the initial variables or at the beginning
# Insert after the first few lines
lines = content.split('\\n')
insert_index = 10  # After initial setup

# Insert the list mode code
lines.insert(insert_index, list_mode_js)
content = '\\n'.join(lines)

# Also need to modify the toggleCrawl function to handle list mode
# Find and update the toggleCrawl/startCrawl function
old_start_crawl = '''    const url = document.getElementById('urlInput').value.trim();
    
    if (!url) {
        alert('Please enter a URL');
        return;
    }'''

new_start_crawl = '''    let url = '';
    let urlList = [];
    
    if (currentCrawlMode === 'standard') {
        url = document.getElementById('urlInput').value.trim();
        if (!url) {
            alert('Please enter a URL');
            return;
        }
    } else {
        // List mode
        if (validUrlList.length === 0) {
            alert('Please provide a valid URL list');
            return;
        }
        urlList = validUrlList;
    }'''

content = content.replace(old_start_crawl, new_start_crawl)

# Update the fetch call to include urlList
old_fetch_body = '''        body: JSON.stringify({ url: url })'''
new_fetch_body = '''        body: JSON.stringify({ 
            url: url || null,
            urlList: urlList.length > 0 ? urlList : null
        })'''

content = content.replace(old_fetch_body, new_fetch_body)

# Write modified file
with open('web/static/js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Successfully added List Mode JavaScript to app.js")
print("✓ Added functions:")
print("  - switchCrawlMode()")
print("  - switchListTab()")
print("  - validateUrlList()")
print("  - handleFileUpload()")
print("  - clearFile()")
print("✓ Modified toggleCrawl() to support list mode")
