"""
Canonical Subsystem Registry for the 8 Enterprise AI Platforms.
"""

from typing import Dict, List, Optional

from app.platform_hardening.models import (
    IntegrationHealthStatus,
    SubsystemIntegrationStatus,
)


class SubsystemRegistry:
    """Registry maintaining metadata, capabilities, dependencies, and routes for all 8 upper intelligence platforms."""

    def __init__(self):
        self._subsystems: Dict[str, SubsystemIntegrationStatus] = {}
        self._register_default_platforms()

    def _register_default_platforms(self):
        defaults = [
            SubsystemIntegrationStatus(
                subsystem_name="Unified Intelligence",
                phase="5.51",
                status=IntegrationHealthStatus.HEALTHY,
                provider_name="UnifiedIntelligenceProvider",
                capabilities=["Holistic Impact", "Situation Awareness", "Prioritized Actions", "Risk Model"],
                dependencies=["Decision Intelligence", "Autonomous Assurance", "Continuous Assurance"],
                dependents=[],
                api_route="/v1/unified-intelligence",
                health_score=100.0,
            ),
            SubsystemIntegrationStatus(
                subsystem_name="Decision Intelligence",
                phase="5.52",
                status=IntegrationHealthStatus.HEALTHY,
                provider_name="DecisionIntelligenceProvider",
                capabilities=["Multi-Criteria Decision Analysis", "Tradeoff Analysis", "Option Evaluation"],
                dependencies=["Autonomous Assurance", "Continuous Assurance"],
                dependents=["Unified Intelligence"],
                api_route="/v1/decision-intelligence",
                health_score=100.0,
            ),
            SubsystemIntegrationStatus(
                subsystem_name="Autonomous Assurance",
                phase="5.53",
                status=IntegrationHealthStatus.HEALTHY,
                provider_name="AutonomousAssuranceProvider",
                capabilities=["Autonomous Workflows", "Plan Generation", "Multi-Step Coordination"],
                dependencies=["Continuous Assurance"],
                dependents=["Decision Intelligence", "Unified Intelligence"],
                api_route="/v1/autonomous-assurance",
                health_score=100.0,
            ),
            SubsystemIntegrationStatus(
                subsystem_name="Continuous Assurance",
                phase="5.54",
                status=IntegrationHealthStatus.HEALTHY,
                provider_name="ContinuousAssuranceProvider",
                capabilities=["Continuous Signal Stream", "Assurance Evaluation", "Drift Detection"],
                dependencies=["Reliability Intelligence", "Capacity Intelligence", "Runtime Intelligence"],
                dependents=["Autonomous Assurance"],
                api_route="/v1/continuous-assurance",
                health_score=100.0,
            ),
            SubsystemIntegrationStatus(
                subsystem_name="Reliability Intelligence",
                phase="5.55",
                status=IntegrationHealthStatus.HEALTHY,
                provider_name="ReliabilityIntelligenceProvider",
                capabilities=["SLO Tracking", "Error Budget Engine", "Failure Mode Prediction"],
                dependencies=["Capacity Intelligence", "Runtime Intelligence"],
                dependents=["Continuous Assurance"],
                api_route="/v1/reliability-intelligence",
                health_score=100.0,
            ),
            SubsystemIntegrationStatus(
                subsystem_name="Capacity Intelligence",
                phase="5.56",
                status=IntegrationHealthStatus.HEALTHY,
                provider_name="CapacityIntelligenceProvider",
                capabilities=["Resource Forecasting", "Utilization Modeling", "Cost Risk Analysis"],
                dependencies=["Runtime Intelligence"],
                dependents=["Reliability Intelligence", "Continuous Assurance"],
                api_route="/v1/capacity-intelligence",
                health_score=100.0,
            ),
            SubsystemIntegrationStatus(
                subsystem_name="Runtime Intelligence",
                phase="5.57",
                status=IntegrationHealthStatus.HEALTHY,
                provider_name="RuntimeIntelligenceProvider",
                capabilities=["Signal Ingestion", "Context Enrichment", "Anomaly Detection", "Adaptation"],
                dependencies=["Platform Integration Fabric"],
                dependents=["Capacity Intelligence", "Reliability Intelligence", "Continuous Assurance"],
                api_route="/v1/runtime-intelligence",
                health_score=100.0,
            ),
            SubsystemIntegrationStatus(
                subsystem_name="Platform Integration Fabric",
                phase="5.58",
                status=IntegrationHealthStatus.HEALTHY,
                provider_name="PlatformIntegrationProvider",
                capabilities=["Cross-Domain Context", "Execution Traceability", "Lineage Tracking"],
                dependencies=[],
                dependents=["Runtime Intelligence"],
                api_route="/v1/platform-integration",
                health_score=100.0,
            ),
        ]
        for s in defaults:
            self.register_subsystem(s)

    def register_subsystem(self, status: SubsystemIntegrationStatus):
        self._subsystems[status.subsystem_name] = status

    def get_subsystem(self, subsystem_name: str) -> Optional[SubsystemIntegrationStatus]:
        return self._subsystems.get(subsystem_name)

    def list_all_subsystems(self) -> List[SubsystemIntegrationStatus]:
        return list(self._subsystems.values())

    def update_subsystem_health(
        self,
        subsystem_name: str,
        status: IntegrationHealthStatus,
        health_score: float,
        error_message: Optional[str] = None,
    ):
        if subsystem_name in self._subsystems:
            self._subsystems[subsystem_name].status = status
            self._subsystems[subsystem_name].health_score = health_score
            self._subsystems[subsystem_name].error_message = error_message
