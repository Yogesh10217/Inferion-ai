"""Mandatory 20 E2E Test Flows for Enterprise AI Data Intelligence Platform (Phase 5.43)."""

import pytest

from app.data_intelligence.anomalies import DataAnomalySeverity, DataAnomalyStatus, DataAnomalyType
from app.data_intelligence.datasets import DatasetType
from app.data_intelligence.drift import DriftType
from app.data_intelligence.exceptions import (
    CrossTenantDataIntelligenceException,
    HighRiskDataActionRequiresApprovalException,
    ImmutableDataRecordException,
)
from app.data_intelligence.freshness import FreshnessStatus
from app.data_intelligence.incidents import DataIncidentSeverity, DataIncidentStatus
from app.data_intelligence.investigations import InvestigationStatus
from app.data_intelligence.lineage import LineageType
from app.data_intelligence.lineage_graph import TraversalDirection
from app.data_intelligence.manager import DataIntelligenceManager
from app.data_intelligence.quality import DataQualityDimension, DataQualityStatus
from app.data_intelligence.remediation import DataRemediationAction, DataRemediationPriority, DataRemediationStatus
from app.data_intelligence.schema import SchemaCompatibility, SchemaField
from app.data_intelligence.signals import DataSignalSource, DataSignalType
from app.data_intelligence.verification import VerificationStatus
from app.platform_contracts.delegation import DelegationRequest
from app.platform_contracts.trust import TrustBand


@pytest.fixture
def manager():
    return DataIntelligenceManager()


def test_flow_1_dataset_registration_and_tenant_isolation(manager):
    """Flow 1: Dataset Registration and Tenant Isolation."""
    ds = manager.dataset_manager.register_dataset(
        name="sales_transactions",
        tenant_id="tenant-alpha",
        dataset_type=DatasetType.TABLE,
    )
    assert ds.dataset_id is not None
    assert ds.tenant_id == "tenant-alpha"
    assert ds.name == "sales_transactions"

    fetched = manager.dataset_manager.get_dataset(ds.dataset_id, "tenant-alpha")
    assert fetched.dataset_id == ds.dataset_id


def test_flow_2_cross_tenant_dataset_access_blocked(manager):
    """Flow 2: Cross-Tenant Dataset Access Blocked (Zero Metadata Leakage)."""
    ds = manager.dataset_manager.register_dataset(
        name="confidential_finance",
        tenant_id="tenant-alpha",
    )

    with pytest.raises(CrossTenantDataIntelligenceException) as exc_info:
        manager.dataset_manager.get_dataset(ds.dataset_id, "tenant-beta")

    # MUST leak zero metadata
    assert str(exc_info.value) == "Access denied."
    assert "confidential_finance" not in str(exc_info.value)
    assert "tenant-alpha" not in str(exc_info.value)


def test_flow_3_data_profiling(manager):
    """Flow 3: Data Profiling."""
    ds = manager.dataset_manager.register_dataset(name="customer_churn", tenant_id="tenant-1")
    profile = manager.profiling_manager.profile_dataset(
        dataset_id=ds.dataset_id,
        tenant_id="tenant-1",
        total_records=1000,
        total_columns=15,
        null_count=50,
        duplicate_count=10,
    )

    assert profile.result.total_records_analyzed == 1000
    assert profile.result.overall_completeness > 0.90
    assert profile.result.overall_uniqueness > 0.90
    assert len(profile.result.metrics) >= 4


def test_flow_4_data_quality_evaluation(manager):
    """Flow 4: Data Quality Evaluation across dimensions."""
    ds = manager.dataset_manager.register_dataset(name="order_items", tenant_id="tenant-1")
    manager.quality_manager.create_rule(
        ds.dataset_id, "tenant-1", "Rule 1", DataQualityDimension.COMPLETENESS, min_threshold=0.85
    )
    manager.quality_manager.create_rule(
        ds.dataset_id, "tenant-1", "Rule 2", DataQualityDimension.ACCURACY, min_threshold=0.90
    )

    result = manager.quality_manager.evaluate_quality(ds.dataset_id, "tenant-1")
    assert result.status == DataQualityStatus.PASSED
    assert result.overall_quality_score >= 0.90
    assert DataQualityDimension.COMPLETENESS in result.dimension_scores
    assert DataQualityDimension.ACCURACY in result.dimension_scores


