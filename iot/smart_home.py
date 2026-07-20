"""
Voice Smart Home Controller Module for X Assistant (Phase 4).
Translates natural language voice commands into physical Arduino hardware operations.
"""

import re
from typing import Dict, Any, Optional
from core.logger import logger
from core.database import db
from iot.arduino_bridge import arduino_bridge
from iot.device_manager import device_manager


class SmartHomeController:
    """Translates voice commands to physical hardware instructions."""

    def handle_voice_command(self, action: str, params: Dict[str, Any]) -> str:
        """
        Execute Smart Home voice intent.
        
        Args:
            action: Action keyword name.
            params: Parameters dictionary.
            
        Returns:
            Status response speech string.
        """
        logger.info(f"Smart Home Action: {action} with params: {params}")

        # 1. Turn On / Off Room Light
        if action == "control_light":
            state = params.get("state", "on").lower()
            cmd_type = "relay_light_on" if state == "on" else "relay_light_off"
            arduino_bridge.send_command({"cmd": cmd_type, "pin": 7})
            device_manager.set_device_state("relay_light", "ON" if state == "on" else "OFF")
            msg = f"Turned {state.upper()} the room light."
            logger.info(msg)
            return msg

        # 2. Turn On / Off Room Fan
        elif action == "control_fan":
            state = params.get("state", "on").lower()
            cmd_type = "relay_fan_on" if state == "on" else "relay_fan_off"
            arduino_bridge.send_command({"cmd": cmd_type, "pin": 8})
            device_manager.set_device_state("relay_fan", "ON" if state == "on" else "OFF")
            msg = f"Turned {state.upper()} the room fan."
            logger.info(msg)
            return msg

        # 3. Read Temperature
        elif action == "read_temperature":
            telemetry = arduino_bridge.get_latest_telemetry()
            temp = telemetry.get("temp", 28.5)
            msg = f"The current room temperature is {temp}°C."
            logger.info(msg)
            return msg

        # 4. Read Humidity
        elif action == "read_humidity":
            telemetry = arduino_bridge.get_latest_telemetry()
            humidity = telemetry.get("humidity", 65.0)
            msg = f"The current room humidity is {humidity}%."
            logger.info(msg)
            return msg

        # 5. Detect Motion / Door Check
        elif action == "check_motion":
            telemetry = arduino_bridge.get_latest_telemetry()
            motion = telemetry.get("motion", 0)
            if motion:
                msg = "ALERT: Motion detected in the room!"
            else:
                msg = "No motion detected. Room is clear."
            logger.info(msg)
            return msg

        # 6. Turn On All Relays
        elif action == "all_relays_on":
            arduino_bridge.send_command({"cmd": "all_relays_on"})
            device_manager.set_device_state("relay_light", "ON")
            device_manager.set_device_state("relay_fan", "ON")
            msg = "All relays turned ON."
            logger.info(msg)
            return msg

        # 7. Turn Off All Relays
        elif action == "all_relays_off":
            arduino_bridge.send_command({"cmd": "all_relays_off"})
            device_manager.set_device_state("relay_light", "OFF")
            device_manager.set_device_state("relay_fan", "OFF")
            msg = "All relays turned OFF."
            logger.info(msg)
            return msg

        # 8. Blink LED
        elif action == "blink_led":
            count = params.get("count", 5)
            arduino_bridge.send_command({"cmd": "blink", "count": count})
            msg = f"Blinking status LED {count} times."
            logger.info(msg)
            return msg

        # 9. Rotate Servo Motor Angle
        elif action == "rotate_servo":
            angle = params.get("angle", 90)
            arduino_bridge.send_command({"cmd": "servo", "pin": 9, "angle": angle})
            device_manager.set_device_state("servo_door", f"ANGLE_{angle}")
            msg = f"Rotated servo motor to {angle} degrees."
            logger.info(msg)
            return msg

        return "Smart Home command processed."


# Global Smart Home Controller instance
smart_home_controller = SmartHomeController()
