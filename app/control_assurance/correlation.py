"""Cross-Control and Cross-Platform Correlation Subsystem (Phase 5.38)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.control_assurance.exceptions import CrossTenantControlAssuranceAccessException


class ControlCorrelationType(str, Enum):
    COMMON_CAUSE = "COMMON_CAUSE"
    DEPENDENCY = "DEPENDENCY"
    CASCADE = "CASCADE"
    CORRELATED_FAILURE = "CORRELATED_FAILURE"
    DUPLICATE_FINDING = "DUPLICATE_FINDING"
    DOWNSTREAM_IMPACT = "DOWNSTREAM_IMPACT"


class CorrelationConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ControlCorrelation(BaseModel):
    correlation_id: str = Field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    primary_control_id: str
    related_control_id: str
    correlation_type: ControlCorrelationType = ControlCorrelationType.COMMON_CAUSE
    confidence: CorrelationConfidence = CorrelationConfidence.HIGH
    source_event_ids: List[str] = Field(default_factory=list)
    description: str = ""


class ControlCorrelationGroup(BaseModel):
    group_id: str = Field(default_factory=lambda: f"cgroup_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    root_cause_control_id: str
    correlated_control_ids: List[str] = Field(default_factory=list)
    correlations: List[ControlCorrelation] = Field(default_factory=list)


class ControlCorrelationManager:
    """Correlates cross-platform control findings and signals."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._correlations: Dict[str, ControlCorrelation] = {}
        self._groups: Dict[str, ControlCorrelationGroup] = {}

    def correlate_controls(
        self,
        tenant_id: str,
        primary_control_id: str,
        related_control_id: str,
        correlation_type: ControlCorrelationType = ControlCorrelationType.COMMON_CAUSE,
        source_event_ids: Optional[List[str]] = None,
    ) -> ControlCorrelation:
        corr = ControlCorrelation(
            tenant_id=tenant_id,
            primary_control_id=primary_control_id,
            related_control_id=related_control_id,
            correlation_type=correlation_type,
            source_event_ids=source_event_ids or [],
        )
        self._correlations[corr.correlation_id] = corr

        # Group management
        grp = self._groups.get(primary_control_id)
        if not grp:
            grp = ControlCorrelationGroup(
                tenant_id=tenant_id,
                root_cause_control_id=primary_control_id,
            )
            self._groups[primary_control_id] = grp
        grp.correlated_control_ids.append(related_control_id)
        grp.correlations.append(corr)

        return corr
