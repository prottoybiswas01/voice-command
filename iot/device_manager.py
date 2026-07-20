"""
IoT Device Manager & Room Registry Module for X Assistant (Phase 4).
Registers physical hardware devices (Relays, LEDs, Servos, Buzzers, Sensors),
maps hardware pins, groups by rooms, and persists configuration in SQLite.
"""

from typing import List, Dict, Any, Optional
from config.settings import settings
from core.logger import logger
from core.database import db as global_db


class IoTDeviceManager:
    """Manages hardware devices, room groupings, and pin mappings."""

    def __init__(self, db_instance: Optional[Any] = None) -> None:
        self.db = db_instance or global_db
        self.init_default_devices()

    def init_default_devices(self) -> None:
        """Register default pre-configured hardware devices in SQLite database."""
        defaults = [
            ("relay_light", "Room Light", "Living Room", 7, "Relay", "OFF"),
            ("relay_fan", "Room Fan", "Bedroom", 8, "Relay", "OFF"),
            ("servo_door", "Door Lock Servo", "Door", 9, "Servo", "LOCKED"),
            ("buzzer_alarm", "Security Alarm Buzzer", "Living Room", 10, "Buzzer", "OFF"),
            ("led_builtin", "Status Indicator LED", "Living Room", 13, "LED", "OFF"),
            ("sensor_dht11", "Temperature & Humidity Sensor", "Living Room", 14, "DHT11", "ONLINE"),
            ("sensor_pir", "Motion Sensor", "Living Room", 2, "PIR", "ONLINE"),
            ("sensor_gas", "Gas & Smoke Detector", "Kitchen", 15, "Gas", "ONLINE")
        ]

        for dev_id, name, room, pin, dev_type, state in defaults:
            self.db.register_iot_device(dev_id, name, room, pin, dev_type, state)

    def register_device(self, device_id: str, name: str, room: str, pin: int, device_type: str) -> str:
        """Register or update custom IoT device."""
        self.db.register_iot_device(device_id, name, room, pin, device_type)
        msg = f"Registered IoT Device '{name}' (Pin {pin}, Room: {room})."
        logger.info(msg)
        return msg

    def set_device_state(self, device_id: str, state: str) -> str:
        """Update active device state."""
        self.db.update_device_state(device_id, state)
        msg = f"Device '{device_id}' state updated to: {state}."
        logger.info(msg)
        return msg

    def get_devices_by_room(self, room_name: str) -> List[Dict[str, Any]]:
        """Get devices filtered by room name."""
        all_devs = self.db.get_all_iot_devices()
        return [d for d in all_devs if d["room"].lower() == room_name.lower()]

    def list_all_devices(self) -> List[Dict[str, Any]]:
        """Fetch all registered hardware devices."""
        return self.db.get_all_iot_devices()


# Global IoT Device Manager instance
device_manager = IoTDeviceManager()
