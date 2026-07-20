# X Assistant - Phase 4 (Arduino, IoT & Smart Home Integration) 🏠⚡

**X Assistant Phase 4** transforms the voice assistant into a complete **Smart Home and IoT AI Assistant** capable of communicating with physical Arduino hardware boards over USB Serial, controlling electronics, reading real-time sensors, and executing automated smart home rules.

---

## 🌟 Key Phase-4 Features

### ⚡ 1. Arduino Two-Way Serial Bridge
- **PySerial Integration**: Connects via USB Serial (`9600` baud rate) with automatic COM port scanning and heartbeat pings.
- **Virtual Simulation Mode**: Automatic fallback mode when no physical Arduino board is connected, allowing complete UI, voice commands, and automation testing without hardware errors.
- **Production Firmware**: Includes complete C++ Arduino sketch [firmware/x_assistant_arduino.ino](file:///c:/voice%20command/firmware/x_assistant_arduino.ino).

### 💡 2. Smart Home Voice Control
- **Relays & Lighting**: *"X, turn on room light"*, *"X, turn off fan"*, *"X, turn on all relays"*.
- **Sensors**: *"X, read room temperature"*, *"X, show humidity"*, *"X, detect motion"*, *"X, check if anyone is at the door"*.
- **Motors & Actuators**: *"X, rotate servo to 90 degrees"*, *"X, blink LED 5 times"*.

### 🔄 3. Rule-Based Automation Engine
- **Rule 1**: Temperature > 32°C ➔ Turn ON Room Fan Relay.
- **Rule 2**: Motion Detected ➔ Turn ON Room Light Relay.
- **Rule 3**: Gas Leak > Threshold ➔ Activate Alarm Buzzer & Voice Warning.

### 🖥️ 4. Upgraded Smart Home IoT Dashboard
- **Live Sensor Telemetry**: Gauges for Temperature (°C), Humidity (%), Motion status, and Gas levels.
- **Interactive Actuator Toggles**: Buttons for toggling Light Relays, Fan Relays, Servo Lock, and Security Alarm.
- **COM Port Status**: Live COM port status & connection monitor.

---

## 📁 Project Architecture

```
c:\voice command\
├── config/
│   ├── config.yaml           # Phase-4 IoT configuration
│   └── settings.py           # Configuration loader
├── core/
│   ├── logger.py             # Dual logger
│   ├── database.py           # Phase-4 SQLite tables (iot_devices, sensor_logs, automation_rules)
│   └── event_bus.py          # Pub-sub event bus
├── firmware/
│   └── x_assistant_arduino.ino # [NEW] Production Arduino C++ firmware sketch
├── iot/
│   ├── arduino_bridge.py     # [NEW] PySerial bridge, auto-COM detection, virtual simulation
│   ├── device_manager.py     # [NEW] Device registry, pin mapping, room grouping
│   ├── smart_home.py         # [NEW] Voice to hardware command translator
│   └── automation_rules.py   # [NEW] Rule-based automation engine
├── brain/
│   ├── agent.py              # Autonomous AI Agent Loop
│   ├── pomodoro.py           # Pomodoro Focus Timer
│   ├── memory.py             # Long-term memory manager
│   ├── reasoning.py          # Task decomposition agent
│   ├── llm_client.py         # Local Ollama client
│   └── intent_parser.py      # Phase-4 Intent classifier
├── actions/
│   ├── window_manager.py     # Win32 Window Manager
│   ├── file_organizer.py     # File System & ZIP Manager
│   ├── recorder.py           # Screen & Audio Recorder
│   ├── network_settings.py   # Wi-Fi, Bluetooth & Settings
│   ├── browser_agent.py      # Playwright Browser Agent
│   ├── productivity_hub.py   # Pomodoro, Calendar, Clipboard
│   └── security_auditor.py   # Security Auditor & Audit Logger
├── ui/
│   └── dashboard.py          # Upgraded Smart Home IoT Tab UI
├── docs/
│   └── wiring_guide.md       # Hardware pinout schematics & wiring guide
├── tests/
│   ├── test_assistant.py     # Phase-1 tests
│   ├── test_phase2.py        # Phase-2 tests
│   ├── test_phase3.py        # Phase-3 tests
│   └── test_phase4.py        # [NEW] Phase-4 unit tests
├── main.py                   # Main entry point
├── requirements.txt          # Python package manifest
├── setup.bat                 # Setup script
├── install.bat               # Dependency installer
└── run.bat                   # App launcher
```

---

## 🛠️ Step-by-Step Installation Guide (Windows)

### Step 1: Prerequisites
1. **Python 3.10+**: Download & install Python from [python.org](https://www.python.org/downloads/).
2. **Ollama**: Installed with model pulled (`ollama pull gemma2:2b`).
3. **Arduino IDE (Optional)**: Download from [arduino.cc](https://www.arduino.cc) to flash firmware to your Arduino board.

### Step 2: Flash Arduino Firmware
1. Open `firmware/x_assistant_arduino.ino` in Arduino IDE.
2. Select your board (Uno / Nano / Mega) and COM port.
3. Click **Upload**.

### Step 3: Launch Assistant
1. Run **`setup.bat`** and **`install.bat`**.
2. Double-click **`run.bat`** or execute `python main.py` in terminal.
3. Say **"Hey X"** to control your Smart Home!

---

## 🗣️ Voice Command Examples

- *"Hey X, turn on the room light"*
- *"X, turn off the fan"*
- *"X, read the room temperature"*
- *"X, show humidity"*
- *"X, detect motion"*
- *"X, rotate the servo to 90 degrees"*
- *"X, blink LED 5 times"*
- *"X, turn on all relays"*
- *"X, minimize Chrome and check room temperature"* (Multi-step agent reasoning)

---

## 🧪 Running Unit Test Suite

Run complete Phase 1 to Phase 4 test suite:
```cmd
$env:PYTHONPATH="." ; .\venv\Scripts\python.exe -m unittest discover tests
```
