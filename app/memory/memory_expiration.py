"""
Memory Expiration Manager: TTL Enforcement & Expired Record Purging
"""

from datetime import datetime, timezone
from typing import Any, Dict, List


class MemoryExpirationManager:
    """Purges expired memory records and reclaims storage."""

    @staticmethod
    def filter_active(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc).isoformat()
        active = []
        for rec in records:
            expires_at = rec.get("expires_at")
            if not expires_at or expires_at > now:
                active.append(rec)
        return active

    @staticmethod
    def get_expired(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc).isoformat()
        expired = []
        for rec in records:
            expires_at = rec.get("expires_at")
            if expires_at and expires_at <= now:
                expired.append(rec)
        return expired
