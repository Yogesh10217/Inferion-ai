"""Master Data Fabric Manager unifying sources, connectors, ingestion, sync, catalog, governance, and lineage."""

import logging
from typing import Any, Dict

from app.data_fabric.agent_integration import AgentDataFabricAdapter
from app.data_fabric.billing import DataFabricBillingTracker
from app.data_fabric.catalog import DataCatalog
from app.data_fabric.change_detection import ChangeDetector
from app.data_fabric.connector import ConnectorFactory, ConnectorRegistry
from app.data_fabric.connectors import register_all_initial_connectors
from app.data_fabric.data_security import RedactionEngine, SensitiveDataDetector
from app.data_fabric.data_source import DataSourceManager
from app.data_fabric.governance import DataGovernanceEngine
from app.data_fabric.ingestion import DataIngestionEngine
from app.data_fabric.lineage import DataLineageManager
from app.data_fabric.normalization import DataNormalizer
from app.data_fabric.observability import DataFabricMetricsCollector
from app.data_fabric.quality import DataQualityEngine
from app.data_fabric.rag_integration import DataSourceKnowledgeAdapter, KnowledgeSyncManager
from app.data_fabric.schema_discovery import SchemaDiscoveryEngine
from app.data_fabric.sync import DataSyncManager

logger = logging.getLogger(__name__)


class DataFabricManager:
    """Master Manager orchestrating the entire Enterprise Data Fabric Platform."""

    def __init__(self) -> None:
        self.source_manager = DataSourceManager()
        self.connector_registry = ConnectorRegistry()
        register_all_initial_connectors(self.connector_registry)

        self.connector_factory = ConnectorFactory(registry=self.connector_registry)
        self.schema_engine = SchemaDiscoveryEngine(connector_factory=self.connector_factory)
        self.ingestion_engine = DataIngestionEngine(connector_factory=self.connector_factory)
        self.normalizer = DataNormalizer()
        self.sync_manager = DataSyncManager(source_manager=self.source_manager, ingestion_engine=self.ingestion_engine)
        self.change_detector = ChangeDetector()
        self.catalog = DataCatalog()
        self.governance_engine = DataGovernanceEngine()
        self.sensitive_detector = SensitiveDataDetector()
        self.redaction_engine = RedactionEngine(detector=self.sensitive_detector)
        self.quality_engine = DataQualityEngine()
        self.lineage_manager = DataLineageManager()
        self.rag_adapter = DataSourceKnowledgeAdapter(lineage_manager=self.lineage_manager)
        self.rag_sync_manager = KnowledgeSyncManager(adapter=self.rag_adapter)
        self.agent_adapter = AgentDataFabricAdapter(source_manager=self.source_manager, governance_engine=self.governance_engine, lineage_manager=self.lineage_manager)
        self.metrics_collector = DataFabricMetricsCollector()
        self.billing_tracker = DataFabricBillingTracker()

        logger.info("[DATA FABRIC MASTER] DataFabricManager initialized cleanly with all initial 10 production connectors & governance modules")

    def get_summary(self) -> Dict[str, Any]:
        """Aggregate Data Fabric status summary."""
        sources = self.source_manager.list_sources()
        jobs = self.sync_manager.list_jobs()
        datasets = self.catalog.list_datasets()

        return {
            "total_data_sources": len(sources),
            "total_sync_jobs": len(jobs),
            "total_datasets": len(datasets),
            "registered_connectors": len(self.connector_registry.list_connectors()),
            "metrics": self.metrics_collector.get_metrics_summary(),
        }
