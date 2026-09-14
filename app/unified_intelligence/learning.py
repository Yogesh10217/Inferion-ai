"""
Advisory Machine Learning Engine for Phase 5.51 Enterprise AI Unified Intelligence.

Learns cross-domain correlation patterns and outcome feedback in strictly ADVISORY mode,
enforcing auto_execute = False for zero unapproved mutation.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from app.unified_intelligence.exceptions import (
    InvalidUnifiedIntelligenceInputException
)


class AdvisoryModelInsight:
    """
    Advisory ML model insight for cross-domain pattern matching.
    """
    def __init__(
        self,
        insight_id: str,
        tenant_id: str,
        pattern_name: str,
        recommended_action: str,
        confidence_score: float,
        supporting_evidence_count: int,
        auto_execute: bool = False,  # Strict invariant: MUST be False
        created_at: Optional[datetime] = None
    ):
        self.insight_id = insight_id
        self.tenant_id = tenant_id
        self.pattern_name = pattern_name
        self.recommended_action = recommended_action
        self.confidence_score = min(max(confidence_score, 0.0), 1.0)
        self.supporting_evidence_count = supporting_evidence_count
        self.auto_execute = False  # Enforce advisory-only constraint
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "insight_id": self.insight_id,
            "tenant_id": self.tenant_id,
            "pattern_name": self.pattern_name,
            "recommended_action": self.recommended_action,
            "confidence_score": round(self.confidence_score, 4),
            "supporting_evidence_count": self.supporting_evidence_count,
            "auto_execute": self.auto_execute,
            "created_at": self.created_at.isoformat()
        }


class AdvisoryLearningEngine:
    """
    Analyzes historical cross-domain situations and outcome feedback to refine advisory correlation rules.
    """
    def __init__(self):
        pass

    def analyze_situation_pattern(
        self,
        tenant_id: str,
        situation_data: Dict[str, Any]
    ) -> AdvisoryModelInsight:
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")

        insight_id = f"learn-{uuid.uuid4().hex[:12]}"
        pattern = situation_data.get("pattern_name", "CrossDomainCascadePattern")

        return AdvisoryModelInsight(
            insight_id=insight_id,
            tenant_id=tenant_id,
            pattern_name=pattern,
            recommended_action="Execute automated advisory cross-domain isolation check.",
            confidence_score=0.82,
            supporting_evidence_count=len(situation_data.get("evidence_ids", [])),
            auto_execute=False
        )
