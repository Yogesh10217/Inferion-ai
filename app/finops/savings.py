"""Savings Verification & Empirical Post-Optimization Measurement Engine."""

import logging
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, List

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SavingsRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"svg_{uuid.uuid4().hex[:10]}")
    recommendation_id: str
    tenant_id: str = "global"

    estimated_savings: Decimal = Decimal("0.0")
    realized_savings: Decimal = Decimal("0.0")
    verified_savings: Decimal = Decimal("0.0")

    quality_regression_detected: bool = False
    verification_status: str = "UNVERIFIED"  # UNVERIFIED, VERIFIED, FAILED_REGRESSION
    measured_at: datetime = Field(default_factory=_now)

    @field_validator("estimated_savings", "realized_savings", "verified_savings", mode="before")
    @classmethod
    def parse_decimal(cls, value: Any) -> Decimal:
        if isinstance(value, float):
            return Decimal(str(value))
        return Decimal(value)


class SavingsVerificationEngine:
    """Measures post-optimization empirical usage and verifies cost reduction without quality regression."""

    def __init__(self) -> None:
        self._savings: List[SavingsRecord] = []

    def verify_savings(
        self,
        recommendation_id: str,
        baseline_cost: Decimal,
        post_optimization_cost: Decimal,
        tenant_id: str = "global",
        quality_score_post: float = 95.0,
        quality_score_pre: float = 95.0,
    ) -> SavingsRecord:
        base_dec = Decimal(str(baseline_cost)) if isinstance(baseline_cost, (float, int, str)) else baseline_cost
        post_dec = (
            Decimal(str(post_optimization_cost))
            if isinstance(post_optimization_cost, (float, int, str))
            else post_optimization_cost
        )

        realized = (base_dec - post_dec).quantize(Decimal("0.000001"))
        has_regression = quality_score_post < (quality_score_pre - 2.0)

        verified = realized if not has_regression and realized > Decimal("0.0") else Decimal("0.0")
        status = (
            "VERIFIED"
            if not has_regression and realized > Decimal("0.0")
            else ("FAILED_REGRESSION" if has_regression else "UNVERIFIED")
        )

        rec = SavingsRecord(
            recommendation_id=recommendation_id,
            tenant_id=tenant_id,
            estimated_savings=base_dec * Decimal("0.2"),
            realized_savings=realized,
            verified_savings=verified,
            quality_regression_detected=has_regression,
            verification_status=status,
        )
        self._savings.append(rec)
        logger.info(
            f"[SAVINGS VERIFICATION] Verified recommendation '{recommendation_id}': Realized = ${realized}, Verified = ${verified}, Status = {status}"
        )
        return rec
