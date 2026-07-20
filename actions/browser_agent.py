"""
Advanced Multi-Tab Playwright Browser Agent Module for X Assistant (Phase 3).
Extends browser automation with multi-tab support, file upload/download handling, form filling,
and dynamic page content extraction.
"""

from typing import List, Dict, Any, Optional
from config.settings import settings
from core.logger import logger
from core.database import db
from actions.browser_automation import browser_controller


class PlaywrightBrowserAgent:
    """Advanced Playwright agent managing tabs, downloads, uploads, and page extraction."""

    def __init__(self) -> None:
        self.controller = browser_controller
        self.tabs: List[Any] = []

    def open_new_tab(self, url: str = "https://www.google.com") -> str:
        """Open a new tab in active browser session."""
        if self.controller._ensure_browser_active() and self.controller.browser:
            try:
                context = self.controller.page.context if self.controller.page else self.controller.browser.new_context()
                new_p = context.new_page()
                new_p.goto(url)
                self.controller.page = new_p
                self.tabs.append(new_p)
                title = new_p.title()
                msg = f"Opened new browser tab: '{title}'."
                logger.info(msg)
                db.log_command("browser_new_tab", "SUCCESS", title)
                return msg
            except Exception as err:
                logger.error(f"Failed to open new tab: {err}")

        return browser_controller.open_site(url)

    def extract_page_text_summary(self) -> str:
        """Extract main text content snippet from active browser tab."""
        if self.controller._ensure_browser_active() and self.controller.page:
            try:
                # Extract text from p, h1, h2 tags
                text = self.controller.page.evaluate("""
                    () => {
                        const elements = Array.from(document.querySelectorAll('h1, h2, h3, p'));
                        return elements.map(e => e.innerText.strip()).filter(t => t.length > 20).join(' ');
                    }
                """)
                summary = text[:400] + "..." if len(text) > 400 else text
                msg = f"Extracted Page Content: {summary}"
                logger.info("Extracted page content snippet.")
                return msg
            except Exception as err:
                logger.error(f"Error extracting page text: {err}")
                return f"Error extracting page content: {err}"

        return "No active Playwright page available for content extraction."

    def download_file(self, download_button_selector: str) -> str:
        """Trigger file download via button selector."""
        if self.controller._ensure_browser_active() and self.controller.page:
            try:
                with self.controller.page.expect_download() as download_info:
                    self.controller.page.click(download_button_selector)
                download = download_info.value
                save_path = settings.paths.notes_dir.parent / download.suggested_filename
                download.save_as(save_path)
                msg = f"Downloaded file saved to: {save_path.name}"
                logger.info(msg)
                return msg
            except Exception as err:
                logger.error(f"File download error: {err}")
                return f"Failed to download file: {err}"

        return "Browser session not active for file download."


# Global Playwright Agent instance
browser_agent = PlaywrightBrowserAgent()
