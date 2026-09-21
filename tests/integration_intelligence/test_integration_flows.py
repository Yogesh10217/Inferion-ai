"""Mandatory 20 End-to-End Integration Flow Tests for Integration Intelligence (Phase 5.40)."""

import pytest

from app.integration_intelligence.compensation import CompensationStep
from app.integration_intelligence.connectors import ConnectorCapability, ConnectorType
from app.integration_intelligence.dependencies import DependencyImpact
from app.integration_intelligence.exceptions import (
    CrossTenantIntegrationAccessException,
    HighRiskIntegrationRequiresApprovalException,
    ImmutableIntegrationRecordException,
    IntegrationRetryException,
    IntegrationValidationException,
)
from app.integration_intelligence.execution import IntegrationExecutionStatus
from app.integration_intelligence.failures import FailureType
from app.integration_intelligence.manager import IntegrationIntelligenceManager
from app.integration_intelligence.mapping import MappingRule
from app.integration_intelligence.recovery import RecoveryStep
from app.integration_intelligence.retries import RetryPolicy
from app.integration_intelligence.routing import RouteHealth, RoutingStrategy
from app.integration_intelligence.verification import VerificationCheck
from app.integration_intelligence.workflows import WorkflowStatus, WorkflowTrigger, WorkflowType


@pytest.fixture
def manager():
    return IntegrationIntelligenceManager()


def test_flow1_connector_registration(manager):
    """Flow 1 — Connector Registration."""
    tenant_id = "tenant_a"
    conn = manager.connector_manager.register_connector(
        tenant_id=tenant_id,
        name="CRM_Connector",
        connector_type=ConnectorType.SAAS,
        external_system_id="crm_prod_01",
        provider_name="SalesCloud",
        base_endpoint_url="https://api.salescloud.com",
        capabilities=[ConnectorCapability.READ, ConnectorCapability.WRITE],
        secret_reference_id="sec_ref_crm_99",
    )

    assert conn.connector_id.startswith("conn_")
    assert conn.tenant_id == tenant_id
    assert conn.reference.secret_reference_id == "sec_ref_crm_99"
    assert conn.reference.base_endpoint_url == "https://api.salescloud.com"


def test_flow2_workflow_validation(manager):
    """Flow 2 — Workflow Validation."""
    tenant_id = "tenant_a"
    wf = manager.workflow_manager.create_workflow(
        tenant_id=tenant_id,
        name="CustomerSyncWorkflow",
        workflow_type=WorkflowType.SYNC_API,
        trigger=WorkflowTrigger.API_INVOCATION,
    )

    assert wf.status == WorkflowStatus.DRAFT
    val_wf = manager.workflow_manager.validate_workflow(tenant_id, wf.workflow_id)
    assert val_wf.status == WorkflowStatus.VALIDATED


def test_flow3_invalid_mapping_blocked(manager):
    """Flow 3 — Invalid Mapping Blocked."""
    tenant_id = "tenant_a"
    mapping = manager.mapping_manager.create_mapping(
        tenant_id=tenant_id,
        name="IncompleteMapping",
        source_schema_id="sch_src",
        target_schema_id="sch_tgt",
        rules=[MappingRule(source_field="name", target_field="first_name")],
    )

    with pytest.raises(IntegrationValidationException) as exc_info:
        manager.mapping_manager.validate_mapping(tenant_id, mapping.mapping_id, ["first_name", "email_address"])

    assert "email_address" in str(exc_info.value)


def test_flow4_dependency_failure_detection(manager):
    """Flow 4 — Dependency Failure Detection."""
    tenant_id = "tenant_a"
    manager.dependency_manager.add_dependency(tenant_id, "sys_auth", "sys_user_db", DependencyImpact.CRITICAL_PATH)
    manager.dependency_manager.add_dependency(tenant_id, "sys_user_db", "sys_billing", DependencyImpact.HIGH)

    impacted = manager.dependency_manager.analyze_impact(tenant_id, "sys_auth")
    assert "sys_user_db" in impacted
    assert "sys_billing" in impacted


def test_flow5_fallback_routing(manager):
    """Flow 5 — Fallback Routing."""
    tenant_id = "tenant_a"
    r_primary = manager.routing_manager.register_route(
        tenant_id, "conn_crm", "ep_01", strategy=RoutingStrategy.PRIMARY, priority=1
    )
    r_fallback = manager.routing_manager.register_route(
        tenant_id, "conn_crm", "ep_02", strategy=RoutingStrategy.FALLBACK, priority=2
    )

    # Mark primary route as failed
    r_primary.health = RouteHealth.FAILED

    decision = manager.routing_manager.resolve_route(tenant_id, "conn_crm")
    assert decision.strategy_used == RoutingStrategy.FALLBACK
    assert decision.selected_route_id == r_fallback.route_id


