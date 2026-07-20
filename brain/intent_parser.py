"""
Intent Parser for X Assistant (Phase 6 Upgrade).
Classifies user prompts into actionable intents covering System, Window Management,
File/ZIP operations, Screen/Audio Recording, Network/Settings, Playwright Browser Agent,
Pomodoro & Productivity Hub, Security Audit, Smart Music, Smart Home IoT, Vision AI,
Local RAG Knowledge Base, Macro Workflows, AI Personalities, System Diagnostics, Plugins, and LLM Chat.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from core.logger import logger


@dataclass
class Intent:
    """Structure representing classified user intent."""
    name: str
    action_type: str  # 'system', 'media', 'web', 'productivity', 'power', 'smart_music', 'browser_auto', 'internet', 'system_control', 'memory', 'window', 'file_system', 'recording', 'network_settings', 'productivity_hub', 'security', 'smart_home', 'vision', 'rag', 'workflow', 'personality', 'diagnostics', 'plugin', 'llm'
    params: Dict[str, Any] = field(default_factory=dict)
    raw_prompt: str = ""


class IntentParser:
    """Classifies incoming text commands into Phase-6 actionable intents."""

    def parse(self, text: str) -> Intent:
        """Classify input prompt string to Intent object."""
        if not text or not text.strip():
            return Intent(name="unknown", action_type="none", raw_prompt=text)

        clean = text.lower().strip()

        # Clean leading wake words
        for wake in ["x listen", "hey x", "x", "হে এক্স", "এক্স শোনো", "এক্স"]:
            if clean.startswith(wake):
                clean = clean[len(wake):].strip()
                break

        if not clean:
            return Intent(name="greeting", action_type="system", params={"type": "greeting"}, raw_prompt=text)

        # 1. Exit / Quit
        if any(w in clean for w in ["exit assistant", "exit", "quit", "close assistant", "stop assistant", "বন্ধ করো", "বিদায়"]):
            return Intent(name="exit", action_type="power", params={"action": "exit"}, raw_prompt=text)

        # 2. Power Confirmations (Shutdown, Restart, Sleep)
        if any(w in clean for w in ["shutdown", "turn off computer", "পিসি বন্ধ", "কম্পিউটার বন্ধ"]):
            return Intent(name="shutdown_confirm", action_type="power", params={"action": "shutdown"}, raw_prompt=text)
        if any(w in clean for w in ["restart computer", "reboot computer", "পিসি রিস্টার্ট"]):
            return Intent(name="restart_confirm", action_type="power", params={"action": "restart"}, raw_prompt=text)
        if any(w in clean for w in ["sleep computer", "put to sleep", "পিসি স্লিপ"]):
            return Intent(name="sleep_confirm", action_type="power", params={"action": "sleep"}, raw_prompt=text)

        # 3. Phase-6 Macro Workflows & Scenes ("start work mode", "good night")
        if any(w in clean for w in ["start work mode", "work mode", "ওয়ার্ক মোড"]):
            return Intent(name="run_workflow", action_type="workflow", params={"keyword": "start work mode"}, raw_prompt=text)

        if any(w in clean for w in ["good night", "night mode", "নাইট মোড", "শুভ রাত্রি"]):
            return Intent(name="run_workflow", action_type="workflow", params={"keyword": "good night"}, raw_prompt=text)

        # 4. Phase-6 RAG Knowledge Base Queries
        if "knowledge base" in clean or "read document" in clean or "import document" in clean or "জ্ঞান ভাণ্ডার" in clean:
            query = re.sub(r".*(knowledge base|read document|import document|জ্ঞান ভাণ্ডার)", "", clean).strip()
            return Intent(name="query_rag", action_type="rag", params={"query": query}, raw_prompt=text)

        # 5. Phase-6 System Health Diagnostics
        if any(w in clean for w in ["system health", "diagnostics scan", "health check", "হেলথ চেক"]):
            return Intent(name="system_diagnostics", action_type="diagnostics", params={}, raw_prompt=text)

        # 6. Phase-6 AI Personalities & Ollama Model Switching
        if "personality" in clean or "পার্সোনালিটি" in clean:
            p_name = re.sub(r".*(personality to|personality|পার্সোনালিটি)", "", clean).strip() or "standard"
            return Intent(name="switch_personality", action_type="personality", params={"personality": p_name}, raw_prompt=text)

        if "switch model" in clean or "change model" in clean:
            m_name = re.sub(r".*(switch model to|change model to|switch model|change model)", "", clean).strip() or "gemma2:2b"
            return Intent(name="switch_model", action_type="personality", params={"model": m_name}, raw_prompt=text)

        # 7. Phase-5 Vision AI Commands
        if any(w in clean for w in ["what do you see", "what is in front of camera", "কী দেখছ", "সামনে কী আছে", "ক্যামেরায় কি আছে"]):
            return Intent(name="describe_scene", action_type="vision", params={}, raw_prompt=text)

        if any(w in clean for w in ["read text on screen", "read screen", "screen text", "স্ক্রিন পড়ো", "স্ক্রিনের লেখা"]):
            return Intent(name="read_screen_text", action_type="vision", params={}, raw_prompt=text)

        if any(w in clean for w in ["count people", "how many people", "count how many", "কতজন মানুষ"]):
            return Intent(name="count_people", action_type="vision", params={}, raw_prompt=text)

        if any(w in clean for w in ["recognize object", "identify object", "অবজেক্ট চেনো"]):
            return Intent(name="recognize_object", action_type="vision", params={}, raw_prompt=text)

        if any(w in clean for w in ["is someone standing at the door", "someone at the door", "door camera", "দরজায় কি কেউ আছে"]):
            return Intent(name="check_door_vision", action_type="vision", params={}, raw_prompt=text)

        if any(w in clean for w in ["take a picture", "take photo", "take picture", "ছবি তোলো"]):
            return Intent(name="take_picture", action_type="vision", params={}, raw_prompt=text)

        if any(w in clean for w in ["start recording video", "start video recording", "start camera recording"]):
            return Intent(name="start_camera_recording", action_type="vision", params={"duration": 5}, raw_prompt=text)

        if any(w in clean for w in ["stop recording video", "stop video recording", "stop camera recording"]):
            return Intent(name="stop_camera_recording", action_type="vision", params={}, raw_prompt=text)

        # 8. Phase-4 Smart Home IoT Commands
        if "light" in clean or "আলো" in clean or "লাইটিং" in clean:
            state = "off" if any(w in clean for w in ["off", "disable", "বন্ধ"]) else "on"
            return Intent(name="control_light", action_type="smart_home", params={"state": state}, raw_prompt=text)

        if "fan" in clean or "ফ্যান" in clean:
            state = "off" if any(w in clean for w in ["off", "disable", "বন্ধ"]) else "on"
            return Intent(name="control_fan", action_type="smart_home", params={"state": state}, raw_prompt=text)

        if "room temperature" in clean or "read temperature" in clean or "ঘরের তাপমাত্রা" in clean or "তাপমাত্রা" in clean:
            return Intent(name="read_temperature", action_type="smart_home", params={}, raw_prompt=text)

        if "humidity" in clean or "আর্দ্রতা" in clean:
            return Intent(name="read_humidity", action_type="smart_home", params={}, raw_prompt=text)

        if any(w in clean for w in ["detect motion", "check motion"]):
            return Intent(name="check_motion", action_type="smart_home", params={}, raw_prompt=text)

        if "all relays on" in clean or "turn on all relays" in clean or "সব রিলে অন" in clean:
            return Intent(name="all_relays_on", action_type="smart_home", params={}, raw_prompt=text)

        if "all relays off" in clean or "turn off all relays" in clean or "সব রিলে অফ" in clean:
            return Intent(name="all_relays_off", action_type="smart_home", params={}, raw_prompt=text)

        if "blink led" in clean or "এলইডি ব্লিঙ্ক" in clean:
            count = 5
            nums = re.findall(r"\d+", clean)
            if nums:
                count = int(nums[0])
            return Intent(name="blink_led", action_type="smart_home", params={"count": count}, raw_prompt=text)

        if "servo" in clean or "সার্ভো" in clean:
            angle = 90
            nums = re.findall(r"\d+", clean)
            if nums:
                angle = int(nums[0])
            return Intent(name="rotate_servo", action_type="smart_home", params={"angle": angle}, raw_prompt=text)

        # 9. Phase-3 Win32 Application Window Controls
        if "minimize" in clean or "মিনিমাইজ" in clean:
            app = re.sub(r".*(minimize|মিনিমাইজ)", "", clean).strip()
            return Intent(name="minimize_window", action_type="window", params={"app": app}, raw_prompt=text)
        if "maximize" in clean or "ম্যাক্সিমাইজ" in clean:
            app = re.sub(r".*(maximize|ম্যাক্সিমাইজ)", "", clean).strip()
            return Intent(name="maximize_window", action_type="window", params={"app": app}, raw_prompt=text)
        if "switch to" in clean or "switch window" in clean or "ফোকাস" in clean:
            app = re.sub(r".*(switch to|switch window|ফোকাস)", "", clean).strip()
            return Intent(name="switch_window", action_type="window", params={"app": app}, raw_prompt=text)
        if "close window" in clean or "বন্ধ করো উইন্ডো" in clean:
            app = re.sub(r".*(close window|বন্ধ করো উইন্ডো)", "", clean).strip()
            return Intent(name="close_window", action_type="window", params={"app": app}, raw_prompt=text)

        # 10. Phase-3 File System & Archive Operations
        if "create folder" in clean or "create directory" in clean or "ফোল্ডার বানাও" in clean:
            path = re.sub(r".*(create folder|create directory|ফোল্ডার বানাও)", "", clean).strip()
            return Intent(name="create_dir", action_type="file_system", params={"path": path}, raw_prompt=text)
        if "rename" in clean or "রিনেম" in clean:
            return Intent(name="rename_item", action_type="file_system", params={"text": text}, raw_prompt=text)
        if "compress zip" in clean or "zip folder" in clean or "জিফ করো" in clean:
            path = re.sub(r".*(compress zip|zip folder|জিফ করো)", "", clean).strip()
            return Intent(name="compress_zip", action_type="file_system", params={"path": path}, raw_prompt=text)
        if "extract zip" in clean or "unzip" in clean or "আনজিফ" in clean:
            path = re.sub(r".*(extract zip|unzip|আনজিফ)", "", clean).strip()
            return Intent(name="extract_zip", action_type="file_system", params={"path": path}, raw_prompt=text)
        if "delete file" in clean or "delete folder" in clean or "ফাইল মুছে ফেলো" in clean:
            path = re.sub(r".*(delete file|delete folder|ফাইল মুছে ফেলো)", "", clean).strip()
            return Intent(name="delete_item_confirm", action_type="file_system", params={"path": path}, raw_prompt=text)

        # 11. Screen & Audio Recording
        if any(w in clean for w in ["record audio", "record voice note", "ভয়েস রেকর্ড"]):
            return Intent(name="record_audio", action_type="recording", params={"duration": 10}, raw_prompt=text)
        if any(w in clean for w in ["record screen", "screen recording", "স্ক্রিন রেকর্ড"]):
            return Intent(name="record_screen", action_type="recording", params={"duration": 5}, raw_prompt=text)

        # 12. Network & Windows Settings
        if "wifi" in clean or "ওয়াইফাই" in clean:
            if "on" in clean or "enable" in clean or "চালু" in clean:
                return Intent(name="wifi_control", action_type="network_settings", params={"action": "on"}, raw_prompt=text)
            elif "off" in clean or "disable" in clean or "বন্ধ" in clean:
                return Intent(name="wifi_control", action_type="network_settings", params={"action": "off"}, raw_prompt=text)
            elif "scan" in clean or "networks" in clean or "স্ক্যান" in clean:
                return Intent(name="wifi_control", action_type="network_settings", params={"action": "scan"}, raw_prompt=text)
        if "open settings" in clean or "windows settings" in clean or "সেটিংস খুলো" in clean:
            cat = re.sub(r".*(open settings|windows settings|সেটিংস খুলো)", "", clean).strip() or "system"
            return Intent(name="open_setting", action_type="network_settings", params={"category": cat}, raw_prompt=text)
        if "startup apps" in clean or "স্টার্টআপ অ্যাপস" in clean:
            return Intent(name="get_startup_apps", action_type="network_settings", params={}, raw_prompt=text)

        # 13. Pomodoro & Productivity Hub
        if "pomodoro" in clean or "পমোডোরো" in clean:
            if "stop" in clean or "বন্ধ" in clean:
                return Intent(name="pomodoro_control", action_type="productivity_hub", params={"action": "stop"}, raw_prompt=text)
            return Intent(name="pomodoro_control", action_type="productivity_hub", params={"action": "start"}, raw_prompt=text)
        if "clipboard history" in clean or "ক্লিপবোর্ড" in clean:
            return Intent(name="clipboard_history", action_type="productivity_hub", params={}, raw_prompt=text)
        if "calendar" in clean or "ক্যালেন্ডার" in clean:
            return Intent(name="show_calendar", action_type="productivity_hub", params={}, raw_prompt=text)

        # 14. Security Audit Logs
        if "audit log" in clean or "audit logs" in clean or "সিকিউরিটি লগ" in clean:
            return Intent(name="show_audit_logs", action_type="security", params={}, raw_prompt=text)

        # 15. Volume Controls
        if "volume up" in clean or "increase volume" in clean or "সাউন্ড বাড়াও" in clean:
            return Intent(name="volume_control", action_type="media", params={"command": "up"}, raw_prompt=text)
        if "volume down" in clean or "decrease volume" in clean or "সাউন্ড কমাও" in clean:
            return Intent(name="volume_control", action_type="media", params={"command": "down"}, raw_prompt=text)
        if "mute" in clean or "unmute" in clean or "সাউন্ড মিউট" in clean:
            return Intent(name="volume_control", action_type="media", params={"command": "mute"}, raw_prompt=text)

        # 16. Smart Music Playback
        if any(w in clean for w in ["play music", "play song", "গান চালাও", "প্লে মিউজিক"]):
            query = re.sub(r".*(play music|play song|গান চালাও|প্লে মিউজিক)", "", clean).strip()
            return Intent(name="play_smart_music", action_type="smart_music", params={"query": query}, raw_prompt=text)

        # 17. Playwright Browser Automation
        browser_sites = {
            "facebook": ["facebook", "fb"],
            "messenger": ["messenger"],
            "instagram": ["instagram", "ig"],
            "linkedin": ["linkedin"],
            "github": ["github"],
            "gmail": ["gmail", "email"],
            "drive": ["google drive", "gdrive"]
        }
        for site_key, keywords in browser_sites.items():
            if any(k in clean for k in keywords):
                if any(w in clean for w in ["open", "go to", "খুলো"]):
                    return Intent(name="open_browser_site", action_type="browser_auto", params={"site": site_key}, raw_prompt=text)

        # 18. Live Internet Data
        if "weather" in clean or "আবহাওয়া" in clean:
            location = re.sub(r".*(weather in|weather for|আবহাওয়া)", "", clean).strip() or "Dhaka"
            return Intent(name="get_live_weather", action_type="internet", params={"location": location}, raw_prompt=text)
        if "news" in clean or "খবর" in clean:
            return Intent(name="get_live_news", action_type="internet", params={}, raw_prompt=text)
        if "wikipedia" in clean or "wiki" in clean or "উইকিপিডিয়া" in clean:
            query = re.sub(r".*(wikipedia search|wikipedia|wiki|উইকিপিডিয়া)", "", clean).strip()
            return Intent(name="search_wikipedia", action_type="internet", params={"query": query}, raw_prompt=text)

        # 19. System Controls
        if "restart explorer" in clean or "explorer restart" in clean:
            return Intent(name="restart_explorer", action_type="system_control", params={}, raw_prompt=text)
        if any(w in clean for w in ["take screenshot", "screenshot", "স্ক্রিনশট"]):
            return Intent(name="take_screenshot", action_type="system_control", params={}, raw_prompt=text)
        if "brightness" in clean or "ব্রাইটনেস" in clean:
            if "up" in clean or "increase" in clean:
                return Intent(name="set_brightness", action_type="system_control", params={"change": 20}, raw_prompt=text)
            elif "down" in clean or "decrease" in clean:
                return Intent(name="set_brightness", action_type="system_control", params={"change": -20}, raw_prompt=text)
            else:
                level = re.findall(r"\d+", clean)
                val = int(level[0]) if level else 70
                return Intent(name="set_brightness", action_type="system_control", params={"level": val}, raw_prompt=text)
        if any(w in clean for w in ["search file", "find file", "ফাইল খোঁজো"]):
            query = re.sub(r".*(search file|find file|ফাইল খোঁজো)", "", clean).strip()
            return Intent(name="search_files", action_type="system_control", params={"query": query}, raw_prompt=text)

        # 20. Basic System App Launchers & Greetings
        if any(w in clean for w in ["hello", "hi", "hey", "good morning", "good evening", "সালাম", "হ্যালো", "আসসালামু আলাইকুম"]):
            return Intent(name="greeting", action_type="system", params={"type": "greeting"}, raw_prompt=text)
        if any(w in clean for w in ["time", "what time", "কয়টা বাজে", "কয়টা বাজে", "সময়", "সময়"]):
            return Intent(name="get_time", action_type="system", params={"type": "time"}, raw_prompt=text)
        if any(w in clean for w in ["date", "what date", "today's date", "আজকের তারিখ", "তারিখ"]):
            return Intent(name="get_date", action_type="system", params={"type": "date"}, raw_prompt=text)

        if any(w in clean for w in ["chrome", "ক্রোম", "ক্রোমিয়াম", "ব্রাউজার"]):
            return Intent(name="open_app", action_type="system", params={"app": "chrome"}, raw_prompt=text)
        if any(w in clean for w in ["edge", "এজ", "মাইক্রোসফট এজ"]):
            return Intent(name="open_app", action_type="system", params={"app": "edge"}, raw_prompt=text)
        if any(w in clean for w in ["vs code", "vscode", "ভিএস কোড", "কোড"]):
            return Intent(name="open_app", action_type="system", params={"app": "vscode"}, raw_prompt=text)
        if any(w in clean for w in ["notepad", "নোটপ্যাড"]):
            return Intent(name="open_app", action_type="system", params={"app": "notepad"}, raw_prompt=text)
        if any(w in clean for w in ["calculator", "calc", "ক্যালকুলেটর"]):
            return Intent(name="open_app", action_type="system", params={"app": "calculator"}, raw_prompt=text)
        if any(w in clean for w in ["explorer", "my computer", "মাই কম্পিউটার", "ফাইল এক্সপ্লোরার"]):
            return Intent(name="open_app", action_type="system", params={"app": "explorer"}, raw_prompt=text)
        if any(w in clean for w in ["task manager", "টাস্ক ম্যানেজার"]):
            return Intent(name="open_app", action_type="system", params={"app": "task_manager"}, raw_prompt=text)

        # 21. Productivity
        if any(w in clean for w in ["battery", "cpu", "ram", "internet", "system info"]):
            return Intent(name="system_info", action_type="productivity", params={"metric": "all"}, raw_prompt=text)

        if "remind me" in clean or "reminder" in clean:
            msg = re.sub(r".*(remind me to|reminder for)", "", clean).strip()
            return Intent(name="add_reminder", action_type="productivity", params={"message": msg}, raw_prompt=text)

        if "todo" in clean or "to-do" in clean:
            if any(w in clean for w in ["add", "create"]):
                task = re.sub(r".*(add todo|create todo)", "", clean).strip()
                return Intent(name="add_todo", action_type="productivity", params={"task": task}, raw_prompt=text)
            return Intent(name="show_todo", action_type="productivity", params={}, raw_prompt=text)

        if "note" in clean or "notes" in clean:
            if any(w in clean for w in ["add", "take", "write"]):
                content = re.sub(r".*(take note|add note|write note)", "", clean).strip()
                return Intent(name="add_note", action_type="productivity", params={"content": content}, raw_prompt=text)
            return Intent(name="show_notes", action_type="productivity", params={}, raw_prompt=text)

        # Fallback to LLM Chat
        return Intent(name="llm_chat", action_type="llm", params={"prompt": clean}, raw_prompt=text)


# Global Phase-6 IntentParser instance
intent_parser = IntentParser()
