"""Master Process Orchestration & Intelligent Automation Manager."""

import logging
from typing import Optional

from app.orchestration.agent_orchestration import AgentOrchestrationManager
from app.orchestration.analytics import ProcessAnalyticsEngine
from app.orchestration.case_management import CaseManager
from app.orchestration.compensation import CompensationManager
from app.orchestration.decisions import DecisionEngine
from app.orchestration.events import EventRouter
from app.orchestration.execution import WorkflowExecutionEngine
from app.orchestration.governance import WorkflowGovernanceEngine
from app.orchestration.human_tasks import HumanTaskManager
from app.orchestration.observability import OrchestrationMetricsCollector
from app.orchestration.recovery import RecoveryManager
from app.orchestration.routing import ExecutionRouter
from app.orchestration.workflow import WorkflowDefinitionManager

logger = logging.getLogger(__name__)


class OrchestrationManager:
    """Master OrchestrationManager orchestrating all 13 process automation & intelligent orchestration domain subsystems."""

    def __init__(
        self,
        definition_manager: Optional[WorkflowDefinitionManager] = None,
        execution_engine: Optional[WorkflowExecutionEngine] = None,
        human_task_manager: Optional[HumanTaskManager] = None,
        case_manager: Optional[CaseManager] = None,
        execution_router: Optional[ExecutionRouter] = None,
        agent_orchestration_manager: Optional[AgentOrchestrationManager] = None,
        decision_engine: Optional[DecisionEngine] = None,
        event_router: Optional[EventRouter] = None,
        compensation_manager: Optional[CompensationManager] = None,
        recovery_manager: Optional[RecoveryManager] = None,
        workflow_governance_engine: Optional[WorkflowGovernanceEngine] = None,
        process_analytics_engine: Optional[ProcessAnalyticsEngine] = None,
        metrics_collector: Optional[OrchestrationMetricsCollector] = None,
    ) -> None:
        self.definition_manager = definition_manager or WorkflowDefinitionManager()
        self.execution_engine = execution_engine or WorkflowExecutionEngine()
        self.human_task_manager = human_task_manager or HumanTaskManager()
        self.case_manager = case_manager or CaseManager()
        self.execution_router = execution_router or ExecutionRouter()
        self.agent_orchestration_manager = agent_orchestration_manager or AgentOrchestrationManager()
        self.decision_engine = decision_engine or DecisionEngine()
        self.event_router = event_router or EventRouter()
        self.compensation_manager = compensation_manager or CompensationManager()
        self.recovery_manager = recovery_manager or RecoveryManager()
        self.workflow_governance_engine = workflow_governance_engine or WorkflowGovernanceEngine()
        self.process_analytics_engine = process_analytics_engine or ProcessAnalyticsEngine()
        self.metrics_collector = metrics_collector or OrchestrationMetricsCollector()

        logger.info("[ORCHESTRATION MANAGER] Master OrchestrationManager initialized with all 13 domain subsystems")
