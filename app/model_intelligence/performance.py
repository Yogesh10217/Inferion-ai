"""Model Performance Intelligence (Phase 5.44)."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException, ModelPerformanceNotFoundException

logger = logging.getLogger(__name__)


class PerformanceDimension(str, Enum):
    LATENCY = "LATENCY"
    THROUGHPUT = "THROUGHPUT"
    ERROR_RATE = "ERROR_RATE"
    AVAILABILITY = "AVAILABILITY"
    RESPONSE_QUALITY = "RESPONSE_QUALITY"
    TOKEN_EFFICIENCY = "TOKEN_EFFICIENCY"
    INFERENCE_RELIABILITY = "INFERENCE_RELIABILITY"


class PerformanceTrend(str, Enum):
    STABLE = "STABLE"
    DEGRADING = "DEGRADING"
    IMPROVING = "IMPROVING"


class PerformanceMetric(BaseModel):
    dimension: PerformanceDimension
    value: float
    unit: str
    threshold: Optional[float] = None
    is_anomaly: bool = False


class PerformanceAssessment(BaseModel):
    assessment_id: str
    model_id: str
    tenant_id: str
    trend: PerformanceTrend = PerformanceTrend.STABLE
    metrics: List[PerformanceMetric] = Field(default_factory=list)
    degraded: bool = False
    notes: str = "Performance operating within normal parameters."
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelPerformance(BaseModel):
    performance_id: str
    model_id: str
    tenant_id: str
    latency_p95_ms: float = 120.0
    throughput_rps: float = 45.0
    error_rate_percentage: float = 0.01
    availability_percentage: float = 99.9
    assessment: PerformanceAssessment
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelPerformanceManager:
    """Manages model performance tracking and degradation analysis."""

    def __init__(self) -> None:
        self._performance_records: Dict[str, List[ModelPerformance]] = {}

    def record_performance(
        self,
        model_id: str,
        tenant_id: str,
        latency_p95_ms: float = 120.0,
        throughput_rps: float = 45.0,
        error_rate_percentage: float = 0.01,
        availability_percentage: float = 99.9,
    ) -> ModelPerformance:
        p_id = f"perf-{uuid.uuid4().hex[:8]}"

        degraded = latency_p95_ms > 500.0 or error_rate_percentage > 5.0 or availability_percentage < 95.0
        trend = PerformanceTrend.DEGRADING if degraded else PerformanceTrend.STABLE

        metrics = [
            PerformanceMetric(dimension=PerformanceDimension.LATENCY, value=latency_p95_ms, unit="ms", threshold=500.0, is_anomaly=latency_p95_ms > 500.0),
            PerformanceMetric(dimension=PerformanceDimension.THROUGHPUT, value=throughput_rps, unit="rps"),
            PerformanceMetric(dimension=PerformanceDimension.ERROR_RATE, value=error_rate_percentage, unit="percentage", threshold=5.0, is_anomaly=error_rate_percentage > 5.0),
            PerformanceMetric(dimension=PerformanceDimension.AVAILABILITY, value=availability_percentage, unit="percentage", threshold=99.0, is_anomaly=availability_percentage < 99.0),
        ]

        assessment = PerformanceAssessment(
            assessment_id=f"passess-{uuid.uuid4().hex[:6]}",
            model_id=model_id,
            tenant_id=tenant_id,
            trend=trend,
            metrics=metrics,
            degraded=degraded,
            notes="Degradation detected" if degraded else "Performance healthy",
        )

        record = ModelPerformance(
            performance_id=p_id,
            model_id=model_id,
            tenant_id=tenant_id,
            latency_p95_ms=latency_p95_ms,
            throughput_rps=throughput_rps,
            error_rate_percentage=error_rate_percentage,
            availability_percentage=availability_percentage,
            assessment=assessment,
        )

        if model_id not in self._performance_records:
            self._performance_records[model_id] = []
        self._performance_records[model_id].append(record)
        return record

    def get_latest_performance(self, model_id: str, tenant_id: str) -> ModelPerformance:
        recs = self._performance_records.get(model_id, [])
        if not recs:
            raise ModelPerformanceNotFoundException(f"No performance record for model '{model_id}'.")
        latest = recs[-1]
        if latest.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return latest

    def list_performance_history(self, model_id: str, tenant_id: str) -> List[ModelPerformance]:
        recs = self._performance_records.get(model_id, [])
        for r in recs:
            if r.tenant_id != tenant_id:
                raise CrossTenantModelIntelligenceException()
        return recs
