"""Lifecycle Monitoring Integration Subsystem (Phase 5.33)."""

import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.reliability_platform.manager import ReliabilityPlatformManager


class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"


class AIAssetHealth(BaseModel):
    asset_id: str
    tenant_id: str
    status: HealthStatus = HealthStatus.HEALTHY
    uptime_percentage: float = 99.9


class ModelHealth(AIAssetHealth):
    latency_p95_ms: float = 120.0
    error_rate: float = 0.001


class AgentHealth(AIAssetHealth):
    active_runs: int = 5
    loop_detection_count: int = 0


class LifecycleSignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: f"lsig_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    asset_id: str
    signal_type: str
    severity: str = "MEDIUM"


class LifecycleMonitoringRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: f"mrule_{uuid.uuid4().hex[:12]}")
    name: str
    threshold: float = 95.0


class LifecycleMonitoringManager:
    """Integrates runtime operational health signals with ReliabilityPlatformManager."""

    def __init__(self, reliability_manager: Optional[ReliabilityPlatformManager] = None) -> None:
        self.reliability_manager = reliability_manager or ReliabilityPlatformManager()

    def get_asset_health(self, tenant_id: str, asset_id: str) -> AIAssetHealth:
        return AIAssetHealth(
            asset_id=asset_id, tenant_id=tenant_id, status=HealthStatus.HEALTHY, uptime_percentage=99.95
        )
