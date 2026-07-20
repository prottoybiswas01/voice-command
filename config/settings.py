"""
X Assistant Configuration Loader Module.
Provides centralized settings management loading from YAML and environment variables.
"""

import os
try:
    import yaml
except ImportError:
    yaml = None
    print("[Info] PyYAML not installed. Using default settings schema.")
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"


@dataclass
class AssistantSettings:
    name: str = "X Assistant"
    wake_words: List[str] = field(default_factory=lambda: ["x", "hey x", "x listen"])
    language: str = "bn-EN"
    debug_mode: bool = True


@dataclass
class SpeechSettings:
    stt_engine: str = "speech_recognition"
    stt_language_primary: str = "bn-BD"
    stt_language_secondary: str = "en-US"
    tts_engine: str = "pyttsx3"
    tts_rate: int = 175
    tts_volume: float = 1.0


@dataclass
class OllamaSettings:
    host: str = "http://localhost:11434"
    model: str = "gemma2:2b"
    timeout: int = 30
    system_prompt: str = "You are X Assistant, a helpful personal AI voice assistant."


@dataclass
class PathSettings:
    db_path: Path = BASE_DIR / "data" / "x_assistant.db"
    logs_dir: Path = BASE_DIR / "logs"
    notes_dir: Path = BASE_DIR / "data" / "notes"


class Settings:
    """Central configuration instance for X Assistant."""

    def __init__(self, config_file: Path = CONFIG_PATH) -> None:
        self.config_file = config_file
        self.assistant = AssistantSettings()
        self.speech = SpeechSettings()
        self.ollama = OllamaSettings()
        self.paths = PathSettings()
        self.load_config()

    def load_config(self) -> None:
        """Load configuration settings from YAML file if available."""
        if not self.config_file.exists():
            return

        try:
            data: Dict[str, Any] = {}
            if yaml:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}

            if "assistant" in data:
                self.assistant.name = data["assistant"].get("name", self.assistant.name)
                self.assistant.wake_words = [
                    w.lower() for w in data["assistant"].get("wake_words", self.assistant.wake_words)
                ]
                self.assistant.language = data["assistant"].get("language", self.assistant.language)
                self.assistant.debug_mode = data["assistant"].get("debug_mode", self.assistant.debug_mode)

            if "speech" in data:
                self.speech.stt_engine = data["speech"].get("stt_engine", self.speech.stt_engine)
                self.speech.stt_language_primary = data["speech"].get("stt_language_primary", self.speech.stt_language_primary)
                self.speech.stt_language_secondary = data["speech"].get("stt_language_secondary", self.speech.stt_language_secondary)
                self.speech.tts_engine = data["speech"].get("tts_engine", self.speech.tts_engine)
                self.speech.tts_rate = data["speech"].get("tts_rate", self.speech.tts_rate)
                self.speech.tts_volume = data["speech"].get("tts_volume", self.speech.tts_volume)

            if "ollama" in data:
                self.ollama.host = data["ollama"].get("host", self.ollama.host)
                self.ollama.model = data["ollama"].get("model", self.ollama.model)
                self.ollama.timeout = data["ollama"].get("timeout", self.ollama.timeout)
                self.ollama.system_prompt = data["ollama"].get("system_prompt", self.ollama.system_prompt)

            if "paths" in data:
                if "db_path" in data["paths"]:
                    self.paths.db_path = BASE_DIR / data["paths"]["db_path"]
                if "logs_dir" in data["paths"]:
                    self.paths.logs_dir = BASE_DIR / data["paths"]["logs_dir"]
                if "notes_dir" in data["paths"]:
                    self.paths.notes_dir = BASE_DIR / data["paths"]["notes_dir"]

        except Exception as err:
            print(f"[Warning] Failed to parse config file: {err}. Using default settings.")

        # Ensure directories exist
        self.paths.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.paths.logs_dir.mkdir(parents=True, exist_ok=True)
        self.paths.notes_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
