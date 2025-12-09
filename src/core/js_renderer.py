"""JavaScript rendering handler using Playwright"""
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from urllib.parse import urlparse


class JavaScriptRenderer:
    """Handles JavaScript rendering for dynamic content using Playwright"""

    def __init__(self, config):
        self.config = config
        self.playwright = None
        self.browser = None
        self.page_pool = []
        self.pool_lock = asyncio.Lock()  # Use asyncio lock for async code
        self.initialized = False

    async def initialize(self):
        """Initialize Playwright browser and page pool"""
        if self.initialized:
            return
            
        try:
            print("Starting Playwright browser...")
            self.playwright = await async_playwright().start()

            # Choose browser based on configuration
            browser_type = self.config.get('js_browser', 'chromium').lower()
            headless = self.config.get('js_headless', True)

            launch_args = {
                'headless': headless
            }
            
            if browser_type == 'firefox':
                self.browser = await self.playwright.firefox.launch(**launch_args)
            elif browser_type == 'webkit':
                self.browser = await self.playwright.webkit.launch(**launch_args)
            else:  # Default to chromium
                launch_args['args'] = ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
                self.browser = await self.playwright.chromium.launch(**launch_args)

            # Create page pool
            max_pages = self.config.get('js_max_concurrent_pages', 3)
            print(f"Creating {max_pages} browser pages...")
            
            for i in range(max_pages):
                try:
                    context = await self.browser.new_context(
                        user_agent=self.config.get('js_user_agent', 'LibreCrawl/1.0 (Web Crawler with JavaScript)'),
                        viewport={
                            'width': self.config.get('js_viewport_width', 1920),
                            'height': self.config.get('js_viewport_height', 1080)
                        },
                        ignore_https_errors=True
                    )
                    page = await context.new_page()
                    page.set_default_timeout(self.config.get('js_timeout', 30) * 1000)
                    self.page_pool.append(page)
                    print(f"  Created browser page {i + 1}/{max_pages}")
                except Exception as e:
                    print(f"  Failed to create browser page {i + 1}: {e}")

            if len(self.page_pool) == 0:
                raise Exception("Failed to create any browser pages")

            self.initialized = True
            print(f"JavaScript rendering initialized with {len(self.page_pool)} browser pages")

        except Exception as e:
            print(f"Failed to initialize JavaScript rendering: {e}")
            await self.cleanup()
            raise

    async def cleanup(self):
        """Clean up Playwright browser and resources"""
        try:
            if self.page_pool:
                for page in self.page_pool:
                    try:
                        await page.context.close()
                    except:
                        pass
                self.page_pool.clear()

            if self.browser:
                await self.browser.close()
                self.browser = None

            if self.playwright:
                await self.playwright.stop()
                self.playwright = None

            self.initialized = False
            print("JavaScript rendering resources cleaned up")

        except Exception as e:
            print(f"Error during JavaScript cleanup: {e}")

    async def get_page(self, max_wait=30):
        """Get an available page from the pool, waiting if necessary"""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            async with self.pool_lock:
                if self.page_pool:
                    return self.page_pool.pop()
            
            # Check if we've waited too long
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > max_wait:
                print(f"Timeout waiting for available JavaScript page after {max_wait}s")
                return None
            
            # Wait a bit before trying again
            await asyncio.sleep(0.1)

    async def return_page(self, page):
        """Return a page to the pool"""
        if page:
            try:
                # Clear page state before returning to pool
                await page.goto('about:blank', wait_until='domcontentloaded', timeout=5000)
            except:
                pass  # Ignore errors on cleanup
            
            async with self.pool_lock:
                self.page_pool.append(page)

    async def render_page(self, url):
        """
        Render a page with JavaScript and return the HTML content

        Returns:
            tuple: (html_content, status_code, error_message)
        """
        if not self.initialized:
            return None, 0, "JavaScript renderer not initialized"
            
        page = None
        try:
            page = await self.get_page(max_wait=60)
            if not page:
                return None, 0, "No JavaScript page available (timeout)"

            # Navigate to the page
            try:
                print(f"  JS rendering: {url}")
                
                # Set longer timeout for navigation
                timeout_ms = self.config.get('js_timeout', 30) * 1000
                
                response = await page.goto(
                    url,
                    wait_until='domcontentloaded',  # Use domcontentloaded as baseline
                    timeout=timeout_ms
                )

                # Try to wait for network idle, but don't fail if it times out
                try:
                    await page.wait_for_load_state('networkidle', timeout=5000)
                except Exception:
                    # Ignore network idle timeout, we have the DOM
                    pass

                # Additional wait for JavaScript to execute
                wait_time = self.config.get('js_wait_time', 2)
                if wait_time > 0:
                    await asyncio.sleep(wait_time)

                # Get the rendered HTML content
                html_content = await page.content()
                status_code = response.status if response else 200
                
                print(f"  JS render complete: {url} (status: {status_code}, size: {len(html_content)} bytes)")

                return html_content, status_code, None

            except PlaywrightTimeoutError:
                print(f"  JS render timeout: {url}")
                return None, 0, "JavaScript rendering timeout"
            except Exception as e:
                print(f"  JS render error: {url} - {str(e)}")
                return None, 0, f"Navigation error: {str(e)}"

        except Exception as e:
            print(f"  JS render exception: {url} - {str(e)}")
            return None, 0, f"JavaScript rendering error: {str(e)}"

        finally:
            if page:
                await self.return_page(page)

    def should_use_javascript(self, url):
        """Determine if a URL should use JavaScript rendering"""
        parsed = urlparse(url)
        path = parsed.path.lower()

        # Skip if it's clearly a non-HTML resource
        if path.endswith(('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.xml', '.txt', '.zip', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot')):
            return False

        return True
