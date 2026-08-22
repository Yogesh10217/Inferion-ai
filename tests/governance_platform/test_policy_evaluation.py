"""Unit tests for UnifiedPolicyEvaluator orchestration across subsystem engines."""

import pytest
from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator, GovernanceDecision


def test_unified_policy_evaluation_allow_and_block():
    evaluator = UnifiedPolicyEvaluator()

    # Allowed evaluation
    res_allow = evaluator.evaluate_request("read", "dataset_public", tenant_id="t_pol", actor_id="admin")
    assert res_allow.decision == GovernanceDecision.ALLOW
    assert res_allow.allow is True
    assert res_allow.deny is False

    # Denied evaluation
    res_deny = evaluator.evaluate_request("admin_override", "restricted_resource", tenant_id="t_pol", actor_id="guest")
    assert res_deny.decision == GovernanceDecision.BLOCK
    assert res_deny.allow is False
    assert res_deny.deny is True
    assert len(res_deny.violations) >= 1
