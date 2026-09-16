"""Root Cause Hypothesis Subsystem (Phase 5.31)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantIsolationValidator


class HypothesisStatus(str, Enum):
    GENERATED = "GENERATED"
    INVESTIGATING = "INVESTIGATING"
    SUPPORTED = "SUPPORTED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class RootCauseHypothesis(BaseModel):
    hypothesis_id: str = Field(default_factory=lambda: f"rch_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    incident_id: str
    description: str
    probability: float = 0.80
    status: HypothesisStatus = HypothesisStatus.GENERATED
    supporting_evidence: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RootCauseManager:
    """Manages and evaluates competing root cause hypotheses for incidents."""

    def __init__(self) -> None:
        self._hypotheses: Dict[str, RootCauseHypothesis] = {}

    def create_hypothesis(
        self,
        tenant_id: str,
        incident_id: str,
        description: str,
        probability: float = 0.80,
    ) -> RootCauseHypothesis:
        rch = RootCauseHypothesis(
            tenant_id=tenant_id,
            incident_id=incident_id,
            description=description,
            probability=probability,
        )
        self._hypotheses[rch.hypothesis_id] = rch
        return rch

    def update_hypothesis_status(
        self,
        hypothesis_id: str,
        tenant_id: str,
        status: HypothesisStatus,
    ) -> RootCauseHypothesis:
        rch = self._hypotheses.get(hypothesis_id)
        if rch:
            TenantIsolationValidator.validate_tenant_access(tenant_id, rch.tenant_id)
            rch.status = status
            return rch
        raise KeyError(f"Hypothesis {hypothesis_id} not found")
