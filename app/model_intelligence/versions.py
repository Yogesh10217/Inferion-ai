"""Model Version Intelligence (Phase 5.44)."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException

logger = logging.getLogger(__name__)


class VersionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    CANDIDATE = "CANDIDATE"
    RETIRED = "RETIRED"


class VersionCompatibility(str, Enum):
    COMPATIBLE = "COMPATIBLE"
    BREAKING_CHANGES = "BREAKING_CHANGES"
    UNKNOWN = "UNKNOWN"


class ModelVersion(BaseModel):
    version_id: str
    model_id: str
    tenant_id: str
    version_tag: str
    status: VersionStatus = VersionStatus.ACTIVE
    compatibility: VersionCompatibility = VersionCompatibility.COMPATIBLE
    release_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VersionComparison(BaseModel):
    base_version_tag: str
    target_version_tag: str
    latency_delta_ms: float = 0.0
    accuracy_delta: float = 0.0
    cost_delta_percentage: float = 0.0
    breaking_api_changes: List[str] = Field(default_factory=list)
    recommendation: str = "PROCEED"


class VersionAssessment(BaseModel):
    assessment_id: str
    model_id: str
    tenant_id: str
    current_version: str
    target_version: str
    risk_level: str = "LOW"
    comparison: VersionComparison
    assessment_notes: str = ""
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelVersionManager:
    """Read-only model version intelligence manager."""

    def __init__(self) -> None:
        self._versions: Dict[str, List[ModelVersion]] = {}

    def add_version(self, version: ModelVersion) -> ModelVersion:
        if version.model_id not in self._versions:
            self._versions[version.model_id] = []
        self._versions[version.model_id].append(version)
        return version

    def get_versions(self, model_id: str, tenant_id: str) -> List[ModelVersion]:
        vers = self._versions.get(model_id, [])
        for v in vers:
            if v.tenant_id != tenant_id:
                raise CrossTenantModelIntelligenceException()
        return vers

    def compare_versions(
        self,
        model_id: str,
        base_version_tag: str,
        target_version_tag: str,
        tenant_id: str,
        latency_delta_ms: float = 0.0,
        accuracy_delta: float = 0.0,
        breaking_changes: Optional[List[str]] = None,
    ) -> VersionAssessment:
        vers = self.get_versions(model_id, tenant_id)
        breaking = breaking_changes or []
        rec = "PROCEED" if not breaking and accuracy_delta >= 0 else "REQUIRE_APPROVAL"
        risk = "HIGH" if breaking or accuracy_delta < -0.05 else ("MEDIUM" if accuracy_delta < 0 else "LOW")

        comp = VersionComparison(
            base_version_tag=base_version_tag,
            target_version_tag=target_version_tag,
            latency_delta_ms=latency_delta_ms,
            accuracy_delta=accuracy_delta,
            breaking_api_changes=breaking,
            recommendation=rec,
        )

        return VersionAssessment(
            assessment_id=f"ver-assess-{uuid.uuid4().hex[:8]}",
            model_id=model_id,
            tenant_id=tenant_id,
            current_version=base_version_tag,
            target_version=target_version_tag,
            risk_level=risk,
            comparison=comp,
            assessment_notes=f"Comparison between {base_version_tag} and {target_version_tag}",
        )
