"""
Multi-step Reasoning & Task Decomposition Agent for X Assistant (Phase 2).
Splits complex user requests into sequential sub-tasks and coordinates multi-step execution.
"""

import re
from typing import List, Dict, Any, Tuple
from core.logger import logger


class ReasoningAgent:
    """Decomposes multi-intent prompts into actionable execution plans."""

    def is_multi_step_request(self, prompt: str) -> bool:
        """
        Determine if user request contains multiple conjunctions or sub-commands.
        Examples:
        - "Take a screenshot and open Chrome"
        - "Check weather then search news"
        """
        if not prompt:
            return False

        clean = prompt.lower().strip()
        # Look for conjunction connectors
        connectors = [" and then ", " then ", " and also ", " and ", " তারপরে ", " এবং "]
        return any(c in clean for c in connectors)

    def decompose_prompt(self, prompt: str) -> List[str]:
        """
        Decompose multi-intent prompt into sequential sub-prompts.
        
        Args:
            prompt: Compound user prompt string.
            
        Returns:
            List of individual sub-task prompt strings.
        """
        if not prompt:
            return []

        # Replace conjunction keywords with split delimiter '|'
        temp = prompt
        patterns = [
            r"\s+and\s+then\s+", r"\s+then\s+", r"\s+and\s+also\s+", r"\s+and\s+",
            r"\s+তারপরে\s+", r"\s+এবং\s+"
        ]
        for pat in patterns:
            temp = re.sub(pat, " | ", temp, flags=re.IGNORECASE)

        sub_tasks = [t.strip() for t in temp.split("|") if t.strip()]
        logger.info(f"Decomposed prompt '{prompt}' into {len(sub_tasks)} sub-tasks: {sub_tasks}")
        return sub_tasks


# Global Reasoning Agent instance
reasoning_agent = ReasoningAgent()
