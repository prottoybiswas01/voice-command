# X Assistant - Phase 3 (AI Agent & Full Computer Control) 🤖

**X Assistant Phase 3** transforms the voice assistant into a fully autonomous **Personal AI Agent** capable of controlling the entire Windows computer through voice and text commands. It features autonomous step planning, verification, and auto-retry, Win32 application window controls, file/folder operations & ZIP archiving, screen & audio recording, network/settings management, Playwright multi-tab browser automation, productivity hub (Pomodoro focus timer, clipboard history, calendar), and a security auditor with complete SQLite audit trails.

---

## 🌟 Key Phase-3 Features

### 🤖 1. Autonomous AI Agent Loop
- **Think Before Acting**: Autonomous plan generation -> step execution -> verification -> auto-retry on errors.
- **Self-Explanation**: Explains active step status and error recovery in clear human-friendly language.

### 🪟 2. Native Win32 Window Manager
- **Application Window Control**: Minimize, Maximize, Restore, Close, and Switch between active Windows applications (Chrome, VS Code, Notepad, Spotify).
- **Window Enumeration**: Inspects top-level desktop open windows.

### 📁 3. File System & Archive Manager
- **File & Directory Management**: Create, Rename, Copy, Move, and Delete files/directories.
- **Security Confirmation Gate**: Asks explicit user confirmation before deleting files or formatting.
- **ZIP Archiving**: Compress directories into `.zip` archives and extract `.zip` files.

### 🎙️ 4. Screen & Audio Recording
- **Microphone Audio Recording**: Captures audio voice notes and saves `.wav` files into `data/audio/`.
- **Screen Recording**: Captures frame sequence snapshots to `data/recordings/`.

### 📶 5. Network & Windows Settings
- **Wi-Fi Management**: Scan nearby networks, turn Wi-Fi on/off via `netsh`.
- **Windows Settings Shortcuts**: Open Bluetooth settings, Sound, Display, Network, Apps settings directly.
- **Startup Apps**: List registered Windows startup applications.

### 🌐 6. Advanced Playwright Browser Agent
- **Multi-Tab Navigation**: Open, switch, and close browser tabs for Chrome, Edge, and Firefox.
- **File Upload & Download**: Automated download triggering and file upload handling.
- **Structured Content Extraction**: Extracts main text snippets, links, and forms from active web pages.

### 🍅 7. Productivity Hub & Focus Tracker
- **Pomodoro Focus Timer**: 25-minute focus session / 5-minute break timer with audio notifications.
- **Clipboard History Tracker**: Monitors and stores Windows clipboard text history using `pyperclip`.
- **Calendar & Schedule Events**: Add and list scheduled events.

### 🔒 8. Security Auditor & Audit Logger
- **Confirmation Safeguards**: Required confirmation before File Deletion, Shutdown, Restart, or closing major applications.
- **SQLite Audit Logs**: Tracks every critical system action in `audit_logs` table.

---

## 📁 Project Architecture

```
c:\voice command\
├── config/
│   ├── config.yaml           # Phase-3 configuration schema
│   └── settings.py           # Configuration loader singleton
├── core/
│   ├── logger.py             # Dual logging system
│   ├── database.py           # Phase-3 SQLite tables (audit_logs, clipboard, pomodoro, calendar)
│   └── event_bus.py          # Pub-sub event bus
├── speech/
│   ├── stt.py                # Speech-To-Text engine
│   ├── tts.py                # Text-To-Speech engine
│   └── wake_word.py          # Wake word listener ("X", "Hey X")
├── brain/
│   ├── agent.py              # [NEW] Autonomous AI Agent Loop (Plan -> Verify -> Retry)
│   ├── pomodoro.py           # [NEW] Pomodoro Focus Timer daemon
│   ├── memory.py             # Long-term memory manager
│   ├── reasoning.py          # Task decomposition agent
│   ├── llm_client.py         # Local Ollama HTTP API client
│   └── intent_parser.py      # Phase-3 Intent classifier
├── actions/
│   ├── window_manager.py     # [NEW] Win32 Window Manager (Minimize, Maximize, Close, Switch)
│   ├── file_organizer.py     # [NEW] File/Folder Manager & ZIP Compress/Extract
│   ├── recorder.py           # [NEW] Screen Recorder & Audio Mic Recorder
│   ├── network_settings.py   # [NEW] Wi-Fi, Bluetooth, Settings, Startup Apps
│   ├── browser_agent.py      # [NEW] Multi-Tab Playwright Browser Agent
│   ├── productivity_hub.py   # [NEW] Pomodoro, Calendar, Clipboard History
│   ├── security_auditor.py   # [NEW] Security Auditor & Audit Logger
│   ├── browser_automation.py # Playwright browser controller
│   ├── smart_music.py        # Priority music dispatcher
│   ├── internet_actions.py   # Weather, News, Wikipedia
│   ├── system_control.py     # Hardware diagnostics & screenshots
│   ├── system_actions.py     # App launchers & power actions
│   ├── media_actions.py      # Volume & media keys
│   ├── web_actions.py        # Web openers & search
│   └── productivity_actions. # Todo, Notes, Reminders
├── ui/
│   └── dashboard.py          # Phase-3 Tkinter dark mode UI
├── utils/
│   └── helpers.py            # Helper utilities
├── tests/
│   ├── test_assistant.py     # Phase-1 test suite
│   ├── test_phase2.py        # Phase-2 test suite
│   └── test_phase3.py        # [NEW] Phase-3 test suite
├── main.py                   # Main orchestrator entry point
├── requirements.txt          # Python package manifest
├── setup.bat                 # Environment setup script
├── install.bat               # Package dependency installer
└── run.bat                   # App launcher script
```

---

## 🛠️ Step-by-Step Installation Guide (Windows)

### Step 1: Prerequisites
1. **Python 3.10+**: Installed and added to System PATH.
2. **Ollama**: Installed from [ollama.com](https://ollama.com) with model pulled:
   ```cmd
   ollama pull gemma2:2b
   ```

### Step 2: Automatic Setup
1. Double click **`setup.bat`** to create virtual environment `venv`.
2. Double click **`install.bat`** to install dependencies.

### Step 3: Launch Assistant
1. Ensure Ollama server is running.
2. Double-click **`run.bat`** or run `python main.py` in terminal.
3. Say **"Hey X"** or **"X"** to wake up your AI Agent!

---

## 🗣️ Voice Command Examples

- *"Hey X, minimize Chrome"*
- *"X, maximize VS Code"*
- *"X, switch to Spotify"*
- *"X, compress zip folder notes"*
- *"X, record voice note"*
- *"X, record screen"*
- *"X, start pomodoro"*
- *"X, show clipboard history"*
- *"X, show audit logs"*
- *"X, scan wifi networks"*
- *"X, open bluetooth settings"*
- *"X, take a screenshot and check weather"* (Multi-step reasoning plan)

---

## 🧪 Running Unit Test Suite

Run full Phase-1, Phase-2, and Phase-3 test suites:
```cmd
$env:PYTHONPATH="." ; .\venv\Scripts\python.exe -m unittest discover tests
```
