import pytest
from app.deployment.models import ProductionDeploymentState
from app.deployment.production_deployment_state_machine import ProductionDeploymentStateMachine


def test_state_machine_valid_transition_path():
    sm = ProductionDeploymentStateMachine(initial_state=ProductionDeploymentState.NOT_EXECUTED)
    assert sm.current_state == ProductionDeploymentState.NOT_EXECUTED

    sm.transition_to(ProductionDeploymentState.AUTHORIZATION_REQUIRED, "Req auth")
    assert sm.current_state == ProductionDeploymentState.AUTHORIZATION_REQUIRED

    sm.transition_to(ProductionDeploymentState.AUTHORIZED, "Auth granted")
    assert sm.current_state == ProductionDeploymentState.AUTHORIZED

    sm.transition_to(ProductionDeploymentState.PREFLIGHT_VALIDATING, "Preflight start")
    assert sm.current_state == ProductionDeploymentState.PREFLIGHT_VALIDATING

    assert len(sm.history) == 3
    assert sm.history[0].fingerprint.startswith("sha256:")
