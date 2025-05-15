from typing import List
from uuid import UUID


class EnvVariableService:
    def set_variable(self, env_id: UUID, key: str, value: str, masked: bool = True) -> None:
        """Set or update a single environment variable."""

    def get_variable(self, env_id: UUID, key: str, reveal: bool = False) -> dict:
        """Retrieve a single environment variable."""

    def delete_variable(self, env_id: UUID, key: str) -> None:
        """Delete a variable."""

    def list_variables(self, env_id: UUID, reveal: bool = False) -> List[dict]:
        """List all variables in an environment."""

    def import_from_text(self, env_id: UUID, raw_text: str) -> None:
        """Import environment variables from `.env`-style text."""

    def export_to_text(self, env_id: UUID, reveal: bool = False) -> str:
        """Export environment variables to `.env` text format."""
