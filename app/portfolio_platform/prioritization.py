"""Deterministic Portfolio Prioritization Engine Subsystem."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.portfolio_platform.business_cases import BusinessCase
from app.portfolio_platform.initiatives import AIInitiative


class PrioritizationDimension(str, Enum):
    STRATEGIC_ALIGNMENT = "STRATEGIC_ALIGNMENT"
    BUSINESS_VALUE = "BUSINESS_VALUE"
    EXPECTED_ROI = "EXPECTED_ROI"
    COST = "COST"
    TIME_TO_VALUE = "TIME_TO_VALUE"
    RISK = "RISK"
    COMPLIANCE_STATUS = "COMPLIANCE_STATUS"
    ARCHITECTURE_TRUST = "ARCHITECTURE_TRUST"
    DATA_TRUST = "DATA_TRUST"
    TECHNICAL_COMPLEXITY = "TECHNICAL_COMPLEXITY"
    DEPENDENCY_RISK = "DEPENDENCY_RISK"
    OPERATIONAL_READINESS = "OPERATIONAL_READINESS"


class PrioritizationWeight(BaseModel):
    dimension: PrioritizationDimension
    weight: float = 1.0


class InitiativeScore(BaseModel):
    initiative_id: str
    tenant_id: str
    total_score: float
    rank: int = 1
    dimension_scores: Dict[PrioritizationDimension, float] = Field(default_factory=dict)
    explanation: str = ""


class PrioritizationResult(BaseModel):
    result_id: str = Field(default_factory=lambda: f"prio_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    ranked_initiatives: List[InitiativeScore] = Field(default_factory=list)
    snapshot_fingerprint: str
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PrioritizationEngine:
    """Calculates deterministic weighted prioritization scores across initiatives."""

    def __init__(self) -> None:
        self.default_weights: Dict[PrioritizationDimension, float] = {
            PrioritizationDimension.STRATEGIC_ALIGNMENT: 0.15,
            PrioritizationDimension.BUSINESS_VALUE: 0.15,
            PrioritizationDimension.EXPECTED_ROI: 0.15,
            PrioritizationDimension.COST: 0.05,
            PrioritizationDimension.TIME_TO_VALUE: 0.05,
            PrioritizationDimension.RISK: 0.05,
            PrioritizationDimension.COMPLIANCE_STATUS: 0.10,
            PrioritizationDimension.ARCHITECTURE_TRUST: 0.10,
            PrioritizationDimension.DATA_TRUST: 0.10,
            PrioritizationDimension.TECHNICAL_COMPLEXITY: 0.05,
            PrioritizationDimension.DEPENDENCY_RISK: 0.025,
            PrioritizationDimension.OPERATIONAL_READINESS: 0.025,
        }

    def score_initiatives(
        self,
        tenant_id: str,
        initiatives: List[AIInitiative],
        business_cases: List[BusinessCase],
        custom_weights: Optional[Dict[PrioritizationDimension, float]] = None,
    ) -> PrioritizationResult:
        weights = custom_weights or self.default_weights
        bc_map = {bc.initiative_id: bc for bc in business_cases}

        scores: List[InitiativeScore] = []
        for init in initiatives:
            bc = bc_map.get(init.initiative_id)

            dim_scores = {
                PrioritizationDimension.STRATEGIC_ALIGNMENT: 90.0,
                PrioritizationDimension.BUSINESS_VALUE: (
                    85.0 if not bc else min(100.0, bc.roi_projection.net_present_value_usd / 1000.0)
                ),
                PrioritizationDimension.EXPECTED_ROI: (
                    80.0 if not bc else min(100.0, bc.roi_projection.estimated_roi_percentage)
                ),
                PrioritizationDimension.COST: (
                    75.0 if not bc else max(0.0, 100.0 - (bc.costs.implementation_cost_usd / 2000.0))
                ),
                PrioritizationDimension.TIME_TO_VALUE: 80.0,
                PrioritizationDimension.RISK: 85.0 if not bc else max(0.0, 100.0 - bc.risk_score),
                PrioritizationDimension.COMPLIANCE_STATUS: 90.0 if not bc else bc.compliance_score,
                PrioritizationDimension.ARCHITECTURE_TRUST: 90.0 if not bc else bc.architecture_trust_score,
                PrioritizationDimension.DATA_TRUST: 95.0 if not bc else bc.data_trust_score,
                PrioritizationDimension.TECHNICAL_COMPLEXITY: 80.0,
                PrioritizationDimension.DEPENDENCY_RISK: 85.0,
                PrioritizationDimension.OPERATIONAL_READINESS: 90.0,
            }

            total_weight = sum(weights.values())
            weighted_score = sum(dim_scores[dim] * weights.get(dim, 0.0) for dim in dim_scores) / max(
                0.001, total_weight
            )

            scores.append(
                InitiativeScore(
                    initiative_id=init.initiative_id,
                    tenant_id=tenant_id,
                    total_score=weighted_score,
                    dimension_scores=dim_scores,
                    explanation=f"Weighted score computed as {weighted_score:.2f}.",
                )
            )

        # Deterministic sorting: higher total score first, then initiative_id for stability
        scores.sort(key=lambda x: (-x.total_score, x.initiative_id))

        # Assign ranks
        for idx, score in enumerate(scores):
            score.rank = idx + 1

        # Calculate SHA-256 fingerprint for snapshot reproducibility
        canonical_str = json.dumps(
            {
                "tenant_id": tenant_id,
                "scores": [{"id": s.initiative_id, "score": s.total_score, "rank": s.rank} for s in scores],
            },
            sort_keys=True,
        )
        fingerprint = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

        return PrioritizationResult(
            tenant_id=tenant_id,
            ranked_initiatives=scores,
            snapshot_fingerprint=fingerprint,
        )
