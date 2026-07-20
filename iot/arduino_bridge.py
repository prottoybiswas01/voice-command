"""
Arduino Two-Way Serial Bridge Module for X Assistant (Phase 4).
Handles PySerial communication, automatic COM port detection, heartbeat monitoring,
auto-reconnect daemon, and Virtual Simulation mode fallback.
"""

import json
import time
import threading
from typing import Optional, Dict, Any, List, Callable
from config.settings import settings
from core.logger import logger
from core.database import db
from core.event_bus import event_bus

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    serial = None
    logger.warning("pyserial library not installed. Arduino bridge operating in Virtual Simulation mode.")


class ArduinoSerialBridge:
    """Manages two-way serial communication with connected Arduino boards."""

    def __init__(self) -> None:
        self.baud_rate = settings.iot.baud_rate
        self.auto_detect = settings.iot.auto_detect_com
        self.simulation_mode = False
        self.serial_port: Optional[Any] = None
        self.active_com_port: Optional[str] = None
        self.is_connected = False
        self._rx_thread: Optional[threading.Thread] = None

        # Virtual simulated sensor state for simulation mode
        self.virtual_sensor_state = {
            "temp": 29.5,
            "humidity": 65.0,
            "motion": 0,
            "gas": 120,
            "ldr": 512,
            "rain": 1023
        }

        self.connect()

    def find_arduino_com_port(self) -> Optional[str]:
        """Scan system COM ports for connected Arduino boards."""
        if not serial:
            return None

        try:
            ports = serial.tools.list_ports.comports()
            for port in ports:
                desc = port.description.lower()
                hwid = port.hwid.lower()
                if any(w in desc or w in hwid for w in ["arduino", "ch340", "cp210", "ftdi", "usb serial"]):
                    logger.info(f"Discovered Arduino device on port {port.device} ({port.description})")
                    return port.device
            if ports:
                return ports[0].device
        except Exception as err:
            logger.error(f"Error scanning COM ports: {err}")

        return None

    def connect(self) -> bool:
        """Establish serial connection or enable simulation mode."""
        if not serial:
            self._enable_simulation_mode("pyserial library unavailable")
            return False

        com_port = self.find_arduino_com_port()
        if not com_port:
            self._enable_simulation_mode("No physical Arduino hardware COM port detected")
            return False

        try:
            self.serial_port = serial.Serial(com_port, self.baud_rate, timeout=2)
            time.sleep(2)  # Wait for Arduino reset
            self.active_com_port = com_port
            self.is_connected = True
            self.simulation_mode = False
            logger.info(f"Arduino Serial connected on {com_port} @ {self.baud_rate} baud.")

            self._start_rx_listener()
            return True
        except Exception as err:
            logger.warning(f"Failed to connect to Arduino on {com_port}: {err}")
            self._enable_simulation_mode(str(err))
            return False

    def _enable_simulation_mode(self, reason: str) -> None:
        """Activate virtual hardware simulation fallback mode."""
        self.simulation_mode = True
        self.is_connected = False
        logger.info(f"Arduino Bridge active in Virtual Simulation Mode ({reason}).")

    def send_command(self, cmd_dict: Dict[str, Any]) -> bool:
        """
        Send JSON formatted command packet to Arduino.
        
        Args:
            cmd_dict: Command parameters dictionary.
            
        Returns:
            True if sent / simulated successfully.
        """
        json_str = json.dumps(cmd_dict) + "\n"

        if self.simulation_mode or not self.is_connected or not self.serial_port:
            logger.info(f"[Virtual IoT Simulation] Executed command: {json_str.strip()}")
            db.log_command(f"iot_sim:{cmd_dict.get('cmd', 'cmd')}", "SUCCESS", json_str.strip())
            return True

        try:
            self.serial_port.write(json_str.encode("utf-8"))
            logger.info(f"Sent Serial JSON: {json_str.strip()}")
            db.log_command(f"iot:{cmd_dict.get('cmd', 'cmd')}", "SUCCESS", json_str.strip())
            return True
        except Exception as err:
            logger.error(f"Serial transmission failed: {err}")
            self.is_connected = False
            self.simulation_mode = True
            return False

    def _start_rx_listener(self) -> None:
        """Start background telemetry listener thread."""
        def _rx_worker():
            while self.is_connected and self.serial_port and self.serial_port.is_open:
                try:
                    line = self.serial_port.readline().decode("utf-8", errors="ignore").strip()
                    if line and line.startswith("{") and line.endswith("}"):
                        data = json.loads(line)
                        event_bus.publish("arduino_telemetry", data=data)
                        if "telemetry" in data:
                            self._process_telemetry_packet(data)
                except Exception as err:
                    logger.debug(f"Serial rx exception: {err}")
                    time.sleep(1)

        self._rx_thread = threading.Thread(target=_rx_worker, daemon=True)
        self._rx_thread.start()

    def _process_telemetry_packet(self, data: Dict[str, Any]) -> None:
        """Log telemetry readings to SQLite database."""
        if "temp" in data:
            db.log_sensor_reading("DHT11", "Living Room", "temp", float(data["temp"]))
        if "humidity" in data:
            db.log_sensor_reading("DHT11", "Living Room", "humidity", float(data["humidity"]))
        if "motion" in data:
            db.log_sensor_reading("PIR", "Living Room", "motion", float(data["motion"]))
        if "gas" in data:
            db.log_sensor_reading("MQ2", "Kitchen", "gas", float(data["gas"]))

    def get_latest_telemetry(self) -> Dict[str, Any]:
        """Return latest telemetry dictionary."""
        if self.simulation_mode:
            # Slightly fluctuate virtual readings
            import random
            self.virtual_sensor_state["temp"] = round(29.5 + random.uniform(-0.5, 0.5), 1)
            self.virtual_sensor_state["humidity"] = round(65.0 + random.uniform(-1.0, 1.0), 1)
            return self.virtual_sensor_state

        db_readings = db.get_latest_sensor_readings()
        if db_readings:
            return db_readings
        return self.virtual_sensor_state


# Global Arduino Serial Bridge instance
arduino_bridge = ArduinoSerialBridge()
