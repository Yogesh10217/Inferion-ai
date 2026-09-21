import pytest

from app.deployment.deployment_simulation import (
    DeploymentLifecycleState,
    DeploymentStateMachine,
    IllegalStateTransitionError,
)
from app.deployment.models import DeploymentIdentity, DeploymentState


@pytest.fixture
def initial_deployment_state():
    identity = DeploymentIdentity(
        application_version="1.0.0",
        deployment_version="5.62",
        build_identifier="build-5.62",
        git_revision="git-562",
        environment="PRODUCTION",
    )
    return DeploymentState(
        status=DeploymentLifecycleState.NOT_EXECUTED.value,
        identity=identity,
    )


def test_state_machine_legal_success_path(initial_deployment_state):
    machine = DeploymentStateMachine(initial_deployment_state)
    assert machine.status == DeploymentLifecycleState.NOT_EXECUTED.value

    machine.transition_to(DeploymentLifecycleState.PREPARING.value)
    assert machine.status == DeploymentLifecycleState.PREPARING.value

    machine.transition_to(DeploymentLifecycleState.VALIDATING.value)
    assert machine.status == DeploymentLifecycleState.VALIDATING.value

    machine.transition_to(DeploymentLifecycleState.DEPLOYING.value)
    assert machine.status == DeploymentLifecycleState.DEPLOYING.value

    machine.transition_to(DeploymentLifecycleState.STARTING.value)
    assert machine.status == DeploymentLifecycleState.STARTING.value

    machine.transition_to(DeploymentLifecycleState.HEALTH_CHECKING.value)
    assert machine.status == DeploymentLifecycleState.HEALTH_CHECKING.value

    machine.transition_to(DeploymentLifecycleState.VALIDATED.value)
    assert machine.status == DeploymentLifecycleState.VALIDATED.value


def test_state_machine_illegal_transition_rejection(initial_deployment_state):
    machine = DeploymentStateMachine(initial_deployment_state)

    # NOT_EXECUTED -> VALIDATED must fail
    with pytest.raises(IllegalStateTransitionError):
        machine.transition_to(DeploymentLifecycleState.VALIDATED.value)

    # NOT_EXECUTED -> ROLLING_BACK must fail
    with pytest.raises(IllegalStateTransitionError):
        machine.transition_to(DeploymentLifecycleState.ROLLING_BACK.value)

    machine.transition_to(DeploymentLifecycleState.PREPARING.value)
    machine.transition_to(DeploymentLifecycleState.VALIDATING.value)
    machine.transition_to(DeploymentLifecycleState.DEPLOYING.value)
    machine.transition_to(DeploymentLifecycleState.STARTING.value)
    machine.transition_to(DeploymentLifecycleState.HEALTH_CHECKING.value)
    machine.transition_to(DeploymentLifecycleState.VALIDATED.value)

    # VALIDATED -> DEPLOYING must fail
    with pytest.raises(IllegalStateTransitionError):
        machine.transition_to(DeploymentLifecycleState.DEPLOYING.value)


def test_state_machine_legal_failure_and_rollback_path(initial_deployment_state):
    machine = DeploymentStateMachine(initial_deployment_state)

    machine.transition_to(DeploymentLifecycleState.PREPARING.value)
    machine.transition_to(DeploymentLifecycleState.VALIDATING.value)
    machine.transition_to(DeploymentLifecycleState.DEPLOYING.value)
    machine.transition_to(DeploymentLifecycleState.STARTING.value)

    # Failure during STARTING
    machine.transition_to(DeploymentLifecycleState.FAILED.value)
    assert machine.status == DeploymentLifecycleState.FAILED.value

    machine.transition_to(DeploymentLifecycleState.ROLLBACK_REQUIRED.value)
    assert machine.status == DeploymentLifecycleState.ROLLBACK_REQUIRED.value

    machine.transition_to(DeploymentLifecycleState.ROLLING_BACK.value)
    assert machine.status == DeploymentLifecycleState.ROLLING_BACK.value

    machine.transition_to(DeploymentLifecycleState.ROLLBACK_VALIDATING.value)
    assert machine.status == DeploymentLifecycleState.ROLLBACK_VALIDATING.value

    machine.transition_to(DeploymentLifecycleState.ROLLED_BACK.value)
    assert machine.status == DeploymentLifecycleState.ROLLED_BACK.value

    # ROLLED_BACK -> HEALTH_CHECKING must fail
    with pytest.raises(IllegalStateTransitionError):
        machine.transition_to(DeploymentLifecycleState.HEALTH_CHECKING.value)
