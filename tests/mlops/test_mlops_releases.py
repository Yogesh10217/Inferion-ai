"""Unit tests for ReleaseManager."""

import pytest

from app.mlops.exceptions import GovernanceViolationException
from app.mlops.releases import ReleaseArtifact, ReleaseManager, ReleaseStatus


def test_release_packaging_validation_and_deployment():
    mgr = ReleaseManager()

    rel = mgr.create_release(
        name="Q3 AI Release",
        tenant_id="tenant_rel",
        artifacts=[ReleaseArtifact(asset_id="ast_1", version_number="1.0.0", asset_type="MODEL")],
    )

    with pytest.raises(GovernanceViolationException):
        mgr.deploy_release(rel.release_id)

    mgr.validate_release(rel.release_id)
    deployed = mgr.deploy_release(rel.release_id)
    assert deployed.status == ReleaseStatus.DEPLOYED
