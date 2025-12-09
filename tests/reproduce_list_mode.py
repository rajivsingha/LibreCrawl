import sys
import os
import time
import shutil

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.crawler import WebCrawler

def reproduce_list_mode_issue():
    print("Starting List Mode reproduction...")
    
    # Create a dummy crawler
    crawler = WebCrawler()
    
    # Use a real site that has links, e.g. python.org or example.com (if it had links)
    # or just use a site that definitely has internal links.
    # Let's use `https://www.python.org/` and `https://www.python.org/about/`
    # If list mode is working, it should crawl EXACTLY these 2 URLs.
    # If it's broken, it will crawl more (following links from them).
    
    url_list = [
        "https://www.python.org/",
        "https://www.python.org/about/"
    ]
    
    print(f"Starting crawl with List Mode: {url_list}")
    
    # Configure to ensure it WOULD follow links if they weren't restricted
    crawler.config['max_depth'] = 2
    crawler.config['max_urls'] = 10 
    
    success, message = crawler.start_crawl(url_list=url_list)
    
    if not success:
        print(f"Failed to start crawl: {message}")
        return
        
    # Wait for crawl to finish
    start_time = time.time()
    while crawler.is_running:
        time.sleep(1)
        stats = crawler.get_status()
        crawled_count = stats['stats']['crawled']
        discovered_count = stats['stats']['discovered']
        print(f"Status: {stats['status']}, Crawled: {crawled_count}, Discovered: {discovered_count}")
        
        if crawled_count > len(url_list):
            print(f"FAIL: Crawled {crawled_count} URLs, expected only {len(url_list)}!")
            crawler.stop_crawl()
            break
            
        if time.time() - start_time > 30: # 30s timeout
            print("Timeout reached - stopping")
            crawler.stop_crawl()
            break
            
    # Final check
    if crawler.stats['crawled'] > len(url_list):
        print(f"TEST FAILED: List mode crawled {crawler.stats['crawled']} URLs (expected {len(url_list)})")
    elif crawler.stats['crawled'] == len(url_list):
        print(f"TEST PASSED: List mode crawled exactly {len(url_list)} URLs")
    else:
        print(f"TEST INCONCLUSIVE: Crawled {crawler.stats['crawled']} URLs")

if __name__ == "__main__":
    reproduce_list_mode_issue()
