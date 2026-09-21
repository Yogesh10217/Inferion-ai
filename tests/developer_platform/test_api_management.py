"""Unit tests for APIManagementEngine."""

from app.developer_platform.api_management import APILifecycleState, APIManagementEngine


def test_api_service_lifecycle():
    engine = APIManagementEngine()
    svc = engine.register_api_service("Inference Gateway API", version="2.0.0", tenant_id="t_api")

    assert svc.name == "Inference Gateway API"
    assert svc.status == APILifecycleState.PUBLISHED

    upd = engine.update_status(svc.service_id, APILifecycleState.DEPRECATED)
    assert upd.status == APILifecycleState.DEPRECATED
