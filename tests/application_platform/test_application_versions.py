"""Unit tests for Application Version Immutability & Fingerprinting."""

import pytest

from app.application_platform.application import (
    ApplicationConfiguration,
    ApplicationRegistry,
    ApplicationStatus,
)
from app.application_platform.exceptions import ImmutableVersionException


def test_version_fingerprint_generation():
    registry = ApplicationRegistry()
    app = registry.create_application(tenant_id="t1", name="App 1")
    ver = registry.create_version(
        application_id=app.application_id,
        tenant_id="t1",
        version_str="1.0.0",
        configuration=ApplicationConfiguration(environment="PRODUCTION"),
    )

    assert ver.version_fingerprint != ""
    initial_fp = ver.version_fingerprint

    # Update config produces a new fingerprint
    updated_ver = registry.update_version_configuration(
        version_id=ver.version_id,
        tenant_id="t1",
        new_configuration=ApplicationConfiguration(environment="STAGING"),
    )
    assert updated_ver.version_fingerprint != initial_fp


def test_immutable_production_version_modification_rejected():
    registry = ApplicationRegistry()
    app = registry.create_application(tenant_id="t1", name="App 1")
    ver = registry.create_version(
        application_id=app.application_id,
        tenant_id="t1",
        version_str="1.0.0",
    )

    # Transition through states to DEPLOYED
    registry.promote_version(ver.version_id, "t1", ApplicationStatus.VALIDATED)
    registry.promote_version(ver.version_id, "t1", ApplicationStatus.REVIEW)
    registry.promote_version(ver.version_id, "t1", ApplicationStatus.APPROVED)
    deployed_ver = registry.promote_version(ver.version_id, "t1", ApplicationStatus.DEPLOYED)

    assert deployed_ver.is_immutable() is True

    # Modifying immutable deployed version MUST fail
    with pytest.raises(ImmutableVersionException):
        registry.update_version_configuration(
            version_id=deployed_ver.version_id,
            tenant_id="t1",
            new_configuration=ApplicationConfiguration(environment="MODIFIED"),
        )
