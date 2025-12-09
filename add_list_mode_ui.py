"""
Script to add List Mode UI to index.html
"""

# Read index.html
with open('web/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add List Mode UI after the URL input section
# Find the URL input section and add mode selector before it
list_mode_ui = '''        <!-- Crawl Mode Selector -->
        <section class="crawl-mode-section">
            <div class="url-container">
                <div class="mode-selector">
                    <label class="mode-option">
                        <input type="radio" name="crawlMode" value="standard" checked onchange="switchCrawlMode('standard')">
                        <span class="mode-label">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"/>
                                <path d="M12 6v6l4 2"/>
                            </svg>
                            Standard Crawl
                        </span>
                        <span class="mode-description">Crawl a website starting from one URL</span>
                    </label>
                    <label class="mode-option">
                        <input type="radio" name="crawlMode" value="list" onchange="switchCrawlMode('list')">
                        <span class="mode-label">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                                <path d="M9 12h6m-6 4h6"/>
                            </svg>
                            List Mode
                        </span>
                        <span class="mode-description">Crawl specific URLs from a list</span>
                    </label>
                </div>
            </div>
        </section>

'''

# Insert before the URL input section
url_section_start = '        <!-- URL Input Section -->'
content = content.replace(url_section_start, list_mode_ui + url_section_start)

# Modify the URL input section to be conditional
old_url_input = '''        <!-- URL Input Section -->
        <section class="url-section">
            <div class="url-container">
                <div class="input-group">
                    <label for="urlInput" class="input-label">URL to Crawl</label>
                    <input
                        type="url"
                        id="urlInput"
                        class="url-input"
                        placeholder="https://example.com"
                        onkeypress="handleUrlKeypress(event)"
                    >
                </div>'''

new_url_input = '''        <!-- URL Input Section -->
        <section class="url-section">
            <div class="url-container">
                <!-- Standard Mode Input -->
                <div id="standardModeInput" class="input-group">
                    <label for="urlInput" class="input-label">URL to Crawl</label>
                    <input
                        type="url"
                        id="urlInput"
                        class="url-input"
                        placeholder="https://example.com"
                        onkeypress="handleUrlKeypress(event)"
                    >
                </div>

                <!-- List Mode Input -->
                <div id="listModeInput" class="input-group" style="display: none;">
                    <div class="list-mode-tabs">
                        <button class="list-tab active" onclick="switchListTab('paste')" id="pasteTab">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/>
                                <path d="M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                            </svg>
                            Paste URLs
                        </button>
                        <button class="list-tab" onclick="switchListTab('upload')" id="uploadTab">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                                <polyline points="17 8 12 3 7 8"/>
                                <line x1="12" y1="3" x2="12" y2="15"/>
                            </svg>
                            Upload File
                        </button>
                    </div>

                    <!-- Paste URLs Tab -->
                    <div id="pasteUrlsContent" class="list-tab-content">
                        <label for="urlListText" class="input-label">
                            Paste URLs (one per line)
                            <span class="label-hint">Supports comments with #</span>
                        </label>
                        <textarea
                            id="urlListText"
                            class="url-list-textarea"
                            placeholder="https://example.com/page1&#10;https://example.com/page2&#10;# This is a comment&#10;https://example.com/page3"
                            rows="8"
                            oninput="validateUrlList()"
                        ></textarea>
                        <div class="url-list-stats" id="urlListStats" style="display: none;">
                            <span class="stat-badge stat-success">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                </svg>
                                <span id="validUrlCount">0</span> valid
                            </span>
                            <span class="stat-badge stat-error" id="invalidUrlBadge" style="display: none;">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                </svg>
                                <span id="invalidUrlCount">0</span> invalid
                            </span>
                            <span class="stat-badge stat-info">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                    <path d="M9 10a1 1 0 011-1h4a1 1 0 110 2h-4a1 1 0 01-1-1z"/>
                                </svg>
                                <span id="uniqueDomainCount">0</span> domains
                            </span>
                        </div>
                    </div>

                    <!-- Upload File Tab -->
                    <div id="uploadFileContent" class="list-tab-content" style="display: none;">
                        <label for="urlListFile" class="input-label">
                            Upload TXT File
                            <span class="label-hint">One URL per line</span>
                        </label>
                        <div class="file-upload-area" id="fileUploadArea">
                            <input
                                type="file"
                                id="urlListFile"
                                accept=".txt"
                                onchange="handleFileUpload(event)"
                                style="display: none;"
                            >
                            <label for="urlListFile" class="file-upload-label">
                                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                    <path d="M7 18a4.6 4.4 0 0 1 0 -9a5 4.5 0 0 1 11 2h1a3.5 3.5 0 0 1 0 7h-1"/>
                                    <polyline points="9 15 12 12 15 15"/>
                                    <line x1="12" y1="12" x2="12" y2="21"/>
                                </svg>
                                <span class="upload-text">Click to upload or drag and drop</span>
                                <span class="upload-hint">TXT files only</span>
                            </label>
                            <div id="fileInfo" class="file-info" style="display: none;">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                                </svg>
                                <span id="fileName"></span>
                                <button onclick="clearFile()" class="clear-file-btn">×</button>
                            </div>
                        </div>
                    </div>
                </div>'''

content = content.replace(old_url_input, new_url_input)

# Write modified file
with open('web/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Successfully added List Mode UI to index.html")
print("✓ Added:")
print("  - Crawl mode selector (Standard vs List)")
print("  - URL paste textarea")
print("  - File upload input")
print("  - URL validation stats display")
