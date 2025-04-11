from typing import List, Optional
from uuid import UUID


class AuditService:
    def log_action(self, user_id: UUID, action: str, metadata: Optional[dict] = None) -> None:
        """Record an audit log entry."""

    def get_logs_for_app(self, app_id: UUID) -> List[dict]:
        """Get all audit logs for an app."""
