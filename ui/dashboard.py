"""
GUI Dashboard Module for X Assistant.
Provides a modern dark-themed Tkinter interface displaying assistant state, speech transcripts, and system metrics.
"""

import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional, Callable
from config.settings import settings
from core.logger import logger
from core.event_bus import event_bus
from actions.productivity_actions import productivity_actions


class AssistantDashboard:
    """Tkinter Desktop Dashboard Interface for X Assistant."""

    def __init__(self, on_user_submit_callback: Optional[Callable[[str], None]] = None) -> None:
        self.on_user_submit_callback = on_user_submit_callback
        self.root = tk.Tk()
        self.root.title(f"{settings.assistant.name} - Control Dashboard")
        self.root.geometry("850x600")
        self.root.minsize(700, 500)

        # Apply dark theme styling
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
        """Construct dashboard components."""
        # Top Header Bar
        header_frame = tk.Frame(self.root, bg=self.card_bg, pady=15, padx=20)
        header_frame.pack(fill=tk.X, side=tk.TOP)

        title_label = tk.Label(
            header_frame,
            text=f"🤖 {settings.assistant.name}",
            font=("Segoe UI", 18, "bold"),
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

        # Main Workspace Container
        main_container = tk.Frame(self.root, bg=self.bg_color, padx=15, pady=15)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left Column: Conversation & Logs
        left_frame = tk.Frame(main_container, bg=self.bg_color)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        log_title = tk.Label(
            left_frame,
            text="Live Transcript & History",
            font=("Segoe UI", 12, "bold"),
            fg=self.fg_color,
            bg=self.bg_color
        )
        log_title.pack(anchor="w", pady=(0, 5))

        self.transcript_box = scrolledtext.ScrolledText(
            left_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=self.card_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT
        )
        self.transcript_box.pack(fill=tk.BOTH, expand=True)
        self.transcript_box.config(state=tk.DISABLED)

        # Manual Text Command Input Bar
        input_frame = tk.Frame(left_frame, bg=self.bg_color, pady=10)
        input_frame.pack(fill=tk.X)

        self.input_entry = tk.Entry(
            input_frame,
            font=("Segoe UI", 11),
            bg=self.card_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_entry.bind("<Return>", lambda e: self._on_send())

        send_btn = tk.Button(
            input_frame,
            text="Send",
            font=("Segoe UI", 10, "bold"),
            bg=self.accent_color,
            fg="#000000",
            activebackground="#A480E0",
            relief=tk.FLAT,
            padx=15,
            command=self._on_send
        )
        send_btn.pack(side=tk.RIGHT)

        # Right Column: Quick Stats & Controls Sidebar
        right_frame = tk.Frame(main_container, bg=self.card_bg, width=220, padx=15, pady=15)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)

        sidebar_title = tk.Label(
            right_frame,
            text="System Diagnostics",
            font=("Segoe UI", 11, "bold"),
            fg=self.accent_color,
            bg=self.card_bg
        )
        sidebar_title.pack(anchor="w", pady=(0, 10))

        self.metrics_label = tk.Label(
            right_frame,
            text="CPU: --%\nRAM: --%\nBattery: --%\nNet: Online",
            font=("Segoe UI", 10),
            fg=self.fg_color,
            bg=self.card_bg,
            justify=tk.LEFT
        )
        self.metrics_label.pack(anchor="w", pady=(0, 20))

        btn_title = tk.Label(
            right_frame,
            text="Quick Commands",
            font=("Segoe UI", 11, "bold"),
            fg=self.accent_color,
            bg=self.card_bg
        )
        btn_title.pack(anchor="w", pady=(0, 10))

        quick_cmds = [
            ("🕒 Current Time", "what time is it"),
            ("📅 Current Date", "what is today's date"),
            ("💻 System Info", "show system info"),
            ("📝 Show Todos", "show todo list"),
            ("🧹 Clear Log", "__clear__")
        ]

        for label, cmd in quick_cmds:
            btn = tk.Button(
                right_frame,
                text=label,
                font=("Segoe UI", 9),
                bg="#383A59",
                fg=self.fg_color,
                activebackground=self.accent_color,
                relief=tk.FLAT,
                anchor="w",
                padx=10,
                pady=4,
                command=lambda c=cmd: self._handle_quick_cmd(c)
            )
            btn.pack(fill=tk.X, pady=3)

    def _subscribe_events(self) -> None:
        """Register listeners on event bus."""
        event_bus.subscribe("wake_word_detected", self._on_wake_word)

    def _on_wake_word(self, text: str = "") -> None:
        """Update status label when wake word is detected."""
        self.root.after(0, lambda: self.status_label.config(text="● Active / Listening...", fg="#FF5555"))
        self.root.after(4000, lambda: self.status_label.config(text="● Listening for 'X' / 'Hey X'", fg=self.highlight_color))

    def append_transcript(self, sender: str, message: str) -> None:
        """Append message to transcript scrollable text view."""
        def _update():
            self.transcript_box.config(state=tk.NORMAL)
            prefix = "👤 User: " if sender.lower() == "user" else "🤖 X Assistant: "
            self.transcript_box.insert(tk.END, f"{prefix}{message}\n\n")
            self.transcript_box.see(tk.END)
            self.transcript_box.config(state=tk.DISABLED)

        self.root.after(0, _update)

    def _on_send(self) -> None:
        """Handle manual text input submission."""
        text = self.input_entry.get().strip()
        if not text:
            return

        self.input_entry.delete(0, tk.END)
        self.append_transcript("User", text)

        if self.on_user_submit_callback:
            threading.Thread(target=self.on_user_submit_callback, args=(text,), daemon=True).start()

    def _handle_quick_cmd(self, cmd: str) -> None:
        """Handle sidebar quick action button click."""
        if cmd == "__clear__":
            self.transcript_box.config(state=tk.NORMAL)
            self.transcript_box.delete(1.0, tk.END)
            self.transcript_box.config(state=tk.DISABLED)
            return

        self.append_transcript("User", cmd)
        if self.on_user_submit_callback:
            threading.Thread(target=self.on_user_submit_callback, args=(cmd,), daemon=True).start()

    def _start_metrics_timer(self) -> None:
        """Periodically update system metrics on sidebar."""
        def _update_metrics():
            info = productivity_actions.get_system_info("all")
            self.metrics_label.config(text=info.replace(". ", "\n"))
            self.root.after(10000, _update_metrics)

        self.root.after(1000, _update_metrics)

    def start(self) -> None:
        """Start Tkinter main GUI loop."""
        self.root.mainloop()


if __name__ == "__main__":
    app = AssistantDashboard()
    app.start()
