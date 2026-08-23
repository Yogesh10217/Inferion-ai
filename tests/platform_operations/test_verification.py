"""Unit tests for Post-Remediation Verification & Rollback Engine."""

import pytest
from app.platform_operations.services import ServiceCatalogManager, ServiceHealth
from app.platform_operations.remediation import RemediationPlanner, RemediationStep, RemediationStrategy, RemediationStatus
from app.platform_operations.verification import RemediationVerifier
from app.governance_platform.risk import RiskLevel


def test_remediation_verification_pass():
    svc_mgr = ServiceCatalogManager()
    svc = svc_mgr.register_service("t1", "API Gateway")

    planner = RemediationPlanner()
    step = RemediationStep(strategy=RemediationStrategy.RESTART, target_resource_id=svc.service_id, action_description="Restart", expected_effect="Ok", risk_level=RiskLevel.LOW)
    plan = planner.create_remediation_plan("t1", "inc_1", svc.service_id, [step])
    planner.execute_remediation_plan(plan.plan_id, "t1")

    verifier = RemediationVerifier(service_catalog_manager=svc_mgr, remediation_planner=planner)
    result = verifier.verify_remediation("t1", plan.plan_id)

    assert result.is_verified is True
    assert result.is_rolled_back is False


def test_remediation_verification_failure_triggers_rollback():
    svc_mgr = ServiceCatalogManager()
    svc = svc_mgr.register_service("t1", "Unhealthy DB Service")
    svc_mgr.update_service_health(svc.service_id, "t1", ServiceHealth.UNHEALTHY)

    planner = RemediationPlanner()
    step = RemediationStep(strategy=RemediationStrategy.RESTART, target_resource_id=svc.service_id, action_description="Restart", expected_effect="Ok", risk_level=RiskLevel.LOW)
    plan = planner.create_remediation_plan("t1", "inc_1", svc.service_id, [step])
    planner.execute_remediation_plan(plan.plan_id, "t1")

    verifier = RemediationVerifier(service_catalog_manager=svc_mgr, remediation_planner=planner)
    result = verifier.verify_remediation("t1", plan.plan_id, auto_rollback_on_failure=True)

    assert result.is_verified is False
    assert result.is_rolled_back is True
    assert planner.get_plan(plan.plan_id, "t1").status == RemediationStatus.ROLLED_BACK
