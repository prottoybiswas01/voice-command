"""
AI Personalities & Model Switcher Module for X Assistant (Phase 6).
Manages configurable AI personalities (Standard, Professional, Friendly, Concise)
and allows dynamic switching between local Ollama models (gemma2:2b, llama3.2, mistral).
"""

from typing import Dict, Any, List
from config.settings import settings
from core.logger import logger
from core.database import db


class AIPersonalityManager:
    """Manages AI assistant personalities and local LLM model switching."""

    PERSONALITIES = {
        "standard": {
            "name": "Standard Assistant",
            "prompt": "You are X Assistant, a balanced, highly capable personal AI Assistant."
        },
        "professional": {
            "name": "Professional Engineer",
            "prompt": "You are X Assistant Professional Mode, a Senior Software Architect and Engineer providing precise technical solutions."
        },
        "friendly": {
            "name": "Friendly Companion",
            "prompt": "You are X Assistant, a warm, encouraging, friendly AI companion."
        },
        "concise": {
            "name": "Concise Executive",
            "prompt": "You are X Assistant Executive Mode. Give extremely short, bullet-pointed, direct answers without pleasantries."
        }
    }

    def __init__(self) -> None:
        self.active_personality = settings.assistant.active_personality
        self.active_model = settings.ollama.model

    def set_personality(self, personality_key: str) -> str:
        """Switch active AI personality profile."""
        key = personality_key.lower().strip()
        if key in self.PERSONALITIES:
            self.active_personality = key
            settings.assistant.active_personality = key
            db.set_user_preference("active_personality", key)
            name = self.PERSONALITIES[key]["name"]
            msg = f"Switched AI personality to '{name}'."
            logger.info(msg)
            return msg
        return f"Unknown personality '{personality_key}'. Available: standard, professional, friendly, concise."

    def set_model(self, model_name: str) -> str:
        """Switch active local Ollama AI model."""
        self.active_model = model_name.strip()
        settings.ollama.model = model_name.strip()
        db.set_user_preference("active_ollama_model", model_name.strip())
        msg = f"Switched local Ollama model to '{model_name}'."
        logger.info(msg)
        return msg

    def get_system_prompt_prefix(self) -> str:
        """Get system prompt prefix for active personality."""
        profile = self.PERSONALITIES.get(self.active_personality, self.PERSONALITIES["standard"])
        return profile["prompt"]


# Global AI Personality Manager instance
personality_manager = AIPersonalityManager()
