"""Unit tests for CostOptimizationEngine."""

from decimal import Decimal
import pytest
from app.finops.optimization import CostOptimizationEngine


def test_optimization_recommendation_generation():
    engine = CostOptimizationEngine()
    recs = engine.generate_recommendations("tenant_opt")

    assert len(recs) >= 2
    assert recs[0].estimated_monthly_savings > Decimal("0.0")
