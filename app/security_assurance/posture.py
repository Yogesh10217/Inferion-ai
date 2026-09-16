"""Security Posture Assessment & Scoring Engine."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from app.security_assurance.asset_inventory import SecurityAssetInventory


class SecurityPostureGrade(str, Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    NEEDS_IMPROVEMENT = "NEEDS_IMPROVEMENT"
    CRITICAL_RISK = "CRITICAL_RISK"


class SecurityPostureAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"posture-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    asset_count: int
    score: float  # 0.0 to 100.0
    grade: SecurityPostureGrade
    open_vulnerabilities_count: int = 0
    misconfigurations_count: int = 0
    threats_count: int = 0
    findings: List[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityPostureEngine:
    """Evaluates security posture score across all registered assets in a tenant."""

    def __init__(self, asset_inventory: SecurityAssetInventory) -> None:
        self.asset_inventory = asset_inventory

    def evaluate_posture(
        self,
        tenant_id: str,
        open_vulnerabilities: int = 0,
        misconfigurations: int = 0,
        active_threats: int = 0,
    ) -> SecurityPostureAssessment:
        assets = self.asset_inventory.list_assets(tenant_id)
        asset_count = len(assets)

        deductions = (open_vulnerabilities * 5.0) + (misconfigurations * 3.0) + (active_threats * 10.0)
        score = max(0.0, min(100.0, 100.0 - deductions))

        if score >= 90.0:
            grade = SecurityPostureGrade.EXCELLENT
        elif score >= 75.0:
            grade = SecurityPostureGrade.GOOD
        elif score >= 50.0:
            grade = SecurityPostureGrade.NEEDS_IMPROVEMENT
        else:
            grade = SecurityPostureGrade.CRITICAL_RISK

        findings = []
        if active_threats > 0:
            findings.append(f"Detected {active_threats} active threats requiring immediate mitigation.")
        if open_vulnerabilities > 0:
            findings.append(f"Found {open_vulnerabilities} open vulnerabilities across monitored assets.")
        if misconfigurations > 0:
            findings.append(f"Identified {misconfigurations} misconfigurations in infrastructure or security controls.")
        if not findings:
            findings.append("No active security posture defects detected.")

        return SecurityPostureAssessment(
            tenant_id=tenant_id,
            asset_count=asset_count,
            score=round(score, 2),
            grade=grade,
            open_vulnerabilities_count=open_vulnerabilities,
            misconfigurations_count=misconfigurations,
            threats_count=active_threats,
            findings=findings,
        )
