"""Unit tests for RootCauseAnalysisEngine."""

from app.operations.root_cause import RootCauseAnalysisEngine
from app.operations.topology import TopologyManager


def test_root_cause_analysis_ranking():
    top_mgr = TopologyManager()
    top_mgr.register_node("db_pool", "DB Pool", "DATABASE", tenant_id="t_rca")
    top_mgr.register_node("auth_service", "Auth Service", "SERVICE", tenant_id="t_rca")
    top_mgr.add_dependency("auth_service", "db_pool", "HARD", tenant_id="t_rca")

    top_mgr.update_node_health("db_pool", "UNHEALTHY")

    rca_engine = RootCauseAnalysisEngine(topology_manager=top_mgr)
    rca = rca_engine.analyze_incident(
        incident_id="inc_100",
        failed_resource_id="db_pool",
        recent_changes=[
            {"resource_id": "auth_service", "change_type": "DEPLOYMENT", "timestamp": "2026-08-22T10:00:00Z"}
        ],
        tenant_id="t_rca",
    )

    assert len(rca.candidates) >= 1
    assert rca.primary_cause_id is not None
