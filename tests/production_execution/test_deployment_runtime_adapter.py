import pytest
from app.deployment.deployment_runtime_adapter import (
    ContainerDeploymentRuntimeAdapter,
    SimulationDeploymentRuntimeAdapter,
)
from app.deployment.deployment_target import DeploymentTarget


def test_simulation_adapter_execution():
    target = DeploymentTarget(target_id="t-sim", environment="STAGING", provider="SIMULATION")
    adapter = SimulationDeploymentRuntimeAdapter(target=target)
    val = adapter.validate_target()
    assert val["status"] == "VALIDATED"
    assert val["classification"] == "SIMULATION_RUNTIME_VALIDATED"

    deploy_res = adapter.deploy_artifact(artifact_digest="sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff", release_manifest_id="manifest-1")
    assert deploy_res["status"] == "SIMULATION_DEPLOYED"


def test_container_adapter_execution():
    target = DeploymentTarget(target_id="t-container", environment="STAGING", provider="LOCAL_DOCKER")
    adapter = ContainerDeploymentRuntimeAdapter(target=target)
    val = adapter.validate_target()
    assert val["status"] == "VALIDATED"
    assert val["classification"] == "CONTAINER_RUNTIME_VALIDATED"
