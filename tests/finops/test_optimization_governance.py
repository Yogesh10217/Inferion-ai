"""Unit tests for FinOpsGovernanceEngine and risk approval gating."""

import pytest
from app.finops.optimization import OptimizationRecommendation, OptimizationRiskLevel
from app.finops.governance import FinOpsGovernanceEngine


def test_optimization_risk_approval_policy():
    gov = FinOpsGovernanceEngine()

    # LOW risk -> Auto permitted
    rec_low = OptimizationRecommendation(target_resource_id="cache_1", risk_level=OptimizationRiskLevel.LOW)
    dec_low = gov.evaluate_optimization(rec_low)
    assert dec_low.permitted is True

    # HIGH risk -> Requires ApprovalEngine approval!
    rec_high = OptimizationRecommendation(target_resource_id="prod_router", risk_level=OptimizationRiskLevel.HIGH)
    dec_high = gov.evaluate_optimization(rec_high)
    assert dec_high.permitted is False
    assert dec_high.requires_approval is True
    assert dec_high.approval_request_id is not None
