from typing import List
from uuid import UUID

class AppService:
    def create_app(self, name: str, owner_id: UUID) -> UUID:
        """Create a new app."""

    def get_app(self, app_id: UUID) -> dict:
        """Retrieve app metadata."""

    def list_apps(self, user_id: UUID) -> List[dict]:
        """List all apps visible to a user."""

    def update_app(self, app_id: UUID, data: dict) -> None:
        """Update app name or settings."""

    def delete_app(self, app_id: UUID) -> None:
        """Delete a app."""
