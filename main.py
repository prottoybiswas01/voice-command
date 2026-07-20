"""
Main Application Entry Point for X Assistant (Phase 5 Upgrade).
Orchestrates Autonomous AI Agent, Multimodal Vision AI, Camera Engine, OCR Engine,
Arduino Serial Bridge, IoT Device Manager, Automation Rules Engine, Win32 Window Manager,
Playwright Browser Agent, Ollama LLM, TTS, and GUI Dashboard.
"""

import sys
import time
import threading
from typing import Optional, List

from config.settings import settings
from core.logger import logger
from core.database import db
from core.event_bus import event_bus

from speech.stt import stt_engine
from speech.tts import tts_engine
from speech.wake_word import wake_word_detector

from brain.memory import memory_manager
from brain.reasoning import reasoning_agent
from brain.agent import autonomous_agent
from brain.pomodoro import pomodoro_timer
from brain.llm_client import ollama_client
from brain.multimodal import multimodal_synthesizer
from brain.intent_parser import intent_parser

from actions.system_actions import system_actions
from actions.media_actions import media_actions
from actions.web_actions import web_actions
from actions.productivity_actions import productivity_actions
from actions.smart_music import smart_music_dispatcher
from actions.browser_automation import browser_controller
from actions.browser_agent import browser_agent
from actions.internet_actions import internet_actions
from actions.system_control import system_control
from actions.window_manager import window_manager
from actions.file_organizer import file_organizer
from actions.recorder import recorder
from actions.network_settings import network_settings_manager
from actions.productivity_hub import productivity_hub
from actions.security_auditor import security_auditor

from iot.arduino_bridge import arduino_bridge
from iot.device_manager import device_manager
from iot.smart_home import smart_home_controller
from iot.automation_rules import automation_rule_engine

from vision.camera_engine import camera_engine
from vision.detector import vision_detector
from vision.ocr_engine import ocr_engine
from vision.vision_actions import vision_actions_handler

from ui.dashboard import AssistantDashboard


