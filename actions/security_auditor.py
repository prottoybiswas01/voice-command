"""
Security Auditor & Confirmation Gate Module for X Assistant (Phase 3).
Enforces security confirmation gates before destructive operations and records complete SQLite audit trails.
"""

from typing import Tuple, Dict, Any, List, Optional
from core.logger import logger
from core.database import db as global_db


class SecurityAuditor:
    """Security Gatekeeper and Audit Logger."""

    CRITICAL_ACTIONS = {
        "delete_file": "File Deletion",
        "delete_note": "Note Deletion",
        "format_drive": "Format Storage Drive",
        "shutdown": "System Shutdown",
        "restart": "System Restart",
        "close_critical_app": "Close System Application",
        "send_email": "Send Email",
        "financial_action": "Financial Action"
    }

    def __init__(self, db_instance: Optional[Any] = None) -> None:
        self.db = db_instance or global_db

    def is_confirmation_required(self, action_type: str) -> bool:
        """Check if action type requires user confirmation."""
        return action_type.lower() in self.CRITICAL_ACTIONS

    def request_confirmation_prompt(self, action_type: str, item_name: str) -> str:
        """Generate security warning confirmation prompt."""
        action_title = self.CRITICAL_ACTIONS.get(action_type.lower(), action_type)
        prompt = f"SECURITY ALERT: Confirm {action_title} for '{item_name}'? Say confirm to proceed."
        logger.warning(f"Security Confirmation Requested: [{action_type}] on '{item_name}'")
        return prompt

    def log_audit_trail(self, action_type: str, target_item: str, user_confirmed: bool = True, status: str = "SUCCESS", details: str = "") -> None:
        """Record audit log entry."""
        self.db.log_audit_event(action_type, target_item, user_confirmed=user_confirmed, status=status, details=details)

    def get_audit_trail_summary(self, limit: int = 10) -> str:
        """Return formatted audit trail summary."""
        logs = self.db.get_recent_audit_logs(limit=limit)
        if not logs:
            return "No audit events recorded yet."

        entries = [f"[{l['timestamp']}] {l['action_type']} -> {l['target_item']} ({l['status']})" for l in logs]
        return "Security Audit Logs:\n" + "\n".join(entries)


# Global Security Auditor instance
security_auditor = SecurityAuditor()
