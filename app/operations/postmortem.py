"""Post-Incident Learning & Structured Postmortem Report Engine."""

from datetime import datetime, timezone
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.operations.incidents import Incident

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Postmortem(BaseModel):
    postmortem_id: str = Field(default_factory=lambda: f"pm_{uuid.uuid4().hex[:10]}")
    incident_id: str
    tenant_id: str = "global"

    summary: str = ""
    impact_summary: str = ""
    root_cause: str = ""
    contributing_factors: List[str] = Field(default_factory=list)
    detection_gaps: List[str] = Field(default_factory=list)

    corrective_actions: List[str] = Field(default_factory=list)
    preventive_actions: List[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=_now)


class PostmortemManager:
    """Generates structured postmortems for post-incident review and learning."""

    def __init__(self) -> None:
        self._postmortems: Dict[str, Postmortem] = {}

    def generate_postmortem(
        self,
        incident: Incident,
        root_cause_summary: str,
        corrective_actions: List[str],
        preventive_actions: List[str],
    ) -> Postmortem:
        pm = Postmortem(
            incident_id=incident.incident_id,
            tenant_id=incident.tenant_id,
            summary=f"Postmortem for '{incident.title}'",
            impact_summary=f"Incident severity {incident.severity.value} on resource {incident.primary_resource_id}",
            root_cause=root_cause_summary,
            corrective_actions=corrective_actions,
            preventive_actions=preventive_actions,
        )
        self._postmortems[pm.postmortem_id] = pm
        logger.info(f"[POSTMORTEM MANAGER] Generated postmortem '{pm.postmortem_id}' for incident '{incident.incident_id}'")
        return pm

    def list_postmortems(self, tenant_id: Optional[str] = None) -> List[Postmortem]:
        res = list(self._postmortems.values())
        if tenant_id:
            res = [p for p in res if p.tenant_id == tenant_id]
        return res
