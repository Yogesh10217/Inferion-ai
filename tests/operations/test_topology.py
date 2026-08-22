"""Unit tests for TopologyManager directed dependency graph and health propagation."""

import pytest
from app.operations.topology import TopologyManager


def test_topology_graph_and_impact_analysis():
    mgr = TopologyManager()

    mgr.register_node("db_primary", "Primary Database", "DATABASE", tenant_id="t_top")
    mgr.register_node("service_auth", "Auth Service", "SERVICE", tenant_id="t_top")
    mgr.register_node("gateway_api", "API Gateway", "GATEWAY", tenant_id="t_top")

    # Dependencies: API Gateway -> Auth Service -> Primary DB
    mgr.add_dependency("gateway_api", "service_auth", "HARD", tenant_id="t_top")
    mgr.add_dependency("service_auth", "db_primary", "HARD", tenant_id="t_top")

    # Update DB health to UNHEALTHY
    mgr.update_node_health("db_primary", "UNHEALTHY")

    # Analyze impact of DB failure
    impact = mgr.analyze_impact("db_primary", tenant_id="t_top")

    assert "service_auth" in impact.affected_nodes
    assert "gateway_api" in impact.affected_nodes
    assert impact.blast_radius_score > 0.0
