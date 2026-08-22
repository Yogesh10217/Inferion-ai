"""Master Governance Platform Manager & Subsystem Orchestration Engine."""

import logging
from typing import Dict, Any, Optional, List

from app.governance_platform.risk import RiskManager, RiskCategory, RiskFactor
from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator, PolicyEvaluationResult
from app.governance_platform.explainability import ExplainabilityEngine, DecisionExplanation
from app.governance_platform.compliance import ComplianceManager, FrameworkType
from app.governance_platform.evidence import EvidenceCollector, EvidenceSource
from app.governance_platform.human_oversight import HumanOversightEngine, AutonomyLevel, OversightLevel
from app.governance_platform.violations import ViolationManager, ViolationType, ViolationSeverity
from app.governance_platform.trust import TrustEngine
from app.governance_platform.monitoring import GovernanceMonitoringEngine
from app.governance_platform.remediation import ControlEnforcementEngine, EnforcementAction
from app.governance_platform.reporting import GovernanceReportGenerator, AuditPackage
from app.governance_platform.observability import GovernanceMetricsCollector

logger = logging.getLogger(__name__)


class GovernancePlatformManager:
    """Master manager orchestrating all 12 Governance, Compliance, Risk & Trust domain subsystems."""

    def __init__(
        self,
        risk_manager: Optional[RiskManager] = None,
        policy_evaluator: Optional[UnifiedPolicyEvaluator] = None,
        explainability_engine: Optional[ExplainabilityEngine] = None,
        compliance_manager: Optional[ComplianceManager] = None,
        evidence_collector: Optional[EvidenceCollector] = None,
        human_oversight_engine: Optional[HumanOversightEngine] = None,
        violation_manager: Optional[ViolationManager] = None,
        trust_engine: Optional[TrustEngine] = None,
        monitoring_engine: Optional[GovernanceMonitoringEngine] = None,
        enforcement_engine: Optional[ControlEnforcementEngine] = None,
        report_generator: Optional[GovernanceReportGenerator] = None,
        metrics_collector: Optional[GovernanceMetricsCollector] = None,
    ) -> None:
        self.risk_manager = risk_manager or RiskManager()
        self.policy_evaluator = policy_evaluator or UnifiedPolicyEvaluator()
        self.explainability_engine = explainability_engine or ExplainabilityEngine()
        self.compliance_manager = compliance_manager or ComplianceManager()
        self.evidence_collector = evidence_collector or EvidenceCollector()
        self.human_oversight_engine = human_oversight_engine or HumanOversightEngine()
        self.violation_manager = violation_manager or ViolationManager()
        self.trust_engine = trust_engine or TrustEngine()
        self.monitoring_engine = monitoring_engine or GovernanceMonitoringEngine(
            violation_manager=self.violation_manager,
            risk_manager=self.risk_manager,
        )
        self.enforcement_engine = enforcement_engine or ControlEnforcementEngine()
        self.report_generator = report_generator or GovernanceReportGenerator()
        self.metrics_collector = metrics_collector or GovernanceMetricsCollector()

        logger.info("[GOVERNANCE MANAGER] Master GovernancePlatformManager initialized with all 12 domain subsystems")
