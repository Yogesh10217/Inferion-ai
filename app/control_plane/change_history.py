"""Change History & Diff Tracking for Control Plane Timeline & Rollback."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ChangeRecord(BaseModel):
    """Timeline entry representing a change."""

    change_id: str = Field(default_factory=lambda: f"chg_{uuid.uuid4().hex[:10]}")
    category: str  # 'configuration', 'policy', 'feature', 'lifecycle', 'admin'
    target_id: str
    tenant_id: str = "global"
    version_label: str
    actor_id: str
    diff: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChangeHistoryTracker:
    """Tracks change timelines and calculates state diffs across platform configuration and policy updates."""

    def __init__(self) -> None:
        self._history: List[ChangeRecord] = []

    def record_change(
        self,
        category: str,
        target_id: str,
        version_label: str,
        actor_id: str,
        tenant_id: str = "global",
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None,
    ) -> ChangeRecord:
        """Compute state diff and record timeline entry."""
        diff = self.compute_diff(previous_state or {}, new_state or {})
        rec = ChangeRecord(
            category=category,
            target_id=target_id,
            version_label=version_label,
            actor_id=actor_id,
            tenant_id=tenant_id,
            diff=diff,
        )
        self._history.append(rec)
        logger.info(f"[CHANGE HISTORY] Recorded {category} change on '{target_id}' (version: {version_label})")
        return rec

    @staticmethod
    def compute_diff(old_dict: Dict[str, Any], new_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Compute added, modified, and removed key-value diffs."""
        diff: Dict[str, Any] = {"added": {}, "modified": {}, "removed": {}}
        all_keys = set(old_dict.keys()).union(set(new_dict.keys()))

        for k in all_keys:
            if k not in old_dict:
                diff["added"][k] = new_dict[k]
            elif k not in new_dict:
                diff["removed"][k] = old_dict[k]
            elif old_dict[k] != new_dict[k]:
                diff["modified"][k] = {"before": old_dict[k], "after": new_dict[k]}

        return diff

    def get_timeline(self, target_id: Optional[str] = None, tenant_id: Optional[str] = None) -> List[ChangeRecord]:
        res = list(self._history)
        if target_id:
            res = [r for r in res if r.target_id == target_id]
        if tenant_id:
            res = [r for r in res if r.tenant_id in (tenant_id, "global")]
        return res
