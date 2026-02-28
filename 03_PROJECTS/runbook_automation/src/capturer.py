import logging
import os
import time
from typing import List

logger = logging.getLogger(__name__)

# Note: Playwright requires 'pip install playwright' and 'playwright install'
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

class Capturer:
    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock

    def capture_aws_console(self, url: str, output_dir: str) -> List[str]:
        """
        Capture screenshots of the AWS Console.
        In mock mode, it returns the path to the stub image.
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = int(time.time())
        screenshot_paths = []
        
        if self.use_mock or sync_playwright is None:
            if sync_playwright is None and not self.use_mock:
                logger.warning("Playwright not found properly. Falling back to MOCK mode.")
            
            logger.info(f"[MOCK] Capturing AWS Console at {url}")
            mock_path = os.path.join(output_dir, f"capture_{timestamp}.png")
            # Create a simple mock file if it doesn't exist
            with open(mock_path, "w") as f:
                f.write("MOCK SCREENSHOT DATA")
            return [mock_path]

        logger.info(f"Starting real capture for {url}")
        with sync_playwright() as p:
            # Note: For AWS Console, session handling (cookies/login) is required.
            # This is a basic implementation that captures the page as-is.
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 800})
            page = context.new_page()
            
            try:
                page.goto(url, wait_until="networkidle")
                path = os.path.join(output_dir, f"capture_{timestamp}_start.png")
                page.screenshot(path=path, full_page=True)
                screenshot_paths.append(path)
                logger.info(f"Screenshot saved to {path}")
            except Exception as e:
                logger.error(f"Failed to capture {url}: {e}")
            finally:
                browser.close()
        
        return screenshot_paths
