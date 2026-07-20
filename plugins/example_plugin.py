"""
Example Custom Plugin for X Assistant (Phase 6).
Demonstrates registering custom plugin commands and extensions cleanly.
"""

from typing import Dict, Any


def sample_plugin_action(prompt: str, params: Dict[str, Any]) -> str:
    """Sample custom plugin command logic."""
    return "Sample Plugin Action executed! X Assistant plugin system working nominal."


def setup_plugin(manager) -> Dict[str, Any]:
    """Plugin initialization entry point hook."""
    manager.register_command("test plugin", sample_plugin_action)
    return {
        "id": "example_plugin",
        "name": "Sample Extension Plugin",
        "version": "1.0.0"
    }
