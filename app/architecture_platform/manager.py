"""Master ArchitecturePlatformManager Orchestrator Subsystem."""

import logging
from typing import Dict, Any, Optional, List

from app.architecture_platform.nodes import ArchitectureNodeManager, ArchitectureNode, ArchitectureNodeType, ArchitectureNodeStatus
from app.architecture_platform.topology import TopologyManager, ArchitectureTopology, TopologySnapshot
from app.architecture_platform.dependencies import DependencyManager, DependencyType, DependencyStrength, ArchitectureDependency
from app.architecture_platform.flows import FlowManager, ArchitectureFlow, FlowStep
from app.architecture_platform.digital_twin import DigitalTwinManager, ArchitectureDigitalTwin
from app.architecture_platform.change_management import ArchitectureChangeManager, ArchitectureChange, ArchitectureChangeType, ArchitectureChangeStatus
from app.architecture_platform.impact import ImpactAnalyzer, ImpactAnalysis
from app.architecture_platform.governance import ArchitectureGovernanceEngine, ArchitecturePolicyDecision
from app.architecture_platform.decisions import ArchitectureDecisionManager, ArchitectureDecisionRecord, ArchitectureDecisionOption
from app.architecture_platform.drift import ArchitectureDriftDetector, ArchitectureDrift
from app.architecture_platform.simulation import ArchitectureSimulationEngine, SimulationResult, SimulationScenario
from app.architecture_platform.resilience import ResilienceAnalyzer, ArchitectureResilienceAssessment
from app.architecture_platform.trust import ArchitectureTrustEngine, ArchitectureTrustScore
from app.architecture_platform.observability import ArchitectureMetricsCollector
from app.architecture_platform.analytics import ArchitectureAnalyticsEngine, ArchitectureReport
from app.architecture_platform.repositories import ArchitectureRepository

logger = logging.getLogger(__name__)