def test_flow6_cross_tenant_access_blocked(manager):
    """Flow 6 — Cross-Tenant Access Blocked with zero metadata leakage."""
    conn_a = manager.connector_manager.register_connector(
        tenant_id="tenant_a",
        name="ConnectorA",
        connector_type=ConnectorType.API,
        external_system_id="sys_a",
        provider_name="ProvA",
        base_endpoint_url="https://api.a.com",
    )

    with pytest.raises(CrossTenantIntegrationAccessException) as exc_info:
        manager.connector_manager.get_connector("tenant_b", conn_a.connector_id)

    msg = str(exc_info.value)
    assert conn_a.connector_id not in msg
    assert "tenant_a" not in msg
    assert "tenant_b" not in msg
    assert msg == "Access denied."


def test_flow7_high_risk_integration_requires_approval(manager):
    """Flow 7 — High-Risk Integration Requires Approval."""
    tenant_id = "tenant_a"
    wf = manager.workflow_manager.create_workflow(tenant_id, "BulkDropDB")
    exec_obj = manager.execution_manager.request_execution(
        tenant_id, wf.workflow_id, "idem_drop_1", requires_approval=True
    )

    with pytest.raises(HighRiskIntegrationRequiresApprovalException):
        manager.execution_manager.delegate_execution(tenant_id, exec_obj.execution_id)

    # Approve and delegate successfully
    manager.execution_manager.approve_execution(tenant_id, exec_obj.execution_id, "appr_999")
    del_req = manager.execution_manager.delegate_execution(tenant_id, exec_obj.execution_id)
    assert del_req.delegation_id.startswith("delreq_")


def test_flow8_delegation_only_execution(manager):
    """Flow 8 — Delegation-Only Execution (no direct external mutations)."""
    tenant_id = "tenant_a"
    wf = manager.workflow_manager.create_workflow(tenant_id, "SyncData")
    exec_obj = manager.execution_manager.request_execution(tenant_id, wf.workflow_id, "idem_sync_1")
    manager.execution_manager.evaluate_governance(tenant_id, exec_obj.execution_id)

    del_req = manager.execution_manager.delegate_execution(tenant_id, exec_obj.execution_id)
    assert del_req.payload["execution_id"] == exec_obj.execution_id
    assert exec_obj.status == IntegrationExecutionStatus.DELEGATED


def test_flow9_duplicate_execution_idempotency_protection(manager):
    """Flow 9 — Duplicate Execution Idempotency Protection."""
    tenant_id = "tenant_a"
    exec1 = manager.execution_manager.request_execution(tenant_id, "wf_01", "idem_key_unique_100")
    exec2 = manager.execution_manager.request_execution(tenant_id, "wf_01", "idem_key_unique_100")

    assert exec1.execution_id == exec2.execution_id


def test_flow10_retry_limit_enforcement(manager):
    """Flow 10 — Retry Limit Enforcement & Dead-Letter Routing."""
    tenant_id = "tenant_a"
    policy = RetryPolicy(max_retries=2)

    # Attempt 1 -> allowed
    dec1 = manager.retry_manager.evaluate_retry(tenant_id, "exec_01", 1, policy)
    assert dec1.status.value == "ALLOWED"

    # Attempt 2 -> limit exceeded -> routed to dead-letter queue
    with pytest.raises(IntegrationRetryException):
        manager.retry_manager.evaluate_retry(tenant_id, "exec_01", 2, policy)

    dlq = manager.retry_manager.list_dead_letter_entries(tenant_id)
    assert len(dlq) == 1
    assert dlq[0]["execution_id"] == "exec_01"


def test_flow11_integration_failure_signal_generation(manager):
    """Flow 11 — Integration Failure Signal Generation."""
    tenant_id = "tenant_a"
    fail = manager.failure_manager.record_failure(
        tenant_id=tenant_id,
        execution_id="exec_100",
        connector_id="conn_100",
        failure_type=FailureType.TIMEOUT,
        error_code="ERR_CONN_TIMEOUT",
        error_message="Connection timed out after 30s",
    )

    assert fail.failure_id.startswith("fail_int_")
    assert fail.evidence.error_code == "ERR_CONN_TIMEOUT"


def test_flow12_recovery_planning(manager):
    """Flow 12 — Controlled Recovery Planning."""
    tenant_id = "tenant_a"
    step = RecoveryStep(action="REROUTE_TRAFFIC", target_system_id="sys_backup")
    plan = manager.recovery_manager.create_recovery_plan(tenant_id, "fail_100", [step], requires_approval=False)

    del_req = manager.recovery_manager.delegate_recovery(tenant_id, plan.plan_id)
    assert del_req.action == "EXECUTE_INTEGRATION_RECOVERY"


