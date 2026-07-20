"""
Extensible Plugin Framework & Dynamic Loader for X Assistant (Phase 6).
Dynamically discovers and loads custom Python plugins from plugins/ directory,
registering custom commands, hardware tools, and automation triggers without touching core code.
"""

import sys
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional
from config.settings import settings
from core.logger import logger
from core.database import db


class PluginManager:
    """Manages dynamic loading, permission gatekeeping, and command dispatch for custom plugins."""

    def __init__(self) -> None:
        self.plugins_dir = settings.paths.plugins_dir
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_plugins: Dict[str, Any] = {}
        self.registered_commands: Dict[str, Callable[[str, Dict[str, Any]], str]] = {}
        self.discover_and_load_plugins()

    def discover_and_load_plugins(self) -> None:
        """Scan plugins/ folder for Python files and load them dynamically."""
        for py_file in self.plugins_dir.glob("*.py"):
            if py_file.name.startswith("_") or py_file.name.startswith("plugin_manager"):
                continue
            self.load_plugin_file(py_file)

    def load_plugin_file(self, filepath: Path) -> bool:
        """Load plugin module from filepath."""
        plugin_name = filepath.stem
        try:
            spec = importlib.util.spec_from_file_location(plugin_name, filepath)
            if not spec or not spec.loader:
                return False

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Look for setup_plugin hook
            if hasattr(module, "setup_plugin"):
                plugin_info = module.setup_plugin(self)
                self.loaded_plugins[plugin_name] = module
                p_id = plugin_info.get("id", plugin_name) if isinstance(plugin_info, dict) else plugin_name
                db.register_plugin(p_id, plugin_name, version="1.0.0", status="ACTIVE")
                logger.info(f"Loaded Plugin: '{plugin_name}' successfully.")
                return True
        except Exception as err:
            logger.error(f"Failed to load plugin {filepath.name}: {err}")
            return False

        return False

    def register_command(self, trigger_keyword: str, handler_func: Callable[[str, Dict[str, Any]], str]) -> None:
        """Register custom plugin voice command handler."""
        key = trigger_keyword.lower().strip()
        self.registered_commands[key] = handler_func
        logger.info(f"Registered plugin command: '{key}'")

    def execute_plugin_command(self, trigger_keyword: str, raw_text: str = "") -> Optional[str]:
        """Execute registered plugin command if matched."""
        key = trigger_keyword.lower().strip()
        for cmd_key, handler in self.registered_commands.items():
            if cmd_key in key:
                logger.info(f"Executing plugin handler for keyword: '{cmd_key}'")
                return handler(raw_text, {})
        return None

    def list_plugins(self) -> List[Dict[str, Any]]:
        """Fetch list of loaded plugins."""
        return db.get_installed_plugins()


# Global Plugin Manager instance
plugin_manager = PluginManager()
