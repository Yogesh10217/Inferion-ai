"""Master KnowledgePlatformManager Orchestrator Subsystem."""

import logging

from app.knowledge_platform.agent_integration import AgentKnowledgeAdapter
from app.knowledge_platform.analytics import KnowledgeAnalyticsEngine
from app.knowledge_platform.billing import KnowledgeBillingTracker
from app.knowledge_platform.compression import ContextCompressor
from app.knowledge_platform.conflicts import KnowledgeConflictManager
from app.knowledge_platform.context import ContextBuilder
from app.knowledge_platform.freshness import FreshnessEvaluator
from app.knowledge_platform.governance import KnowledgeGovernanceEngine
from app.knowledge_platform.knowledge import KnowledgeItem, KnowledgeManager, KnowledgeType
from app.knowledge_platform.knowledge_graph import KnowledgeGraphManager
from app.knowledge_platform.learning import KnowledgeLearningEngine
from app.knowledge_platform.memory import MemoryManager
from app.knowledge_platform.observability import KnowledgeMetricsCollector
from app.knowledge_platform.orchestration_integration import OrchestrationKnowledgeAdapter
from app.knowledge_platform.provenance import ProvenanceManager
from app.knowledge_platform.retrieval import RetrievalPipeline
from app.knowledge_platform.trust import KnowledgeTrustEngine
from app.knowledge_platform.validation import KnowledgeValidationEngine
from app.knowledge_platform.workflow_integration import WorkflowKnowledgeAdapter

logger = logging.getLogger(__name__)


class KnowledgePlatformManager:
    """Master orchestrator for all 18 Knowledge Platform & Organizational Intelligence subsystems."""

    def __init__(self) -> None:
        self.knowledge_manager = KnowledgeManager()
        self.retrieval_pipeline = RetrievalPipeline(knowledge_manager=self.knowledge_manager)
        self.context_builder = ContextBuilder()
        self.context_compressor = ContextCompressor()
        self.memory_manager = MemoryManager()
        self.knowledge_graph_manager = KnowledgeGraphManager()
        self.freshness_evaluator = FreshnessEvaluator(knowledge_manager=self.knowledge_manager)
        self.conflict_manager = KnowledgeConflictManager(knowledge_manager=self.knowledge_manager)
        self.provenance_manager = ProvenanceManager()
        self.trust_engine = KnowledgeTrustEngine()
        self.validation_engine = KnowledgeValidationEngine()
        self.learning_engine = KnowledgeLearningEngine(knowledge_manager=self.knowledge_manager)
        self.governance_engine = KnowledgeGovernanceEngine()
        self.agent_adapter = AgentKnowledgeAdapter(retrieval_pipeline=self.retrieval_pipeline)
        self.workflow_adapter = WorkflowKnowledgeAdapter(knowledge_manager=self.knowledge_manager, retrieval_pipeline=self.retrieval_pipeline)
        self.orchestration_adapter = OrchestrationKnowledgeAdapter()
        self.analytics_engine = KnowledgeAnalyticsEngine()
        self.metrics_collector = KnowledgeMetricsCollector()
        self.billing_tracker = KnowledgeBillingTracker()

        logger.info("[KNOWLEDGE PLATFORM MANAGER] Master KnowledgePlatformManager initialized with all 18 domain subsystems")

    def create_and_index_knowledge(
        self,
        title: str,
        content: str,
        knowledge_type: KnowledgeType = KnowledgeType.DOCUMENT,
        tenant_id: str = "global",
        classification: str = "INTERNAL",
        source_system: str = "DataFabric",
    ) -> KnowledgeItem:
        item = self.knowledge_manager.create_knowledge_item(
            title=title,
            content=content,
            knowledge_type=knowledge_type,
            tenant_id=tenant_id,
            classification=classification,
        )
        self.provenance_manager.create_chain(item.item_id, tenant_id=tenant_id, source_system=source_system)
        return item
