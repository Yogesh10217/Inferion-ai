"""Requirement-to-Control Traceability & Coverage Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.compliance_platform.requirements import RequirementManager
from app.compliance_platform.controls import ControlManager


class CoverageStatus(str, Enum):
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"


class RequirementControlMapping(BaseModel):
    mapping_id: str = Field(default_factory=lambda: f"map_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    requirement_id: str
    control_id: str
    mapped_by: str = "system"
    mapped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ControlEvidenceRequirement(BaseModel):
    requirement_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    control_id: str
    evidence_type: str
    min_freshness_seconds: int = 86400  # 24h default


class ComplianceCoverage(BaseModel):
    tenant_id: str
    total_requirements_count: int
    mapped_requirements_count: int
    unmapped_requirements_count: int
    coverage_percentage: float
    status: CoverageStatus
    unmapped_requirement_ids: List[str] = Field(default_factory=list)
    controls_without_evidence: List[str] = Field(default_factory=list)


class MappingManager:
    """Manages requirement-to-control mappings and traceability gaps."""

    def __init__(self, requirement_manager: RequirementManager, control_manager: ControlManager) -> None:
        self.requirement_manager = requirement_manager
        self.control_manager = control_manager
        self._mappings: Dict[str, RequirementControlMapping] = {}

    def map_requirement_to_control(self, tenant_id: str, requirement_id: str, control_id: str) -> RequirementControlMapping:
        mapping = RequirementControlMapping(
            tenant_id=tenant_id,
            requirement_id=requirement_id,
            control_id=control_id,
        )
        self._mappings[mapping.mapping_id] = mapping
        return mapping

    def list_mappings_for_requirement(self, tenant_id: str, requirement_id: str) -> List[RequirementControlMapping]:
        return [m for m in self._mappings.values() if m.tenant_id == tenant_id and m.requirement_id == requirement_id]

    def evaluate_coverage(self, tenant_id: str) -> ComplianceCoverage:
        reqs = self.requirement_manager.list_requirements(tenant_id)
        mapped_req_ids = {m.requirement_id for m in self._mappings.values() if m.tenant_id == tenant_id}

        total_reqs = len(reqs)
        mapped_count = sum(1 for r in reqs if r.requirement_id in mapped_req_ids)
        unmapped_ids = [r.requirement_id for r in reqs if r.requirement_id not in mapped_req_ids]

        coverage_pct = (mapped_count / max(1, total_reqs)) * 100.0

        if coverage_pct >= 100.0:
            status = CoverageStatus.FULL
        elif coverage_pct >= 50.0:
            status = CoverageStatus.PARTIAL
        else:
            status = CoverageStatus.NONE

        return ComplianceCoverage(
            tenant_id=tenant_id,
            total_requirements_count=total_reqs,
            mapped_requirements_count=mapped_count,
            unmapped_requirements_count=len(unmapped_ids),
            coverage_percentage=coverage_pct,
            status=status,
            unmapped_requirement_ids=unmapped_ids,
        )