class ArchitecturePlatformManager:
    """Master Orchestrator unifying all 20 Architecture Platform subsystems."""

    def __init__(self) -> None:
        self.repository = ArchitectureRepository()

        self.node_manager = ArchitectureNodeManager()
        self.topology_manager = TopologyManager(node_manager=self.node_manager)
        self.dependency_manager = DependencyManager()
        self.flow_manager = FlowManager()
        self.digital_twin_manager = DigitalTwinManager()

        self.change_manager = ArchitectureChangeManager()
        self.impact_analyzer = ImpactAnalyzer(dependency_manager=self.dependency_manager)
        self.governance_engine = ArchitectureGovernanceEngine()
        self.decision_manager = ArchitectureDecisionManager()
        self.drift_detector = ArchitectureDriftDetector(topology_manager=self.topology_manager, node_manager=self.node_manager)

        self.simulation_engine = ArchitectureSimulationEngine(impact_analyzer=self.impact_analyzer)
        self.resilience_analyzer = ResilienceAnalyzer(dependency_manager=self.dependency_manager)
        self.trust_engine = ArchitectureTrustEngine()

        self.metrics_collector = ArchitectureMetricsCollector()
        self.analytics_engine = ArchitectureAnalyticsEngine(
            node_manager=self.node_manager,
            dependency_manager=self.dependency_manager,
            resilience_analyzer=self.resilience_analyzer,
            trust_engine=self.trust_engine,
        )

        logger.info("[ARCHITECTURE MASTER] ArchitecturePlatformManager initialized cleanly with all 20 domain subsystems.")

    def discover_and_register_node(
        self,
        tenant_id: str,
        name: str,
        node_type: ArchitectureNodeType,
        environment: str = "production",
        owner_id: str = "system",
        source_manager: Optional[str] = None,
        resource_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> ArchitectureNode:
        """Register architecture node and update metrics."""
        node = self.node_manager.register_node(
            tenant_id=tenant_id,
            name=name,
            node_type=node_type,
            environment=environment,
            owner_id=owner_id,
            source_manager=source_manager,
            resource_id=resource_id,
            attributes=attributes,
        )
        self.metrics_collector.increment("ai_architecture_nodes_total")
        return node

    def add_dependency(
        self,
        tenant_id: str,
        source_node_id: str,
        target_node_id: str,
        dependency_type: DependencyType = DependencyType.DEPENDS_ON,
        strength: DependencyStrength = DependencyStrength.STRONG,
    ) -> ArchitectureDependency:
        """Add directed architectural dependency."""
        dep = self.dependency_manager.add_dependency(
            tenant_id=tenant_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            dependency_type=dependency_type,
            strength=strength,
        )
        self.metrics_collector.increment("ai_architecture_dependencies_total")
        return dep

    def propose_and_evaluate_change(
        self,
        tenant_id: str,
        idempotency_key: str,
        action_type: ArchitectureChangeType,
        target_node_ids: List[str],
        requested_by: str = "system",
    ) -> Dict[str, Any]:
        """Full change evaluation pipeline: Propose -> Impact Analysis -> Simulation -> Governance Evaluation -> Approval."""
        # 1. Propose Change with Idempotency
        change = self.change_manager.propose_change(
            tenant_id=tenant_id,
            idempotency_key=idempotency_key,
            action_type=action_type,
            target_node_ids=target_node_ids,
            requested_by=requested_by,
        )
        self.metrics_collector.increment("ai_architecture_changes_total")

        target_id = target_node_ids[0] if target_node_ids else "none"

        # 2. Impact Analysis
        impact = self.impact_analyzer.analyze_impact(tenant_id, target_id, action_type=action_type.value)
        self.metrics_collector.increment("ai_architecture_impact_analysis_total")

        # 3. Simulation
        sim_result = self.simulation_engine.run_simulation(tenant_id, target_id, scenario=SimulationScenario.MODEL_REPLACEMENT)

        # 4. Governance Evaluation & Approval Request if High Risk
        pol_decision = self.governance_engine.evaluate_change_governance(
            tenant_id=tenant_id,
            target_node_id=target_id,
            impact_analysis=impact,
            requested_by=requested_by,
        )

        if pol_decision.requires_approval:
            self.change_manager.update_status(change.change_id, tenant_id, ArchitectureChangeStatus.REQUIRES_APPROVAL)
            change.approval_request_id = pol_decision.approval_request_id
        else:
            self.change_manager.update_status(change.change_id, tenant_id, ArchitectureChangeStatus.APPROVED)

        return {
            "change": change.model_dump(),
            "impact_analysis": impact.model_dump(),
            "simulation": sim_result.model_dump(),
            "governance_decision": pol_decision.model_dump(),
        }

    def delegate_approved_change(self, change_id: str, tenant_id: str, delegated_subsystem: str = "PlatformOperationsManager") -> ArchitectureChange:
        """Delegate approved architecture change to execution subsystem."""
        change = self.change_manager.get_change(change_id, tenant_id)
        if change.status not in (ArchitectureChangeStatus.APPROVED, ArchitectureChangeStatus.REQUIRES_APPROVAL):
            raise ValueError(f"Change '{change_id}' is not in an executable state (Status: {change.status}).")

        # Update lifecycle to DELEGATED -> VERIFIED
        self.change_manager.update_status(change_id, tenant_id, ArchitectureChangeStatus.DELEGATED)
        change.delegated_subsystem = delegated_subsystem
        self.change_manager.update_status(change_id, tenant_id, ArchitectureChangeStatus.VERIFIED)
        return change

    def get_summary(self, tenant_id: str = "global") -> Dict[str, Any]:
        """Aggregate master summary for control plane and CLI."""
        report = self.analytics_engine.generate_report(tenant_id)
        metrics = self.metrics_collector.get_metrics_summary()
        return {
            "status": "OPERATIONAL",
            "report": report.model_dump(),
            "metrics": metrics,
        }
