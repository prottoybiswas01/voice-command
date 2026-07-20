"""
Local Ollama LLM Client for X Assistant (Phase 2 Upgrade).
Interacts with locally hosted Ollama models (Gemma, Llama, Mistral) over HTTP REST API
with context memory injection and long context prompt handling.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from config.settings import settings
from core.logger import logger
from brain.memory import memory_manager


class OllamaClient:
    """Client for querying local Ollama LLM server with memory injection."""

    def __init__(self, host: Optional[str] = None, model: Optional[str] = None) -> None:
        self.host = (host or settings.ollama.host).rstrip("/")
        self.model = model or settings.ollama.model
        self.timeout = settings.ollama.timeout
        self.system_prompt = settings.ollama.system_prompt

    def is_server_available(self) -> bool:
        """Check if local Ollama server is running."""
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
        except Exception:
            return False

    def generate_response(self, user_prompt: str, include_memory: bool = True) -> str:
        """
        Generate response from Ollama local model with memory context injection.
        
        Args:
            user_prompt: User's spoken or typed prompt.
            include_memory: Whether to inject long-term context memory.
            
        Returns:
            Assistant text response string.
        """
        if not user_prompt or not user_prompt.strip():
            return "I am listening. How can I help you today?"

        # Build context prompt from memory manager
        context_block = memory_manager.build_context_prompt() if include_memory else ""

        endpoint = f"{self.host}/api/generate"
        full_system = f"{self.system_prompt}\n{context_block}"
        
        payload = {
            "model": self.model,
            "prompt": f"System: {full_system}\nUser: {user_prompt}\nAssistant:",
            "stream": False
        }

        try:
            json_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                endpoint,
                data=json_bytes,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    response_text = data.get("response", "").strip()
                    if response_text:
                        return response_text

        except urllib.error.URLError as url_err:
            logger.warning(f"Ollama server connection failed: {url_err}. Utilizing fallback offline generator.")
        except Exception as err:
            logger.error(f"Error querying Ollama LLM: {err}")

        # Intelligent offline fallback response generator if Ollama server is down
        return self._generate_fallback_response(user_prompt)

    def _generate_fallback_response(self, text: str) -> str:
        """Generates friendly offline responses when local LLM server is unavailable."""
        clean = text.lower().strip()

        if any(w in clean for w in ["hello", "hi", "hey", "সালাম", "হ্যালো"]):
            return "Hello! I am X Assistant Phase 2. How can I help you today?"
        elif any(w in clean for w in ["who are you", "কে তুমি", "তোমার নাম কি", "what is your name"]):
            return "I am X Assistant Phase 2, your personal AI assistant built with local open-source tools."
        elif any(w in clean for w in ["how are you", "কেমন আছো", "কেমন আছেন"]):
            return "I am doing great! Ready to execute smart automation for you."
        elif any(w in clean for w in ["thank you", "thanks", "ধন্যবাদ"]):
            return "You are very welcome! Let me know if you need anything else."
        elif any(w in clean for w in ["bye", "goodbye", "বিদায়"]):
            return "Goodbye! Have a wonderful day!"
        
        return f"I processed your request: '{text}'. Start Ollama locally for deep conversational responses."


# Global Phase-2 Ollama client instance
ollama_client = OllamaClient()
