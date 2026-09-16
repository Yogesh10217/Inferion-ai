"""Data impact intelligence (Phase 5.43)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field


class DataImpactDimension(str, Enum):
    DOWNSTREAM = "DOWNSTREAM"
    MODEL = "MODEL"
    BUSINESS = "BUSINESS"
    OPERATIONAL = "OPERATIONAL"
    COMPLIANCE = "COMPLIANCE"
    SECURITY = "SECURITY"


class DataImpactAssessment(BaseModel):
    assessment_id: str
    dataset_id: str
    tenant_id: str
    overall_impact_score: float  # 0.0 - 100.0
    impacted_dimensions: Dict[DataImpactDimension, float]
    impacted_models_count: int = 0
    impacted_pipelines_count: int = 0
    impacted_agents_count: int = 0
    summary: str
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataImpactManager:
    """Evaluates multi-dimensional impact of data anomalies, quality issues, or schema changes."""

    def evaluate_impact(
        self,
        dataset_id: str,
        tenant_id: str,
        downstream_nodes_count: int = 1,
        is_sensitive: bool = False,
    ) -> DataImpactAssessment:
        aid = f"dia-{uuid.uuid4().hex[:8]}"

        ds_impact = min(100.0, downstream_nodes_count * 15.0)
        model_impact = min(100.0, downstream_nodes_count * 20.0)
        biz_impact = min(100.0, downstream_nodes_count * 10.0)
        op_impact = min(100.0, downstream_nodes_count * 12.0)
        comp_impact = 80.0 if is_sensitive else 20.0
        sec_impact = 90.0 if is_sensitive else 15.0

        dims = {
            DataImpactDimension.DOWNSTREAM: ds_impact,
            DataImpactDimension.MODEL: model_impact,
            DataImpactDimension.BUSINESS: biz_impact,
            DataImpactDimension.OPERATIONAL: op_impact,
            DataImpactDimension.COMPLIANCE: comp_impact,
            DataImpactDimension.SECURITY: sec_impact,
        }

        overall = round(sum(dims.values()) / len(dims), 2)

        return DataImpactAssessment(
            assessment_id=aid,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            overall_impact_score=overall,
            impacted_dimensions=dims,
            impacted_models_count=max(1, downstream_nodes_count // 2),
            impacted_pipelines_count=max(1, downstream_nodes_count),
            impacted_agents_count=max(0, downstream_nodes_count // 3),
            summary=f"Impact assessment for dataset {dataset_id}: score={overall:.1f}, downstream_nodes={downstream_nodes_count}",
        )
