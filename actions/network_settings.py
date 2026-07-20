"""
Network, Windows Settings & System Startup Manager for X Assistant (Phase 3).
Controls Wi-Fi, Bluetooth shortcuts, Windows Settings menus, Task Manager, and Startup Application inspection.
"""

import subprocess
import os
from typing import List, Dict, Any
from core.logger import logger
from core.database import db


class NetworkAndSettingsManager:
    """Manages Windows network interfaces, settings shortcuts, and startup applications."""

    def manage_wifi(self, action: str = "status") -> str:
        """
        Manage Wi-Fi network interface or scan networks.
        
        Args:
            action: 'on', 'off', 'scan', or 'status'.
        """
        try:
            if action == "scan":
                res = subprocess.run(["netsh", "wlan", "show", "networks"], capture_output=True, text=True)
                lines = [line.strip() for line in res.stdout.split("\n") if "SSID" in line]
                msg = f"Available Wi-Fi Networks: {', '.join(lines[:5])}" if lines else "No Wi-Fi networks found."
                logger.info(msg)
                return msg

            elif action == "on":
                subprocess.run("netsh interface set interface \"Wi-Fi\" admin=enable", shell=True)
                msg = "Wi-Fi interface enabled."
                logger.info(msg)
                db.log_command("wifi:on", "SUCCESS", msg)
                return msg

            elif action == "off":
                subprocess.run("netsh interface set interface \"Wi-Fi\" admin=disable", shell=True)
                msg = "Wi-Fi interface disabled."
                logger.info(msg)
                db.log_command("wifi:off", "SUCCESS", msg)
                return msg

            else:
                res = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True)
                msg = "Wi-Fi Interface Status: " + ("Connected" if "State : connected" in res.stdout.lower() else "Disconnected")
                return msg

        except Exception as err:
            logger.error(f"Error managing Wi-Fi: {err}")
            return f"Wi-Fi command error: {err}"

    def open_windows_setting(self, category: str = "system") -> str:
        """
        Open Windows Settings app directly to specific URI category.
        
        Args:
            category: 'bluetooth', 'wifi', 'sound', 'display', 'apps', 'network', 'system'.
        """
        settings_uris = {
            "bluetooth": "ms-settings:bluetooth",
            "wifi": "ms-settings:network-wifi",
            "sound": "ms-settings:sound",
            "display": "ms-settings:display",
            "apps": "ms-settings:appsfeatures",
            "network": "ms-settings:network",
            "system": "ms-settings:"
        }

        uri = settings_uris.get(category.lower(), "ms-settings:")

        try:
            subprocess.Popen(f"start {uri}", shell=True)
            msg = f"Opening Windows Settings ({category.capitalize()})."
            logger.info(msg)
            db.log_command(f"open_setting:{category}", "SUCCESS", msg)
            return msg
        except Exception as err:
            logger.error(f"Failed to open Windows Settings '{category}': {err}")
            return f"Failed to open settings: {err}"

    def get_startup_apps(self) -> str:
        """Query registry for Windows startup applications."""
        ps_script = 'Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run, HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run | Select-Object -Property PSChildName'
        try:
            res = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
            lines = [line.strip() for line in res.stdout.split("\n") if line.strip() and not line.startswith("PSChildName") and not line.startswith("-")]
            if lines:
                msg = "Startup Apps registered: " + ", ".join(lines[:5])
                logger.info(msg)
                return msg
            return "No custom startup applications registered in Registry."
        except Exception as err:
            logger.error(f"Failed to fetch startup apps: {err}")
            return f"Failed to list startup apps: {err}"


# Global Network & Settings Manager instance
network_settings_manager = NetworkAndSettingsManager()
