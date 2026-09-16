"""Master DataIntelligenceManager (Phase 5.43)."""

import logging
from typing import Any, Dict

from app.data_intelligence.analytics import DataIntelligenceAnalyticsEngine
from app.data_intelligence.anomalies import DataAnomalyManager, DataAnomalySeverity, DataAnomalyType
from app.data_intelligence.billing import DataIntelligenceBillingTracker
from app.data_intelligence.correlation import CorrelationType, DataCorrelationManager
from app.data_intelligence.datasets import DatasetIntelligenceManager, DatasetType
from app.data_intelligence.delegation import DataDelegationManager
from app.data_intelligence.dependencies import DataDependencyManager, DependencyType
from app.data_intelligence.drift import DataDriftManager, DriftType
from app.data_intelligence.evidence import DataEvidenceManager
from app.data_intelligence.freshness import DataFreshnessManager
from app.data_intelligence.governance import DataIntelligenceGovernanceEngine
from app.data_intelligence.impact import DataImpactManager
from app.data_intelligence.incidents import DataIncidentManager, DataIncidentSeverity
from app.data_intelligence.investigations import DataInvestigationManager
from app.data_intelligence.learning import DataLearningManager
from app.data_intelligence.lineage import DataLineageManager, LineageType
from app.data_intelligence.lineage_graph import DataLineageGraphManager
from app.data_intelligence.observability import DataIntelligenceMetricsCollector
from app.data_intelligence.pipeline_reliability import PipelineReliabilityManager
from app.data_intelligence.pipelines import DataPipelineManager
from app.data_intelligence.profiling import DataProfilingManager
from app.data_intelligence.quality import DataQualityDimension, DataQualityManager
from app.data_intelligence.remediation import DataRemediationAction, DataRemediationManager, DataRemediationPriority
from app.data_intelligence.repositories import (
    DataAnomalyRepository,
    DataEvidenceRepository,
    DataIncidentRepository,
    DatasetRepository,
    DataSourceRepository,
)
from app.data_intelligence.risk import DataRiskManager
from app.data_intelligence.schema import SchemaField, SchemaManager
from app.data_intelligence.schema_evolution import SchemaEvolutionManager
from app.data_intelligence.signals import DataSignalManager, DataSignalSource, DataSignalType
from app.data_intelligence.snapshots import DataIntelligenceSnapshotManager
from app.data_intelligence.sources import DataSourceManager, DataSourceType
from app.data_intelligence.trust import DatasetTrustEngine
from app.data_intelligence.validation import DataValidationManager, ValidationType
from app.data_intelligence.verification import DataVerificationManager
from app.platform_contracts.idempotency import IdempotencyManager
from app.platform_contracts.trust import TrustAssessment

logger = logging.getLogger(__name__)


