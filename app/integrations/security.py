"""Integration Security Engine & Secret Redaction Subsystem."""

import logging
from typing import Optional

from app.security.secrets import SecretManager

logger = logging.getLogger(__name__)


class IntegrationSecurityEngine:
    """Sanitizes external payloads, redacts secrets, and verifies tenant isolation."""

    def __init__(self, secret_manager: Optional[SecretManager] = None) -> None:
        self.secret_manager = secret_manager or SecretManager()

    def sanitize_payload(self, payload: str) -> str:
        return self.secret_manager.sanitize_text(payload)
