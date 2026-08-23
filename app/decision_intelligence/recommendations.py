"""Recommendation Generation Engine Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.decision_intelligence.tradeoffs import TradeoffAnalysis
from app.decision_intelligence.constraints import ConstraintResult


class RecommendationType(str, Enum):
    PROCEED = "PROCEED"
    PROCEED_WITH_CONDITIONS = "PROCEED_WITH_CONDITIONS"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    DEFER = "DEFER"
    MODIFY = "MODIFY"
    REJECT = "REJECT"
    ESCALATE = "ESCALATE"


class RecommendationConfidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class RecommendationStatus(str, Enum):
    PROPOSED = "PROPOSED"
    ACTIVE = "ACTIVE"
    STALE = "STALE"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class DecisionRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    context_id: str
    recommendation_type: RecommendationType = RecommendationType.PROCEED
    confidence: RecommendationConfidence = RecommendationConfidence.HIGH
    status: RecommendationStatus = RecommendationStatus.PROPOSED
    rationale: str
    recommended_alternative_id: Optional[str] = None
    evidence_references: List[str] = Field(default_factory=list)
    tradeoff_summary: Optional[TradeoffAnalysis] = None
    requires_approval: bool = False
    recommended_next_action: str = "PROCEED_TO_GOVERNANCE"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RecommendationEngine:
    """Generates structured decision recommendations with supporting rationale."""

    def generate_recommendation(
        self,
        tenant_id: str,
        context_id: str,
        constraint_result: ConstraintResult,
        tradeoff_analysis: Optional[TradeoffAnalysis] = None,
        risk_score: float = 20.0,
        trust_score: float = 90.0,
        alternative_id: Optional[str] = None,
    ) -> DecisionRecommendation:
        # Check hard constraint block first!
        if not constraint_result.passed_all:
            return DecisionRecommendation(
                tenant_id=tenant_id,
                context_id=context_id,
                recommendation_type=RecommendationType.REJECT,
                confidence=RecommendationConfidence.HIGH,
                status=RecommendationStatus.PROPOSED,
                rationale=f"Hard constraint violation detected ({constraint_result.hard_violations_count} violation(s)). Recommendation REJECTED.",
                requires_approval=True,
                recommended_next_action="REVISE_CONSTRAINTS_OR_ALTERNATIVE",
            )

        if risk_score > 70.0 or trust_score < 70.0:
            rec_type = RecommendationType.REQUIRE_APPROVAL
            req_appr = True
            rat = f"High Risk ({risk_score}) or Low Trust ({trust_score}) detected. Human approval required."
        elif tradeoff_analysis and tradeoff_analysis.has_major_negative_impact:
            rec_type = RecommendationType.PROCEED_WITH_CONDITIONS
            req_appr = False
            rat = "Proceed with conditions due to major negative trade-offs identified."
        else:
            rec_type = RecommendationType.PROCEED
            req_appr = False
            rat = "All constraints passed, risk low, trust high. Proceed with decision."

        return DecisionRecommendation(
            tenant_id=tenant_id,
            context_id=context_id,
            recommendation_type=rec_type,
            confidence=RecommendationConfidence.HIGH if trust_score >= 80 else RecommendationConfidence.MEDIUM,
            status=RecommendationStatus.PROPOSED,
            rationale=rat,
            recommended_alternative_id=alternative_id,
            tradeoff_summary=tradeoff_analysis,
            requires_approval=req_appr,
            recommended_next_action="SUBMIT_FOR_GOVERNANCE",
        )
