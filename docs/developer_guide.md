# Developer & Architecture Guide - X Assistant (Phase 6 Ecosystem) 🛠️

Welcome to the **Developer, Plugin Development, and Architecture Guide** for X Assistant Phase 6.

---

## 🏗️ Architecture Overview

X Assistant is built on a clean, modular Python architecture organized into five primary layers:

1. **Config & Core (`config/`, `core/`)**:
   - `Settings`: Singleton configuration loader from `config/config.yaml`.
   - `DatabaseManager`: SQLite persistence for conversations, memory, audit logs, IoT devices, RAG documents, plugins, and health logs.
   - `SystemDiagnostics`: Background daemon monitoring CPU %, RAM %, Disk %, and SQLite database size.

2. **Speech & Multimodal Brain (`speech/`, `brain/`, `vision/`)**:
   - `stt_engine` & `tts_engine`: Offline-first Speech-To-Text and Text-To-Speech interfaces.
   - `AutonomousAgent`: Multi-step task planner, step verifier, and auto-retry loop.
   - `LocalRAGKnowledgeBase`: Indexing and searching PDF, TXT, MD, DOCX files in `data/knowledge/`.
   - `AIPersonalityManager`: Personality switching (Standard, Professional, Friendly, Concise) and local Ollama model selection.
   - `MultimodalSynthesizer`: Context fusion combining Voice + Vision + OCR + Memories + IoT Telemetry.

3. **Actions & Computer Control (`actions/`)**:
   - `window_manager`: Native Win32 application window controls (minimize, maximize, close, bring to front).
   - `file_organizer`: File CRUD, directory management, and `.zip` archive compression/extraction.
   - `recorder`: Background screen snapshot recorder and microphone WAV recorder.
   - `workflow_engine`: Custom macro routines ("Start Work Mode", "Good Night").

4. **IoT & Smart Home (`iot/`)**:
   - `arduino_bridge`: PySerial manager with auto-COM port discovery and Virtual Simulation mode.
   - `device_manager`: Device registry and room grouping.
   - `automation_rule_engine`: Background trigger evaluator (Temp > 32°C ➔ Fan ON, Motion ➔ Light ON, Gas ➔ Alarm).

5. **Extensible Plugins (`plugins/`)**:
   - Dynamic plugin loader loading custom `.py` files in `plugins/`.

---

## 🔌 How to Write a Custom Plugin

Creating a plugin requires adding a `.py` file into the `plugins/` directory:

```python
# plugins/my_custom_plugin.py
from typing import Dict, Any

def my_custom_command(raw_text: str, params: Dict[str, Any]) -> str:
    return "Custom plugin command executed successfully!"

def setup_plugin(manager) -> Dict[str, Any]:
    # Register voice trigger keyword
    manager.register_command("my custom trigger", my_custom_command)
    return {
        "id": "my_custom_plugin",
        "name": "My Custom Extension Plugin",
        "version": "1.0.0"
    }
```

The `PluginManager` will automatically discover and load `my_custom_plugin.py` upon startup!

---

## 📚 Ingesting Documents into RAG Knowledge Base

Copy PDF, TXT, Markdown, or Word `.docx` documents into `data/knowledge/` or run via voice:
- *"X, import document C:\docs\manual.pdf"*
- *"X, search knowledge base for database configuration"*