def test_flow_5_data_validation_failure(manager):
    """Flow 5: Data Validation Failure generates explainable validation result."""
    ds = manager.dataset_manager.register_dataset(name="user_profiles", tenant_id="tenant-1")
    manager.validation_manager.create_rule(
        dataset_id=ds.dataset_id,
        tenant_id="tenant-1",
        name="Age Constraint",
        validation_type=manager.validation_manager._rules.get("test")
        or __import__("app.data_intelligence.validation", fromlist=["ValidationType"]).ValidationType.RANGE,
        target_field="age",
        validation_spec={"min": 18, "max": 100},
    )

    sample = [{"age": 12}]  # Underage, violates range [18, 100]
    result = manager.validation_manager.validate_data(ds.dataset_id, "tenant-1", sample)

    assert result.status.value == "FAILED"
    assert result.failed_rules > 0
    assert len(result.failure_reasons) > 0
    assert "age" in result.failure_reasons[0]


def test_flow_6_data_freshness_detection(manager):
    """Flow 6: Data Freshness Detection identifies stale datasets."""
    ds = manager.dataset_manager.register_dataset(name="realtime_stream", tenant_id="tenant-1")
    manager.freshness_manager.set_policy(
        ds.dataset_id, "tenant-1", expected_interval_minutes=15, max_allowed_delay_minutes=30
    )

    from datetime import datetime, timedelta, timezone

    stale_time = datetime.now(timezone.utc) - timedelta(hours=5)

    ass = manager.freshness_manager.evaluate_freshness(ds.dataset_id, "tenant-1", last_updated_at=stale_time)

    assert ass.freshness.status in (FreshnessStatus.STALE, FreshnessStatus.CRITICAL_STALE)
    assert ass.freshness_score < 0.5


def test_flow_7_data_anomaly_detection(manager):
    """Flow 7: Data Anomaly Detection detects abnormal pattern spikes."""
    ds = manager.dataset_manager.register_dataset(name="web_clicks", tenant_id="tenant-1")
    anom = manager.anomaly_manager.detect_anomaly(
        dataset_id=ds.dataset_id,
        tenant_id="tenant-1",
        anomaly_type=DataAnomalyType.UNUSUAL_VOLUME,
        severity=DataAnomalySeverity.HIGH,
        metric_name="clicks_per_sec",
        expected_value=100.0,
        actual_value=5000.0,
    )

    assert anom.anomaly_id is not None
    assert anom.evidence.deviation_pct > 100.0
    assert anom.status == DataAnomalyStatus.DETECTED


def test_flow_8_data_drift_detection(manager):
    """Flow 8: Data Drift Detection evaluates distribution/schema drift."""
    ds = manager.dataset_manager.register_dataset(name="model_features", tenant_id="tenant-1")
    manager.drift_manager.detect_drift(
        ds.dataset_id, "tenant-1", DriftType.DISTRIBUTION_DRIFT, 0.65, feature_name="income"
    )

    ass = manager.drift_manager.evaluate_drift_assessment(ds.dataset_id, "tenant-1")
    assert ass.overall_drift_detected is True
    assert ass.max_drift_score == 0.65


def test_flow_9_lineage_traversal(manager):
    """Flow 9: Upstream and Downstream Lineage Traversal."""
    n1 = manager.lineage_manager.register_node("raw_db", "SOURCE", "tenant-1", "src-1")
    n2 = manager.lineage_manager.register_node("stage_table", "DATASET", "tenant-1", "ds-1")
    n3 = manager.lineage_manager.register_node("scoring_model", "MODEL", "tenant-1", "mdl-1")

    manager.lineage_manager.add_relationship(n1.node_id, n2.node_id, LineageType.SOURCE_TO_DATASET, "tenant-1")
    manager.lineage_manager.add_relationship(n2.node_id, n3.node_id, LineageType.DATASET_TO_MODEL, "tenant-1")

    res = manager.lineage_graph_manager.traverse("tenant-1", n1.node_id, TraversalDirection.DOWNSTREAM)
    assert n3.node_id in res.visited_node_ids
    assert "mdl-1" in res.impacted_models


