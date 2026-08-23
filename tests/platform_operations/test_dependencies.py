"""Unit tests for Service Dependency Graph Resolution."""

import pytest
from app.platform_operations.services import ServiceCatalogManager, ServiceDependencyType


def test_dependency_graph_resolution():
    mgr = ServiceCatalogManager()
    s1 = mgr.register_service("t1", "API Gateway")
    s2 = mgr.register_service("t1", "Auth Service")
    s3 = mgr.register_service("t1", "Database Cluster")

    mgr.add_dependency("t1", source_service_id=s1.service_id, target_service_id=s2.service_id)
    mgr.add_dependency("t1", source_service_id=s2.service_id, target_service_id=s3.service_id)

    # Test upstream resolution for s1 (API Gateway -> Auth -> Database)
    upstreams = mgr.resolve_dependencies(s1.service_id, "t1", direction=ServiceDependencyType.UPSTREAM, transitive=True)
    upstream_ids = [u.service_id for u in upstreams]
    assert s2.service_id in upstream_ids
    assert s3.service_id in upstream_ids

    # Test downstream resolution for s3 (Database -> Auth -> API Gateway)
    downstreams = mgr.resolve_dependencies(s3.service_id, "t1", direction=ServiceDependencyType.DOWNSTREAM, transitive=True)
    downstream_ids = [d.service_id for d in downstreams]
    assert s1.service_id in downstream_ids
    assert s2.service_id in downstream_ids
