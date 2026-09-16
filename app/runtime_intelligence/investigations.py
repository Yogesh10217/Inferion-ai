"""Runtime Investigation Manager for Phase 5.57 Runtime Intelligence."""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List

logger = logging.getLogger(__name__)


@dataclass
class RuntimeInvestigation:
    investigation_id: str
    tenant_id: str
    target_resource_id: str
    status: str  # OPEN, INVESTIGATING, CONCLUDED, CLOSED
    findings: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class RuntimeInvestigationManager:
    """Manages runtime investigations, evidence collection, and state snapshotting."""

    def __init__(self) -> None:
        self._investigations: Dict[str, RuntimeInvestigation] = {}

    def create_investigation(self, tenant_id: str, target_resource_id: str) -> RuntimeInvestigation:
        inv = RuntimeInvestigation(
            investigation_id=f"inv_{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            target_resource_id=target_resource_id,
            status="OPEN",
        )
        self._investigations[inv.investigation_id] = inv
        logger.info(f"Created runtime investigation '{inv.investigation_id}' for '{target_resource_id}'")
        return inv

    def conclude_investigation(
        self, tenant_id: str, investigation_id: str, findings: List[str], evidence_ids: List[str]
    ) -> RuntimeInvestigation:
        inv = self._investigations.get(investigation_id)
        if inv and inv.tenant_id == tenant_id:
            inv.status = "CONCLUDED"
            inv.findings = findings
            inv.evidence_ids = evidence_ids
            logger.info(f"Concluded investigation '{investigation_id}' with {len(findings)} findings")
        return inv
