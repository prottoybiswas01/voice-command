"""
Intent Parser for X Assistant.
Analyzes recognized user prompts to classify system commands vs general LLM queries.
Supports Bangla, English, and Mixed Banglish phrasing.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from core.logger import logger


@dataclass
class Intent:
    """Structure representing classified user intent."""
    name: str
    action_type: str  # 'system', 'media', 'web', 'productivity', 'power', 'llm'
    params: Dict[str, Any] = field(default_factory=dict)
    raw_prompt: str = ""


class IntentParser:
    """Classifies incoming text commands into actionable system intents."""

    def parse(self, text: str) -> Intent:
        """
        Classify text command to Intent object.
        
        Args:
            text: Raw input text from STT or user input.
            
        Returns:
            Intent object containing action type and metadata parameters.
        """
        if not text or not text.strip():
            return Intent(name="unknown", action_type="none", raw_prompt=text)

        clean = text.lower().strip()

        # Clean leading wake word if present in prompt
        for wake in ["x listen", "hey x", "x", "হে এক্স", "এক্স শোনো", "এক্স"]:
            if clean.startswith(wake):
                clean = clean[len(wake):].strip()
                break

        if not clean:
            return Intent(name="greeting", action_type="system", params={"type": "greeting"}, raw_prompt=text)

        # 1. Exit / Quit Command
        if any(w in clean for w in ["exit assistant", "exit", "quit", "close assistant", "stop assistant", "বন্ধ করো", "বিদায়"]):
            return Intent(name="exit", action_type="power", params={"action": "exit"}, raw_prompt=text)

        # 2. Shutdown / Restart / Sleep Confirmations
        if any(w in clean for w in ["shutdown", "turn off computer", "পিসি বন্ধ", "কম্পিউটার বন্ধ"]):
            return Intent(name="shutdown_confirm", action_type="power", params={"action": "shutdown"}, raw_prompt=text)
        if any(w in clean for w in ["restart", "reboot", "পিসি রিস্টার্ট"]):
            return Intent(name="restart_confirm", action_type="power", params={"action": "restart"}, raw_prompt=text)
        if any(w in clean for w in ["sleep computer", "put to sleep", "পিসি স্লিপ"]):
            return Intent(name="sleep_confirm", action_type="power", params={"action": "sleep"}, raw_prompt=text)

        # 3. Greetings
        if any(w in clean for w in ["hello", "hi", "hey", "good morning", "good evening", "সালাম", "হ্যালো"]):
            return Intent(name="greeting", action_type="system", params={"type": "greeting"}, raw_prompt=text)

        # 4. Current Time and Date
        if any(w in clean for w in ["time", "what time", "কয়টা বাজে", "সময়"]):
            return Intent(name="get_time", action_type="system", params={"type": "time"}, raw_prompt=text)
        if any(w in clean for w in ["date", "what date", "today's date", "আজকের তারিখ", "তারিখ"]):
            return Intent(name="get_date", action_type="system", params={"type": "date"}, raw_prompt=text)

        # 5. Open Applications
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

        # 6. Web & Media Actions
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

        # Media Control: Play / Pause / Stop Music
        if any(w in clean for w in ["play music", "play song", "গান চালাও", "প্লে মিউজিক"]):
            return Intent(name="media_control", action_type="media", params={"command": "play"}, raw_prompt=text)
        if any(w in clean for w in ["pause music", "pause song", "গান থামাও", "পজ"]):
            return Intent(name="media_control", action_type="media", params={"command": "pause"}, raw_prompt=text)
        if any(w in clean for w in ["stop music", "stop song", "গান বন্ধ"]):
            return Intent(name="media_control", action_type="media", params={"command": "stop"}, raw_prompt=text)

        # Volume Controls
        if "volume up" in clean or "increase volume" in clean or "সাউন্ড বাড়াও" in clean:
            return Intent(name="volume_control", action_type="media", params={"command": "up"}, raw_prompt=text)
        if "volume down" in clean or "decrease volume" in clean or "সাউন্ড কমাও" in clean:
            return Intent(name="volume_control", action_type="media", params={"command": "down"}, raw_prompt=text)
        if "mute" in clean or "unmute" in clean or "সাউন্ড মিউট" in clean:
            return Intent(name="volume_control", action_type="media", params={"command": "mute"}, raw_prompt=text)

        # 7. System Information Metrics
        if any(w in clean for w in ["battery", "battery status", "ব্যাটারি"]):
            return Intent(name="system_info", action_type="productivity", params={"metric": "battery"}, raw_prompt=text)
        if any(w in clean for w in ["cpu", "cpu usage", "সিপিইউ"]):
            return Intent(name="system_info", action_type="productivity", params={"metric": "cpu"}, raw_prompt=text)
        if any(w in clean for w in ["ram", "ram usage", "মেমোরি"]):
            return Intent(name="system_info", action_type="productivity", params={"metric": "ram"}, raw_prompt=text)
        if any(w in clean for w in ["internet", "network status", "ইন্টারনেট"]):
            return Intent(name="system_info", action_type="productivity", params={"metric": "internet"}, raw_prompt=text)
        if any(w in clean for w in ["system info", "system status", "পিসি অবস্থা"]):
            return Intent(name="system_info", action_type="productivity", params={"metric": "all"}, raw_prompt=text)

        # 8. Productivity: Weather & News Placeholders
        if "weather" in clean or "আবহাওয়া" in clean:
            return Intent(name="weather", action_type="web", params={}, raw_prompt=text)
        if "news" in clean or "খবর" in clean:
            return Intent(name="news", action_type="web", params={}, raw_prompt=text)

        # 9. Productivity: Reminders, Todos, Notes
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

        # 10. History Queries
        if "history" in clean or "হিস্ট্রি" in clean:
            return Intent(name="show_history", action_type="productivity", params={}, raw_prompt=text)

        # Default fallback to LLM conversation
        return Intent(name="llm_chat", action_type="llm", params={"prompt": clean}, raw_prompt=text)


# Global IntentParser instance
intent_parser = IntentParser()
