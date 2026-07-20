"""
Playwright Browser Automation Module for X Assistant (Phase 2).
Automates web browsing, social network navigation (Facebook, Messenger, Instagram, LinkedIn, GitHub, Gmail, Drive),
form filling, button clicking, page scrolling, and title reading using Playwright or webbrowser fallback.
"""

import time
import webbrowser
from typing import Optional, Dict, Any
from config.settings import settings
from core.logger import logger
from core.database import db

try:
    from playwright.sync_api import sync_playwright, Browser, Page
except ImportError:
    sync_playwright = None
    logger.warning("playwright module not installed. Browser automation will fallback to system default browser.")


class PlaywrightBrowserController:
    """Manages browser automation using Playwright or webbrowser fallback."""

    def __init__(self) -> None:
        self.preferred_browser = settings.browser.preferred_browser
        self.headless = settings.browser.headless
        self.slow_mo = settings.browser.slow_mo
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

        self.sites = {
            "facebook": "https://www.facebook.com",
            "messenger": "https://www.messenger.com",
            "instagram": "https://www.instagram.com",
            "linkedin": "https://www.linkedin.com",
            "github": "https://www.github.com",
            "gmail": "https://mail.google.com",
            "drive": "https://drive.google.com"
        }

    def _ensure_browser_active(self) -> bool:
        """Start Playwright browser instance if available."""
        if not sync_playwright:
            return False

        if self.page and not self.page.is_closed():
            return True

        try:
            self.playwright = sync_playwright().start()
            browser_type = getattr(self.playwright, self.preferred_browser, self.playwright.chromium)
            self.browser = browser_type.launch(headless=self.headless, slow_mo=self.slow_mo)
            self.page = self.browser.new_page()
            logger.info(f"Playwright browser ({self.preferred_browser}) launched successfully.")
            return True
        except Exception as err:
            logger.warning(f"Failed to launch Playwright browser: {err}. Falling back to default browser.")
            return False

    def open_site(self, site_key: str) -> str:
        """
        Open specified social or web site.
        
        Args:
            site_key: 'facebook', 'messenger', 'instagram', 'linkedin', 'github', 'gmail', 'drive', or raw URL.
        """
        url = self.sites.get(site_key.lower(), site_key if site_key.startswith("http") else f"https://{site_key}")

        if self._ensure_browser_active() and self.page:
            try:
                self.page.goto(url)
                title = self.page.title()
                msg = f"Navigated to {site_key.capitalize()} (Title: '{title}')."
                logger.info(msg)
                db.log_command(f"browser_open:{site_key}", "SUCCESS", title)
                return msg
            except Exception as err:
                logger.error(f"Playwright navigation error for {url}: {err}")

        # Fallback to system default browser
        webbrowser.open(url)
        msg = f"Opened {site_key} in system browser."
        logger.info(msg)
        db.log_command(f"browser_open:{site_key}", "SUCCESS", msg)
        return msg

    def search_in_page(self, query: str, selector: str = "input[type='search'], input[name='q'], input[type='text']") -> str:
        """Fill search bar input field and press Enter."""
        if self._ensure_browser_active() and self.page:
            try:
                self.page.fill(selector, query)
                self.page.keyboard.press("Enter")
                msg = f"Searched for '{query}' on active page."
                logger.info(msg)
                return msg
            except Exception as err:
                logger.error(f"Failed in-page search for '{query}': {err}")

        # Fallback to Google Search
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Searched Google for '{query}'."

    def scroll_page(self, direction: str = "down", amount: int = 500) -> str:
        """Scroll active page up or down."""
        if self._ensure_browser_active() and self.page:
            try:
                y_delta = amount if direction.lower() == "down" else -amount
                self.page.evaluate(f"window.scrollBy(0, {y_delta});")
                msg = f"Scrolled page {direction}."
                logger.info(msg)
                return msg
            except Exception as err:
                logger.error(f"Error scrolling page: {err}")
                return f"Failed to scroll page: {err}"

        return "Active Playwright browser page not open."

    def read_page_title(self) -> str:
        """Read and return active page title."""
        if self._ensure_browser_active() and self.page:
            try:
                title = self.page.title()
                msg = f"Active page title: '{title}'."
                logger.info(msg)
                return msg
            except Exception as err:
                return f"Error reading page title: {err}"

        return "No active browser page open."

    def read_notifications(self) -> str:
        """Attempt to extract notification badges or text from active page."""
        if self._ensure_browser_active() and self.page:
            try:
                # General notification badge selectors
                selectors = ["[aria-label*='Notifications']", ".notification-badge", ".badge", "#notifications"]
                for sel in selectors:
                    element = self.page.query_selector(sel)
                    if element:
                        text = element.inner_text()
                        if text:
                            return f"Active notification status: {text.strip()}"

                return "Checked page notifications. No active unread badge found."
            except Exception as err:
                return f"Unable to read page notifications: {err}"

        return "Playwright browser session not active."

    def close(self) -> None:
        """Close browser instance."""
        if self.browser:
            try:
                self.browser.close()
            except Exception:
                pass
        if self.playwright:
            try:
                self.playwright.stop()
            except Exception:
                pass


# Global Playwright Browser Controller instance
browser_controller = PlaywrightBrowserController()
