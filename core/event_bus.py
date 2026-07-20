"""
Simple Event Bus for decoupling modules and components in X Assistant.
"""

from typing import Callable, Dict, List, Any
from core.logger import logger


class EventBus:
    """Publish-Subscribe event bus for internal events."""

    def __init__(self) -> None:
        self._listeners: Dict[str, List[Callable[..., Any]]] = {}

    def subscribe(self, event_name: str, listener: Callable[..., Any]) -> None:
        """Subscribe a handler function to a specific event."""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(listener)

    def publish(self, event_name: str, **kwargs: Any) -> None:
        """Broadcast an event with optional arguments to all subscribers."""
        if event_name in self._listeners:
            for listener in self._listeners[event_name]:
                try:
                    listener(**kwargs)
                except Exception as err:
                    logger.error(f"Error executing listener for event '{event_name}': {err}")


# Global EventBus instance
event_bus = EventBus()
