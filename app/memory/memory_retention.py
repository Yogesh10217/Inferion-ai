"""
Memory Retention Manager: Policies, Archiving, Soft & Hard Deletion
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from app.memory.memory_types import RetentionPolicy


class MemoryRetentionManager:
    """Enforces retention policies, handles archiving, soft and hard deletions."""

    @staticmethod
    def calculate_expiration(policy: RetentionPolicy) -> Optional[datetime]:
        now = datetime.now(timezone.utc)
        if policy == RetentionPolicy.EPHEMERAL:
            return now + timedelta(minutes=15)
        elif policy == RetentionPolicy.SESSION:
            return now + timedelta(hours=24)
        elif policy == RetentionPolicy.TTL_30_DAYS:
            return now + timedelta(days=30)
        elif policy == RetentionPolicy.TTL_90_DAYS:
            return now + timedelta(days=90)
        elif policy in (RetentionPolicy.PERMANENT, RetentionPolicy.ARCHIVE):
            return None
        return None

    @staticmethod
    def should_archive(policy: RetentionPolicy, age_days: float) -> bool:
        if policy == RetentionPolicy.ARCHIVE:
            return True
        if policy == RetentionPolicy.TTL_30_DAYS and age_days > 30:
            return True
        return False
