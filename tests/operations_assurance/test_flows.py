"""E2E Flow Tests for Phase 5.49 Enterprise AI Operations Assurance Platform."""

import pytest

from app.operations_assurance.anomalies import AnomalyCategory
from app.operations_assurance.capacity import CapacityResourceType, CapacityRiskLevel
from app.operations_assurance.events import OperationalEventType, OperationalSeverity
from app.operations_assurance.exceptions import (
    CrossTenantOperationsAssuranceException,
    ImmutableOperationalRecordException,
)
from app.operations_assurance.forecasting import ForecastScenario
from app.operations_assurance.governance import OperationsGovernanceOutcome, OperationsGovernanceRequest
from app.operations_assurance.incidents import OperationalIncidentSeverity, OperationalIncidentState
from app.operations_assurance.manager import OperationsAssuranceManager
from app.operations_assurance.root_cause import RootCauseCategory
from app.operations_assurance.service_dependencies import DependencyCriticality, DependencyType
from app.operations_assurance.service_health import ServiceHealthStatus
from app.operations_assurance.services import ServiceType


@pytest.fixture
def manager() -> OperationsAssuranceManager:
    return OperationsAssuranceManager()


def test_flow_01_service_registration_and_tenant_isolation(manager: OperationsAssuranceManager):
    """Flow 1: Service registration and tenant isolation."""
    svc_a = manager.register_service("tenant_a", "InferenceGateway", ServiceType.API_GATEWAY)
    svc_b = manager.register_service("tenant_b", "VectorSearch", ServiceType.MICROSERVICE)

    assert svc_a.tenant_id == "tenant_a"
    assert svc_b.tenant_id == "tenant_b"

    services_a = manager.service_manager.list_services("tenant_a")
    assert len(services_a) == 1
    assert services_a[0].name == "InferenceGateway"


def test_flow_02_cross_tenant_access_blocked_with_zero_metadata_leakage(manager: OperationsAssuranceManager):
    """Flow 2: Cross-tenant access blocked with zero metadata leakage."""
    svc_a = manager.register_service("tenant_a", "SecretService", ServiceType.MICROSERVICE)

    with pytest.raises(CrossTenantOperationsAssuranceException) as exc_info:
        manager.service_manager.get_service("tenant_b", svc_a.service_id)

    # Ensure zero metadata leakage in exception detail
    err_str = str(exc_info.value)
    assert svc_a.service_id not in err_str
    assert "SecretService" not in err_str
    assert "tenant_a" not in err_str


def test_flow_03_service_health_assessment(manager: OperationsAssuranceManager):
    """Flow 3: Service health assessment."""
    svc = manager.register_service("tenant_a", "ModelServingAPI", ServiceType.API_GATEWAY)

    health = manager.health_manager.evaluate_health(
        tenant_id="tenant_a",
        service_id=svc.service_id,
        availability=0.99,
        latency_p99_ms=150.0,
        error_rate=0.01,
        active_incidents=0,
    )

    assert health.status in [ServiceHealthStatus.GOOD, ServiceHealthStatus.EXCELLENT]
    assert len(health.explanations) > 0


def test_flow_04_service_dependency_mapping(manager: OperationsAssuranceManager):
    """Flow 4: Service dependency mapping across APIs, DBs, Models, Agents."""
    svc = manager.register_service("tenant_a", "AgentOrchestrator", ServiceType.AGENT_SERVICE)

    dep1 = manager.dependency_manager.add_dependency(
        tenant_id="tenant_a",
        source_service_id=svc.service_id,
        target_id="llm-model-v1",
        dependency_type=DependencyType.MODEL,
        criticality=DependencyCriticality.CRITICAL,
    )
    manager.dependency_manager.add_dependency(
        tenant_id="tenant_a",
        source_service_id=svc.service_id,
        target_id="redis-cache-cluster",
        dependency_type=DependencyType.DATABASE,
        criticality=DependencyCriticality.HIGH,
    )

    deps = manager.dependency_manager.list_dependencies_for_service("tenant_a", svc.service_id)
    assert len(deps) == 2
    assert dep1.dependency_type == DependencyType.MODEL


def test_flow_05_dependency_graph_traversal(manager: OperationsAssuranceManager):
    """Flow 5: Analytical dependency graph traversal."""
    graph = manager.dependency_graph
    graph.add_edge("tenant_a", "Frontend", "APIGateway")
    graph.add_edge("tenant_a", "APIGateway", "ModelInference")
    graph.add_edge("tenant_a", "ModelInference", "GPUCluster")

    upstream = graph.get_upstream("tenant_a", "Frontend")
    assert "APIGateway" in upstream
    assert "ModelInference" in upstream
    assert "GPUCluster" in upstream

    downstream = graph.get_downstream("tenant_a", "GPUCluster")
    assert "ModelInference" in downstream
    assert "APIGateway" in downstream
    assert "Frontend" in downstream


