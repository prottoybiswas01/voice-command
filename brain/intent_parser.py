"""
Intent Parser for X Assistant (Phase 2 Upgrade).
Classifies recognized user prompts into actionable intents covering System, Browser Automation,
Smart Music, Internet Data, System Controls, Memory, and LLM Chat.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from core.logger import logger


@dataclass
class Intent:
    """Structure representing classified user intent."""
    name: str
    action_type: str  # 'system', 'media', 'web', 'productivity', 'power', 'smart_music', 'browser_auto', 'internet', 'system_control', 'memory', 'llm'
    params: Dict[str, Any] = field(default_factory=dict)
    raw_prompt: str = ""


class IntentParser:
    """Classifies incoming text commands into Phase-2 actionable intents."""

    def parse(self, text: str) -> Intent:
        """Classify input prompt string to Intent object."""
        if not text or not text.strip():
            return Intent(name="unknown", action_type="none", raw_prompt=text)

        clean = text.lower().strip()

        # Clean leading wake words if present
        for wake in ["x listen", "hey x", "x", "হে এক্স", "এক্স শোনো", "এক্স"]:
            if clean.startswith(wake):
                clean = clean[len(wake):].strip()
                break

        if not clean:
            return Intent(name="greeting", action_type="system", params={"type": "greeting"}, raw_prompt=text)

        # 1. Exit / Quit
        if any(w in clean for w in ["exit assistant", "exit", "quit", "close assistant", "stop assistant", "বন্ধ করো", "বিদায়"]):
            return Intent(name="exit", action_type="power", params={"action": "exit"}, raw_prompt=text)

        # 2. Power Confirmations (Shutdown, Restart, Sleep)
        if any(w in clean for w in ["shutdown", "turn off computer", "পিসি বন্ধ", "কম্পিউটার বন্ধ"]):
            return Intent(name="shutdown_confirm", action_type="power", params={"action": "shutdown"}, raw_prompt=text)
        if any(w in clean for w in ["restart computer", "reboot computer", "পিসি রিস্টার্ট"]):
            return Intent(name="restart_confirm", action_type="power", params={"action": "restart"}, raw_prompt=text)
        if any(w in clean for w in ["sleep computer", "put to sleep", "পিসি স্লিপ"]):
            return Intent(name="sleep_confirm", action_type="power", params={"action": "sleep"}, raw_prompt=text)

        # 3. Phase-2 System Control: Explorer Restart, Screenshots, Brightness, File Search
        if "restart explorer" in clean or "explorer restart" in clean or "এক্সপ্লোরার রিস্টার্ট" in clean:
            return Intent(name="restart_explorer", action_type="system_control", params={}, raw_prompt=text)
        if any(w in clean for w in ["take screenshot", "screenshot", "স্ক্রিনশট"]):
            return Intent(name="take_screenshot", action_type="system_control", params={}, raw_prompt=text)
        if "brightness" in clean or "ব্রাইটনেস" in clean:
            if "up" in clean or "increase" in clean or "বাড়াও" in clean:
                return Intent(name="set_brightness", action_type="system_control", params={"change": 20}, raw_prompt=text)
            elif "down" in clean or "decrease" in clean or "কমাও" in clean:
                return Intent(name="set_brightness", action_type="system_control", params={"change": -20}, raw_prompt=text)
            else:
                level = re.findall(r"\d+", clean)
                val = int(level[0]) if level else 70
                return Intent(name="set_brightness", action_type="system_control", params={"level": val}, raw_prompt=text)
        if any(w in clean for w in ["search file", "find file", "ফাইল খোঁজো", "ফাইল খুজ"]):
            query = re.sub(r".*(search file|find file|ফাইল খোঁজো|ফাইল খুজ)", "", clean).strip()
            return Intent(name="search_files", action_type="system_control", params={"query": query}, raw_prompt=text)

        # 4. Phase-2 Smart Music Playback (Priority: 1. Spotify -> 2. YouTube -> 3. Local)
        if any(w in clean for w in ["play music", "play song", "গান চালাও", "প্লে মিউজিক"]):
            query = re.sub(r".*(play music|play song|গান চালাও|প্লে মিউজিক)", "", clean).strip()
            return Intent(name="play_smart_music", action_type="smart_music", params={"query": query}, raw_prompt=text)

        # 5. Phase-2 Playwright Browser Automation & Social Sites
        browser_sites = {
            "facebook": ["facebook", "fb", "ফেসবুক"],
            "messenger": ["messenger", "মেসেঞ্জার"],
            "instagram": ["instagram", "ig", "ইনস্টাগ্রাম"],
            "linkedin": ["linkedin", "লিঙ্কডইন"],
            "github": ["github", "গিটহাব"],
            "gmail": ["gmail", "email", "ইমেইল"],
            "drive": ["google drive", "gdrive", "ড্রাইভ"]
        }
        for site_key, keywords in browser_sites.items():
            if any(k in clean for k in keywords):
                if any(w in clean for w in ["open", "go to", "খুলো", "যাও"]):
                    return Intent(name="open_browser_site", action_type="browser_auto", params={"site": site_key}, raw_prompt=text)

        if "scroll down" in clean or "scroll up" in clean or "স্ক্রোল" in clean:
            direction = "down" if "down" in clean else "up"
            return Intent(name="browser_scroll", action_type="browser_auto", params={"direction": direction}, raw_prompt=text)
        if "read title" in clean or "page title" in clean:
            return Intent(name="browser_read_title", action_type="browser_auto", params={}, raw_prompt=text)
        if "read notification" in clean or "notifications" in clean:
            return Intent(name="browser_read_notifications", action_type="browser_auto", params={}, raw_prompt=text)

        # 6. Phase-2 Live Internet Data (Weather, News, Wikipedia)
        if "weather" in clean or "আবহাওয়া" in clean:
            location = re.sub(r".*(weather in|weather for|আবহাওয়া)", "", clean).strip() or "Dhaka"
            return Intent(name="get_live_weather", action_type="internet", params={"location": location}, raw_prompt=text)

        if "news" in clean or "খবর" in clean:
            return Intent(name="get_live_news", action_type="internet", params={}, raw_prompt=text)

        if "wikipedia" in clean or "wiki" in clean or "উইকিপিডিয়া" in clean:
            query = re.sub(r".*(wikipedia search|wikipedia|wiki|উইকিপিডিয়া)", "", clean).strip()
            return Intent(name="search_wikipedia", action_type="internet", params={"query": query}, raw_prompt=text)

        # 7. Greetings, Time & Date
        if any(w in clean for w in ["hello", "hi", "hey", "good morning", "good evening", "সালাম", "হ্যালো"]):
            return Intent(name="greeting", action_type="system", params={"type": "greeting"}, raw_prompt=text)
        if any(w in clean for w in ["time", "what time", "কয়টা বাজে", "সময়"]):
            return Intent(name="get_time", action_type="system", params={"type": "time"}, raw_prompt=text)
        if any(w in clean for w in ["date", "what date", "today's date", "আজকের তারিখ", "তারিখ"]):
            return Intent(name="get_date", action_type="system", params={"type": "date"}, raw_prompt=text)

        # 8. System App Launchers
        if "chrome" in clean or "ক্রোম" in clean:
            return Intent(name="open_app", action_type="system", params={"app": "chrome"}, raw_prompt=text)
        if "edge" in clean or "এজ" in clean:
            return Intent(name="open_app", action_type="system", params={"app": "edge"}, raw_prompt=text)
        if "vs code" in clean or "vscode" in clean or "code" in clean:
            return Intent(name="open_app", action_type="system", params={"app": "vscode"}, raw_prompt=text)
        if "notepad" in clean or "নোটপ্যাড" in clean:
            return Intent(name="open_app", action_type="system", params={"app": "notepad"}, raw_prompt=text)
        if "calculator" in clean or "calc" in clean or "ক্যালকুলেটর" in clean:
            return Intent(name="open_app", action_type="system", params={"app": "calculator"}, raw_prompt=text)
        if "explorer" in clean or "my computer" in clean or "file manager" in clean or "ফাইল এক্সপ্লোরার" in clean:
            return Intent(name="open_app", action_type="system", params={"app": "explorer"}, raw_prompt=text)
        if "task manager" in clean or "টাস্ক ম্যানেজার" in clean:
            return Intent(name="open_app", action_type="system", params={"app": "task_manager"}, raw_prompt=text)

        # 9. Web Search & Volume Controls
        if "youtube" in clean or "ইউটিউব" in clean:
            if "search" in clean or "খুঁজো" in clean or "খোজ" in clean:
                query = re.sub(r".*youtube search (for)?", "", clean).strip()
                query = re.sub(r".*ইউটিউব (সার্চ|খুঁজো|খোজ)", "", query).strip()
                return Intent(name="youtube_search", action_type="web", params={"query": query}, raw_prompt=text)
            elif any(w in clean for w in ["open", "খুলো"]):
                return Intent(name="open_web", action_type="web", params={"site": "youtube"}, raw_prompt=text)

        if "google search" in clean or "search google" in clean or "গুগল সার্চ" in clean or "সার্চ করো" in clean:
            query = re.sub(r".*(google search|search google for|গুগল সার্চ|সার্চ করো)", "", clean).strip()
            return Intent(name="google_search", action_type="web", params={"query": query}, raw_prompt=text)

        if "volume up" in clean or "increase volume" in clean or "সাউন্ড বাড়াও" in clean:
            return Intent(name="volume_control", action_type="media", params={"command": "up"}, raw_prompt=text)
        if "volume down" in clean or "decrease volume" in clean or "সাউন্ড কমাও" in clean:
            return Intent(name="volume_control", action_type="media", params={"command": "down"}, raw_prompt=text)
        if "mute" in clean or "unmute" in clean or "সাউন্ড মিউট" in clean:
            return Intent(name="volume_control", action_type="media", params={"command": "mute"}, raw_prompt=text)

        # 10. Memory Statements ("remember that ...", "my favorite ...")
        if "remember that" in clean or "my favorite" in clean or "মনে রাখো" in clean:
            return Intent(name="save_memory", action_type="memory", params={"text": text}, raw_prompt=text)

        # 11. Productivity (Todo, Notes, Reminders, System Diagnostics)
        if any(w in clean for w in ["battery", "cpu", "ram", "internet", "system info", "system status", "পিসি অবস্থা"]):
            return Intent(name="system_info", action_type="productivity", params={"metric": "all"}, raw_prompt=text)

        if "remind me" in clean or "reminder" in clean or "মনে করিয়ে দাও" in clean:
            msg = re.sub(r".*(remind me to|reminder for|মনে করিয়ে দাও)", "", clean).strip()
            return Intent(name="add_reminder", action_type="productivity", params={"message": msg}, raw_prompt=text)

        if "todo" in clean or "to-do" in clean or "টুডু" in clean or "টাস্ক" in clean:
            if any(w in clean for w in ["add", "create", "যোগ"]):
                task = re.sub(r".*(add todo|create todo|যোগ করো|টাস্ক)", "", clean).strip()
                return Intent(name="add_todo", action_type="productivity", params={"task": task}, raw_prompt=text)
            return Intent(name="show_todo", action_type="productivity", params={}, raw_prompt=text)

        if "note" in clean or "notes" in clean or "নোট" in clean:
            if any(w in clean for w in ["add", "take", "write", "লিখ"]):
                content = re.sub(r".*(take note|add note|write note|নোট লিখো)", "", clean).strip()
                return Intent(name="add_note", action_type="productivity", params={"content": content}, raw_prompt=text)
            return Intent(name="show_notes", action_type="productivity", params={}, raw_prompt=text)

        # Fallback to LLM Chat
        return Intent(name="llm_chat", action_type="llm", params={"prompt": clean}, raw_prompt=text)


# Global Phase-2 IntentParser instance
intent_parser = IntentParser()
