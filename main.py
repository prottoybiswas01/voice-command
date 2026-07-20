"""
Main Application Entry Point for X Assistant (Phase-1).
Orchestrates Wake Word Detection, STT, Intent Parsing, Action Execution, LLM Generation, TTS, and GUI Dashboard.
"""

import sys
import time
import threading
from typing import Optional

from config.settings import settings
from core.logger import logger
from core.database import db
from core.event_bus import event_bus

from speech.stt import stt_engine
from speech.tts import tts_engine
from speech.wake_word import wake_word_detector

from brain.llm_client import ollama_client
from brain.intent_parser import intent_parser

from actions.system_actions import system_actions
from actions.media_actions import media_actions
from actions.web_actions import web_actions
from actions.productivity_actions import productivity_actions

from ui.dashboard import AssistantDashboard


class XAssistantController:
    """Central Orchestrator combining all assistant subsystems."""

    def __init__(self) -> None:
        logger.info("Initializing X Assistant Phase-1 Core...")
        self.dashboard: Optional[AssistantDashboard] = None
        self.is_running = True
        self.pending_confirmation: Optional[str] = None

    def process_command(self, user_text: str) -> str:
        """
        Main pipeline executing input text -> intent -> action / LLM -> response.
        
        Args:
            user_text: Raw input text spoken or typed by user.
            
        Returns:
            Assistant speech output response.
        """
        if not user_text or not user_text.strip():
            return ""

        logger.info(f"Processing command: '{user_text}'")

        # Handle pending confirmation (for shutdown/restart)
        if self.pending_confirmation:
            action = self.pending_confirmation
            self.pending_confirmation = None
            if any(w in user_text.lower() for w in ["confirm", "yes", "হ্যাঁ", "proceed"]):
                response = system_actions.execute_confirmed_power_action(action)
                tts_engine.speak(response)
                return response
            else:
                response = "Action canceled."
                tts_engine.speak(response)
                return response

        # Parse user intent
        intent = intent_parser.parse(user_text)
        logger.info(f"Parsed Intent: {intent.name} (Category: {intent.action_type})")

        response = ""

        # 1. System Actions
        if intent.action_type == "system":
            if intent.name == "greeting":
                response = system_actions.handle_greeting()
            elif intent.name == "get_time":
                response = system_actions.get_current_time()
            elif intent.name == "get_date":
                response = system_actions.get_current_date()
            elif intent.name == "open_app":
                app_name = intent.params.get("app", "")
                response = system_actions.execute_app_launch(app_name)

        # 2. Power & Exit Actions
        elif intent.action_type == "power":
            if intent.name == "exit":
                response = "Goodbye! Shutting down X Assistant."
                tts_engine.speak(response, sync=True)
                self.stop()
                sys.exit(0)
            elif intent.name in ["shutdown_confirm", "restart_confirm", "sleep_confirm"]:
                action = intent.params.get("action", "")
                if action == "sleep":
                    response = system_actions.confirm_power_action(action)
                else:
                    self.pending_confirmation = action
                    response = system_actions.confirm_power_action(action)

        # 3. Media Actions
        elif intent.action_type == "media":
            if intent.name == "volume_control":
                cmd = intent.params.get("command", "")
                response = media_actions.control_volume(cmd)
            elif intent.name == "media_control":
                cmd = intent.params.get("command", "")
                response = media_actions.control_media(cmd)

        # 4. Web Actions
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
            elif intent.name == "weather":
                response = web_actions.get_weather()
            elif intent.name == "news":
                response = web_actions.get_news()

        # 5. Productivity & Info Actions
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
            elif intent.name == "show_history":
                history = db.get_recent_conversations(limit=3)
                if history:
                    response = f"Your last query was: {history[0]['user_input']}"
                else:
                    response = "No history recorded yet."

        # 6. Fallback LLM Chat Conversation
        elif intent.action_type == "llm":
            prompt = intent.params.get("prompt", user_text)
            response = ollama_client.generate_response(prompt)

        # Default fallback if empty
        if not response:
            response = ollama_client.generate_response(user_text)

        # Speak output and log conversation
        tts_engine.speak(response)
        db.log_conversation(user_text, response)

        # Update GUI Dashboard if open
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

            # Capture command immediately following wake word
            voice_prompt = stt_engine.listen_and_recognize(timeout=5, phrase_time_limit=10)
            if voice_prompt:
                if self.dashboard:
                    self.dashboard.append_transcript("User", voice_prompt)
                self.process_command(voice_prompt)

        wake_word_detector.start_loop(on_wake_detected)

    def start(self) -> None:
        """Launch X Assistant controller and GUI Dashboard."""
        logger.info("Starting X Assistant Phase-1 application...")
        tts_engine.speak("X Assistant ready.")

        # Start continuous voice listener loop in background thread
        listener_thread = threading.Thread(target=self._voice_listener_loop, daemon=True)
        listener_thread.start()

        # Start GUI Dashboard on main thread
        self.dashboard = AssistantDashboard(on_user_submit_callback=self.process_command)
        self.dashboard.append_transcript("Assistant", "X Assistant is online. Say 'X' or 'Hey X' to activate!")
        self.dashboard.start()

    def stop(self) -> None:
        """Stop all background processes."""
        self.is_running = False
        wake_word_detector.stop()
        tts_engine.stop()
        logger.info("X Assistant stopped gracefully.")


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
