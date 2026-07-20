"""
Multi-Device Ecosystem Architecture Module for X Assistant (Phase 6).
Maps hardware profiles and communication specs for Desktop, Laptop, Arduino, ESP8266, and ESP32 nodes.
"""

from typing import Dict, Any, List
from core.logger import logger


class MultiDeviceEcosystem:
    """Manages multi-device target profiles and communication specs."""

    DEVICE_PROFILES = {
        "desktop_primary": {
            "type": "PC",
            "role": "Master Host Orchestrator & Local Ollama LLM Server",
            "os": "Windows 10/11",
            "comm": "Local AsyncIO & Subprocesses"
        },
        "arduino_uno": {
            "type": "Microcontroller",
            "role": "Sensors & Relay Actuator Node",
            "board": "ATmega328P",
            "comm": "USB Serial @ 9600 Baud"
        },
        "esp32_node": {
            "type": "Microcontroller with Wi-Fi/BT",
            "role": "Wireless Sensor Node & Smart Camera",
            "board": "ESP32-WROOM / ESP32-CAM",
            "comm": "Wi-Fi HTTP / WebSocket / Serial"
        },
        "esp8266_node": {
            "type": "Microcontroller with Wi-Fi",
            "role": "Wireless Relay & Environment Monitor",
            "board": "NodeMCU V3 / ESP-12E",
            "comm": "Wi-Fi HTTP / Serial"
        }
    }

    def list_device_profiles(self) -> Dict[str, Any]:
        """Fetch all supported device ecosystem profiles."""
        return self.DEVICE_PROFILES

    def get_device_summary(self) -> str:
        """Return human-friendly multi-device ecosystem summary."""
        profiles_txt = [f"- {k.upper()}: {v['role']} ({v['comm']})" for k, v in self.DEVICE_PROFILES.items()]
        return "Multi-Device Ecosystem Nodes:\n" + "\n".join(profiles_txt)


# Global Multi-Device Ecosystem instance
multi_device_ecosystem = MultiDeviceEcosystem()