def test_flow13_compensation_planning_and_escalation(manager):
    """Flow 13 — Compensation Planning & Unsupported Step Escalation."""
    tenant_id = "tenant_a"
    step_supp = CompensationStep(original_step_id="step_1", compensation_action="DELETE_RECORD", is_supported=True)
    step_unsupp = CompensationStep(
        original_step_id="step_2",
        compensation_action="UNSEND_EMAIL",
        is_supported=False,
        reason_unsupported="Email cannot be un-sent",
    )

    plan = manager.compensation_manager.create_compensation_plan(tenant_id, "exec_100", [step_supp, step_unsupp])
    assert plan.status.value == "UNSUPPORTED_ESCALATED"
    assert plan.has_unsupported_steps is True

    # Delegation without approval should be blocked
    with pytest.raises(HighRiskIntegrationRequiresApprovalException):
        manager.compensation_manager.delegate_compensation(tenant_id, plan.plan_id)


def test_flow14_verification_failure(manager):
    """Flow 14 — Outcome Verification Failure."""
    tenant_id = "tenant_a"
    check_failed = VerificationCheck(
        target_system_id="sys_ext",
        expected_status_code=200,
        observed_status_code=500,
        passed=False,
        is_destructive_action=True,
    )
    verif = manager.verification_manager.verify_execution(tenant_id, "exec_100", [check_failed])

    assert verif.status.value == "FAILURE"
    assert verif.auto_retry_allowed is False  # Prevents auto retry for failed destructive action!


def test_flow15_sensitive_data_redaction(manager):
    """Flow 15 — Sensitive Data Redaction."""
    tenant_id = "tenant_a"
    raw_payload = {"user_email": "john@company.com", "api_token": "secret_bearer_token_xyz"}

    bundle = manager.evidence_manager.create_bundle(tenant_id, "AuthEvidence")
    ev = manager.evidence_manager.add_evidence(tenant_id, bundle.bundle_id, "AUTH_PAYLOAD", "ref_01", raw_payload)

    assert "api_token" in ev.sanitized_payload
    assert ev.sanitized_payload["api_token"] != "secret_bearer_token_xyz"


def test_flow16_immutable_finalized_execution(manager):
    """Flow 16 — Immutable Finalized Execution Record."""
    tenant_id = "tenant_a"
    bundle = manager.evidence_manager.create_bundle(tenant_id, "FinalEvidence")
    manager.evidence_manager.add_evidence(tenant_id, bundle.bundle_id, "RECORD", "ref_1", {"key": "val"})
    manager.evidence_manager.finalize_bundle(tenant_id, bundle.bundle_id)

    with pytest.raises(ImmutableIntegrationRecordException):
        manager.evidence_manager.add_evidence(tenant_id, bundle.bundle_id, "RECORD", "ref_2", {"key2": "val2"})


def test_flow17_integration_investigation_snapshot(manager):
    """Flow 17 — Integration Investigation Snapshot Generation."""
    tenant_id = "tenant_a"
    inv = manager.investigation_manager.open_investigation(tenant_id, "Failure Investigation", "wf_failed_1")
    manager.investigation_manager.start_investigating(tenant_id, inv.investigation_id)
    manager.investigation_manager.record_finding(tenant_id, inv.investigation_id, "Timeout during payload transfer")

    concluded = manager.investigation_manager.conclude_investigation(tenant_id, inv.investigation_id)
    assert concluded.is_concluded is True
    assert concluded.snapshot_id is not None
    assert concluded.snapshot_id.startswith("snap_")


def test_flow18_trust_assessment_compatibility(manager):
    """Flow 18 — Trust Assessment Compatibility."""
    tenant_id = "tenant_a"
    asm = manager.trust_engine.evaluate_trust(
        tenant_id,
        "conn_crm",
        connector_reliability_score=95.0,
        verification_success_score=90.0,
        recent_failures_count=0,
    )

    assert asm.score >= 80.0
    assert asm.band.value in ["HIGH_TRUST", "TRUSTED"]


def test_flow19_learning_recommendation_advisory_only(manager):
    """Flow 19 — Learning Recommendation Does Not Auto-Modify Workflow."""
    tenant_id = "tenant_a"
    rec = manager.learning_manager.record_learning_pattern(
        tenant_id,
        "FrequentTimeoutPattern",
        "Endpoint times out during peak hours",
        "Increase Timeout",
        "Increase endpoint timeout setting to 60s",
        target_workflow_id="wf_01",
    )

    item = rec.recommendations[0]
    assert item.auto_execute is False  # Advisory only!


def test_flow20_full_enterprise_integration_lifecycle(manager):
    """Flow 20 — Full Enterprise Integration Lifecycle."""
    tenant_id = "tenant_enterprise"
    result = manager.run_full_lifecycle(tenant_id, "EnterpriseOrderPipeline")

    assert result["status"] == "COMPLETED"
    assert result["workflow_id"].startswith("wf_")
    assert result["execution_id"].startswith("exec_int_")
    assert result["delegation_id"].startswith("delreq_")
    assert result["governance_status"] == "ALLOW"
    assert result["execution_fingerprint"] != ""
