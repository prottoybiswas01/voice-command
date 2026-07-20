"""
Phase 4 Unit Test Suite for X Assistant.
Tests Arduino Serial Bridge, IoT Device Manager, Smart Home Controller, and Automation Rules Engine.
"""

import os
import unittest
from pathlib import Path
from core.database import DatabaseManager
from iot.arduino_bridge import ArduinoSerialBridge
from iot.device_manager import IoTDeviceManager
from iot.smart_home import SmartHomeController
from iot.automation_rules import AutomationRuleEngine


class TestXAssistantPhase4(unittest.TestCase):
    """Test suite covering Phase-4 Arduino, IoT & Smart Home Integration."""

    def setUp(self) -> None:
        self.test_db_path = Path("data/test_x_assistant_p4.db")
        if self.test_db_path.exists():
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

        self.db = DatabaseManager(db_path=str(self.test_db_path))
        self.bridge = ArduinoSerialBridge()
        self.dev_mgr = IoTDeviceManager(db_instance=self.db)
        self.smart_home = SmartHomeController()
        self.rules_engine = AutomationRuleEngine(db_instance=self.db)

    def tearDown(self) -> None:
        if self.test_db_path.exists():
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

    # Arduino Bridge Tests
    def test_bridge_simulation_mode(self) -> None:
        """Test virtual simulation mode fallback."""
        self.assertTrue(self.bridge.simulation_mode or self.bridge.is_connected)
        res = self.bridge.send_command({"cmd": "ping"})
        self.assertTrue(res)

    # Device Manager Tests
    def test_device_manager_registration(self) -> None:
        """Test device registration and room filtering."""
        devs = self.db.get_all_iot_devices()
        self.assertGreater(len(devs), 0)

        living_devs = self.dev_mgr.get_devices_by_room("Living Room")
        self.assertTrue(len(living_devs) > 0)

    # Smart Home Voice Controller Tests
    def test_smart_home_light_control(self) -> None:
        """Test light control voice command."""
        res_on = self.smart_home.handle_voice_command("control_light", {"state": "on"})
        self.assertIn("ON", res_on)

        res_off = self.smart_home.handle_voice_command("control_light", {"state": "off"})
        self.assertIn("OFF", res_off)

    def test_smart_home_telemetry_reading(self) -> None:
        """Test temperature and humidity voice queries."""
        temp_msg = self.smart_home.handle_voice_command("read_temperature", {})
        self.assertIn("temperature", temp_msg)

        hum_msg = self.smart_home.handle_voice_command("read_humidity", {})
        self.assertIn("humidity", hum_msg)

    # Automation Rules Engine Tests
    def test_automation_rules_evaluation(self) -> None:
        """Test automation rule creation and trigger evaluation."""
        rules = self.db.get_active_automation_rules()
        self.assertTrue(len(rules) > 0)
        self.rules_engine.evaluate_rules()


if __name__ == "__main__":
    unittest.main()
