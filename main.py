"""
Main Application Entry Point for X Assistant (Phase 2).
Orchestrates Wake Word Detection, STT, Multi-Step Reasoning, Smart Memory, Intent Parsing,
Browser Automation, Smart Music, Live Internet Actions, System Controls, Ollama LLM, TTS, and GUI Dashboard.
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
from brain.llm_client import ollama_client
from brain.intent_parser import intent_parser

from actions.system_actions import system_actions
from actions.media_actions import media_actions
from actions.web_actions import web_actions
from actions.productivity_actions import productivity_actions
from actions.smart_music import smart_music_dispatcher
from actions.browser_automation import browser_controller
from actions.internet_actions import internet_actions
from actions.system_control import system_control

from ui.dashboard import AssistantDashboard


class XAssistantController:
    """Central Phase-2 Orchestrator combining all assistant AI brain & automation subsystems."""

    def __init__(self) -> None:
        logger.info(f"Initializing {settings.assistant.name} (v{settings.assistant.version}) Core...")
        self.dashboard: Optional[AssistantDashboard] = None
        self.is_running = True
        self.pending_confirmation: Optional[str] = None

    def process_command(self, user_text: str) -> str:
        """
        Main Phase-2 pipeline executing:
        input text -> memory extraction -> multi-step reasoning -> intent -> action / Ollama LLM -> response.
        
        Args:
            user_text: Raw input text spoken or typed by user.
            
        Returns:
            Assistant speech output response.
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

        # 1. Pending Security Confirmations (Shutdown / Restart / Delete)
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

        # 2. Multi-Step Prompt Reasoning Decomposition
        if reasoning_agent.is_multi_step_request(user_text):
            sub_tasks = reasoning_agent.decompose_prompt(user_text)
            responses: List[str] = []
            for task in sub_tasks:
                res = self._execute_single_intent(task)
                if res:
                    responses.append(res)
            
            combined_response = " ".join(responses)
            if self.dashboard:
                self.dashboard.append_transcript("Assistant", combined_response)
            return combined_response

        # Single Intent Execution
        return self._execute_single_intent(user_text)

    def _execute_single_intent(self, prompt_text: str) -> str:
        """Execute single intent prompt."""
        intent = intent_parser.parse(prompt_text)
        logger.info(f"Parsed Intent: {intent.name} (Category: {intent.action_type})")

        response = ""

        # A. Phase-2 Smart Music Playback (Priority: 1. Spotify -> 2. YouTube -> 3. Local)
        if intent.action_type == "smart_music":
            query = intent.params.get("query", "")
            response = smart_music_dispatcher.play_music(query)

        # B. Phase-2 Playwright Browser Automation & Social Sites
        elif intent.action_type == "browser_auto":
            if intent.name == "open_browser_site":
                site = intent.params.get("site", "github")
                response = browser_controller.open_site(site)
            elif intent.name == "browser_scroll":
                direction = intent.params.get("direction", "down")
                response = browser_controller.scroll_page(direction)
            elif intent.name == "browser_read_title":
                response = browser_controller.read_page_title()
            elif intent.name == "browser_read_notifications":
                response = browser_controller.read_notifications()

        # C. Phase-2 Live Internet Data (Weather, News, Wikipedia)
        elif intent.action_type == "internet":
            if intent.name == "get_live_weather":
                loc = intent.params.get("location", "Dhaka")
                response = internet_actions.get_live_weather(loc)
            elif intent.name == "get_live_news":
                response = internet_actions.get_live_news()
            elif intent.name == "search_wikipedia":
                query = intent.params.get("query", "")
                response = internet_actions.search_wikipedia(query)

        # D. Phase-2 System Controls (Screenshots, Brightness, File Search, Explorer Restart)
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

        # E. Phase-2 Explicit Memory Management
        elif intent.action_type == "memory":
            text = intent.params.get("text", prompt_text)
            response = memory_manager.remember_fact("user_note", text)

        # F. System Actions & App Launchers
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

        # G. Power Actions & Safety Confirmations
        elif intent.action_type == "power":
            if intent.name == "exit":
                response = "Goodbye! Shutting down X Assistant Phase 2."
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

        # H. Media & Volume Controls
        elif intent.action_type == "media":
            if intent.name == "volume_control":
                cmd = intent.params.get("command", "")
                response = media_actions.control_volume(cmd)

        # I. Web Actions
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

        # J. Productivity Actions
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

        # K. Fallback LLM Conversation with Memory Context Injection
        elif intent.action_type == "llm":
            prompt = intent.params.get("prompt", prompt_text)
            response = ollama_client.generate_response(prompt)

        # Default Fallback
        if not response:
            response = ollama_client.generate_response(prompt_text)

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
        """Launch X Assistant Phase-2 controller and GUI Dashboard."""
        logger.info(f"Starting {settings.assistant.name} Phase-2 application...")
        tts_engine.speak(f"{settings.assistant.name} Phase 2 ready.")

        listener_thread = threading.Thread(target=self._voice_listener_loop, daemon=True)
        listener_thread.start()

        self.dashboard = AssistantDashboard(on_user_submit_callback=self.process_command)
        self.dashboard.append_transcript("Assistant", "X Assistant Phase 2 online. AI Brain & Smart Automation active!")
        self.dashboard.start()

    def stop(self) -> None:
        """Stop all background processes."""
        self.is_running = False
        wake_word_detector.stop()
        tts_engine.stop()
        browser_controller.close()
        logger.info("X Assistant Phase 2 stopped gracefully.")


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
