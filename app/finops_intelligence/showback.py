"""Showback Reporting for Cost Transparency (Phase 5.42)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import CrossTenantFinOpsIntelligenceException


class ShowbackDimension(BaseModel):
    key: str
    value: str
    cost_usd: float


class ShowbackReport(BaseModel):
    report_id: str = Field(default_factory=lambda: f"sb_rpt_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    dimensions: List[ShowbackDimension] = Field(default_factory=list)
    total_showback_usd: float = 0.0
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ShowbackManager:
    """Manages showback cost transparency reporting across organizational units."""

    def __init__(self) -> None:
        self._reports: Dict[str, ShowbackReport] = {}

    def generate_showback_report(
        self,
        tenant_id: str,
        title: str,
        dimensions: List[ShowbackDimension],
    ) -> ShowbackReport:
        total = sum(d.cost_usd for d in dimensions)
        rpt = ShowbackReport(
            tenant_id=tenant_id,
            title=title,
            dimensions=dimensions,
            total_showback_usd=round(total, 2),
        )
        self._reports[rpt.report_id] = rpt
        return rpt

    def get_report(self, tenant_id: str, report_id: str) -> ShowbackReport:
        rpt = self._reports.get(report_id)
        if not rpt or rpt.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return rpt
