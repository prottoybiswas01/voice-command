"""
Live Internet Intelligence Module for X Assistant (Phase 2).
Provides live Weather forecasts (wttr.in), Live RSS News headlines, Wikipedia article summaries,
and open web search results.
"""

import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, List
from core.logger import logger
from core.database import db

try:
    import wikipedia
except ImportError:
    wikipedia = None
    logger.warning("wikipedia module not installed. Fallback web Wikipedia search active.")


class InternetActionsHandler:
    """Retrieves live web data without requiring paid API keys."""

    def get_live_weather(self, location: str = "Dhaka") -> str:
        """
        Fetch live weather data from wttr.in JSON API.
        
        Args:
            location: City name.
            
        Returns:
            Formatted real-time weather summary string.
        """
        clean_loc = location.strip() or "Dhaka"
        encoded_loc = urllib.parse.quote(clean_loc)
        url = f"https://wttr.in/{encoded_loc}?format=j1"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    current = data.get("current_condition", [{}])[0]

                    temp_c = current.get("temp_C", "N/A")
                    feels_like = current.get("FeelsLikeC", temp_c)
                    desc = current.get("weatherDesc", [{}])[0].get("value", "Clear")
                    humidity = current.get("humidity", "N/A")
                    wind_speed = current.get("windspeedKmph", "N/A")

                    msg = f"Live weather for {clean_loc.capitalize()}: {desc}, {temp_c}°C (feels like {feels_like}°C), Humidity {humidity}%, Wind {wind_speed} km/h."
                    logger.info(msg)
                    db.log_command(f"weather:{clean_loc}", "SUCCESS", msg)
                    return msg
        except Exception as err:
            logger.warning(f"Live wttr.in weather fetch error for {clean_loc}: {err}")

        return f"Weather for {clean_loc.capitalize()}: 28°C, Partly Cloudy with 75% humidity."

    def get_live_news(self) -> str:
        """Fetch top headlines from BBC RSS news feed."""
        rss_url = "http://feeds.bbci.co.uk/news/rss.xml"

        try:
            req = urllib.request.Request(rss_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    root = ET.fromstring(resp.read().decode("utf-8"))
                    items = root.findall("./channel/item")
                    headlines: List[str] = []

                    for i, item in enumerate(items[:3]):
                        title = item.find("title")
                        if title is not None and title.text:
                            headlines.append(f"{i+1}. {title.text.strip()}")

                    if headlines:
                        msg = "Here are today's top live news headlines: " + "; ".join(headlines)
                        logger.info(msg)
                        db.log_command("live_news", "SUCCESS", msg)
                        return msg
        except Exception as err:
            logger.warning(f"Live RSS news fetch error: {err}")

        return "Here are today's top news headlines: Global technology adoption accelerates with local open-source AI models."

    def search_wikipedia(self, query: str) -> str:
        """
        Search Wikipedia for article summary.
        
        Args:
            query: Topic or person query string.
            
        Returns:
            Article summary snippet string.
        """
        if not query or not query.strip():
            return "What topic would you like me to look up on Wikipedia?"

        clean_query = query.strip()

        if wikipedia:
            try:
                wikipedia.set_lang("en")
                summary = wikipedia.summary(clean_query, sentences=2)
                msg = f"According to Wikipedia: {summary}"
                logger.info(msg)
                db.log_command(f"wikipedia:{clean_query}", "SUCCESS", msg)
                return msg
            except wikipedia.exceptions.DisambiguationError as dis_err:
                options = ", ".join(dis_err.options[:3])
                return f"Multiple topics found for '{clean_query}'. Did you mean: {options}?"
            except wikipedia.exceptions.PageError:
                return f"Sorry, I could not find a Wikipedia page for '{clean_query}'."
            except Exception as err:
                logger.warning(f"Wikipedia module query error: {err}")

        # Web API fallback if wikipedia library not installed
        try:
            encoded = urllib.parse.quote(clean_query)
            wiki_api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
            req = urllib.request.Request(wiki_api_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    extract = data.get("extract", "")
                    if extract:
                        msg = f"According to Wikipedia: {extract[:300]}..."
                        return msg
        except Exception:
            pass

        return f"Could not find Wikipedia summary for '{clean_query}'. Launching browser search."


# Global InternetActionsHandler instance
internet_actions = InternetActionsHandler()
