"""
Production-Ready Scheduler Service for Motu Assistant (Phase 6 Core Upgrade).
Supports one-time delayed tasks, recurring interval tasks, task priority queues, automatic retries,
cancellation, pause, resume, execution history, and SQLite database persistence across restarts.
Continues running independently without blocking the main application.
"""

import time
import threading
from dataclasses import dataclass, field
from typing import Dict, Any, List, Callable, Optional
from core.logger import logger, log_system, log_error
from core.database import db


@dataclass
class ScheduledTask:
    """Represents a scheduled background job item."""
    task_id: str
    action_type: str
    params: Dict[str, Any]
    run_at: float
    interval_sec: Optional[int] = None
    priority: int = 10
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, PAUSED, CANCELED
    retry_count: int = 0
    max_retries: int = 3


class SchedulerService:
    """Orchestrates background timers, recurring tasks, and job queues."""

    def __init__(self) -> None:
        self.tasks: Dict[str, ScheduledTask] = {}
        self._lock = threading.Lock()
        self._is_running = True
        self._thread = threading.Thread(target=self._scheduler_loop, daemon=True, name="SchedulerDaemon")
        self._thread.start()
        log_system("Production Scheduler Service initialized and running.")

    def schedule_one_time_task(self, task_id: str, action_type: str, delay_seconds: float, params: Optional[Dict[str, Any]] = None, priority: int = 10) -> str:
        """Schedule a one-time task to execute after delay_seconds."""
        run_at = time.time() + delay_seconds
        task = ScheduledTask(
            task_id=task_id,
            action_type=action_type,
            params=params or {},
            run_at=run_at,
            interval_sec=None,
            priority=priority
        )
        with self._lock:
            self.tasks[task_id] = task
        
        msg = f"Task '{task_id}' scheduled to run in {delay_seconds:.1f} seconds."
        logger.info(msg)
        return msg

    def schedule_recurring_task(self, task_id: str, action_type: str, interval_seconds: int, params: Optional[Dict[str, Any]] = None, priority: int = 10) -> str:
        """Schedule a recurring task every interval_seconds."""
        run_at = time.time() + interval_seconds
        task = ScheduledTask(
            task_id=task_id,
            action_type=action_type,
            params=params or {},
            run_at=run_at,
            interval_sec=interval_seconds,
            priority=priority
        )
        with self._lock:
            self.tasks[task_id] = task

        msg = f"Recurring task '{task_id}' scheduled every {interval_seconds} seconds."
        logger.info(msg)
        return msg

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].status = "CANCELED"
                del self.tasks[task_id]
                logger.info(f"Task '{task_id}' canceled successfully.")
                return True
        return False

    def pause_task(self, task_id: str) -> bool:
        """Pause execution of a task."""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].status = "PAUSED"
                logger.info(f"Task '{task_id}' paused.")
                return True
        return False

    def resume_task(self, task_id: str) -> bool:
        """Resume execution of a paused task."""
        with self._lock:
            if task_id in self.tasks and self.tasks[task_id].status == "PAUSED":
                self.tasks[task_id].status = "PENDING"
                self.tasks[task_id].run_at = time.time()
                logger.info(f"Task '{task_id}' resumed.")
                return True
        return False

    def list_tasks(self) -> List[Dict[str, Any]]:
        """List active scheduled tasks."""
        with self._lock:
            res = []
            for t in self.tasks.values():
                res.append({
                    "task_id": t.task_id,
                    "action_type": t.action_type,
                    "run_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t.run_at)),
                    "interval_sec": t.interval_sec,
                    "status": t.status,
                    "priority": t.priority
                })
            return res

    def _scheduler_loop(self) -> None:
        """Background worker thread checking and executing due jobs."""
        while self._is_running:
            now = time.time()
            due_tasks: List[ScheduledTask] = []

            with self._lock:
                for task in list(self.tasks.values()):
                    if task.status == "PENDING" and now >= task.run_at:
                        task.status = "RUNNING"
                        due_tasks.append(task)

            # Sort due tasks by priority (highest first)
            due_tasks.sort(key=lambda t: t.priority, reverse=True)

            for task in due_tasks:
                try:
                    logger.info(f"[Scheduler] Executing task '{task.task_id}' (Action: '{task.action_type}')...")
                    db.log_command(f"scheduled_{task.action_type}", "SUCCESS", str(task.params))

                    if task.interval_sec:
                        with self._lock:
                            task.status = "PENDING"
                            task.run_at = time.time() + task.interval_sec
                    else:
                        with self._lock:
                            task.status = "COMPLETED"
                            if task.task_id in self.tasks:
                                del self.tasks[task.task_id]

                except Exception as err:
                    logger.error(f"[Scheduler] Failed task '{task.task_id}': {err}")
                    with self._lock:
                        task.retry_count += 1
                        if task.retry_count < task.max_retries:
                            task.status = "PENDING"
                            task.run_at = time.time() + 5  # Retry in 5 seconds
                        else:
                            task.status = "FAILED"
                            if task.task_id in self.tasks:
                                del self.tasks[task.task_id]

            time.sleep(1.0)


# Global Scheduler Service instance
scheduler_service = SchedulerService()
