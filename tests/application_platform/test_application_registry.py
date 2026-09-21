"""Unit tests for Application Registry and status transitions."""

import pytest

from app.application_platform.application import (
    ApplicationLifecycle,
    ApplicationRegistry,
    ApplicationStatus,
    ApplicationType,
)
from app.application_platform.exceptions import (
    ApplicationNotFoundException,
    InvalidLifecycleTransitionException,
)


def test_create_and_get_application():
    registry = ApplicationRegistry()
    app = registry.create_application(
        tenant_id="tenant_a",
        name="Support Copilot",
        app_type=ApplicationType.COPILOT,
    )
    assert app.name == "Support Copilot"
    assert app.tenant_id == "tenant_a"

    fetched = registry.get_application(app.application_id, "tenant_a")
    assert fetched.application_id == app.application_id


def test_application_not_found():
    registry = ApplicationRegistry()
    with pytest.raises(ApplicationNotFoundException):
        registry.get_application("non_existent", "tenant_a")


def test_valid_lifecycle_transitions():
    assert (
        ApplicationLifecycle.transition_status(ApplicationStatus.DRAFT, ApplicationStatus.VALIDATED)
        == ApplicationStatus.VALIDATED
    )
    assert (
        ApplicationLifecycle.transition_status(ApplicationStatus.APPROVED, ApplicationStatus.DEPLOYED)
        == ApplicationStatus.DEPLOYED
    )
    assert (
        ApplicationLifecycle.transition_status(ApplicationStatus.DEPLOYED, ApplicationStatus.ACTIVE)
        == ApplicationStatus.ACTIVE
    )


def test_invalid_lifecycle_transition():
    with pytest.raises(InvalidLifecycleTransitionException):
        ApplicationLifecycle.transition_status(ApplicationStatus.DRAFT, ApplicationStatus.ACTIVE)
