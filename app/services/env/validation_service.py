from typing import List


class ValidationService:
    def validate_key(self, key: str) -> bool:
        """Validate key naming rules."""

    def validate_content(self, raw_text: str) -> List[str]:
        """Return a list of errors from raw `.env` content."""
