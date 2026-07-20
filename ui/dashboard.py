"""
GUI Dashboard Module for X Assistant (Phase 6 Upgrade).
Provides a modern dark-themed Tkinter interface displaying autonomous AI agent status, speech transcripts,
hardware diagnostics, Pomodoro timer, Audit logs, Smart Home IoT Tab, Vision AI Tab,
Knowledge Base RAG Tab, Plugins Tab, and Workflows Tab.
"""

import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from typing import Optional, Callable
from config.settings import settings
from core.logger import logger
from core.database import db
from core.event_bus import event_bus
from actions.productivity_actions import productivity_actions
from brain.pomodoro import pomodoro_timer
from brain.rag_knowledge import rag_knowledge_base
from brain.personalities import personality_manager
from plugins.plugin_manager import plugin_manager
from actions.security_auditor import security_auditor
from actions.workflow_engine import workflow_engine
from iot.arduino_bridge import arduino_bridge
from iot.smart_home import smart_home_controller
from vision.camera_engine import camera_engine
from vision.detector import vision_detector
from vision.ocr_engine import ocr_engine
from vision.vision_actions import vision_actions_handler


class AssistantDashboard:
    """Tkinter Desktop Dashboard Interface for X Assistant Phase 6 Personal AI Ecosystem."""

    def __init__(self, on_user_submit_callback: Optional[Callable[[str], None]] = None) -> None:
        self.on_user_submit_callback = on_user_submit_callback
        self.root = tk.Tk()
        self.root.title(f"{settings.assistant.name} Phase 6 - Personal AI Ecosystem")
        self.root.geometry("1100x800")
        self.root.minsize(900, 650)

        # Dark theme styling
        self.bg_color = "#1E1E2E"
        self.card_bg = "#282A36"
        self.fg_color = "#F8F8F2"
        self.accent_color = "#BD93F9"
        self.highlight_color = "#50FA7B"

        self.root.configure(bg=self.bg_color)
        self._setup_ui()
        self._subscribe_events()
        self._start_metrics_timer()

    def _setup_ui(self) -> None:
        """Construct dashboard components with Notebook tab bar."""
        # Top Header Bar
        header_frame = tk.Frame(self.root, bg=self.card_bg, pady=15, padx=20)
        header_frame.pack(fill=tk.X, side=tk.TOP)

        title_label = tk.Label(
            header_frame,
            text=f"🤖 {settings.assistant.name} (v{settings.assistant.version}) - Personal AI Ecosystem",
            font=("Segoe UI", 15, "bold"),
            fg=self.accent_color,
            bg=self.card_bg
        )
        title_label.pack(side=tk.LEFT)

        self.status_label = tk.Label(
            header_frame,
            text="● Listening for 'X' / 'Hey X'",
            font=("Segoe UI", 11, "bold"),
            fg=self.highlight_color,
            bg=self.card_bg
        )
        self.status_label.pack(side=tk.RIGHT)

        # Tabbed Notebook Container
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # TAB 1: AI Agent & Desktop Controls
        self.tab_agent = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.tab_agent, text="🤖 AI Agent")
        self._setup_agent_tab()

        # TAB 2: Smart Home & IoT Control
        self.tab_iot = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.tab_iot, text="🏠 Smart Home")
        self._setup_iot_tab()

        # TAB 3: Vision AI & Camera
        self.tab_vision = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.tab_vision, text="👁️ Vision AI")
        self._setup_vision_tab()

        # TAB 4: Knowledge Base RAG
        self.tab_rag = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.tab_rag, text="📚 Knowledge Base")
        self._setup_rag_tab()

        # TAB 5: Workflows & Scenes
        self.tab_workflows = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.tab_workflows, text="⚡ Workflows & Scenes")
        self._setup_workflows_tab()

        # TAB 6: Plugins Framework
        self.tab_plugins = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.tab_plugins, text="🔌 Plugins")
        self._setup_plugins_tab()

    def _setup_agent_tab(self) -> None:
        """Construct Main AI Agent tab."""
        main_container = tk.Frame(self.tab_agent, bg=self.bg_color, padx=10, pady=10)
        main_container.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main_container, bg=self.bg_color)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        log_title = tk.Label(left_frame, text="Live AI Reasoning Log", font=("Segoe UI", 11, "bold"), fg=self.fg_color, bg=self.bg_color)
        log_title.pack(anchor="w", pady=(0, 5))

        self.transcript_box = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, font=("Consolas", 10), bg=self.card_bg, fg=self.fg_color, insertbackground=self.fg_color, relief=tk.FLAT)
        self.transcript_box.pack(fill=tk.BOTH, expand=True)
        self.transcript_box.config(state=tk.DISABLED)

        input_frame = tk.Frame(left_frame, bg=self.bg_color, pady=10)
        input_frame.pack(fill=tk.X)

        self.input_entry = tk.Entry(input_frame, font=("Segoe UI", 11), bg=self.card_bg, fg=self.fg_color, insertbackground=self.fg_color, relief=tk.FLAT)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_entry.bind("<Return>", lambda e: self._on_send())

        send_btn = tk.Button(input_frame, text="Execute", font=("Segoe UI", 10, "bold"), bg=self.accent_color, fg="#000000", relief=tk.FLAT, padx=15, command=self._on_send)
        send_btn.pack(side=tk.RIGHT)

        right_frame = tk.Frame(main_container, bg=self.card_bg, width=260, padx=15, pady=15)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)

        sidebar_title = tk.Label(right_frame, text="System Health", font=("Segoe UI", 11, "bold"), fg=self.accent_color, bg=self.card_bg)
        sidebar_title.pack(anchor="w", pady=(0, 5))

        self.metrics_label = tk.Label(right_frame, text="CPU: --%\nRAM: --%\nBattery: --%", font=("Segoe UI", 9), fg=self.fg_color, bg=self.card_bg, justify=tk.LEFT)
        self.metrics_label.pack(anchor="w", pady=(0, 10))

        quick_cmds = [
            ("🍅 Start Pomodoro", "start pomodoro"),
            ("📋 Clipboard History", "__clipboard__"),
            ("📸 Take Screenshot", "take screenshot"),
            ("🔒 Security Logs", "__audit__"),
            ("🧹 Clear Log", "__clear__")
        ]

        for label, cmd in quick_cmds:
            btn = tk.Button(right_frame, text=label, font=("Segoe UI", 9), bg="#383A59", fg=self.fg_color, relief=tk.FLAT, anchor="w", padx=10, pady=3, command=lambda c=cmd: self._handle_quick_cmd(c))
            btn.pack(fill=tk.X, pady=2)

    def _setup_iot_tab(self) -> None:
        """Construct Smart Home IoT control tab."""
        container = tk.Frame(self.tab_iot, bg=self.bg_color, padx=15, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        conn_card = tk.Frame(container, bg=self.card_bg, padx=15, pady=10)
        conn_card.pack(fill=tk.X, pady=(0, 15))

        self.arduino_status_lbl = tk.Label(conn_card, text="⚡ Arduino Status: Scanning Serial Ports...", font=("Segoe UI", 11, "bold"), fg=self.highlight_color, bg=self.card_bg)
        self.arduino_status_lbl.pack(side=tk.LEFT)

        sensor_card = tk.LabelFrame(container, text="Live Sensor Telemetry", font=("Segoe UI", 11, "bold"), fg=self.accent_color, bg=self.card_bg, padx=15, pady=15)
        sensor_card.pack(fill=tk.X, pady=(0, 15))

        self.temp_lbl = tk.Label(sensor_card, text="🌡️ Temp: 28.5 °C", font=("Segoe UI", 12, "bold"), fg=self.fg_color, bg=self.card_bg)
        self.temp_lbl.grid(row=0, column=0, padx=20, pady=10)

        self.humidity_lbl = tk.Label(sensor_card, text="💧 Humidity: 65 %", font=("Segoe UI", 12, "bold"), fg=self.fg_color, bg=self.card_bg)
        self.humidity_lbl.grid(row=0, column=1, padx=20, pady=10)

        self.motion_lbl = tk.Label(sensor_card, text="🏃 Motion: Clear", font=("Segoe UI", 12, "bold"), fg=self.fg_color, bg=self.card_bg)
        self.motion_lbl.grid(row=0, column=2, padx=20, pady=10)

        self.gas_lbl = tk.Label(sensor_card, text="⚠️ Gas Level: Safe", font=("Segoe UI", 12, "bold"), fg=self.fg_color, bg=self.card_bg)
        self.gas_lbl.grid(row=0, column=3, padx=20, pady=10)

        control_card = tk.LabelFrame(container, text="Hardware Actuator Controls", font=("Segoe UI", 11, "bold"), fg=self.accent_color, bg=self.card_bg, padx=15, pady=15)
        control_card.pack(fill=tk.BOTH, expand=True)

        iot_actions = [
            ("💡 Toggle Light ON", "turn on room light"),
            ("💡 Toggle Light OFF", "turn off room light"),
            ("🌀 Toggle Fan ON", "turn on fan"),
            ("🌀 Toggle Fan OFF", "turn off fan"),
            ("🔔 Test Alarm Buzzer", "blink led"),
            ("🔑 Servo Lock (90°)", "rotate servo to 90 degrees"),
            ("⚡ All Relays ON", "turn on all relays"),
            ("🛑 All Relays OFF", "turn off all relays")
        ]

        r, c = 0, 0
        for label, cmd in iot_actions:
            btn = tk.Button(control_card, text=label, font=("Segoe UI", 10, "bold"), bg="#383A59", fg=self.fg_color, activebackground=self.accent_color, relief=tk.FLAT, padx=15, pady=10, command=lambda c=cmd: self._handle_quick_cmd(c))
            btn.grid(row=r, column=c, padx=10, pady=10, sticky="ew")
            c += 1
            if c > 3:
                c = 0
                r += 1

    def _setup_vision_tab(self) -> None:
        """Construct Vision AI tab."""
        container = tk.Frame(self.tab_vision, bg=self.bg_color, padx=15, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        privacy_card = tk.Frame(container, bg=self.card_bg, padx=15, pady=10)
        privacy_card.pack(fill=tk.X, pady=(0, 15))

        self.privacy_lbl = tk.Label(privacy_card, text="🔒 Privacy Status: Camera & Mic OFF (Standby)", font=("Segoe UI", 11, "bold"), fg=self.highlight_color, bg=self.card_bg)
        self.privacy_lbl.pack(side=tk.LEFT)

        left_col = tk.Frame(container, bg=self.bg_color)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        scene_card = tk.LabelFrame(left_col, text="Camera Vision Analysis", font=("Segoe UI", 11, "bold"), fg=self.accent_color, bg=self.card_bg, padx=15, pady=15)
        scene_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.vision_result_box = scrolledtext.ScrolledText(scene_card, wrap=tk.WORD, font=("Consolas", 10), bg=self.bg_color, fg=self.fg_color, height=8, relief=tk.FLAT)
        self.vision_result_box.pack(fill=tk.BOTH, expand=True)
        self.vision_result_box.insert(tk.END, "Vision AI Ready.")

        right_col = tk.Frame(container, bg=self.card_bg, width=280, padx=15, pady=15)
        right_col.pack(side=tk.RIGHT, fill=tk.Y)
        right_col.pack_propagate(False)

        vision_cmds = [
            ("👁️ What Do You See?", "what do you see"),
            ("📄 Read Screen Text", "read text on screen"),
            ("👥 Count People", "count people"),
            ("📸 Take Photo", "take a picture"),
            ("🎥 Record Video", "start video recording")
        ]

        for label, cmd in vision_cmds:
            btn = tk.Button(right_col, text=label, font=("Segoe UI", 10, "bold"), bg="#383A59", fg=self.fg_color, activebackground=self.accent_color, relief=tk.FLAT, padx=10, pady=8, anchor="w", command=lambda c=cmd: self._handle_quick_cmd(c))
            btn.pack(fill=tk.X, pady=4)

    def _setup_rag_tab(self) -> None:
        """Construct Knowledge Base RAG tab."""
        container = tk.Frame(self.tab_rag, bg=self.bg_color, padx=15, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        header_card = tk.Frame(container, bg=self.card_bg, padx=15, pady=10)
        header_card.pack(fill=tk.X, pady=(0, 15))

        lbl = tk.Label(header_card, text="📚 Local RAG Knowledge Base Documents (.pdf, .txt, .md, .docx)", font=("Segoe UI", 11, "bold"), fg=self.accent_color, bg=self.card_bg)
        lbl.pack(side=tk.LEFT)

        import_btn = tk.Button(header_card, text="📥 Import Document File", font=("Segoe UI", 10, "bold"), bg=self.accent_color, fg="#000000", relief=tk.FLAT, command=self._import_doc_file)
        import_btn.pack(side=tk.RIGHT)

        docs_card = tk.LabelFrame(container, text="Indexed Knowledge Documents", font=("Segoe UI", 11, "bold"), fg=self.accent_color, bg=self.card_bg, padx=15, pady=15)
        docs_card.pack(fill=tk.BOTH, expand=True)

        self.rag_docs_box = scrolledtext.ScrolledText(docs_card, wrap=tk.WORD, font=("Consolas", 10), bg=self.bg_color, fg=self.fg_color, relief=tk.FLAT)
        self.rag_docs_box.pack(fill=tk.BOTH, expand=True)
        self._refresh_rag_docs_list()

    def _setup_workflows_tab(self) -> None:
        """Construct Macro Workflows & Scenes tab."""
        container = tk.Frame(self.tab_workflows, bg=self.bg_color, padx=15, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        wf_card = tk.LabelFrame(container, text="Active Macro Workflows & Smart Home Scenes", font=("Segoe UI", 11, "bold"), fg=self.accent_color, bg=self.card_bg, padx=15, pady=15)
        wf_card.pack(fill=tk.BOTH, expand=True)

        workflows = [
            ("⚡ Start Work Mode", "start work mode", "Launches VS Code, Chrome, GitHub, and Pomodoro Focus Mode"),
            ("🌙 Good Night Scene", "good night", "Turns off all relays, locks door servo, and arms security sensors")
        ]

        for title, cmd, desc in workflows:
            card = tk.Frame(wf_card, bg="#383A59", padx=15, pady=12)
            card.pack(fill=tk.X, pady=8)

            t_lbl = tk.Label(card, text=title, font=("Segoe UI", 12, "bold"), fg=self.highlight_color, bg="#383A59")
            t_lbl.pack(anchor="w")

            d_lbl = tk.Label(card, text=desc, font=("Segoe UI", 9), fg=self.fg_color, bg="#383A59")
            d_lbl.pack(anchor="w", pady=(2, 5))

            run_btn = tk.Button(card, text="Execute Routine", font=("Segoe UI", 9, "bold"), bg=self.accent_color, fg="#000000", relief=tk.FLAT, padx=15, command=lambda c=cmd: self._handle_quick_cmd(c))
            run_btn.pack(anchor="e")

    def _setup_plugins_tab(self) -> None:
        """Construct Plugins tab."""
        container = tk.Frame(self.tab_plugins, bg=self.bg_color, padx=15, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        plugin_card = tk.LabelFrame(container, text="Installed Extensible Plugins", font=("Segoe UI", 11, "bold"), fg=self.accent_color, bg=self.card_bg, padx=15, pady=15)
        plugin_card.pack(fill=tk.BOTH, expand=True)

        self.plugins_box = scrolledtext.ScrolledText(plugin_card, wrap=tk.WORD, font=("Consolas", 10), bg=self.bg_color, fg=self.fg_color, relief=tk.FLAT)
        self.plugins_box.pack(fill=tk.BOTH, expand=True)

        plugins = plugin_manager.list_plugins()
        text = "\n".join([f"🔌 Plugin: {p['name']} (ID: {p['plugin_id']}, Status: {p['status']})" for p in plugins]) if plugins else "No plugins loaded."
        self.plugins_box.insert(tk.END, text)

    def _import_doc_file(self) -> None:
        file_path = filedialog.askopenfilename(filetypes=[("Documents", "*.pdf *.txt *.md *.docx")])
        if file_path:
            msg = rag_knowledge_base.import_document(file_path)
            messagebox.showinfo("RAG Ingestion", msg)
            self._refresh_rag_docs_list()

    def _refresh_rag_docs_list(self) -> None:
        self.rag_docs_box.config(state=tk.NORMAL)
        self.rag_docs_box.delete(1.0, tk.END)
        docs = db.get_all_knowledge_documents()
        if docs:
            lines = [f"📄 {d['filename']} ({d['doc_type'].upper()}, {d['total_chunks']} chunks, Imported: {d['imported_at']})" for d in docs]
            self.rag_docs_box.insert(tk.END, "\n".join(lines))
        else:
            self.rag_docs_box.insert(tk.END, "No knowledge documents imported yet. Click 'Import Document File' above.")
        self.rag_docs_box.config(state=tk.DISABLED)

    def _subscribe_events(self) -> None:
        event_bus.subscribe("wake_word_detected", self._on_wake_word)
        event_bus.subscribe("arduino_telemetry", self._on_telemetry)

    def _on_wake_word(self, text: str = "") -> None:
        self.root.after(0, lambda: self.status_label.config(text="● Active / Listening...", fg="#FF5555"))
        self.root.after(4000, lambda: self.status_label.config(text="● Listening for 'X' / 'Hey X'", fg=self.highlight_color))

    def _on_telemetry(self, data: dict = None) -> None:
        if not data:
            return
        def _update():
            if "temp" in data:
                self.temp_lbl.config(text=f"🌡️ Temp: {data['temp']} °C")
            if "humidity" in data:
                self.humidity_lbl.config(text=f"💧 Humidity: {data['humidity']} %")
            if "motion" in data:
                m_txt = "DETECTED!" if data['motion'] else "Clear"
                self.motion_lbl.config(text=f"🏃 Motion: {m_txt}")
        self.root.after(0, _update)

    def append_transcript(self, sender: str, message: str) -> None:
        def _update():
            self.transcript_box.config(state=tk.NORMAL)
            prefix = "👤 User: " if sender.lower() == "user" else "🤖 X Assistant: "
            self.transcript_box.insert(tk.END, f"{prefix}{message}\n\n")
            self.transcript_box.see(tk.END)
            self.transcript_box.config(state=tk.DISABLED)

        self.root.after(0, _update)

    def _on_send(self) -> None:
        text = self.input_entry.get().strip()
        if not text:
            return

        self.input_entry.delete(0, tk.END)
        self.append_transcript("User", text)

        if self.on_user_submit_callback:
            threading.Thread(target=self.on_user_submit_callback, args=(text,), daemon=True).start()

    def _handle_quick_cmd(self, cmd: str) -> None:
        if cmd == "__clear__":
            self.transcript_box.config(state=tk.NORMAL)
            self.transcript_box.delete(1.0, tk.END)
            self.transcript_box.config(state=tk.DISABLED)
            return

        if cmd == "__clipboard__":
            history = db.get_clipboard_history(limit=10)
            text = "\n\n".join([f"{i+1}. {item['content']}" for i, item in enumerate(history)]) if history else "Clipboard history empty."
            messagebox.showinfo("Clipboard History", text)
            return

        if cmd == "__audit__":
            summary = security_auditor.get_audit_trail_summary(limit=10)
            messagebox.showinfo("Security Audit Logs", summary)
            return

        self.append_transcript("User", cmd)
        if self.on_user_submit_callback:
            threading.Thread(target=self.on_user_submit_callback, args=(cmd,), daemon=True).start()

    def _start_metrics_timer(self) -> None:
        def _update_metrics():
            info = productivity_actions.get_system_info("all")
            pomo_status = pomodoro_timer.get_status()
            self.metrics_label.config(text=f"{info.replace('. ', '\n')}\n\n{pomo_status}")

            if camera_engine.is_camera_active:
                self.privacy_lbl.config(text="🔴 Privacy Status: Camera ACTIVE", fg="#FF5555")
            else:
                self.privacy_lbl.config(text="🔒 Privacy Status: Camera & Mic OFF (Standby)", fg=self.highlight_color)

            self.root.after(5000, _update_metrics)

        self.root.after(1000, _update_metrics)

    def start(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    app = AssistantDashboard()
    app.start()
