"""
Local Ollama LLM Client for X Assistant (Phase 6 Upgraded).
Interacts with locally hosted Ollama models (Gemma, Llama, Mistral) over HTTP REST API
with context memory injection, auto-server start, model verification, and safe mode fallback.
"""

import json
import time
import subprocess
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from config.settings import settings
from core.logger import logger
from brain.memory import memory_manager


class OllamaClient:
    """Client for querying local Ollama LLM server with memory injection and Safe Mode."""

    def __init__(self, host: Optional[str] = None, model: Optional[str] = None) -> None:
        self.host = (host or settings.ollama.host).rstrip("/")
        self.model = model or settings.ollama.model
        self.timeout = settings.ollama.timeout
        self.system_prompt = settings.ollama.system_prompt

    def is_server_available(self) -> bool:
        """Check if local Ollama server is running. Auto-starts server if offline."""
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
        except Exception:
            pass

        # Attempt to auto-start Ollama server
        try:
            logger.info("Ollama server offline. Attempting auto-start: 'ollama serve'...")
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
        except Exception as err:
            logger.warning(f"Could not auto-start Ollama server: {err}")

        return False

    def is_model_installed(self) -> bool:
        """Verify if configured model is installed locally in Ollama."""
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    models = [m.get("name", "") for m in data.get("models", [])]
                    for m in models:
                        if self.model.split(":")[0] in m:
                            return True
        except Exception:
            pass
        return False

    def generate_response(self, user_prompt: str, include_memory: bool = True) -> str:
        """
        Generate response from Ollama local model with memory context injection.
        Operates in Safe Mode if Ollama server is offline or model is missing.
        """
        if not user_prompt or not user_prompt.strip():
            return "I am listening. How can I help you today?"

        if not self.is_server_available():
            logger.warning("Ollama server unavailable. Running in Safe Mode.")
            return self._generate_fallback_response(user_prompt)

        if not self.is_model_installed():
            install_cmd = f"ollama pull {self.model}"
            logger.warning(f"Model '{self.model}' missing. Installation command: {install_cmd}")
            return f"Model '{self.model}' is missing. Please run in terminal: '{install_cmd}'. (Operating in Safe Mode)"

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
            logger.warning(f"Ollama server connection failed: {url_err}. Utilizing Safe Mode generator.")
        except Exception as err:
            logger.error(f"Error querying Ollama LLM: {err}")

        # Intelligent Safe Mode response generator if Ollama fails
        return self._generate_fallback_response(user_prompt)

    def _generate_fallback_response(self, text: str) -> str:
        """Generates friendly Safe Mode responses when local LLM server is unavailable."""
        clean = text.lower().strip()

        if any(w in clean for w in ["hello", "hi", "hey", "সালাম", "হ্যালো"]):
            return "Hello! I am X Assistant Phase 6. How can I help you today?"
        elif any(w in clean for w in ["who are you", "কে তুমি", "তোমার নাম কি", "what is your name"]):
            return "I am X Assistant Phase 6, your Personal AI Ecosystem built with local open-source tools."
        elif any(w in clean for w in ["how are you", "কেমন আছো", "কেমন আছেন"]):
            return "I am doing great! All local AI modules and automation systems are ready."
        elif any(w in clean for w in ["thank you", "thanks", "ধন্যবাদ"]):
            return "You are very welcome! Let me know if you need anything else."
        elif any(w in clean for w in ["bye", "goodbye", "বিদায়"]):
            return "Goodbye! Have a wonderful day!"
        
        return f"Safe Mode Output: Handled prompt '{text}'. Run 'ollama serve' and 'ollama pull {self.model}' for full conversational AI."


# Global Ollama client instance
ollama_client = OllamaClient()
