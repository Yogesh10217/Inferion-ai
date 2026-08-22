"""Unit tests for SavingsVerificationEngine (Estimated vs. Realized vs. Verified)."""

from decimal import Decimal
import pytest
from app.finops.savings import SavingsVerificationEngine


def test_savings_verification_and_quality_regression_check():
    engine = SavingsVerificationEngine()

    # 1. Successful verification (No quality regression)
    rec1 = engine.verify_savings(
        recommendation_id="rec_model_route",
        baseline_cost=Decimal("100.0"),
        post_optimization_cost=Decimal("60.0"),
        quality_score_pre=95.0,
        quality_score_post=95.0,
    )

    assert rec1.realized_savings == Decimal("40.000000")
    assert rec1.verified_savings == Decimal("40.000000")
    assert rec1.verification_status == "VERIFIED"

    # 2. Failed verification due to quality regression
    rec2 = engine.verify_savings(
        recommendation_id="rec_bad_compress",
        baseline_cost=Decimal("100.0"),
        post_optimization_cost=Decimal("40.0"),
        quality_score_pre=95.0,
        quality_score_post=85.0,  # 10% drop -> Quality Regression!
    )

    assert rec2.realized_savings == Decimal("60.000000")
    assert rec2.verified_savings == Decimal("0.0")  # Verified savings reset to 0!
    assert rec2.verification_status == "FAILED_REGRESSION"
