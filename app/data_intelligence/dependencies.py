"""Dataset & pipeline dependency intelligence (Phase 5.43)."""

import uuid
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import CrossTenantDataIntelligenceException


class DependencyType(str, Enum):
    DATASET_TO_DATASET = "DATASET_TO_DATASET"
    PIPELINE_TO_DATASET = "PIPELINE_TO_DATASET"
    DATASET_TO_MODEL = "DATASET_TO_MODEL"
    MODEL_TO_AGENT = "MODEL_TO_AGENT"
    AGENT_TO_KNOWLEDGE = "AGENT_TO_KNOWLEDGE"


class DependencyImpact(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DataDependency(BaseModel):
    dependency_id: str
    source_asset_id: str
    target_asset_id: str
    dependency_type: DependencyType
    tenant_id: str
    impact_level: DependencyImpact = DependencyImpact.MEDIUM
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DependencyAssessment(BaseModel):
    assessment_id: str
    tenant_id: str
    root_asset_id: str
    dependencies: List[DataDependency] = Field(default_factory=list)
    impact_score: float = 0.0
    summary: str


class DataDependencyManager:
    """Manages dependencies across datasets, pipelines, models, agents, and knowledge bases."""

    def __init__(self) -> None:
        self._deps: Dict[str, DataDependency] = {}

    def register_dependency(
        self,
        source_asset_id: str,
        target_asset_id: str,
        dependency_type: DependencyType,
        tenant_id: str,
        impact_level: DependencyImpact = DependencyImpact.MEDIUM,
        dependency_id: Optional[str] = None,
    ) -> DataDependency:
        did = dependency_id or f"dep-{uuid.uuid4().hex[:8]}"
        dep = DataDependency(
            dependency_id=did,
            source_asset_id=source_asset_id,
            target_asset_id=target_asset_id,
            dependency_type=dependency_type,
            tenant_id=tenant_id,
            impact_level=impact_level,
        )
        self._deps[did] = dep
        return dep

    def list_dependencies(self, tenant_id: str, source_asset_id: Optional[str] = None) -> List[DataDependency]:
        deps = [d for d in self._deps.values() if d.tenant_id == tenant_id]
        if source_asset_id:
            deps = [d for d in deps if d.source_asset_id == source_asset_id]
        return deps

    def evaluate_dependencies(self, root_asset_id: str, tenant_id: str) -> DependencyAssessment:
        deps = self.list_dependencies(tenant_id, source_asset_id=root_asset_id)
        aid = f"dep-ass-{uuid.uuid4().hex[:8]}"
        impact = len(deps) * 2.0

        return DependencyAssessment(
            assessment_id=aid,
            tenant_id=tenant_id,
            root_asset_id=root_asset_id,
            dependencies=deps,
            impact_score=round(impact, 2),
            summary=f"Root asset {root_asset_id} has {len(deps)} direct dependencies.",
        )
