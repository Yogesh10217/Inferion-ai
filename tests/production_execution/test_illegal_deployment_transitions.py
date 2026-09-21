import pytest

from app.deployment.exceptions import IllegalStateTransitionError
from app.deployment.models import ProductionDeploymentState
from app.deployment.production_deployment_state_machine import ProductionDeploymentStateMachine


def test_illegal_state_transitions_rejected():
    sm = ProductionDeploymentStateMachine(initial_state=ProductionDeploymentState.NOT_EXECUTED)

    # NOT_EXECUTED -> DEPLOYMENT_VALIDATED must be rejected
    with pytest.raises(IllegalStateTransitionError):
        sm.transition_to(ProductionDeploymentState.DEPLOYMENT_VALIDATED, "Illegal jump")

    # NOT_EXECUTED -> AUTHORIZED must be rejected
    with pytest.raises(IllegalStateTransitionError):
        sm.transition_to(ProductionDeploymentState.AUTHORIZED, "Illegal jump")