def test_flow_10_schema_breaking_change_detection(manager):
    """Flow 10: Schema Breaking Change Detection."""
    f1 = SchemaField(name="id", data_type="int")
    f2 = SchemaField(name="email", data_type="str")

    manager.schema_manager.register_schema("ds-schema-test", "tenant-1", [f1, f2])

    # Target fields removing 'email' -> breaking change
    assessment = manager.schema_manager.compare_schemas("ds-schema-test", "tenant-1", [f1])

    assert assessment.is_breaking_change is True
    assert assessment.compatibility == SchemaCompatibility.INCOMPATIBLE
    assert "email" in assessment.removed_fields


def test_flow_11_pipeline_reliability_failure(manager):
    """Flow 11: Pipeline Reliability Failure affects dataset health."""
    pipe = manager.pipeline_manager.register_pipeline("daily_ingest", "tenant-1")
    manager.pipeline_reliability_manager.record_failure(pipe.pipeline_id, "tenant-1", "TIMEOUT", "Execution timed out")

    ass = manager.pipeline_reliability_manager.evaluate_reliability("tenant-1", pipe.pipeline_id)
    assert ass.failures_count == 1
    assert ass.overall_reliability_score < 1.0


def test_flow_12_downstream_impact_analysis(manager):
    """Flow 12: Downstream Impact Analysis identifies affected models & pipelines."""
    ds = manager.dataset_manager.register_dataset(name="core_users", tenant_id="tenant-1")
    impact = manager.impact_manager.evaluate_impact(
        ds.dataset_id, "tenant-1", downstream_nodes_count=6, is_sensitive=True
    )

    assert impact.overall_impact_score > 30.0
    assert impact.impacted_models_count > 0
    assert impact.impacted_pipelines_count > 0


def test_flow_13_data_incident_creation(manager):
    """Flow 13: Data Incident Creation from severe anomaly."""
    ds = manager.dataset_manager.register_dataset(name="orders", tenant_id="tenant-1")
    anom = manager.anomaly_manager.detect_anomaly(
        ds.dataset_id, "tenant-1", DataAnomalyType.MISSING_RECORDS, DataAnomalySeverity.CRITICAL, "rows", 1000, 0
    )

    inc = manager.incident_manager.create_incident(
        ds.dataset_id,
        "tenant-1",
        "Zero Order Ingestion",
        DataIncidentSeverity.P1_CRITICAL,
        anomaly_id=anom.anomaly_id,
    )

    assert inc.incident_id is not None
    assert inc.severity == DataIncidentSeverity.P1_CRITICAL
    assert inc.status == DataIncidentStatus.DETECTED


def test_flow_14_high_risk_remediation_requires_approval(manager):
    """Flow 14: High-Risk Remediation Requires Approval."""
    ds = manager.dataset_manager.register_dataset(name="prod_logs", tenant_id="tenant-1")
    inc = manager.incident_manager.create_incident(
        ds.dataset_id, "tenant-1", "Data corruption", DataIncidentSeverity.P1_CRITICAL
    )

    action = DataRemediationAction(
        action_id="a1", action_type="DATASET_ROLLBACK", target_subsystem="data_fabric", is_high_risk=True
    )

    with pytest.raises(HighRiskDataActionRequiresApprovalException) as exc_info:
        manager.remediation_manager.create_remediation_plan(
            inc.incident_id,
            ds.dataset_id,
            "tenant-1",
            DataRemediationPriority.P1_CRITICAL,
            actions=[action],
        )

    assert "requires human approval" in str(exc_info.value)


