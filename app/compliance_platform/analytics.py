"""Tenant-Isolated Compliance Analytics Subsystem."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.compliance_platform.frameworks import FrameworkManager
from app.compliance_platform.controls import ControlManager
from app.compliance_platform.findings import FindingManager
from app.compliance_platform.posture import CompliancePostureManager


class ComplianceInsight(BaseModel):
    insight_id: str = Field(default_factory=lambda: f"ins_{uuid.uuid4().hex[:12]}")
    title: str
    description: str
    severity: str = "MEDIUM"


class ComplianceReport(BaseModel):
    report_id: str = Field(default_factory=lambda: f"comprep_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    adopted_frameworks_count: int = 0
    total_controls_count: int = 0
    open_findings_count: int = 0
    posture_score: float = 90.0
    insights: List[ComplianceInsight] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ComplianceAnalyticsEngine:
    """Generates tenant-isolated compliance intelligence reports."""

    def __init__(
        self,
        framework_manager: FrameworkManager,
        control_manager: ControlManager,
        finding_manager: FindingManager,
        posture_manager: CompliancePostureManager,
    ) -> None:
        self.framework_manager = framework_manager
        self.control_manager = control_manager
        self.finding_manager = finding_manager
        self.posture_manager = posture_manager

    def generate_report(self, tenant_id: str) -> ComplianceReport:
        fws = self.framework_manager.list_frameworks(tenant_id)
        ctrls = self.control_manager.list_controls(tenant_id)
        findings = self.finding_manager.list_findings(tenant_id)
        posture = self.posture_manager.get_posture(tenant_id)

        insights = []
        if len(findings) > 0:
            insights.append(
                ComplianceInsight(
                    title="Active Compliance Findings",
                    description=f"Identified {len(findings)} open finding(s) requiring remediation.",
                    severity="HIGH" if len(findings) >= 3 else "MEDIUM",
                )
            )

        return ComplianceReport(
            tenant_id=tenant_id,
            adopted_frameworks_count=len(fws),
            total_controls_count=len(ctrls),
            open_findings_count=len(findings),
            posture_score=posture.overall_score,
            insights=insights,
        )
