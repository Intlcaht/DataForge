from typing import List
from uuid import UUID


class AccessControlService:
    def assign_role(self, user_id: UUID, app_id: UUID, role: str) -> None:
        """Assign a user a role in a app."""

    def check_permission(self, user_id: UUID, app_id: UUID, permission: str) -> bool:
        """Check if the user has the given permission in the app."""

    def list_members(self, app_id: UUID) -> List[dict]:
        """List all members of a app and their roles."""
