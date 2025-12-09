import sys
import os
import asyncio
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.crawler import WebCrawler

def reproduce_issue():
    print("Starting JS crawl reproduction...")
    
    # Configure crawler for JS
    crawler = WebCrawler()
    crawler.config['enable_javascript'] = True
    crawler.config['js_headless'] = True
    crawler.config['max_urls'] = 5
    crawler.config['max_depth'] = 1
    
    # Use a site that definitely needs JS or at least works with it
    # Google is complex, let's try something simpler but dynamic or just a regular site rendered with JS
    # We can use a test site or a real one. Let's try to crawl a single page.
    url = "https://example.com" 
    
    print(f"Crawling {url} with JS enabled...")
    start_time = time.time()
    
    success, message = crawler.start_crawl(url=url)
    
    if not success:
        print(f"Failed to start crawl: {message}")
        return
        
    # Wait for crawl to finish
    while crawler.is_running:
        time.sleep(1)
        stats = crawler.get_status()
        print(f"Status: {stats['status']}, Crawled: {stats['stats']['crawled']}, Pending: {stats['stats']['discovered'] - stats['stats']['crawled']}")
        
        if time.time() - start_time > 60:
            print("Timeout reached!")
            crawler.stop_crawl()
            break
            
    print("Crawl finished.")
    print(f"Total crawled: {crawler.stats['crawled']}")
    
    if crawler.stats['crawled'] == 0:
        print("FAIL: No pages crawled with JS enabled.")
    else:
        print("SUCCESS: Pages crawled with JS enabled.")

if __name__ == "__main__":
    reproduce_issue()
