"""
X Assistant Configuration Loader Module (Phase 6 Upgrade).
Provides centralized settings management loading from YAML and environment variables.
"""

import os
try:
    import yaml
except ImportError:
    yaml = None

from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"


@dataclass
class AssistantSettings:
    name: str = "X Assistant"
    version: str = "6.0.0"
    wake_words: List[str] = field(default_factory=lambda: ["x", "hey x", "x listen"])
    language: str = "bn-EN"
    debug_mode: bool = True
    active_personality: str = "standard"


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
    timeout: int = 45
    max_context_length: int = 4096
    system_prompt: str = "You are X Assistant Phase 6, the Ultimate Personal AI Ecosystem."


@dataclass
class BrowserSettings:
    preferred_browser: str = "chrome"
    headless: bool = False
    slow_mo: int = 500


@dataclass
class MusicSettings:
    priority: List[str] = field(default_factory=lambda: ["spotify", "youtube", "local"])
    local_music_dir: Path = Path.home() / "Music"


@dataclass
class AgentSettings:
    auto_retry_attempts: int = 2
    pomodoro_focus_minutes: int = 25
    pomodoro_break_minutes: int = 5


@dataclass
class IoTSettings:
    baud_rate: int = 9600
    auto_detect_com: bool = True
    simulation_mode_if_disconnected: bool = True
    default_room: str = "Living Room"


@dataclass
class VisionSettings:
    camera_index: int = 0
    camera_fps: int = 30
    frame_width: int = 640
    frame_height: int = 480
    privacy_default_off: bool = True
    tesseract_cmd: str = "tesseract"


@dataclass
class RagSettings:
    knowledge_dir: Path = BASE_DIR / "data" / "knowledge"
    chunk_size: int = 500
    top_k_results: int = 3


@dataclass
class PathSettings:
    db_path: Path = BASE_DIR / "data" / "x_assistant.db"
    logs_dir: Path = BASE_DIR / "logs"
    notes_dir: Path = BASE_DIR / "data" / "notes"
    screenshots_dir: Path = BASE_DIR / "data" / "screenshots"
    recordings_dir: Path = BASE_DIR / "data" / "recordings"
    audio_dir: Path = BASE_DIR / "data" / "audio"
    captures_dir: Path = BASE_DIR / "data" / "captures"
    knowledge_dir: Path = BASE_DIR / "data" / "knowledge"
    plugins_dir: Path = BASE_DIR / "plugins"


