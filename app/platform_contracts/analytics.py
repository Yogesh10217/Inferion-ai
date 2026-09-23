"""Shared Analytics Output Contract (Phase 5.30)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AnalyticsPeriod(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"


class AnalyticsDimension(BaseModel):
    dimension_name: str
    dimension_value: str


class AnalyticsMetric(BaseModel):
    metric_name: str
    metric_value: float
    dimensions: List[AnalyticsDimension] = Field(default_factory=list)


class PlatformInsight(BaseModel):
    insight_id: str = Field(default_factory=lambda: f"ins_{uuid.uuid4().hex[:12]}")
    title: str
    description: str
    impact_level: str = "MEDIUM"


class PlatformReport(BaseModel):
    report_id: str = Field(default_factory=lambda: f"rep_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    report_type: str
    period: AnalyticsPeriod = AnalyticsPeriod.DAILY
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metrics: List[AnalyticsMetric] = Field(default_factory=list)
    insights: List[PlatformInsight] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    fingerprint: Optional[str] = None
