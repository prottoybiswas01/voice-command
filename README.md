# X Assistant (Phase-1) 🤖

**X Assistant** is a complete, production-ready, clean-architecture Personal AI Voice Assistant built in Python using **100% Free and Open Source local tools**. It features offline voice recognition, wake word detection (**"X"**, **"Hey X"**, **"X Listen"**), local LLM integration via Ollama, native Windows automation, productivity tools (todos, notes, reminders), hardware diagnostics, multi-language support (Bangla, English, Mixed Banglish), and a visual Tkinter GUI dashboard.

---

## 🌟 Key Features

### 🎙️ Voice & AI Intelligence
- **Wake Word Engine**: Listens continuously for `"X"`, `"Hey X"`, or `"X Listen"` before triggering activation.
- **Offline Speech-To-Text (STT)**: Recognizes voice prompts in English (`en-US`) and Bangla (`bn-BD`).
- **Text-To-Speech (TTS)**: Offline voice synthesis using `pyttsx3` with Windows SAPI5 engines.
- **Local LLM Conversation**: Connects to **Ollama** (`gemma2:2b`, `llama3.2`, `mistral`) for privacy-first AI responses without paid APIs.

### 💻 System & OS Automation
- **App Launchers**: Launch Chrome, Edge, VS Code, Notepad, Calculator, File Explorer, Task Manager.
- **Media Controls**: Play, Pause, Stop music via hardware media keys.
- **System Volume**: Volume Up, Volume Down, Mute/Unmute.
- **Power Controls**: Computer Shutdown, Restart, and Sleep with safety confirmation prompts.
- **Date & Time**: Speech query for current time and date.

### 🌐 Web & Productivity Tools
- **Web Integrations**: Google Search, YouTube Search, Open YouTube.
- **Productivity Systems**: Todo List, Voice Notes, Scheduled Reminders (with background checker).
- **System Diagnostics**: Live CPU usage %, RAM %, Battery percentage & status, Internet connection check.
- **Offline Placeholders**: Weather & News forecast engines.

### 🖥️ Modern Dashboard & Logs
- **Tkinter Dark Mode Dashboard**: Animated status bar, interactive chat transcript, and hardware stats sidebar.
- **SQLite Database**: Persistent history for conversations, commands, todos, notes, and reminders.
- **Dual Logger**: Daily execution logs (`logs/daily_YYYY-MM-DD.log`) and Error logs (`logs/error_YYYY-MM-DD.log`).

---

## 📁 Project Architecture

```
c:\voice command\
├── config/
│   ├── config.yaml           # YAML App configuration settings
│   └── settings.py           # Configuration loader & settings singleton
├── core/
│   ├── logger.py             # Dual logging system (Daily & Error)
│   ├── database.py           # SQLite database CRUD manager
│   └── event_bus.py          # Pub-sub event bus
├── speech/
│   ├── stt.py                # Speech-To-Text engine
│   ├── tts.py                # Text-To-Speech engine
│   └── wake_word.py          # Wake word listener ("X", "Hey X")
├── brain/
│   ├── llm_client.py         # Local Ollama HTTP API client
│   └── intent_parser.py      # Natural language intent classifier
├── actions/
│   ├── system_actions.py     # Windows OS apps & power actions
│   ├── media_actions.py      # Hardware media keys & volume control
│   ├── web_actions.py        # Web search & site opening
│   └── productivity_actions. # Todo, Notes, Reminders & System metrics
├── ui/
│   └── dashboard.py          # Tkinter visual UI dashboard
├── utils/
│   └── helpers.py            # Text sanitization & timestamp utils
├── tests/
│   └── test_assistant.py     # Unit test suite
├── main.py                   # Main application entry point
├── requirements.txt          # Python package manifest
├── .env.example              # Environment variables template
├── setup.bat                 # Windows virtual environment setup
├── install.bat               # Package dependency installer
└── run.bat                   # App launcher
```

---

## 🛠️ Step-by-Step Installation Instructions (Windows)

### Step 1: Prerequisites
1. **Python 3.10+**: Download & install Python from [python.org](https://www.python.org/downloads/). Ensure **"Add Python to PATH"** is checked during installation.
2. **Ollama (Local LLM Server)**: Download & install Ollama from [ollama.com](https://ollama.com/download/windows).
   Open Command Prompt / Terminal and pull a lightweight model:
   ```cmd
   ollama pull gemma2:2b
   ```

---

### Step 2: Automatic Setup & Installation
1. Double-click **`setup.bat`** to create the Python virtual environment (`venv`).
2. Double-click **`install.bat`** to install all required dependencies.
   *(Note: If PyAudio compilation raises an error on Python 3.14, install the prebuilt wheel via `pip install pyaudio --only-binary=:all:` or use the GUI text input fallback).*

---

### Step 3: Launching X Assistant
1. Ensure Ollama is running in the background.
2. Double-click **`run.bat`** (or execute `python main.py` in terminal).
3. Say **"Hey X"** or **"X"** to wake up the assistant!

---

## 🗣️ Example Voice Commands

### English Commands
- *"Hey X, what time is it?"*
- *"X, open Chrome"*
- *"X, open VS Code"*
- *"X, volume up"*
- *"X, search Google for Python clean architecture"*
- *"X, add todo buy milk"*
- *"X, take note meeting at 4 PM"*
- *"X, check battery status"*
- *"X, shutdown computer"*

### Bangla / Mixed Commands
- *"হে এক্স, এখন কয়টা বাজে?"*
- *"এক্স শোনো, নোটিপ্যাড খুলো"*
- *"এক্স, সাউন্ড বাড়াও"*
- *"এক্স, গুগল সার্চ করো বাংলাদেশ আবহাওয়া"*
- *"এক্স, পিসি অবস্থা দেখাও"*

---

## 🧪 Running Unit Tests

To verify all database, intent, and helper functions:
```cmd
python -m unittest discover tests
```

---

## 📄 License
This project is released under the **MIT Open Source License**. Built with 100% Free Tools.
