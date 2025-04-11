from uuid import UUID


class ExportService:
    def generate_download_link(self, env_id: UUID, expires_in: int) -> str:
        """Generate a secure one-time download link."""

    def validate_download_link(self, link_id: str) -> bool:
        """Validate whether a download link is still valid."""

    def retrieve_by_link(self, link_id: str) -> str:
        """Retrieve the environment file content by link."""
