"""
Fixed script to add list mode support to crawler.py
"""
import re

# Read original file
with open('src/crawler.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Convert to string for easier manipulation
content = ''.join(lines)

# Modification 1: Add list_mode and url_list instance variables
# Find the line with memory_monitor and add after it
content = content.replace(
    '        self.seo_extractor = SEOExtractor()\r\n        self.memory_monitor = MemoryMonitor()\r\n',
    '        self.seo_extractor = SEOExtractor()\r\n        self.memory_monitor = MemoryMonitor()\r\n\r\n        # List mode support\r\n        self.list_mode = False\r\n        self.url_list = []\r\n'
)

# Modification 2: Update start_crawl signature
content = content.replace(
    '    def start_crawl(self, url, user_id=None, session_id=None):',
    '    def start_crawl(self, url=None, user_id=None, session_id=None, url_list=None):'
)

# Modification 3: Update start_crawl to handle list mode
# Find and replace the URL validation section
old_validation = '''        try:
            # Validate and normalize URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            parsed = urlparse(url)
            self.base_url = f"{parsed.scheme}://{parsed.netloc}"
            self.base_domain = parsed.netloc

            # If URL has a path (not just domain), set max_depth to 0 to only crawl that page
            has_path = parsed.path and parsed.path not in ('/', '')
            if has_path:
                print(f"URL has path '{parsed.path}' - limiting crawl to single page only")
                self.config['max_depth'] = 0'''

new_validation = '''        try:
            # Check if list mode
            if url_list and len(url_list) > 0:
                self.list_mode = True
                self.url_list = url_list
                # Use first URL to determine base domain
                first_url = url_list[0]
                if not first_url.startswith(('http://', 'https://')):
                    first_url = 'https://' + first_url
                parsed = urlparse(first_url)
                self.base_url = f"{parsed.scheme}://{parsed.netloc}"
                self.base_domain = parsed.netloc
                print(f"List mode enabled with {len(url_list)} URLs")
            elif url:
                # Standard mode - validate and normalize URL
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url

                parsed = urlparse(url)
                self.base_url = f"{parsed.scheme}://{parsed.netloc}"
                self.base_domain = parsed.netloc

                # If URL has a path (not just domain), set max_depth to 0 to only crawl that page
                has_path = parsed.path and parsed.path not in ('/', '')
                if has_path:
                    print(f"URL has path '{parsed.path}' - limiting crawl to single page only")
                    self.config['max_depth'] = 0
            else:
                return False, "Either url or url_list must be provided"'''

content = content.replace(old_validation, new_validation)

# Modification 4: Replace URL queue initialization
old_queue = '''            # Add initial URL
            self.link_manager.add_url(url, 0)
            self.stats['discovered'] = 1

            # Discover sitemaps if enabled
            if self.config.get('discover_sitemaps', True):
                print(f"Starting sitemap discovery for {url}")
                self._discover_and_add_sitemap_urls(url)
                print(f"Sitemap discovery completed. Total discovered URLs: {self.stats['discovered']}")'''

new_queue = '''            # Add URLs to queue
            if self.list_mode:
                # List mode: add all URLs from the list
                for list_url in self.url_list:
                    # Normalize URL
                    if not list_url.startswith(('http://', 'https://')):
                        list_url = 'http://' + list_url
                    self.link_manager.add_url(list_url, 0)
                self.stats['discovered'] = len(self.url_list)
                print(f"Added {len(self.url_list)} URLs from list to queue")
                # Disable sitemap discovery in list mode
                self.config['discover_sitemaps'] = False
            else:
                # Standard mode: add initial URL
                self.link_manager.add_url(url, 0)
                self.stats['discovered'] = 1

                # Discover sitemaps if enabled
                if self.config.get('discover_sitemaps', True):
                    print(f"Starting sitemap discovery for {url}")
                    self._discover_and_add_sitemap_urls(url)
                    print(f"Sitemap discovery completed. Total discovered URLs: {self.stats['discovered']}")'''

content = content.replace(old_queue, new_queue)

# Modification 5: Skip link extraction in list mode (HTTP crawling)
content = content.replace(
    '                # Extract links from page\r\n                self.link_manager.extract_links(',
    '                # Extract links from page (skip in list mode)\r\n                if not self.list_mode:\r\n                    self.link_manager.extract_links('
)

# Write modified file
with open('src/crawler.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Successfully added list mode support to crawler.py")
