"""
Script to add list mode API endpoints to main.py
"""

# Read main.py
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Modify start_crawl endpoint to accept url_list
old_start_crawl_data = '''    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'success': False, 'error': 'URL is required'})'''

new_start_crawl_data = '''    data = request.get_json()
    url = data.get('url')
    url_list = data.get('urlList', [])

    # Either url or url_list must be provided
    if not url and not url_list:
        return jsonify({'success': False, 'error': 'Either URL or URL list is required'})'''

content = content.replace(old_start_crawl_data, new_start_crawl_data)

# 2. Modify crawler.start_crawl call to include url_list
old_crawl_call = '    success, message = crawler.start_crawl(url, user_id=user_id, session_id=session_id)'
new_crawl_call = '    success, message = crawler.start_crawl(url, user_id=user_id, session_id=session_id, url_list=url_list)'

content = content.replace(old_crawl_call, new_crawl_call)

# 3. Add new API endpoints for URL list parsing and file upload
# Find a good place to insert - after the start_crawl endpoint
api_endpoints = '''

@app.route('/api/parse_url_list', methods=['POST'])
@login_required
def parse_url_list():
    """Parse and validate a URL list from text"""
    from src.utils.url_list_parser import parse_url_list, get_url_statistics
    
    data = request.get_json()
    url_text = data.get('urlText', '')
    
    if not url_text:
        return jsonify({'success': False, 'error': 'URL text is required'})
    
    try:
        valid_urls, invalid_urls = parse_url_list(url_text)
        stats = get_url_statistics(valid_urls)
        
        return jsonify({
            'success': True,
            'validUrls': valid_urls,
            'invalidUrls': invalid_urls,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/upload_url_list', methods=['POST'])
@login_required
def upload_url_list():
    """Handle URL list file upload"""
    from src.utils.url_list_parser import parse_file_content, parse_url_list, get_url_statistics
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    # Check file extension
    if not file.filename.endswith('.txt'):
        return jsonify({'success': False, 'error': 'Only .txt files are supported'})
    
    try:
        # Read file content
        file_content = file.read()
        url_text = parse_file_content(file_content)
        
        # Parse URLs
        valid_urls, invalid_urls = parse_url_list(url_text)
        stats = get_url_statistics(valid_urls)
        
        return jsonify({
            'success': True,
            'validUrls': valid_urls,
            'invalidUrls': invalid_urls,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

'''

# Insert after stop_crawl endpoint
insert_marker = '@app.route(\'/api/stop_crawl\', methods=[\'POST\'])'
if insert_marker in content:
    # Find the end of stop_crawl function
    stop_crawl_start = content.find(insert_marker)
    # Find the next @app.route after stop_crawl
    next_route_start = content.find('@app.route', stop_crawl_start + 100)
    if next_route_start > 0:
        # Insert before the next route
        content = content[:next_route_start] + api_endpoints + '\n' + content[next_route_start:]
    else:
        # Append at the end if no next route found
        content += api_endpoints

# Write modified file
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Successfully added list mode API endpoints to main.py")
print("✓ Added endpoints:")
print("  - /api/parse_url_list (POST)")
print("  - /api/upload_url_list (POST)")
print("✓ Modified /api/start_crawl to accept url_list parameter")
