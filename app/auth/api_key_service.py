import hashlib
import secrets
from typing import Tuple

from app.core.config import get_settings

settings = get_settings()


class APIKeyService:
    @staticmethod
    def generate_api_key(prefix: str = "sk") -> Tuple[str, str, str]:
        """
        Generate a new API key.
        Returns:
            Tuple of (raw_key, prefix, hashed_key)
        """
        # Generate random bytes and encode as urlsafe base64
        random_part = secrets.token_urlsafe(settings.api_key_length)
        raw_key = f"{prefix}_{random_part}"

        # We store the hash of the raw_key using SHA-256
        # (Since it's high entropy, SHA-256 is sufficient and fast compared to bcrypt)
        hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()

        return raw_key, prefix, hashed_key

    @staticmethod
    def hash_api_key(raw_key: str) -> str:
        """Hash an incoming raw API key for comparison."""
        return hashlib.sha256(raw_key.encode()).hexdigest()

    @staticmethod
    def verify_api_key(raw_key: str, hashed_key: str) -> bool:
        """Verify a raw API key against a stored hash."""
        expected_hash = APIKeyService.hash_api_key(raw_key)
        return secrets.compare_digest(expected_hash, hashed_key)
