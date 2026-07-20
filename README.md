# X Assistant - Phase 5 (Vision AI, Multimodal Intelligence & Smart Recognition) 👁️🤖

**X Assistant Phase 5** transforms the assistant into a multimodal AI Assistant that can **SEE, LISTEN, UNDERSTAND, and RESPOND**. It integrates real-time webcam vision (`OpenCV`), object detection & person counting, Optical Character Recognition (`Tesseract OCR`), desktop screen text extraction, multimodal prompt context synthesis, security privacy safeguards (Camera OFF by default), and an expanded Vision AI Dashboard.

---

## 🌟 Key Phase-5 Features

### 👁️ 1. Vision AI & Privacy Safeguards
- **Privacy-First Architecture**: Camera & Microphone remain **OFF by default** until explicitly invoked by voice/button command, with red active indicators.
- **Webcam Stream**: Multi-camera stream processing with single-frame photo snapshots saved to `data/captures/` and video recordings saved to `data/recordings/`.

### 👥 2. Object, Person & Scene Detection
- **Person Counter**: Detects and counts visible people in front of the camera.
- **Face & Hand Detection**: Face detection bounding boxes and hand gesture recognition.
- **Scene Summary**: Generates structured descriptions (e.g. *"I see 2 people, a laptop, and a chair"*).

### 📄 3. Optical Character Recognition (Tesseract OCR)
- **Document & Poster Reader**: Reads printed/handwritten text from camera snapshots.
- **On-Screen Desktop OCR**: Captures active desktop screen snapshot and extracts screen text snippet.
- **Searchable OCR History**: Stores extracted text in SQLite `ocr_history` table.

### 🧠 4. Multimodal Intelligence Synthesizer
- Synthesizes Voice prompt + Camera Vision scene + Desktop Screen OCR + SQLite Memory preferences + Arduino IoT Sensor Telemetry into a unified context prompt for local Ollama LLM responses.

### 🖥️ 5. Upgraded Vision AI Dashboard
- **Vision AI Tab**: Camera view status, live object detection summary, Tesseract OCR text display box, and camera control action buttons.

---

## 📁 Project Architecture

```
c:\voice command\
├── config/
│   ├── config.yaml           # Phase-5 Vision & Multimodal config
│   └── settings.py           # Configuration loader
├── core/
│   ├── logger.py             # Dual logger
│   ├── database.py           # Phase-5 SQLite tables (vision_captures, ocr_history, detected_objects)
│   └── event_bus.py          # Pub-sub event bus
├── vision/
│   ├── camera_engine.py      # [NEW] Camera manager, video recorder, privacy state
│   ├── detector.py           # [NEW] Object detection, person counter, scene summary
│   ├── ocr_engine.py         # [NEW] Tesseract OCR text reader & Desktop screen OCR
│   └── vision_actions.py     # [NEW] Smart Vision voice command handler
├── brain/
│   ├── multimodal.py         # [NEW] Multimodal Context Synthesizer
│   ├── agent.py              # Autonomous AI Agent Loop
│   ├── pomodoro.py           # Pomodoro Focus Timer
│   ├── memory.py             # Long-term memory manager
│   ├── reasoning.py          # Task decomposition agent
│   ├── llm_client.py         # Local Ollama client
│   └── intent_parser.py      # Phase-5 Intent classifier
├── actions/
│   ├── window_manager.py     # Win32 Window Manager
│   ├── file_organizer.py     # File System & ZIP Manager
│   ├── recorder.py           # Screen & Audio Recorder
│   ├── network_settings.py   # Wi-Fi, Bluetooth & Settings
│   ├── browser_agent.py      # Playwright Browser Agent
│   ├── productivity_hub.py   # Pomodoro, Calendar, Clipboard
│   └── security_auditor.py   # Security Auditor & Audit Logger
├── iot/
│   ├── arduino_bridge.py     # Arduino serial bridge
│   ├── device_manager.py     # IoT Device registry
│   ├── smart_home.py         # Smart Home voice controller
│   └── automation_rules.py   # Rule-based automation engine
├── ui/
│   └── dashboard.py          # Upgraded Vision AI Tab UI
├── firmware/
│   └── x_assistant_arduino.ino # Production Arduino C++ sketch
├── docs/
│   └── wiring_guide.md       # Hardware pinout guide
├── tests/
│   ├── test_assistant.py     # Phase-1 tests
│   ├── test_phase2.py        # Phase-2 tests
│   ├── test_phase3.py        # Phase-3 tests
│   ├── test_phase4.py        # Phase-4 tests
│   └── test_phase5.py        # [NEW] Phase-5 unit tests
├── main.py                   # Main entry point
├── requirements.txt          # Package manifest
├── setup.bat                 # Setup script
├── install.bat               # Dependency installer
└── run.bat                   # App launcher
```

---

## 🛠️ Step-by-Step Installation Guide (Windows)

### Step 1: Prerequisites
1. **Python 3.10+**: Download & install Python from [python.org](https://www.python.org/downloads/).
2. **Ollama**: Installed with model pulled (`ollama pull gemma2:2b`).
3. **Tesseract OCR (Optional)**: Download Windows binary installer from [GitHub Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) to enable OCR text reading.

### Step 2: Install & Launch
1. Run **`setup.bat`** and **`install.bat`**.
2. Double-click **`run.bat`** or run `python main.py` in terminal.
3. Say **"Hey X"** to test your Vision AI Assistant!

---

## 🗣️ Voice Command Examples

- *"Hey X, what do you see?"*
- *"X, read the text on the screen"*
- *"X, count how many people are here"*
- *"X, recognize this object"*
- *"X, is someone standing at the door?"*
- *"X, take a picture"*
- *"X, start video recording"*
- *"X, minimize Chrome and what do you see?"* (Autonomous Multi-Step Vision Agent)

---

## 🧪 Running Unit Test Suite

Run complete Phase 1 to Phase 5 test suite:
```cmd
$env:PYTHONPATH="." ; .\venv\Scripts\python.exe -m unittest discover tests
```
