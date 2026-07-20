"""
Memory Manager for X Assistant (Phase 2).
Handles long-term context memory, user preference extraction, and prompt context building.
"""

import re
from typing import Dict, Any, List, Optional
from core.database import db
from core.logger import logger


class MemoryManager:
    """Manages long-term memories, user preferences, and context injection."""

    def __init__(self) -> None:
        self.db = db

    def remember_preference(self, key: str, value: str) -> str:
        """Explicitly save user preference."""
        self.db.set_user_preference(key, value)
        msg = f"Got it! I will remember that your {key} is {value}."
        logger.info(msg)
        return msg

    def remember_fact(self, key: str, fact: str) -> str:
        """Explicitly save general fact to memory buffer."""
        self.db.add_memory(key, fact)
        msg = f"Saved to memory: '{fact}'."
        logger.info(msg)
        return msg

    def extract_implicit_memory(self, text: str) -> Optional[str]:
        """
        Analyze prompt text to detect user preference statements.
        Examples:
        - "my favorite song is X"
        - "my favorite music is X"
        - "remember that my name is X"
        """
        if not text:
            return None

        clean = text.lower().strip()

        # Favorite music match
        fav_music_match = re.search(r"my favorite (music|song|artist|genre) is (.+)", clean)
        if fav_music_match:
            category = fav_music_match.group(1)
            val = fav_music_match.group(2).strip()
            self.remember_preference(f"favorite_{category}", val)
            return f"I have saved your favorite {category} as '{val}'."

        # Preferred browser match
        browser_match = re.search(r"my preferred browser is (chrome|edge|firefox)", clean)
        if browser_match:
            browser = browser_match.group(1).strip()
            self.remember_preference("preferred_browser", browser)
            return f"Saved preferred browser: {browser}."

        # User name match
        name_match = re.search(r"(my name is|call me) ([a-zA-Z\s]+)", clean)
        if name_match:
            user_name = name_match.group(2).strip()
            self.remember_preference("user_name", user_name)
            return f"Nice to meet you, {user_name}! I will remember your name."

        return None

    def build_context_prompt(self, recent_messages_limit: int = 5) -> str:
        """
        Build persistent context block combining user preferences, stored memories,
        and recent conversation history to inject into Ollama system prompt.
        """
        context_parts: List[str] = []

        # 1. User Preferences
        prefs = self.db.get_all_preferences()
        if prefs:
            pref_strs = [f"- {k}: {v}" for k, v in prefs.items()]
            context_parts.append("User Preferences:\n" + "\n".join(pref_strs))

        # 2. Key Memories
        memories = self.db.get_all_memories(limit=10)
        if memories:
            mem_strs = [f"- {m['memory_key']}: {m['memory_value']}" for m in memories]
            context_parts.append("Stored Memories:\n" + "\n".join(mem_strs))

        # 3. Recent Conversation History
        history = self.db.get_recent_conversations(limit=recent_messages_limit)
        if history:
            hist_strs = []
            for h in reversed(history):
                hist_strs.append(f"User: {h['user_input']}\nAssistant: {h['assistant_response']}")
            context_parts.append("Recent Conversation Context:\n" + "\n\n".join(hist_strs))

        if not context_parts:
            return ""

        return "\n\n=== CONTEXT MEMORY ===\n" + "\n\n".join(context_parts) + "\n======================"


# Global Memory Manager instance
memory_manager = MemoryManager()
