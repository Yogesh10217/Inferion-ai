"""Master DataGovernanceManager Orchestrator Subsystem."""

import logging
from typing import Any, Dict, List, Optional

from app.data_governance.access import DataAccessDecision, DataAccessManager, DataAccessRequest
from app.data_governance.analytics import DataGovernanceAnalyticsEngine
from app.data_governance.assets import DataAssetManager, DataAssetOwner, DataAssetType, DataDomain
from app.data_governance.billing import DataGovernanceBillingTracker
from app.data_governance.catalog import DataCatalogManager, SchemaFieldMetadata
from app.data_governance.classification import DataClassificationEngine
from app.data_governance.consent import ConsentManager
from app.data_governance.contracts import DataContractManager
from app.data_governance.governance import DataGovernanceEngine
from app.data_governance.lineage import DataLineageManager
from app.data_governance.observability import DataGovernanceMetricsCollector
from app.data_governance.ownership import OwnershipManager, OwnershipRole
from app.data_governance.privacy import PrivacyManager
from app.data_governance.quality import DataQualityManager
from app.data_governance.remediation import DataRemediationManager
from app.data_governance.repositories import DataGovernanceRepository
from app.data_governance.retention import RetentionManager
from app.data_governance.sharing import DataSharingManager
from app.data_governance.trust import DataTrustEngine
from app.data_governance.usage import DataUsageManager

logger = logging.getLogger(__name__)


class DataGovernanceManager:
    """Master Orchestrator unifying all 23 Data Governance, Information Lifecycle & Data Trust Platform modules."""

    def __init__(self) -> None:

        self.repository = DataGovernanceRepository()

        self.asset_manager = DataAssetManager()
        self.catalog_manager = DataCatalogManager(asset_manager=self.asset_manager)
        self.classification_engine = DataClassificationEngine()
        self.ownership_manager = OwnershipManager()
        self.contract_manager = DataContractManager()
        self.quality_manager = DataQualityManager()
        self.lineage_manager = DataLineageManager()
        self.privacy_manager = PrivacyManager()
        self.consent_manager = ConsentManager()
        self.trust_engine = DataTrustEngine()
        self.retention_manager = RetentionManager()
        self.usage_manager = DataUsageManager()

        self.access_manager = DataAccessManager(
            asset_manager=self.asset_manager,
            classification_engine=self.classification_engine,
            consent_manager=self.consent_manager,
            retention_manager=self.retention_manager,
            trust_engine=self.trust_engine,
        )

        self.sharing_manager = DataSharingManager()
        self.governance_engine = DataGovernanceEngine()
        self.remediation_manager = DataRemediationManager()
        self.analytics_engine = DataGovernanceAnalyticsEngine(
            asset_manager=self.asset_manager,
            usage_manager=self.usage_manager,
            trust_engine=self.trust_engine,
        )
        self.metrics_collector = DataGovernanceMetricsCollector()
        self.billing_tracker = DataGovernanceBillingTracker()

        logger.info("[DATA GOVERNANCE MASTER] DataGovernanceManager initialized successfully with all 23 platform modules.")

    def register_and_govern_asset(
        self,
        tenant_id: str,
        name: str,
        asset_type: DataAssetType,
        owner: DataAssetOwner,
        domain: DataDomain = DataDomain.GENERAL,
        source_reference: Optional[Dict[str, Any]] = None,
        schema_fields: Optional[List[SchemaFieldMetadata]] = None,
        content_sample: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Full automated governance flow: Discover/Register -> Classify -> Catalog -> Assign Ownership -> Trust."""

        # 1. Register Asset
        asset = self.asset_manager.register_asset(
            tenant_id=tenant_id,
            name=name,
            asset_type=asset_type,
            owner=owner,
            domain=domain,
            source_reference=source_reference,
        )
        self.metrics_collector.increment("ai_data_governance_assets_total")

        # 2. Classify
        field_names = [f.name for f in schema_fields] if schema_fields else []
        class_res = self.classification_engine.classify_asset(
            tenant_id=tenant_id,
            asset_id=asset.asset_id,
            content_sample=content_sample,
            schema_fields=field_names,
        )
        asset = self.asset_manager.update_asset_classification(
            asset_id=asset.asset_id,
            tenant_id=tenant_id,
            classification=class_res.assigned_level.name,
        )

        # 3. Catalog & Ownership
        catalog_entry = self.catalog_manager.register_catalog_entry(
            tenant_id=tenant_id,
            asset_id=asset.asset_id,
            description=f"Governed asset {asset.name}",
            schema_fields=schema_fields,
        )
        self.ownership_manager.assign_role(
            tenant_id=tenant_id,
            asset_id=asset.asset_id,
            principal_id=owner.owner_id,
            role=OwnershipRole.OWNER,
        )

        # 4. Calculate Trust
        trust_score = self.trust_engine.calculate_trust_score(tenant_id=tenant_id, asset_id=asset.asset_id)
        self.billing_tracker.record_cost(tenant_id=tenant_id, operation_type="CLASSIFICATION", resource_id=asset.asset_id)

        return {
            "asset": asset.model_dump(),
            "classification": class_res.model_dump(),
            "catalog_entry": catalog_entry.model_dump(),
            "trust_score": trust_score.model_dump(),
        }

    def evaluate_access(self, request: DataAccessRequest) -> DataAccessDecision:
        """Central access evaluation enforcing pre-retrieval authorization pipeline."""
        self.metrics_collector.increment("ai_data_governance_access_requests_total")
        decision = self.access_manager.evaluate_access(request)

        if not decision.allowed:
            self.metrics_collector.increment("ai_data_governance_access_denied_total")

        # Log Usage Event
        self.usage_manager.log_usage_event(
            tenant_id=request.tenant_id,
            principal_id=request.principal_id,
            principal_type=request.principal_type,
            asset_id=request.asset_id,
            purpose=request.purpose.value,
            action=request.action,
            authorization_decision=decision.decision.value,
            decision_id=decision.decision_id,
        )
        return decision

    def get_summary(self, tenant_id: str = "global") -> Dict[str, Any]:
        """Aggregate summary for control plane and CLI."""
        report = self.analytics_engine.generate_report(tenant_id)
        metrics = self.metrics_collector.get_metrics_summary()
        return {
            "status": "OPERATIONAL",
            "report": report.model_dump(),
            "metrics": metrics,
        }
