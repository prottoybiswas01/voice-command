"""
Centralized Priority & Asynchronous Event Bus for Motu Assistant (Phase 6 Core Upgrade).
Decouples system modules by routing events through a thread-safe publish-subscribe architecture
with priority queues, async thread-pool dispatching, and exception boundary protection.
"""

import sys
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, List, Any, Optional
from core.logger import logger, log_system, log_error

# Standard Event Topic Constants
EVENT_STARTUP = "system.startup"
EVENT_SHUTDOWN = "system.shutdown"
EVENT_AI = "ai.response"
EVENT_VOICE = "voice.recognized"
EVENT_ARDUINO = "arduino.event"
EVENT_BROWSER = "browser.action"
EVENT_SYSTEM = "system.event"
EVENT_ERROR = "system.error"


class ListenerEntry:
    """Encapsulates a subscriber callback with priority level."""

    def __init__(self, callback: Callable[..., Any], priority: int = 10) -> None:
        self.callback = callback
        self.priority = priority

    def __lt__(self, other: "ListenerEntry") -> bool:
        # Higher priority value runs first
        return self.priority > other.priority


class EventBus:
    """Publish-Subscribe priority event bus for internal system decoupling."""

    def __init__(self, max_workers: int = 4) -> None:
        self._listeners: Dict[str, List[ListenerEntry]] = {}
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="EventBusWorker")

    def subscribe(self, event_name: str, listener: Callable[..., Any], priority: int = 10) -> None:
        """
        Subscribe a callback listener to a specific event topic.
        
        Args:
            event_name: Topic string.
            listener: Callback function.
            priority: Higher numbers execute first (default: 10).
        """
        with self._lock:
            if event_name not in self._listeners:
                self._listeners[event_name] = []
            entry = ListenerEntry(callback=listener, priority=priority)
            self._listeners[event_name].append(entry)
            self._listeners[event_name].sort()

    def unsubscribe(self, event_name: str, listener: Callable[..., Any]) -> bool:
        """Unsubscribe a callback from an event topic."""
        with self._lock:
            if event_name in self._listeners:
                original_len = len(self._listeners[event_name])
                self._listeners[event_name] = [
                    entry for entry in self._listeners[event_name] if entry.callback != listener
                ]
                return len(self._listeners[event_name]) < original_len
        return False

    def publish(self, event_name: str, **kwargs: Any) -> None:
        """Synchronously broadcast an event to all subscribers in priority order."""
        listeners_to_run = []
        with self._lock:
            if event_name in self._listeners:
                listeners_to_run = list(self._listeners[event_name])

        for entry in listeners_to_run:
            try:
                entry.callback(**kwargs)
            except Exception as err:
                log_error(f"Error executing listener '{entry.callback.__name__}' for event '{event_name}': {err}")

    def publish_async(self, event_name: str, **kwargs: Any) -> None:
        """Asynchronously dispatch an event via background worker thread pool."""
        self._executor.submit(self.publish, event_name, **kwargs)

    def shutdown(self) -> None:
        """Gracefully shutdown event bus thread pool."""
        try:
            self._executor.shutdown(wait=False)
        except Exception:
            pass


# Global EventBus instance
event_bus = EventBus()
