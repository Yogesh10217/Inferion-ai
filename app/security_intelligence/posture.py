"""Security Posture Management Subsystem (Phase 5.32)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.security_intelligence.exceptions import CrossTenantSecurityAccessException


class SecurityPostureBand(str, Enum):
    CRITICAL = "CRITICAL"  # <40
    HIGH_RISK = "HIGH_RISK"  # 40-59
    ELEVATED = "ELEVATED"  # 60-74
    MODERATE = "MODERATE"  # 75-89
    STRONG = "STRONG"  # 90-100


class SecurityPostureDimension(BaseModel):
    dimension_name: str
    score: float  # 0.0 to 100.0


class SecurityPosture(BaseModel):
    posture_id: str = Field(default_factory=lambda: f"post_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    overall_score: float  # 0.0 to 100.0
    band: SecurityPostureBand
    dimensions: List[SecurityPostureDimension] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityPostureManager:
    """Calculates deterministic security posture scores based on active threats and vulnerabilities."""

    def __init__(self) -> None:
        self._postures: Dict[str, SecurityPosture] = {}

    def calculate_posture(
        self,
        tenant_id: str,
        active_threats_count: int = 0,
        active_vulnerabilities_count: int = 0,
    ) -> SecurityPosture:
        threat_penalty = min(50.0, active_threats_count * 15.0)
        vuln_penalty = min(40.0, active_vulnerabilities_count * 10.0)

        overall = max(0.0, round(100.0 - threat_penalty - vuln_penalty, 2))

        if overall >= 90.0:
            band = SecurityPostureBand.STRONG
        elif overall >= 75.0:
            band = SecurityPostureBand.MODERATE
        elif overall >= 60.0:
            band = SecurityPostureBand.ELEVATED
        elif overall >= 40.0:
            band = SecurityPostureBand.HIGH_RISK
        else:
            band = SecurityPostureBand.CRITICAL

        dims = [
            SecurityPostureDimension(dimension_name="Threat Exposure", score=max(0.0, 100.0 - threat_penalty)),
            SecurityPostureDimension(dimension_name="Vulnerability Health", score=max(0.0, 100.0 - vuln_penalty)),
            SecurityPostureDimension(dimension_name="Identity Security", score=95.0),
            SecurityPostureDimension(dimension_name="Data Security", score=90.0),
            SecurityPostureDimension(dimension_name="AI Security", score=85.0),
        ]

        post = SecurityPosture(
            tenant_id=tenant_id,
            overall_score=overall,
            band=band,
            dimensions=dims,
        )
        self._postures[post.posture_id] = post
        return post

    def get_posture(self, posture_id: str, tenant_id: str) -> SecurityPosture:
        post = self._postures.get(posture_id)
        if not post:
            raise KeyError(f"Posture '{posture_id}' not found.")
        if tenant_id != "global" and post.tenant_id != "global" and tenant_id != post.tenant_id:
            raise CrossTenantSecurityAccessException(tenant_id, post.tenant_id)
        return post
