"""Mandatory End-to-End Delivery Flows for Phase 5.21."""

import pytest

from app.developer_platform.api_contracts import APIContract
from app.developer_platform.exceptions import (
    APIContractBreakingChangeException,
    DependencyRiskViolationException,
)
from app.developer_platform.manager import DeveloperPlatformManager


def test_flow_1_api_breaking_change_governance():
    """FLOW 1 — API Breaking Change Governance"""
    mgr = DeveloperPlatformManager()
    old_c = APIContract(contract_id="c1", service_id="svc_flow1", endpoints={"/v1/data": {}})
    new_c = APIContract(contract_id="c2", service_id="svc_flow1", endpoints={"/v2/data": {}})

    with pytest.raises(APIContractBreakingChangeException):
        mgr.contract_validator.compare_contracts(old_c, new_c, tenant_id="t_flow1")


def test_flow_2_secure_cicd_release():
    """FLOW 2 — Secure CI/CD Release"""
    mgr = DeveloperPlatformManager()
    proj = mgr.create_project_with_repository("Core Service", tenant_id="t_flow2")
    pipe = mgr.pipeline_manager.create_pipeline(proj.project_id, "main_ci", tenant_id="t_flow2")
    run = mgr.pipeline_manager.trigger_pipeline_run(pipe.pipeline_id, tenant_id="t_flow2")

    assert run.status.value == "SUCCEEDED"
    rel = mgr.release_manager.create_release(proj.project_id, "1.0.0", tenant_id="t_flow2")
    assert rel.status == "DEPLOYED"


def test_flow_3_deployment_regression():
    """FLOW 3 — Deployment Regression & Rollback Recommendation"""
    mgr = DeveloperPlatformManager()
    rel = mgr.release_manager.create_release("p_reg", "1.1.0", tenant_id="t_flow3")

    rec = mgr.deployment_intelligence.evaluate_deployment_health(
        rel.release_id, error_rate_pct=12.5, tenant_id="t_flow3"
    )
    assert rec is not None
    assert rec.approval_request_id is not None

    appr = mgr.deployment_intelligence.approval_engine.approve(
        rec.approval_request_id, approver_id="sre_lead@company.com"
    )
    assert appr.status.value == "APPROVED"


def test_flow_4_dependency_risk():
    """FLOW 4 — Dependency Vulnerability Risk Enforcement"""
    mgr = DeveloperPlatformManager()
    deps = [{"name": "bad-package", "version": "0.0.1", "risk_level": "CRITICAL"}]

    with pytest.raises(DependencyRiskViolationException):
        mgr.dependency_manager.analyze_dependencies(deps, tenant_id="t_flow4")


def test_flow_5_authorized_ai_developer_assistance():
    """FLOW 5 — Authorized AI Developer Assistance"""
    mgr = DeveloperPlatformManager()
    rec = mgr.developer_assistant.assist_developer(
        "Explain error handling", repository_id="repo_flow5", tenant_id="t_flow5"
    )

    assert rec.guidance is not None
    assert len(rec.source_references) > 0


def test_flow_6_developer_workspace_security():
    """FLOW 6 — Developer Workspace Security & Session Ephemerality"""
    mgr = DeveloperPlatformManager()
    ws = mgr.workspace_manager.create_workspace("p_flow6", "dev_bob", tenant_id="t_flow6")

    assert ws.status == "READY"
    assert len(mgr.workspace_manager._sessions) == 1


def test_flow_7_strict_cross_tenant_isolation():
    """FLOW 7 — Strict Cross-Tenant Isolation"""
    mgr = DeveloperPlatformManager()
    p_a = mgr.create_project_with_repository("Tenant A Project", tenant_id="tenant_A")
    p_b = mgr.create_project_with_repository("Tenant B Project", tenant_id="tenant_B")

    items_a = mgr.project_manager.list_projects(tenant_id="tenant_A")
    assert len(items_a) == 1
    assert items_a[0].project_id == p_a.project_id
    assert p_b.project_id not in [i.project_id for i in items_a]


def test_flow_8_budget_aware_build_routing():
    """FLOW 8 — Budget-Aware Build Cost Attribution"""
    mgr = DeveloperPlatformManager()
    cost = mgr.billing_adapter.record_build_cost(
        tenant_id="t_flow8", build_duration_minutes=10.0, resource_type="standard_build"
    )
    assert cost == 0.50
