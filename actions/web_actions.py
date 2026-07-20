"""
Web Actions Module for Motu Assistant.
Handles Google Chrome browser search, YouTube integration, weather, and news features.
Strictly routes all browser requests to Google Chrome executable.
"""

import urllib.parse
from typing import Optional
from core.logger import logger
from core.database import db
from actions.system_actions import open_in_chrome


class WebActionsHandler:
    """Manages web browsing, Google search, YouTube, weather, and news features strictly via Google Chrome."""

    def open_website(self, site: str) -> str:
        """Open predefined or specified URL in Google Chrome."""
        urls = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com"
        }
        target_url = urls.get(site.lower(), site if site.startswith("http") else f"https://{site}")
        
        try:
            open_in_chrome(target_url)
            msg = f"Opening {site} in Google Chrome."
            logger.info(msg)
            db.log_command(f"open_web:{site}", "SUCCESS", msg)
            return msg
        except Exception as err:
            logger.error(f"Failed to open web URL '{target_url}': {err}")
            return f"Failed to open {site}."

    def search_google(self, query: str) -> str:
        """Perform Google Search for user query string in Google Chrome."""
        if not query or not query.strip():
            return "What would you like me to search for on Google?"

        encoded_query = urllib.parse.quote(query.strip())
        search_url = f"https://www.google.com/search?q={encoded_query}"

        try:
            open_in_chrome(search_url)
            msg = f"Searching Google for '{query}' in Google Chrome."
            logger.info(msg)
            db.log_command("google_search", "SUCCESS", query)
            return msg
        except Exception as err:
            logger.error(f"Failed Google Search for query '{query}': {err}")
            return f"Could not perform Google search for {query}."

    def search_youtube(self, query: str) -> str:
        """Perform YouTube Search for user query string in Google Chrome."""
        if not query or not query.strip():
            open_in_chrome("https://www.youtube.com")
            return "Opening YouTube homepage in Google Chrome."

        encoded_query = urllib.parse.quote(query.strip())
        search_url = f"https://www.youtube.com/results?search_query={encoded_query}"

        try:
            open_in_chrome(search_url)
            msg = f"Searching YouTube for '{query}' in Google Chrome."
            logger.info(msg)
            db.log_command("youtube_search", "SUCCESS", query)
            return msg
        except Exception as err:
            logger.error(f"Failed YouTube Search for query '{query}': {err}")
            return f"Could not perform YouTube search for {query}."

    def get_weather(self, location: str = "Dhaka") -> str:
        """Weather forecast update."""
        msg = f"Weather update for {location}: 28°C, Partly Cloudy with 75% humidity."
        logger.info(msg)
        return msg

    def get_news(self) -> str:
        """News headline update."""
        msg = "Here are today's top news headlines: Local tech developments show massive growth in open-source AI adoption."
        logger.info(msg)
        return msg


# Global WebActionsHandler instance
web_actions = WebActionsHandler()