def test_flow_06_operational_event_correlation(manager: OperationsAssuranceManager):
    """Flow 6: Operational event correlation."""
    svc = manager.register_service("tenant_a", "PaymentProcessor", ServiceType.MICROSERVICE)

    manager.event_manager.record_event(
        tenant_id="tenant_a",
        service_id=svc.service_id,
        event_type=OperationalEventType.LATENCY_SPIKE,
        summary="Latency p99 exceeded 500ms threshold.",
        severity=OperationalSeverity.HIGH,
    )

    evts = manager.event_manager.list_events_for_service("tenant_a", svc.service_id)
    assert len(evts) == 1
    assert evts[0].event_type == OperationalEventType.LATENCY_SPIKE


def test_flow_07_operational_anomaly_detection(manager: OperationsAssuranceManager):
    """Flow 7: Operational anomaly detection."""
    svc = manager.register_service("tenant_a", "KnowledgeRAG", ServiceType.MICROSERVICE)

    metrics = {
        "error_rate": 0.12,
        "latency_p99_ms": 650.0,
        "cpu_saturation": 0.92,
    }
    anomalies = manager.anomaly_detector.detect_anomalies("tenant_a", svc.service_id, metrics)
    assert len(anomalies) >= 3

    categories = [a.category for a in anomalies]
    assert AnomalyCategory.ERROR_SPIKE in categories
    assert AnomalyCategory.LATENCY_SPIKE in categories
    assert AnomalyCategory.RESOURCE_SATURATION in categories


def test_flow_08_reliability_assessment(manager: OperationsAssuranceManager):
    """Flow 8: Reliability assessment (MTBF, MTTR, stability index)."""
    svc = manager.register_service("tenant_a", "DatabaseService", ServiceType.DATABASE)

    rel = manager.reliability_engine.assess_reliability(
        tenant_id="tenant_a",
        service_id=svc.service_id,
        availability=0.999,
        mtbf_hours=720.0,
        mttr_minutes=10.0,
        failures_30d=1,
    )

    assert rel.reliability_score >= 0.85
    assert rel.mtbf_hours == 720.0
    assert rel.mttr_minutes == 10.0


def test_flow_09_availability_and_slo_assessment(manager: OperationsAssuranceManager):
    """Flow 9: Availability and SLO assessment."""
    svc = manager.register_service("tenant_a", "SearchEngine", ServiceType.MICROSERVICE)

    report = manager.availability_engine.evaluate_availability(
        tenant_id="tenant_a",
        service_id=svc.service_id,
        uptime_percentage=99.95,
        slo_target=99.90,
    )

    assert report.slo_status == "MET"
    assert report.error_budget_remaining_percentage > 0.0


def test_flow_10_performance_degradation_detection(manager: OperationsAssuranceManager):
    """Flow 10: Performance degradation detection."""
    svc = manager.register_service("tenant_a", "AnalyticsPipeline", ServiceType.DATA_PIPELINE)

    perf = manager.performance_engine.analyze_performance(
        tenant_id="tenant_a",
        service_id=svc.service_id,
        latency_p99=600.0,
        error_rate=0.08,
    )

    assert perf.trend == "CRITICAL"


def test_flow_11_capacity_risk_assessment(manager: OperationsAssuranceManager):
    """Flow 11: Capacity risk assessment (Advisory guidance only)."""
    svc = manager.register_service("tenant_a", "InferencePool", ServiceType.AI_MODEL_SERVICE)

    assessment = manager.capacity_engine.evaluate_capacity(
        tenant_id="tenant_a",
        service_id=svc.service_id,
        resource_type=CapacityResourceType.AI_INFERENCE_CAPACITY,
        current_utilization=0.82,
        projected_utilization=0.94,
    )

    assert assessment.risk_level == CapacityRiskLevel.CRITICAL
    assert assessment.auto_execute is False  # Mandatory invariant


def test_flow_12_operational_forecasting(manager: OperationsAssuranceManager):
    """Flow 12: Operational forecasting under multiple scenarios."""
    svc = manager.register_service("tenant_a", "AuthServer", ServiceType.MICROSERVICE)

    forecast = manager.forecasting_engine.generate_forecast(
        tenant_id="tenant_a",
        service_id=svc.service_id,
        scenario=ForecastScenario.HIGH_DEMAND,
        horizon_days=60,
    )

    assert forecast.scenario == ForecastScenario.HIGH_DEMAND
    assert forecast.horizon_days == 60
    assert forecast.auto_execute is False


def test_flow_13_operational_incident_creation(manager: OperationsAssuranceManager):
    """Flow 13: Operational incident lifecycle state machine."""
    svc = manager.register_service("tenant_a", "BillingService", ServiceType.MICROSERVICE)

    inc = manager.incident_manager.create_incident(
        tenant_id="tenant_a",
        service_id=svc.service_id,
        title="Payment Gateway Timeout",
        severity=OperationalIncidentSeverity.SEV1,
    )
    assert inc.state == OperationalIncidentState.DETECTED

    inc_updated = manager.incident_manager.transition_state(
        tenant_id="tenant_a",
        incident_id=inc.incident_id,
        new_state=OperationalIncidentState.INVESTIGATING,
    )
    assert inc_updated.state == OperationalIncidentState.INVESTIGATING


