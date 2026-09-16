"""Multi-Dimensional Trade-Off Analysis Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TradeoffDimension(str, Enum):
    COST = "COST"
    VALUE = "VALUE"
    RISK = "RISK"
    TRUST = "TRUST"
    PERFORMANCE = "PERFORMANCE"
    RESILIENCE = "RESILIENCE"
    SECURITY = "SECURITY"
    COMPLIANCE = "COMPLIANCE"
    DATA_QUALITY = "DATA_QUALITY"
    TIME_TO_VALUE = "TIME_TO_VALUE"
    STRATEGIC_ALIGNMENT = "STRATEGIC_ALIGNMENT"
    OPERATIONAL_COMPLEXITY = "OPERATIONAL_COMPLEXITY"


class TradeoffSeverity(str, Enum):
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"


class Tradeoff(BaseModel):
    dimension: TradeoffDimension
    gain_description: str
    sacrifice_description: str
    severity: TradeoffSeverity = TradeoffSeverity.MODERATE
    is_negative_impact: bool = True


class TradeoffAnalysis(BaseModel):
    analysis_id: str = Field(default_factory=lambda: f"tradeoff_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    context_id: str
    alternative_id: str
    tradeoffs: List[Tradeoff] = Field(default_factory=list)
    has_major_negative_impact: bool = False
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TradeoffAnalyzer:
    """Surfaces explicit trade-offs and prevents masking negative impacts."""

    def analyze_tradeoffs(
        self,
        tenant_id: str,
        context_id: str,
        alternative_id: str,
        tradeoffs: Optional[List[Tradeoff]] = None,
    ) -> TradeoffAnalysis:
        items = tradeoffs if tradeoffs is not None else [
            Tradeoff(
                dimension=TradeoffDimension.OPERATIONAL_COMPLEXITY,
                gain_description="Scalability",
                sacrifice_description="Transition complexity",
                severity=TradeoffSeverity.MODERATE,
            )
        ]
        has_major = any(
            t.severity in (TradeoffSeverity.MAJOR, TradeoffSeverity.CRITICAL) and t.is_negative_impact
            for t in items
        )
        return TradeoffAnalysis(
            tenant_id=tenant_id,
            context_id=context_id,
            alternative_id=alternative_id,
            tradeoffs=items,
            has_major_negative_impact=has_major,
        )
