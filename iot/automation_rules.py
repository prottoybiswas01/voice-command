"""
Rule-Based Automation Engine Module for X Assistant (Phase 4).
Evaluates real-time sensor triggers against active automation rules
(e.g. Temp > 32°C -> Fan ON, Motion -> Light ON, Gas -> Alarm Buzzer).
"""

import time
import threading
from typing import List, Dict, Any, Optional
from config.settings import settings
from core.logger import logger
from core.database import db as global_db
from speech.tts import tts_engine
from iot.arduino_bridge import arduino_bridge
from iot.device_manager import device_manager


class AutomationRuleEngine:
    """Evaluates sensor telemetry rules and triggers automated hardware actions."""

    def __init__(self, db_instance: Optional[Any] = None) -> None:
        self.db = db_instance or global_db
        self.is_active = False
        self.init_default_rules()
        self._eval_thread: Optional[threading.Thread] = None

    def init_default_rules(self) -> None:
        """Register default smart home automation rules in SQLite."""
        existing = self.db.get_active_automation_rules()
        if not existing:
            self.db.add_automation_rule("Auto Cool Fan", "temp", ">", 32.0, "relay_fan", "relay_fan_on")
            self.db.add_automation_rule("Motion Night Light", "motion", "==", 1.0, "relay_light", "relay_light_on")
            self.db.add_automation_rule("Gas Leak Safety Alarm", "gas", ">", 400.0, "buzzer_alarm", "buzzer_on")

    def start_engine(self) -> None:
        """Start background rule evaluation thread."""
        if self.is_active:
            return

        self.is_active = True

        def _worker():
            logger.info("Rule-Based Automation Engine active. Background monitoring ready.")
            while self.is_active:
                try:
                    self.evaluate_rules()
                except Exception as err:
                    logger.error(f"Error evaluating automation rules: {err}")
                time.sleep(3)

        self._eval_thread = threading.Thread(target=_worker, daemon=True)
        self._eval_thread.start()

    def stop_engine(self) -> None:
        """Stop automation engine thread."""
        self.is_active = False

    def evaluate_rules(self) -> None:
        """Fetch latest sensor readings and check against active rules."""
        rules = self.db.get_active_automation_rules()
        if not rules:
            return

        telemetry = arduino_bridge.get_latest_telemetry()

        for rule in rules:
            sensor_key = rule["trigger_sensor"].lower()
            if sensor_key not in telemetry:
                continue

            current_val = float(telemetry[sensor_key])
            op = rule["condition_op"]
            threshold = float(rule["threshold_value"])

            triggered = False
            if op == ">" and current_val > threshold:
                triggered = True
            elif op == "<" and current_val < threshold:
                triggered = True
            elif op in ["==", "="] and current_val == threshold:
                triggered = True

            if triggered:
                action_cmd = rule["action_command"]
                logger.info(f"Automation Rule Triggered: [{rule['rule_name']}] ({sensor_key}={current_val} {op} {threshold}) -> Action: {action_cmd}")
                
                arduino_bridge.send_command({"cmd": action_cmd})
                
                if "gas" in sensor_key or "buzzer" in action_cmd:
                    warning_msg = "WARNING! Gas leak detected! Activating security buzzer alarm!"
                    tts_engine.speak(warning_msg)


# Global Automation Rule Engine instance
automation_rule_engine = AutomationRuleEngine()