class XAssistantController:
    """Central Phase-5 Multimodal Autonomous Orchestrator combining Vision AI & Computer Control."""

    def __init__(self) -> None:
        logger.info(f"Initializing {settings.assistant.name} (v{settings.assistant.version}) Core...")
        self.dashboard: Optional[AssistantDashboard] = None
        self.is_running = True
        self.pending_confirmation: Optional[dict] = None

        # Start Rule-Based Automation Engine daemon
        automation_rule_engine.start_engine()

    def process_command(self, user_text: str) -> str:
        """
        Main Phase-5 Multimodal Pipeline:
        Input text -> Memory -> Security Confirmations -> Multi-step Reasoning -> Intent / Vision / Hardware -> LLM / Speech.
        """
        if not user_text or not user_text.strip():
            return ""

        logger.info(f"Processing command: '{user_text}'")

        # 0. Implicit Memory Extraction
        mem_msg = memory_manager.extract_implicit_memory(user_text)
        if mem_msg:
            tts_engine.speak(mem_msg)
            if self.dashboard:
                self.dashboard.append_transcript("Assistant", mem_msg)

        # 1. Pending Security Confirmation Gate
        if self.pending_confirmation:
            conf_data = self.pending_confirmation
            self.pending_confirmation = None
            if any(w in user_text.lower() for w in ["confirm", "yes", "হ্যাঁ", "proceed"]):
                action_type = conf_data.get("action_type", "")
                target = conf_data.get("target", "")

                if action_type in ["shutdown", "restart"]:
                    response = system_actions.execute_confirmed_power_action(action_type)
                elif action_type == "delete_file":
                    response = file_organizer.delete_item(target, confirmed=True)
                else:
                    response = f"Confirmed action '{action_type}' executed."

                security_auditor.log_audit_trail(action_type, target, user_confirmed=True, status="SUCCESS")
                tts_engine.speak(response)
                return response
            else:
                response = "Action canceled for security."
                security_auditor.log_audit_trail(conf_data.get("action_type", "UNKNOWN"), conf_data.get("target", ""), user_confirmed=False, status="CANCELED")
                tts_engine.speak(response)
                return response

        # 2. Autonomous Agent Multi-Step Loop
        if reasoning_agent.is_multi_step_request(user_text):
            plan = autonomous_agent.create_plan(user_text)
            if self.dashboard:
                self.dashboard.append_transcript("Assistant", autonomous_agent.explain_current_status())

            response = autonomous_agent.execute_plan(self._execute_single_intent)
            tts_engine.speak(response)
            if self.dashboard:
                self.dashboard.append_transcript("Assistant", response)
            return response

        # Single Intent Execution
        return self._execute_single_intent(user_text)

    def _execute_single_intent(self, prompt_text: str) -> str:
        """Execute single intent prompt across all action engines."""
        intent = intent_parser.parse(prompt_text)
        logger.info(f"Parsed Intent: {intent.name} (Category: {intent.action_type})")

        response = ""

        # A. Phase-5 Vision AI Commands
        if intent.action_type == "vision":
            response = vision_actions_handler.handle_vision_command(intent.name, intent.params)

        # B. Phase-4 Smart Home & IoT Hardware Controls
        elif intent.action_type == "smart_home":
            response = smart_home_controller.handle_voice_command(intent.name, intent.params)

        # C. Phase-3 Win32 Application Window Controls
        elif intent.action_type == "window":
            app = intent.params.get("app", "")
            if intent.name == "minimize_window":
                response = window_manager.minimize_window(app)
            elif intent.name == "maximize_window":
                response = window_manager.maximize_window(app)
            elif intent.name == "switch_window":
                response = window_manager.bring_to_front(app)
            elif intent.name == "close_window":
                response = window_manager.close_window(app)

        # D. Phase-3 File System & Archive Operations
        elif intent.action_type == "file_system":
            path = intent.params.get("path", "")
            if intent.name == "create_dir":
                response = file_organizer.create_directory(path)
            elif intent.name == "compress_zip":
                response = file_organizer.compress_to_zip(path)
            elif intent.name == "extract_zip":
                response = file_organizer.extract_zip(path)
            elif intent.name == "delete_item_confirm":
                self.pending_confirmation = {"action_type": "delete_file", "target": path}
                response = security_auditor.request_confirmation_prompt("delete_file", path)

        # E. Phase-3 Screen & Audio Recording
        elif intent.action_type == "recording":
            if intent.name == "record_audio":
                response = recorder.record_audio_note(duration_seconds=10)
            elif intent.name == "record_screen":
                response = recorder.record_screen_snapshot_series(duration_seconds=5)

        # F. Phase-3 Network & Windows Settings
        elif intent.action_type == "network_settings":
            if intent.name == "wifi_control":
                act = intent.params.get("action", "status")
                response = network_settings_manager.manage_wifi(act)
            elif intent.name == "open_setting":
                cat = intent.params.get("category", "system")
                response = network_settings_manager.open_windows_setting(cat)
            elif intent.name == "get_startup_apps":
                response = network_settings_manager.get_startup_apps()

        # G. Phase-3 Pomodoro & Productivity Hub
        elif intent.action_type == "productivity_hub":
            if intent.name == "pomodoro_control":
                act = intent.params.get("action", "start")
                response = productivity_hub.control_pomodoro(act)
            elif intent.name == "clipboard_history":
                response = productivity_hub.get_clipboard_history()
            elif intent.name == "show_calendar":
                response = productivity_hub.list_calendar_events()

        # H. Phase-3 Security Audit Logs
        elif intent.action_type == "security":
            response = security_auditor.get_audit_trail_summary()

        # I. Phase-2 Smart Music Playback
        elif intent.action_type == "smart_music":
            query = intent.params.get("query", "")
            response = smart_music_dispatcher.play_music(query)

        # J. Phase-2 Playwright Browser Automation
        elif intent.action_type == "browser_auto":
            if intent.name == "open_browser_site":
                site = intent.params.get("site", "github")
                response = browser_controller.open_site(site)
            elif intent.name == "browser_scroll":
                direction = intent.params.get("direction", "down")
                response = browser_controller.scroll_page(direction)

        # K. Phase-2 Live Internet Data
        elif intent.action_type == "internet":
            if intent.name == "get_live_weather":
                loc = intent.params.get("location", "Dhaka")
                response = internet_actions.get_live_weather(loc)
            elif intent.name == "get_live_news":
                response = internet_actions.get_live_news()
            elif intent.name == "search_wikipedia":
                query = intent.params.get("query", "")
                response = internet_actions.search_wikipedia(query)

        # L. System Controls
        elif intent.action_type == "system_control":
            if intent.name == "take_screenshot":
                response = system_control.take_screenshot()
            elif intent.name == "set_brightness":
                level = intent.params.get("level")
                change = intent.params.get("change")
                response = system_control.set_brightness(level=level, change=change)
            elif intent.name == "restart_explorer":
                response = system_control.restart_explorer()
            elif intent.name == "search_files":
                query = intent.params.get("query", "")
                response = system_control.search_local_files(query)

        # M. System Actions & App Launchers
        elif intent.action_type == "system":
            if intent.name == "greeting":
                response = system_actions.handle_greeting()
            elif intent.name == "get_time":
                response = system_actions.get_current_time()
            elif intent.name == "get_date":
                response = system_actions.get_current_date()
            elif intent.name == "open_app":
                app_name = intent.params.get("app", "")
                response = system_actions.execute_app_launch(app_name)

        # N. Power Actions & Security Gate
        elif intent.action_type == "power":
            if intent.name == "exit":
                response = "Goodbye! Shutting down X Assistant Phase 5."
                tts_engine.speak(response, sync=True)
                self.stop()
                sys.exit(0)
            elif intent.name in ["shutdown_confirm", "restart_confirm", "sleep_confirm"]:
                action = intent.params.get("action", "")
                if action == "sleep":
                    response = system_actions.confirm_power_action(action)
                else:
                    self.pending_confirmation = {"action_type": action, "target": "System Computer"}
                    response = security_auditor.request_confirmation_prompt(action, "System Computer")

        # O. Media & Volume Controls
        elif intent.action_type == "media":
            if intent.name == "volume_control":
                cmd = intent.params.get("command", "")
                response = media_actions.control_volume(cmd)

        # P. Web Openers
        elif intent.action_type == "web":
            if intent.name == "open_web":
                site = intent.params.get("site", "youtube")
                response = web_actions.open_website(site)
            elif intent.name == "google_search":
                query = intent.params.get("query", "")
                response = web_actions.search_google(query)
            elif intent.name == "youtube_search":
                query = intent.params.get("query", "")
                response = web_actions.search_youtube(query)

        # Q. Productivity Actions
        elif intent.action_type == "productivity":
            if intent.name == "system_info":
                metric = intent.params.get("metric", "all")
                response = productivity_actions.get_system_info(metric)
            elif intent.name == "add_todo":
                task = intent.params.get("task", "")
                response = productivity_actions.add_todo_task(task)
            elif intent.name == "show_todo":
                response = productivity_actions.list_todo_tasks()
            elif intent.name == "add_note":
                content = intent.params.get("content", "")
                response = productivity_actions.save_simple_note(content)
            elif intent.name == "show_notes":
                response = productivity_actions.read_notes()
            elif intent.name == "add_reminder":
                msg = intent.params.get("message", "")
                response = productivity_actions.set_reminder(msg)

        # R. Multimodal LLM Conversation Synthesis
        elif intent.action_type == "llm":
            prompt = intent.params.get("prompt", prompt_text)
            response = multimodal_synthesizer.generate_multimodal_response(prompt)

        # Default Fallback
        if not response:
            response = multimodal_synthesizer.generate_multimodal_response(prompt_text)

        tts_engine.speak(response)
        db.log_conversation(prompt_text, response)

        if self.dashboard:
            self.dashboard.append_transcript("Assistant", response)

        return response

    def _voice_listener_loop(self) -> None:
        """Background thread listening for Wake Word and processing voice input."""
        logger.info("Voice Listener thread active. Continuous monitoring ready.")

        def on_wake_detected():
            tts_engine.speak("Yes? I am listening.")
            if self.dashboard:
                self.dashboard.append_transcript("Assistant", "Yes? I am listening.")

            voice_prompt = stt_engine.listen_and_recognize(timeout=5, phrase_time_limit=10)
            if voice_prompt:
                if self.dashboard:
                    self.dashboard.append_transcript("User", voice_prompt)
                self.process_command(voice_prompt)

        wake_word_detector.start_loop(on_wake_detected)

    def start(self) -> None:
        """Launch X Assistant Phase-5 controller and GUI Dashboard."""
        logger.info(f"Starting {settings.assistant.name} Phase-5 application...")
        tts_engine.speak(f"{settings.assistant.name} Phase 5 ready. Multimodal Vision AI online.")

        listener_thread = threading.Thread(target=self._voice_listener_loop, daemon=True)
        listener_thread.start()

        self.dashboard = AssistantDashboard(on_user_submit_callback=self.process_command)
        self.dashboard.append_transcript("Assistant", "X Assistant Phase 5 online. Multimodal Vision AI & Smart Recognition active!")
        self.dashboard.start()

    def stop(self) -> None:
        """Stop all background processes."""
        self.is_running = False
        camera_engine.stop_camera()
        automation_rule_engine.stop_engine()
        wake_word_detector.stop()
        tts_engine.stop()
        browser_controller.close()
        logger.info("X Assistant Phase 5 stopped gracefully.")


def main() -> None:
    """Application main entry point."""
    assistant = XAssistantController()
    try:
        assistant.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received.")
        assistant.stop()


if __name__ == "__main__":
    main()
