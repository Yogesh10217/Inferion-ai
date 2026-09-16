"""Performance intelligence analyzing latency, throughput, error rates, degradation, and resource efficiency."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field


class PerformanceTrend(str, Enum):
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"


class PerformanceMetrics(BaseModel):
    metric_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    latency_p50_ms: float = 20.0
    latency_p95_ms: float = 80.0
    latency_p99_ms: float = 150.0
    throughput_tps: float = 250.0
    error_rate: float = 0.001
    resource_efficiency_score: float = 0.85
    trend: PerformanceTrend = PerformanceTrend.STABLE
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationsPerformanceEngine:
    """Evaluates service performance indicators and detects degradation trends."""

    def __init__(self) -> None:
        self._metrics: Dict[str, Dict[str, PerformanceMetrics]] = {}  # tenant_id -> {service_id: metrics}

    def analyze_performance(
        self,
        tenant_id: str,
        service_id: str,
        latency_p50: float = 20.0,
        latency_p95: float = 80.0,
        latency_p99: float = 150.0,
        throughput_tps: float = 250.0,
        error_rate: float = 0.001,
        efficiency_score: float = 0.85,
    ) -> PerformanceMetrics:
        if error_rate > 0.05 or latency_p99 > 500.0:
            trend = PerformanceTrend.CRITICAL
        elif error_rate > 0.01 or latency_p99 > 250.0:
            trend = PerformanceTrend.DEGRADED
        else:
            trend = PerformanceTrend.STABLE

        pm = PerformanceMetrics(
            tenant_id=tenant_id,
            service_id=service_id,
            latency_p50_ms=latency_p50,
            latency_p95_ms=latency_p95,
            latency_p99_ms=latency_p99,
            throughput_tps=throughput_tps,
            error_rate=error_rate,
            resource_efficiency_score=efficiency_score,
            trend=trend,
        )

        if tenant_id not in self._metrics:
            self._metrics[tenant_id] = {}
        self._metrics[tenant_id][service_id] = pm
        return pm
