"""Unit tests for Service Catalog Manager."""

import pytest

from app.platform_operations.exceptions import ServiceNotFoundException
from app.platform_operations.services import ServiceCatalogManager, ServiceHealth, ServiceTier


def test_register_and_get_service():
    mgr = ServiceCatalogManager()
    svc = mgr.register_service(
        tenant_id="t1", name="Inference Gateway Service", service_tier=ServiceTier.TIER_0_CRITICAL
    )
    assert svc.service_id.startswith("svc_")
    assert svc.name == "Inference Gateway Service"

    fetched = mgr.get_service(svc.service_id, "t1")
    assert fetched.name == "Inference Gateway Service"


def test_service_not_found():
    mgr = ServiceCatalogManager()
    with pytest.raises(ServiceNotFoundException):
        mgr.get_service("invalid_id", "t1")


def test_update_service_health():
    mgr = ServiceCatalogManager()
    svc = mgr.register_service(tenant_id="t1", name="Model Router")
    assert svc.health == ServiceHealth.HEALTHY

    updated = mgr.update_service_health(svc.service_id, "t1", ServiceHealth.DEGRADED)
    assert updated.health == ServiceHealth.DEGRADED