class Settings:
    """Central configuration instance for X Assistant Phase 6."""

    def __init__(self, config_file: Path = CONFIG_PATH) -> None:
        self.config_file = config_file
        self.assistant = AssistantSettings()
        self.speech = SpeechSettings()
        self.ollama = OllamaSettings()
        self.browser = BrowserSettings()
        self.music = MusicSettings()
        self.agent = AgentSettings()
        self.iot = IoTSettings()
        self.vision = VisionSettings()
        self.rag = RagSettings()
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
                self.assistant.version = data["assistant"].get("version", self.assistant.version)
                self.assistant.wake_words = [
                    w.lower() for w in data["assistant"].get("wake_words", self.assistant.wake_words)
                ]
                self.assistant.language = data["assistant"].get("language", self.assistant.language)
                self.assistant.debug_mode = data["assistant"].get("debug_mode", self.assistant.debug_mode)
                self.assistant.active_personality = data["assistant"].get("active_personality", self.assistant.active_personality)

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
                self.ollama.max_context_length = data["ollama"].get("max_context_length", self.ollama.max_context_length)
                self.ollama.system_prompt = data["ollama"].get("system_prompt", self.ollama.system_prompt)

            if "browser" in data:
                self.browser.preferred_browser = data["browser"].get("preferred_browser", self.browser.preferred_browser)
                self.browser.headless = data["browser"].get("headless", self.browser.headless)
                self.browser.slow_mo = data["browser"].get("slow_mo", self.browser.slow_mo)

            if "music" in data:
                self.music.priority = data["music"].get("priority", self.music.priority)
                dir_str = data["music"].get("local_music_dir", "")
                if dir_str:
                    self.music.local_music_dir = Path(os.path.expanduser(dir_str))

            if "agent" in data:
                self.agent.auto_retry_attempts = data["agent"].get("auto_retry_attempts", self.agent.auto_retry_attempts)
                self.agent.pomodoro_focus_minutes = data["agent"].get("pomodoro_focus_minutes", self.agent.pomodoro_focus_minutes)
                self.agent.pomodoro_break_minutes = data["agent"].get("pomodoro_break_minutes", self.agent.pomodoro_break_minutes)

            if "iot" in data:
                self.iot.baud_rate = data["iot"].get("baud_rate", self.iot.baud_rate)
                self.iot.auto_detect_com = data["iot"].get("auto_detect_com", self.iot.auto_detect_com)
                self.iot.simulation_mode_if_disconnected = data["iot"].get("simulation_mode_if_disconnected", self.iot.simulation_mode_if_disconnected)
                self.iot.default_room = data["iot"].get("default_room", self.iot.default_room)

            if "vision" in data:
                self.vision.camera_index = data["vision"].get("camera_index", self.vision.camera_index)
                self.vision.camera_fps = data["vision"].get("camera_fps", self.vision.camera_fps)
                self.vision.frame_width = data["vision"].get("frame_width", self.vision.frame_width)
                self.vision.frame_height = data["vision"].get("frame_height", self.vision.frame_height)
                self.vision.privacy_default_off = data["vision"].get("privacy_default_off", self.vision.privacy_default_off)
                self.vision.tesseract_cmd = data["vision"].get("tesseract_cmd", self.vision.tesseract_cmd)

            if "rag" in data:
                if "knowledge_dir" in data["rag"]:
                    self.rag.knowledge_dir = BASE_DIR / data["rag"]["knowledge_dir"]
                self.rag.chunk_size = data["rag"].get("chunk_size", self.rag.chunk_size)
                self.rag.top_k_results = data["rag"].get("top_k_results", self.rag.top_k_results)

            if "paths" in data:
                if "db_path" in data["paths"]:
                    self.paths.db_path = BASE_DIR / data["paths"]["db_path"]
                if "logs_dir" in data["paths"]:
                    self.paths.logs_dir = BASE_DIR / data["paths"]["logs_dir"]
                if "notes_dir" in data["paths"]:
                    self.paths.notes_dir = BASE_DIR / data["paths"]["notes_dir"]
                if "screenshots_dir" in data["paths"]:
                    self.paths.screenshots_dir = BASE_DIR / data["paths"]["screenshots_dir"]
                if "recordings_dir" in data["paths"]:
                    self.paths.recordings_dir = BASE_DIR / data["paths"]["recordings_dir"]
                if "audio_dir" in data["paths"]:
                    self.paths.audio_dir = BASE_DIR / data["paths"]["audio_dir"]
                if "captures_dir" in data["paths"]:
                    self.paths.captures_dir = BASE_DIR / data["paths"]["captures_dir"]
                if "knowledge_dir" in data["paths"]:
                    self.paths.knowledge_dir = BASE_DIR / data["paths"]["knowledge_dir"]
                if "plugins_dir" in data["paths"]:
                    self.paths.plugins_dir = BASE_DIR / data["paths"]["plugins_dir"]

        except Exception as err:
            print(f"[Warning] Failed to parse config file: {err}. Using default settings.")

        # Ensure directories exist
        self.paths.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.paths.logs_dir.mkdir(parents=True, exist_ok=True)
        self.paths.notes_dir.mkdir(parents=True, exist_ok=True)
        self.paths.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.paths.recordings_dir.mkdir(parents=True, exist_ok=True)
        self.paths.audio_dir.mkdir(parents=True, exist_ok=True)
        self.paths.captures_dir.mkdir(parents=True, exist_ok=True)
        self.paths.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.paths.plugins_dir.mkdir(parents=True, exist_ok=True)


# Global Phase-6 settings instance
settings = Settings()
