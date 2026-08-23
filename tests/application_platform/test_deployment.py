"""Unit tests for Application Deployment Manager."""

import pytest
from app.application_platform.deployment import (
    DeploymentManager,
    DeploymentStrategy,
    DeploymentStatus,
)
from app.approvals.approval_engine import ApprovalEngine


def test_direct_low_risk_deployment():
    dep_mgr = DeploymentManager()
    dep = dep_mgr.create_deployment(
        application_id="app_1",
        version_id="ver_1",
        tenant_id="t1",
        environment="STAGING",
        strategy=DeploymentStrategy.DIRECT,
        risk_level="LOW",
    )
    assert dep.status == DeploymentStatus.IN_PROGRESS

    executed = dep_mgr.execute_deployment(dep.deployment_id)
    assert executed.status == DeploymentStatus.SUCCESSFUL


def test_high_risk_production_release_requires_approval():
    appr_engine = ApprovalEngine()
    dep_mgr = DeploymentManager(approval_engine=appr_engine)
    dep = dep_mgr.create_deployment(
        application_id="app_1",
        version_id="ver_1",
        tenant_id="t1",
        environment="PRODUCTION",
        strategy=DeploymentStrategy.CANARY,
        risk_level="HIGH",
    )

    assert dep.status == DeploymentStatus.AWAITING_APPROVAL
    assert dep.approval_request_id is not None

    # Approve request
    appr_engine.approve(dep.approval_request_id, approver_id="admin")

    executed = dep_mgr.execute_deployment(dep.deployment_id)
    assert executed.status == DeploymentStatus.SUCCESSFUL