def test_flow_15_delegation_only_enforcement(manager):
    """Flow 15: Delegation-Only Enforcement via DelegationRequest."""
    ds = manager.dataset_manager.register_dataset(name="sales", tenant_id="tenant-1")
    action = DataRemediationAction(action_id="a1", action_type="PIPELINE_RESTART", target_subsystem="orchestration")

    plan = manager.remediation_manager.create_remediation_plan(
        "inc-123", ds.dataset_id, "tenant-1", DataRemediationPriority.P3_MEDIUM, actions=[action]
    )
    plan = manager.remediation_manager.execute_remediation(plan.plan_id, "tenant-1", approved=False)

    assert plan.status == DataRemediationStatus.DELEGATED
    assert len(plan.delegation_requests) == 1
    assert isinstance(plan.delegation_requests[0], DelegationRequest)
    assert plan.delegation_requests[0].target == "ORCHESTRATION"


def test_flow_16_sensitive_data_redaction(manager):
    """Flow 16: Sensitive Data Redaction in signals and evidence."""
    sig = manager.signal_manager.emit_signal(
        tenant_id="tenant-1",
        dataset_id="ds-1",
        signal_type=DataSignalType.QUALITY_DEGRADED,
        source=DataSignalSource.DATA_GOVERNANCE,
        payload={"secret_token": "sk-secret-123", "user_email": "alice@example.com"},
    )

    assert sig.sanitized_payload.get("secret_token") != "sk-secret-123"


def test_flow_17_immutable_evidence(manager):
    """Flow 17: Immutable Evidence prevents modification."""
    ev = manager.evidence_manager.record_evidence("tenant-1", "ds-1", "QUALITY", "ref-1")
    bundle = manager.evidence_manager.create_bundle("tenant-1", "ds-1", [ev.evidence_id])

    manager.evidence_repo.save(bundle)

    with pytest.raises(ImmutableDataRecordException):
        manager.evidence_repo.save(bundle)


def test_flow_18_dataset_trust_assessment(manager):
    """Flow 18: Dataset Trust Assessment combines quality, freshness, lineage, reliability, anomalies."""
    trust = manager.trust_engine.evaluate_trust(
        dataset_id="ds-trust-1",
        tenant_id="tenant-1",
        quality_score=0.98,
        freshness_score=0.95,
        lineage_score=1.0,
        reliability_score=0.99,
        anomaly_score=1.0,
    )

    assert trust.score >= 90.0
    assert trust.band == TrustBand.HIGH_TRUST
    assert len(trust.dimensions) == 7


def test_flow_19_learning_does_not_auto_execute(manager):
    """Flow 19: Advisory Learning enforces auto_execute=False."""
    rec = manager.learning_manager.generate_recommendation(
        tenant_id="tenant-1",
        dataset_id="ds-1",
        title="Optimize Freshness SLA",
        recommendation_type="SCHEDULE_OPTIMIZATION",
        proposed_action="Increase sync frequency to 15m",
        reasoning="Prevents lagging freshness score.",
    )

    assert rec.auto_execute is False


def test_flow_20_full_enterprise_data_intelligence_lifecycle(manager):
    """Flow 20: Full Enterprise Data Intelligence Lifecycle from dataset to snapshot."""
    res = manager.run_full_lifecycle(tenant_id="tenant-e2e-20")

    assert res["dataset"].dataset_id is not None
    assert res["source"].source_id is not None
    assert res["profile"].profile_id is not None
    assert res["quality_result"].status == DataQualityStatus.PASSED
    assert res["validation_result"].status.value == "PASSED"
    assert res["freshness_assessment"].freshness.status is not None
    assert res["anomaly"].anomaly_id is not None
    assert res["drift_assessment"].assessment_id is not None
    assert res["schema"].schema_id is not None
    assert res["pipeline"].pipeline_id is not None
    assert res["impact_assessment"].assessment_id is not None
    assert res["risk_assessment"].assessment_id is not None
    assert res["trust_assessment"].score > 0
    assert res["governance_decision"].status is not None
    assert res["incident"].incident_id is not None
    assert res["remediation_plan"].status == DataRemediationStatus.DELEGATED
    assert res["verification"].status == VerificationStatus.PASSED
    assert res["evidence_bundle"].bundle_fingerprint is not None
    assert res["investigation"].status == InvestigationStatus.CONCLUDED
    assert res["learning_recommendation"].auto_execute is False
    assert res["analytics_report"].report_id is not None
    assert res["snapshot"].snapshot_id is not None