class DataIntelligenceManager:
    """Master Orchestrator for Enterprise AI Data Intelligence Platform."""

    def __init__(self) -> None:
        self.dataset_manager = DatasetIntelligenceManager()
        self.source_manager = DataSourceManager()
        self.profiling_manager = DataProfilingManager()
        self.quality_manager = DataQualityManager()
        self.validation_manager = DataValidationManager()
        self.freshness_manager = DataFreshnessManager()
        self.anomaly_manager = DataAnomalyManager()
        self.drift_manager = DataDriftManager()
        self.schema_manager = SchemaManager()
        self.schema_evolution_manager = SchemaEvolutionManager(schema_manager=self.schema_manager)
        self.lineage_manager = DataLineageManager()
        self.lineage_graph_manager = DataLineageGraphManager(lineage_manager=self.lineage_manager)
        self.pipeline_manager = DataPipelineManager()
        self.pipeline_reliability_manager = PipelineReliabilityManager(pipeline_manager=self.pipeline_manager)
        self.dependency_manager = DataDependencyManager()
        self.impact_manager = DataImpactManager()
        self.incident_manager = DataIncidentManager()
        self.investigation_manager = DataInvestigationManager()
        self.remediation_manager = DataRemediationManager()
        self.governance_engine = DataIntelligenceGovernanceEngine()
        self.delegation_manager = DataDelegationManager()
        self.verification_manager = DataVerificationManager()
        self.evidence_manager = DataEvidenceManager()
        self.trust_engine = DatasetTrustEngine()
        self.risk_manager = DataRiskManager()
        self.correlation_manager = DataCorrelationManager()
        self.signal_manager = DataSignalManager()
        self.snapshot_manager = DataIntelligenceSnapshotManager()
        self.learning_manager = DataLearningManager()
        self.analytics_engine = DataIntelligenceAnalyticsEngine()
        self.metrics_collector = DataIntelligenceMetricsCollector()
        self.billing_tracker = DataIntelligenceBillingTracker()
        self.idempotency_manager = IdempotencyManager()

        # Repositories
        self.dataset_repo = DatasetRepository()
        self.source_repo = DataSourceRepository()
        self.anomaly_repo = DataAnomalyRepository()
        self.incident_repo = DataIncidentRepository()
        self.evidence_repo = DataEvidenceRepository()

        logger.info("[DATA INTELLIGENCE] Master DataIntelligenceManager initialized with all 36 domain engines.")

    def run_full_lifecycle(
        self,
        tenant_id: str,
        dataset_name: str = "prod_features_v1",
        source_name: str = "snowflake_warehouse",
    ) -> Dict[str, Any]:
        """Execute complete 26-step data intelligence lifecycle."""

        # 1. Register Source Reference
        source = self.source_manager.register_source(
            name=source_name,
            tenant_id=tenant_id,
            source_type=DataSourceType.DATA_WAREHOUSE,
            connection_endpoint="snowflake://prod-wh.internal/db",
        )
        self.source_repo.save(source)

        # 2. Register Dataset Reference
        dataset = self.dataset_manager.register_dataset(
            name=dataset_name,
            tenant_id=tenant_id,
            dataset_type=DatasetType.TABLE,
            source_id=source.source_id,
        )
        self.dataset_repo.save(dataset)

        # 3. Profile Dataset
        profile = self.profiling_manager.profile_dataset(dataset.dataset_id, tenant_id, total_records=5000, total_columns=20)
        self.billing_tracker.record_cost_event(tenant_id, dataset.dataset_id, "PROFILING", 0.05)

        # 4. Evaluate Quality
        self.quality_manager.create_rule(dataset.dataset_id, tenant_id, "Completeness Check", DataQualityDimension.COMPLETENESS, min_threshold=0.90)
        quality_result = self.quality_manager.evaluate_quality(dataset.dataset_id, tenant_id)
        self.metrics_collector.set_gauge("quality_score", quality_result.overall_quality_score)

        # 5. Validate Data
        self.validation_manager.create_rule(dataset.dataset_id, tenant_id, "User ID Not Null", ValidationType.CONSTRAINT, "user_id", {"not_null": True})
        validation_result = self.validation_manager.validate_data(dataset.dataset_id, tenant_id, [{"user_id": "usr-123", "age": 30}])

        # 6. Evaluate Freshness
        freshness_ass = self.freshness_manager.evaluate_freshness(dataset.dataset_id, tenant_id)
        self.metrics_collector.set_gauge("freshness_score", freshness_ass.freshness_score)

        # 7. Detect Anomalies
        anomaly = self.anomaly_manager.detect_anomaly(
            dataset.dataset_id,
            tenant_id,
            DataAnomalyType.UNUSUAL_VOLUME,
            DataAnomalySeverity.HIGH,
            metric_name="row_count",
            expected_value=5000.0,
            actual_value=12000.0,
        )
        self.anomaly_repo.save(anomaly)
        self.metrics_collector.increment("anomalies_total")

        # 8. Detect Drift
        drift = self.drift_manager.detect_drift(dataset.dataset_id, tenant_id, DriftType.DISTRIBUTION_DRIFT, 0.45, feature_name="age")
        drift_ass = self.drift_manager.evaluate_drift_assessment(dataset.dataset_id, tenant_id)

        # 9. Evaluate Schema
        schema = self.schema_manager.register_schema(
            dataset.dataset_id,
            tenant_id,
            fields=[SchemaField(name="user_id", data_type="str"), SchemaField(name="age", data_type="int")],
        )

        # 10. Build Lineage
        node1 = self.lineage_manager.register_node(source_name, "SOURCE", tenant_id, source.source_id)
        node2 = self.lineage_manager.register_node(dataset_name, "DATASET", tenant_id, dataset.dataset_id)
        self.lineage_manager.add_relationship(node1.node_id, node2.node_id, LineageType.SOURCE_TO_DATASET, tenant_id)

        # 11. Analyze Dependencies
        self.dependency_manager.register_dependency(dataset.dataset_id, "model-recommendation-v2", DependencyType.DATASET_TO_MODEL, tenant_id)

        # 12. Evaluate Pipeline Health
        pipeline = self.pipeline_manager.register_pipeline("etl_daily_features", tenant_id, input_dataset_ids=[dataset.dataset_id])
        self.pipeline_manager.record_execution(pipeline.pipeline_id, tenant_id, "SUCCESS", records_processed=5000)
        pipe_ass = self.pipeline_manager.evaluate_pipeline_health(pipeline.pipeline_id, tenant_id)

        # 13. Analyze Downstream Impact
        impact_ass = self.impact_manager.evaluate_impact(dataset.dataset_id, tenant_id, downstream_nodes_count=4)

        # 14. Correlate Platform Signals
        sig = self.signal_manager.emit_signal(tenant_id, dataset.dataset_id, DataSignalType.ANOMALY_DETECTED, DataSignalSource.EVENT_INTELLIGENCE)
        corr = self.correlation_manager.correlate(tenant_id, CorrelationType.DATA_ANOMALY_TO_PIPELINE_FAILURE, anomaly.anomaly_id, pipeline.pipeline_id)

        # 15. Calculate Risk
        risk_ass = self.risk_manager.evaluate_risk(dataset.dataset_id, tenant_id, quality_risk=15.0, downstream_risk=80.0 if anomaly else 15.0)

        # 16. Calculate Dataset Trust
        trust_ass: TrustAssessment = self.trust_engine.evaluate_trust(
            dataset.dataset_id,
            tenant_id,
            quality_score=quality_result.overall_quality_score,
            freshness_score=freshness_ass.freshness_score,
            reliability_score=pipe_ass.success_rate_pct / 100.0,
        )
        self.metrics_collector.set_gauge("trust_score", trust_ass.score)

        # 17. Apply Governance
        gov_dec = self.governance_engine.evaluate_governance(tenant_id, dataset.dataset_id, "evaluate_dataset")

        # 18. Create Incident
        incident = self.incident_manager.create_incident(
            dataset.dataset_id,
            tenant_id,
            "Unusual Data Volume Spike",
            DataIncidentSeverity.P2_HIGH,
            anomaly_id=anomaly.anomaly_id,
        )
        self.incident_repo.save(incident)
        self.metrics_collector.increment("incidents_total")

        # 19. Create Remediation Plan & Generate Delegation Request
        rem_plan = self.remediation_manager.create_remediation_plan(
            incident.incident_id,
            dataset.dataset_id,
            tenant_id,
            DataRemediationPriority.P2_HIGH,
            actions=[DataRemediationAction(action_id="act-1", action_type="PIPELINE_RESTART", target_subsystem="orchestration")],
        )
        rem_plan = self.remediation_manager.execute_remediation(rem_plan.plan_id, tenant_id, approved=True)

        # 20. Verification
        verif = self.verification_manager.verify_remediation(dataset.dataset_id, tenant_id, rem_plan.plan_id)

        # 21. Collect Evidence
        evidence = self.evidence_manager.record_evidence(tenant_id, dataset.dataset_id, "QUALITY", quality_result.result_id)
        bundle = self.evidence_manager.create_bundle(tenant_id, dataset.dataset_id, [evidence.evidence_id])
        self.evidence_repo.save(bundle)

        # 22. Investigation
        inv = self.investigation_manager.start_investigation(incident.incident_id, tenant_id, dataset.dataset_id)
        self.investigation_manager.add_finding(inv.investigation_id, tenant_id, "Upstream API Spike", "Third-party vendor API emitted duplicate payload.", "Vendor API change")
        inv = self.investigation_manager.conclude_investigation(inv.investigation_id, tenant_id)

        # 23. Learning Recommendations
        learn_rec = self.learning_manager.generate_recommendation(
            tenant_id,
            dataset.dataset_id,
            "Rate Limit Upstream Ingestion",
            "REMEDIATION_POLICY",
            "Apply rate limiting on source connector",
            reasoning="Prevents volume spike anomalies from upstream vendor APIs.",
        )

        # 24. Analytics
        report = self.analytics_engine.generate_report(tenant_id, avg_dataset_trust_score=trust_ass.score)

        # 25. Immutable Snapshot
        snapshot = self.snapshot_manager.create_snapshot(tenant_id, dataset.dataset_id, {"trust_score": trust_ass.score, "status": "HEALTHY"})

        return {
            "dataset": dataset,
            "source": source,
            "profile": profile,
            "quality_result": quality_result,
            "validation_result": validation_result,
            "freshness_assessment": freshness_ass,
            "anomaly": anomaly,
            "drift_assessment": drift_ass,
            "schema": schema,
            "pipeline": pipeline,
            "impact_assessment": impact_ass,
            "risk_assessment": risk_ass,
            "trust_assessment": trust_ass,
            "governance_decision": gov_dec,
            "incident": incident,
            "remediation_plan": rem_plan,
            "verification": verif,
            "evidence_bundle": bundle,
            "investigation": inv,
            "learning_recommendation": learn_rec,
            "analytics_report": report,
            "snapshot": snapshot,
        }
