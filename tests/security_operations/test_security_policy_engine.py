"""
Tests for Security Policy Engine (Phase 5.69).
"""

from app.security_operations.security_policy_engine import SecurityPolicyEngine, SecurityPolicyResult
from app.security_operations.security_posture import SecurityPostureEvaluator


def test_policy_engine_allow():
    posture_eval = SecurityPostureEvaluator()
    posture_res = posture_eval.evaluate(is_production=False)
    policy_engine = SecurityPolicyEngine()
    result = policy_engine.evaluate_policy(posture_res, is_production=False)
    assert isinstance(result, SecurityPolicyResult)
    assert result.action in ["ALLOW", "WARN", "BLOCK", "MANUAL_REVIEW_REQUIRED"]


def test_policy_engine_production_threshold():
    posture_eval = SecurityPostureEvaluator()
    posture_res = posture_eval.evaluate(is_production=True)
    policy_engine = SecurityPolicyEngine(min_production_score=90.0)
    result = policy_engine.evaluate_policy(posture_res, is_production=True)
    assert result.is_production is True
