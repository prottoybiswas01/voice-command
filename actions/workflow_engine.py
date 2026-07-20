"""
Macro Workflows & Smart Home Scenes Engine for X Assistant (Phase 6).
Executes user-defined macro routines (e.g. "Start Work Mode", "Good Night")
combining desktop apps, browser agent, Pomodoro timer, and IoT hardware scenes.
"""

from typing import List, Dict, Any, Callable, Optional
from core.logger import logger
from core.database import db
from speech.tts import tts_engine


class WorkflowEngine:
    """Manages custom macro routines and smart home scenes."""

    def __init__(self) -> None:
        self.init_default_workflows()

    def init_default_workflows(self) -> None:
        """Register default macro routines in SQLite database if empty."""
        existing = db.get_all_workflows()
        if not existing:
            db.add_user_workflow(
                "Work Mode Routine",
                "start work mode",
                ["open_app:vscode", "open_app:chrome", "open_site:github", "start_pomodoro"]
            )
            db.add_user_workflow(
                "Good Night Scene",
                "good night",
                ["all_relays_off", "lock_door", "control_fan_off"]
            )

    def execute_workflow(self, trigger_keyword: str, single_intent_executor_func: Callable[[str], str]) -> Optional[str]:
        """
        Execute macro workflow routine matching trigger keyword.
        
        Args:
            trigger_keyword: Input voice command keyword.
            single_intent_executor_func: Executor function callback.
            
        Returns:
            Speech summary of executed macro steps or None if not matched.
        """
        clean_key = trigger_keyword.lower().strip()
        workflows = db.get_all_workflows()

        matched_wf = None
        for wf in workflows:
            if wf["trigger_keyword"] in clean_key or clean_key in wf["trigger_keyword"]:
                matched_wf = wf
                break

        if not matched_wf:
            return None

        wf_name = matched_wf["workflow_name"]
        actions = matched_wf.get("actions", [])
        logger.info(f"Executing Macro Workflow [{wf_name}] with {len(actions)} steps.")

        executed_steps = []
        for step in actions:
            # Map macro action string to assistant intent prompt
            if step == "open_app:vscode":
                single_intent_executor_func("open vs code")
            elif step == "open_app:chrome":
                single_intent_executor_func("open chrome")
            elif step == "open_site:github":
                single_intent_executor_func("open github")
            elif step == "start_pomodoro":
                single_intent_executor_func("start pomodoro")
            elif step == "all_relays_off":
                single_intent_executor_func("turn off all relays")
            elif step == "lock_door":
                single_intent_executor_func("rotate servo to 90 degrees")
            elif step == "control_fan_off":
                single_intent_executor_func("turn off fan")
            else:
                single_intent_executor_func(step)

            executed_steps.append(step)

        msg = f"Executed macro workflow '{wf_name}' ({len(executed_steps)} actions completed)."
        logger.info(msg)
        return msg


# Global Workflow Engine instance
workflow_engine = WorkflowEngine()
