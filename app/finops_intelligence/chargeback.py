"""Chargeback Intelligence (Phase 5.42)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import CrossTenantFinOpsIntelligenceException


class ChargebackPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: f"cb_pol_{uuid.uuid4().hex[:8]}")
    target_business_unit: str
    rate_multiplier: float = 1.0


class ChargebackRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"cb_rec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_business_unit: str
    billed_amount_usd: float
    billing_period: str = "2026-09"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChargebackAssessment(BaseModel):
    tenant_id: str
    business_unit: str
    total_chargeback_usd: float
    record_count: int


class ChargebackManager:
    """Manages internal chargeback financial intelligence (no external monetary transfers)."""

    def __init__(self) -> None:
        self._records: Dict[str, ChargebackRecord] = {}

    def generate_chargeback(
        self,
        tenant_id: str,
        target_business_unit: str,
        total_cost_usd: float,
        policy: Optional[ChargebackPolicy] = None,
        billing_period: str = "2026-09",
    ) -> ChargebackRecord:
        mult = policy.rate_multiplier if policy else 1.0
        final_amount = round(total_cost_usd * mult, 2)

        rec = ChargebackRecord(
            tenant_id=tenant_id,
            target_business_unit=target_business_unit,
            billed_amount_usd=final_amount,
            billing_period=billing_period,
        )
        self._records[rec.record_id] = rec
        return rec

    def get_assessment(self, tenant_id: str, business_unit: str) -> ChargebackAssessment:
        recs = [r for r in self._records.values() if r.tenant_id == tenant_id and r.target_business_unit == business_unit]
        total = sum(r.billed_amount_usd for r in recs)
        return ChargebackAssessment(
            tenant_id=tenant_id,
            business_unit=business_unit,
            total_chargeback_usd=round(total, 2),
            record_count=len(recs),
        )

    def get_record(self, tenant_id: str, record_id: str) -> ChargebackRecord:
        rec = self._records.get(record_id)
        if not rec or rec.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return rec
