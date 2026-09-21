"""Unit tests for DeploymentManager and approval gating."""

import pytest

from app.mlops.deployment import DeploymentEnvironment, DeploymentManager, DeploymentStatus
from app.mlops.exceptions import GovernanceViolationException
from app.mlops.registry import AIAssetRegistry, AIAssetType


def test_deployment_lifecycle_and_production_approval_gating():
    registry = AIAssetRegistry()
    asset = registry.register_asset("Doc Bot", AIAssetType.AGENT)
    mgr = DeploymentManager(registry=registry)

    # 1. Dev deployment deploys directly
    dev_dep = mgr.create_deployment("Dev Dep", asset.asset_id, "1.0.0", DeploymentEnvironment.DEVELOPMENT)
    assert dev_dep.status == DeploymentStatus.PENDING
    deployed_dev = mgr.deploy(dev_dep.deployment_id)
    assert deployed_dev.status == DeploymentStatus.ACTIVE

    # 2. Production deployment requires approval if version is not locked as immutable production
    prod_dep = mgr.create_deployment("Prod Dep", asset.asset_id, "1.0.0", DeploymentEnvironment.PRODUCTION)
    assert prod_dep.status == DeploymentStatus.APPROVAL_REQUIRED

    with pytest.raises(GovernanceViolationException):
        mgr.deploy(prod_dep.deployment_id)

    # Approve and deploy
    mgr.approve_deployment(prod_dep.deployment_id)
    deployed_prod = mgr.deploy(prod_dep.deployment_id)
    assert deployed_prod.status == DeploymentStatus.ACTIVE
