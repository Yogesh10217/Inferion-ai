"""Change Intelligence & Operational Regression Correlation Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field

from app.control_plane.change_history import ChangeHistoryTracker

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class OperationalChange(BaseModel):
    change_id: str = Field(default_factory=lambda: f"chg_{uuid.uuid4().hex[:10]}")
    change_type: str  # DEPLOYMENT, CONFIG_CHANGE, FEATURE_FLAG, EXTENSION_UPGRADE, MARKETPLACE_INSTALL, CONTROL_PLANE
    resource_id: str
    tenant_id: str = "global"
    description: str = ""
    actor: str = "admin"
    timestamp: datetime = Field(default_factory=_now)


class ChangeCorrelationEngine:
    """Correlates operational incidents and metric regressions with recent platform configuration/deployment changes."""

    def __init__(self, change_history_tracker: Optional[ChangeHistoryTracker] = None) -> None:
        self.change_history_tracker = change_history_tracker or ChangeHistoryTracker()
        self._recent_changes: List[OperationalChange] = []

    def record_change(
        self,
        change_type: str,
        resource_id: str,
        description: str,
        tenant_id: str = "global",
        actor: str = "admin",
    ) -> OperationalChange:
        chg = OperationalChange(
            change_type=change_type,
            resource_id=resource_id,
            description=description,
            tenant_id=tenant_id,
            actor=actor,
        )
        self._recent_changes.append(chg)

        # Also record on underlying ChangeHistoryTracker
        if hasattr(self.change_history_tracker, "record_change"):
            try:
                self.change_history_tracker.record_change(
                    category=change_type,
                    target_id=resource_id,
                    version_label="v1",
                    actor_id=actor,
                    tenant_id=tenant_id,
                )
            except Exception:  # nosec B110
                pass

        logger.info(
            f"[CHANGE INTELLIGENCE] Recorded change '{chg.change_id}' ({change_type}) on resource '{resource_id}'"
        )
        return chg

    def find_recent_changes(
        self, tenant_id: Optional[str] = None, resource_id: Optional[str] = None
    ) -> List[OperationalChange]:
        res = self._recent_changes
        if tenant_id:
            res = [c for c in res if c.tenant_id in (tenant_id, "global")]
        if resource_id:
            res = [c for c in res if c.resource_id == resource_id]
        return res
