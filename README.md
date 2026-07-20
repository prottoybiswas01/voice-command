# X Assistant - Phase 2 (AI Brain & Smart Automation) 🤖

**X Assistant Phase 2** is a production-ready, clean-architecture Personal AI Voice Assistant built in Python using **100% Free and Open Source local tools**. Phase-2 introduces multi-step AI reasoning, persistent user memory, Playwright browser automation, smart music playback, live internet data (weather, news, Wikipedia), and advanced Windows system controls.

---

## 🚀 Phase-2 Features

### 🧠 1. Smart Memory & Context Buffer
- **User Preferences**: Remembers your favorite song, artist, preferred browser, user name, and custom preferences in local SQLite database.
- **Context Injection**: Automatically injects past conversation context and user memory into Ollama system prompts.
- **Implicit Memory Extraction**: Listens for statements like *"My favorite song is Hotel California"* or *"Remember that my name is Alex"* and saves them automatically.

### 🧩 2. Multi-Step Reasoning Agent
- **Task Decomposition**: Automatically breaks multi-intent prompts like *"Take a screenshot, search news, and open GitHub"* into sequential ordered sub-tasks.

### 🌐 3. Playwright Browser Automation
- **Browser Support**: Chrome, Edge, Firefox.
- **Social Media & Web Portals**: Quick navigation & interaction for Facebook, Messenger, Instagram, LinkedIn, GitHub, Gmail, and Google Drive.
- **Automation Actions**: Fill forms, click buttons, scroll pages up/down, read page titles, and check notification badges.

### 🎵 4. Smart Music Playback Engine
- **Priority Dispatch Hierarchy**:
  1. **Spotify**: Opens Spotify app or web search.
  2. **YouTube**: Searches & plays song on YouTube.
  3. **Local Music Folder**: Scans `C:\Users\<user>\Music` for `.mp3`, `.wav`, `.flac` files.

### 📡 5. Live Web Intelligence (No API Keys)
- **Live Weather**: Real-time temperature & forecast for any city via `wttr.in`.
- **Live News**: Top global and local headlines via RSS feeds.
- **Wikipedia Search**: Summarizes any topic using `wikipedia` package.

### 💻 6. Advanced System Controls & Security Gates
- **Screen Brightness**: Adjust monitor brightness up/down/set level.
- **Screen Capture**: Takes desktop screenshots and saves to `data/screenshots/`.
- **File Search**: Searches Documents, Downloads, and Desktop for files matching query.
- **Explorer Restart**: Restarts Windows File Explorer (`explorer.exe`).
- **Security Confirmation Safeguards**: Asks double-confirmation before executing Shutdown, Restart, File Deletion, or closing major apps.

---

## 📁 Project Architecture

```
c:\voice command\
├── config/
│   ├── config.yaml           # Phase-2 settings schema
│   └── settings.py           # Configuration loader singleton
├── core/
│   ├── logger.py             # Dual logging system
│   ├── database.py           # Phase-2 SQLite tables (preferences, memory, stats)
│   └── event_bus.py          # Pub-sub event bus
├── speech/
│   ├── stt.py                # Speech-To-Text engine
│   ├── tts.py                # Text-To-Speech engine
│   └── wake_word.py          # Wake word listener ("X", "Hey X")
├── brain/
│   ├── memory.py             # [NEW] Long-term memory & preference manager
│   ├── reasoning.py          # [NEW] Multi-step reasoning agent
│   ├── llm_client.py         # Local Ollama HTTP API client
│   └── intent_parser.py      # Phase-2 Intent classifier
├── actions/
│   ├── browser_automation.py # [NEW] Playwright browser automation
│   ├── smart_music.py        # [NEW] Priority music dispatcher
│   ├── internet_actions.py   # [NEW] Weather, RSS News, Wikipedia
│   ├── system_control.py     # [NEW] Screenshots, Brightness, File Search
│   ├── system_actions.py     # OS app launches & confirmation gates
│   ├── media_actions.py      # Volume & media keys
│   ├── web_actions.py        # Web openers & search
│   └── productivity_actions. # Todo, Notes, Reminders
├── ui/
│   └── dashboard.py          # Phase-2 Tkinter dark mode UI
├── utils/
│   └── helpers.py            # Sanitization & timestamp helpers
├── tests/
│   ├── test_assistant.py     # Phase-1 test suite
│   └── test_phase2.py        # [NEW] Phase-2 unit test suite
├── main.py                   # Main orchestrator entry point
├── requirements.txt          # Python package manifest
├── setup.bat                 # Environment setup script
├── install.bat               # Package dependency installer
└── run.bat                   # App launcher script
```

---

## 🛠️ Step-by-Step Installation Guide (Windows)

### Step 1: Prerequisites
1. **Python 3.10+**: Download & install Python from [python.org](https://www.python.org/downloads/).
2. **Ollama**: Download & install from [ollama.com](https://ollama.com). Run terminal command:
   ```cmd
   ollama pull gemma2:2b
   ```

### Step 2: Automatic Setup
1. Run **`setup.bat`** to create virtual environment `venv`.
2. Run **`install.bat`** to install dependencies:
   ```cmd
   install.bat
   ```

### Step 3: Launch Assistant
1. Ensure Ollama server is running locally.
2. Double-click **`run.bat`** or run `python main.py` in terminal.
3. Say **"Hey X"** or **"X"** to wake up the assistant!

---

## 🗣️ Example Voice Commands

- *"Hey X, play music"* (Dispatches via Spotify -> YouTube -> Local)
- *"X, check weather in Dhaka"*
- *"X, what are the latest news headlines?"*
- *"X, search Wikipedia for Artificial Intelligence"*
- *"X, open GitHub"*
- *"X, take a screenshot"*
- *"X, set brightness to 80%"*
- *"X, search file report"*
- *"X, take a screenshot and check weather"* (Multi-step reasoning)

---

## 🧪 Running Unit Tests

Run Phase-1 and Phase-2 unit test suites:
```cmd
$env:PYTHONPATH="." ; .\venv\Scripts\python.exe -m unittest discover tests
```
