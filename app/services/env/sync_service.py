from uuid import UUID


class SyncService:
    def sync_to_external(self, env_id: UUID, target: str, credentials: dict) -> bool:
        """Sync environment to external target like AWS, Docker, Vault."""

    def register_webhook(self, env_id: UUID, url: str, event: str) -> None:
        """Register a webhook for environment changes."""