def test_flow_14_explainable_root_cause_analysis(manager: OperationsAssuranceManager):
    """Flow 14: Explainable root cause analysis."""
    svc = manager.register_service("tenant_a", "DocumentProcessor", ServiceType.MICROSERVICE)

    rca = manager.root_cause_engine.analyze_root_cause(
        tenant_id="tenant_a",
        service_id=svc.service_id,
        category=RootCauseCategory.DEPENDENCY_FAILURE,
        summary="Upstream Storage Service connection timeout.",
        confidence=0.92,
        evidence=[{"log_id": "log-102", "error": "ETIMEDOUT"}],
    )

    assert rca.primary_category == RootCauseCategory.DEPENDENCY_FAILURE
    assert rca.confidence_score == 0.92
    assert len(rca.evidence_items) == 1


def test_flow_15_blast_radius_analysis(manager: OperationsAssuranceManager):
    """Flow 15: Operational blast radius analysis."""
    assessment = manager.blast_radius_engine.evaluate_blast_radius(
        tenant_id="tenant_a",
        target_id="core-auth-service",
        affected_services=["service1", "service2", "service3", "service4", "service5", "service6"],
        affected_users=2500,
    )

    assert assessment.impact_level in ["EXTENSIVE", "CATASTROPHIC"]
    assert assessment.affected_users_count == 2500


def test_flow_16_cross_domain_operational_correlation(manager: OperationsAssuranceManager):
    """Flow 16: Cross-domain operational correlation (Model + Latency + Infra)."""
    result = manager.correlation_engine.correlate(
        tenant_id="tenant_a",
        target_service_id="llm-rag-service",
        model_degraded=True,
        service_latency_high=True,
        infra_saturated=True,
    )

    assert result.risk_score >= 0.8
    assert len(result.correlated_domains) == 3


def test_flow_17_high_risk_action_requires_human_approval(manager: OperationsAssuranceManager):
    """Flow 17: Governance evaluation for high-risk operational action returning REQUIRE_APPROVAL."""
    req = OperationsGovernanceRequest(
        tenant_id="tenant_a",
        action_type="PRODUCTION_SERVICE_RESTART",
        target_resource_id="prod-db-01",
    )

    res = manager.governance_engine.evaluate_action(req)
    assert res.outcome == OperationsGovernanceOutcome.REQUIRE_APPROVAL
    assert res.requires_human_approval is True


def test_flow_18_delegation_only_execution_enforcement(manager: OperationsAssuranceManager):
    """Flow 18: Delegation-Only execution enforcement producing DelegationRequest."""
    plan = manager.remediation_planner.create_remediation_plan(
        tenant_id="tenant_a",
        service_id="svc-123",
        action_type="RESTART_SERVICE",
    )

    assert plan.delegation_request is not None
    assert plan.delegation_request.action == "RESTART_SERVICE"
    assert plan.requires_approval is True


def test_flow_19_metadata_sanitization_and_immutable_sha256_evidence(manager: OperationsAssuranceManager):
    """Flow 19: Metadata sanitization and immutable SHA-256 evidence enforcement."""
    content = {
        "event": "service_restart",
        "secret_token": "SUPER_SECRET_TOKEN_123",
        "api_key": "KEY_98765",
    }

    evidence = manager.evidence_manager.record_evidence(
        tenant_id="tenant_a",
        service_id="svc-1",
        evidence_type="OPERATIONAL_AUDIT",
        content=content,
    )

    assert evidence.sha256_hash != ""
    assert evidence.content.get("secret_token") == "[REDACTED]"
    assert evidence.content.get("api_key") == "[REDACTED]"

    # Test immutability enforcement
    with pytest.raises(ImmutableOperationalRecordException):
        manager.evidence_manager.update_evidence("tenant_a", evidence.evidence_id, {"event": "tampered"})


def test_flow_20_full_enterprise_operations_assurance_lifecycle(manager: OperationsAssuranceManager):
    """Flow 20: Full enterprise operations assurance lifecycle including advisory learning with auto_execute=False."""
    # 1. Register service
    svc = manager.register_service("tenant_corp", "CoreInferenceCluster", ServiceType.AI_MODEL_SERVICE)

    # 2. Evaluate assurance
    assurance = manager.evaluate_assurance("tenant_corp", svc.service_id)
    assert assurance.overall_score > 0.0

    # 3. Create investigation & conclude with snapshot
    inv = manager.investigation_manager.create_investigation("tenant_corp", svc.service_id)
    snap = manager.investigation_manager.conclude_investigation(
        tenant_id="tenant_corp",
        investigation_id=inv.investigation_id,
        findings=[],
    )
    assert snap.metadata.snapshot_id != ""

    # 4. Record advisory learning
    learning = manager.learning_manager.record_learning(
        tenant_id="tenant_corp",
        service_id=svc.service_id,
        event_summary="High latency spike resolved via cache adjustment.",
        learned_insight="Cache size allocation must be pre-warmed for high demand.",
    )
    assert learning.auto_execute is False  # Mandatory invariant!

    # 5. Generate analytics report
    report = manager.analytics_engine.generate_report("tenant_corp")
    assert report.tenant_id == "tenant_corp"
