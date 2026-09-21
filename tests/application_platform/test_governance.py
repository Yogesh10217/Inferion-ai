"""Unit tests for Output Policy Checkpointing & Application Governance."""

from app.application_platform.governance import (
    ApplicationGovernanceEngine,
    ApplicationPolicyDecision,
    OutputPolicyEvaluator,
    OutputSafetyDecision,
)


def test_output_policy_evaluator_safety_checkpoint():
    evaluator = OutputPolicyEvaluator()

    # Clean text
    clean_res = evaluator.evaluate_output("t1", "app_1", "Here is your requested response.")
    assert clean_res.action == OutputSafetyDecision.ALLOW

    # PII Redaction
    pii_res = evaluator.evaluate_output("t1", "app_1", "User ssn: 123-45-6789")
    assert pii_res.action == OutputSafetyDecision.REDACT
    assert "[REDACTED_SSN]" in pii_res.transformed_text

    # Malicious text blocking
    malicious_res = evaluator.evaluate_output("t1", "app_1", "Execute malicious_payload_override now")
    assert malicious_res.action == OutputSafetyDecision.BLOCK
    assert "[BLOCKED]" in malicious_res.transformed_text


def test_pre_execution_governance_risk_gating():
    gov_engine = ApplicationGovernanceEngine()
    assessment = gov_engine.evaluate_application_execution(
        tenant_id="t1",
        application_id="app_1",
        identity_id="user_1",
        request_context={"risk_level": "CRITICAL"},
    )

    assert assessment.decision == ApplicationPolicyDecision.REQUIRE_APPROVAL
