"""Telemetry Data Retention & Tier Storage Manager."""

import logging
from enum import Enum
from typing import Dict

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class RetentionTier(str, Enum):
    HOT = "HOT"
    WARM = "WARM"
    ARCHIVE = "ARCHIVE"


class RetentionPolicy(BaseModel):
    tenant_id: str = "global"
    hot_days: int = 7
    warm_days: int = 30
    archive_days: int = 365
    legal_hold_enabled: bool = False


class TelemetryRetentionManager:
    """Manages telemetry retention policies while protecting immutable administrative audit ledgers."""

    def __init__(self) -> None:
        self._policies: Dict[str, RetentionPolicy] = {}

    def set_policy(
        self, tenant_id: str, hot_days: int = 7, warm_days: int = 30, archive_days: int = 365
    ) -> RetentionPolicy:
        pol = RetentionPolicy(tenant_id=tenant_id, hot_days=hot_days, warm_days=warm_days, archive_days=archive_days)
        self._policies[tenant_id] = pol
        logger.info(
            f"[RETENTION MANAGER] Configured retention policy for tenant '{tenant_id}': Hot={hot_days}d, Warm={warm_days}d, Archive={archive_days}d"
        )
        return pol

    def get_policy(self, tenant_id: str) -> RetentionPolicy:
        return self._policies.get(tenant_id, RetentionPolicy(tenant_id=tenant_id))
