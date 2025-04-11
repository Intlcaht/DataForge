from typing import List
from uuid import UUID


class EnvironmentService:
    def create_environment(self, app_id: UUID, name: str) -> UUID:
        """Create a new environment within a app."""

    def list_environments(self, app_id: UUID) -> List[dict]:
        """List all environments for a app."""

    def get_environment(self, env_id: UUID) -> dict:
        """Retrieve environment metadata."""

    def delete_environment(self, env_id: UUID) -> None:
        """Delete an environment."""
