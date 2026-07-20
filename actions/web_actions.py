"""
Web Actions Module for X Assistant.
Handles browser search, YouTube integration, weather, and news placeholders.
"""

import webbrowser
import urllib.parse
from typing import Optional
from core.logger import logger
from core.database import db


class WebActionsHandler:
    """Manages web browsing, Google search, YouTube, weather, and news features."""

    def open_website(self, site: str) -> str:
        """Open predefined or specified URL in user's default browser."""
        urls = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com"
        }
        target_url = urls.get(site.lower(), site if site.startswith("http") else f"https://{site}")
        
        try:
            webbrowser.open(target_url)
            msg = f"Opening {site} in browser."
            logger.info(msg)
            db.log_command(f"open_web:{site}", "SUCCESS", msg)
            return msg
        except Exception as err:
            logger.error(f"Failed to open web URL '{target_url}': {err}")
            return f"Failed to open {site}."

    def search_google(self, query: str) -> str:
        """Perform Google Search for user query string."""
        if not query or not query.strip():
            return "What would you like me to search for on Google?"

        encoded_query = urllib.parse.quote(query.strip())
        search_url = f"https://www.google.com/search?q={encoded_query}"

        try:
            webbrowser.open(search_url)
            msg = f"Searching Google for '{query}'."
            logger.info(msg)
            db.log_command("google_search", "SUCCESS", query)
            return msg
        except Exception as err:
            logger.error(f"Failed Google Search for query '{query}': {err}")
            return f"Could not perform Google search for {query}."

    def search_youtube(self, query: str) -> str:
        """Perform YouTube Search for user query string."""
        if not query or not query.strip():
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube homepage."

        encoded_query = urllib.parse.quote(query.strip())
        search_url = f"https://www.youtube.com/results?search_query={encoded_query}"

        try:
            webbrowser.open(search_url)
            msg = f"Searching YouTube for '{query}'."
            logger.info(msg)
            db.log_command("youtube_search", "SUCCESS", query)
            return msg
        except Exception as err:
            logger.error(f"Failed YouTube Search for query '{query}': {err}")
            return f"Could not perform YouTube search for {query}."

    def get_weather(self, location: str = "Dhaka") -> str:
        """
        Weather forecast placeholder for Phase-1.
        Can be upgraded in Phase-2 to fetch open-meteo or wttr.in API.
        """
        msg = f"Weather update for {location}: 28°C, Partly Cloudy with 75% humidity. Offline weather forecast module active."
        logger.info(msg)
        return msg

    def get_news(self) -> str:
        """
        News headline placeholder for Phase-1.
        Can be upgraded in Phase-2 to parse local RSS news feeds.
        """
        msg = "Here are today's top news headlines: Local tech developments show massive growth in open-source AI adoption."
        logger.info(msg)
        return msg


# Global WebActionsHandler instance
web_actions = WebActionsHandler()
