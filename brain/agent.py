"""
Autonomous AI Agent Module for X Assistant (Phase 3).
Coordinates Plan -> Execute -> Verify -> Auto-Retry -> Explain loop for complex automation requests.
"""

import time
from typing import List, Dict, Any, Callable, Optional, Tuple
from config.settings import settings
from core.logger import logger
from brain.reasoning import reasoning_agent


class AgentStep:
    """Represents a single executable sub-task in agent plan."""

    def __init__(self, step_number: int, description: str, handler_func: Optional[Callable[[], str]] = None) -> None:
        self.step_number = step_number
        self.description = description
        self.handler_func = handler_func
        self.status = "PENDING"  # PENDING, RUNNING, SUCCESS, FAILED
        self.result_output = ""
        self.retry_count = 0


class AutonomousAgent:
    """Autonomous AI Agent managing task execution, verification, auto-retry, and explanations."""

    def __init__(self) -> None:
        self.max_retries = settings.agent.auto_retry_attempts
        self.current_plan: List[AgentStep] = []
        self.current_step_index = 0
        self.is_executing = False

    def create_plan(self, user_prompt: str) -> List[AgentStep]:
        """
        Decompose prompt into ordered AgentStep list.
        
        Args:
            user_prompt: Raw user command string.
            
        Returns:
            List of AgentStep items.
        """
        sub_tasks = reasoning_agent.decompose_prompt(user_prompt)
        if not sub_tasks:
            sub_tasks = [user_prompt]

        self.current_plan = [
            AgentStep(step_number=i+1, description=task) for i, task in enumerate(sub_tasks)
        ]
        self.current_step_index = 0
        logger.info(f"Autonomous Agent created plan with {len(self.current_plan)} steps.")
        return self.current_plan

    def execute_plan(self, executor_callback: Callable[[str], str]) -> str:
        """
        Execute planned steps sequentially with verification and auto-retry loop.
        
        Args:
            executor_callback: Function executing single prompt string and returning result.
            
        Returns:
            Combined execution summary response string.
        """
        if not self.current_plan:
            return "No execution plan active."

        self.is_executing = True
        results: List[str] = []

        for index, step in enumerate(self.current_plan):
            self.current_step_index = index
            step.status = "RUNNING"
            logger.info(f"Executing Agent Step {step.step_number}/{len(self.current_plan)}: '{step.description}'")

            success = False
            output = ""

            for attempt in range(self.max_retries + 1):
                step.retry_count = attempt
                try:
                    output = executor_callback(step.description)
                    # Simple output verification check
                    if output and not any(w in output.lower() for w in ["failed", "error", "unable", "not found"]):
                        success = True
                        step.status = "SUCCESS"
                        step.result_output = output
                        logger.info(f"Step {step.step_number} succeeded: {output}")
                        break
                    else:
                        logger.warning(f"Step {step.step_number} attempt {attempt+1} failed verification: {output}")
                except Exception as err:
                    output = f"Error: {err}"
                    logger.error(f"Step {step.step_number} exception on attempt {attempt+1}: {err}")

                time.sleep(0.5)

            if not success:
                step.status = "FAILED"
                step.result_output = output or "Step failed verification after retries."
                explanation = f"Step {step.step_number} ('{step.description}') encountered an issue: {step.result_output}"
                results.append(explanation)
            else:
                results.append(output)

        self.is_executing = False
        return " ".join(results)

    def explain_current_status(self) -> str:
        """Return human-readable explanation of active plan status."""
        if not self.current_plan:
            return "I am currently idle and ready for your commands."

        status_lines = [f"Agent Execution Plan ({len(self.current_plan)} steps):"]
        for step in self.current_plan:
            marker = "🟢" if step.status == "SUCCESS" else ("🔴" if step.status == "FAILED" else "🟡")
            status_lines.append(f"{marker} Step {step.step_number}: {step.description} [{step.status}]")

        return "\n".join(status_lines)


# Global Autonomous Agent instance
autonomous_agent = AutonomousAgent()
