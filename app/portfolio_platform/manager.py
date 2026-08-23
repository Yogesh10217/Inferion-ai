"""Master PortfolioPlatformManager Orchestrator Subsystem."""

import logging
from typing import Dict, Any, Optional, List

from app.portfolio_platform.strategy import StrategyManager, EnterpriseStrategy, StrategicTheme
from app.portfolio_platform.opportunities import OpportunityManager, AIOpportunity, OpportunitySource, OpportunityType
from app.portfolio_platform.initiatives import InitiativeManager, AIInitiative, InitiativeType, InitiativePriority, InitiativeStatus
from app.portfolio_platform.business_cases import BusinessCaseManager, BusinessCase, CostEstimate, BenefitEstimate
from app.portfolio_platform.prioritization import PrioritizationEngine, PrioritizationResult
from app.portfolio_platform.investment import InvestmentManager, InvestmentProposal, InvestmentRisk, InvestmentDecision
from app.portfolio_platform.funding import FundingManager, FundingAllocation, BudgetEnvelope
from app.portfolio_platform.value import ValueManager, ValueDimension, ValueMeasurement
from app.portfolio_platform.benefits import BenefitsManager, Benefit, BenefitType
from app.portfolio_platform.portfolio import PortfolioManager, Portfolio
from app.portfolio_platform.optimization import PortfolioOptimizationEngine, PortfolioOptimizationResult, PortfolioConstraint, OptimizationGoal
from app.portfolio_platform.scenarios import PortfolioScenarioManager, PortfolioScenario
from app.portfolio_platform.governance import PortfolioGovernanceEngine, PortfolioGovernanceDecision
from app.portfolio_platform.execution import PortfolioExecutionManager, InitiativeExecutionPlan, ExecutionTarget
from app.portfolio_platform.outcomes import OutcomeEvaluator, InitiativeOutcome
from app.portfolio_platform.learning import PortfolioLearningManager, PortfolioRecommendation
from app.portfolio_platform.trust import PortfolioTrustEngine, PortfolioTrustScore
from app.portfolio_platform.observability import PortfolioMetricsCollector
from app.portfolio_platform.analytics import PortfolioAnalyticsEngine, PortfolioReport
from app.portfolio_platform.billing import PortfolioBillingTracker
from app.portfolio_platform.repositories import PortfolioRepository

logger = logging.getLogger(__name__)


class PortfolioPlatformManager:
    """Master Orchestrator unifying all 23 Portfolio Platform domain subsystems."""

    def __init__(self) -> None:
        self.repository = PortfolioRepository()

        self.strategy_manager = StrategyManager()
        self.opportunity_manager = OpportunityManager()
        self.initiative_manager = InitiativeManager()
        self.business_case_manager = BusinessCaseManager()

        self.prioritization_engine = PrioritizationEngine()
        self.optimization_engine = PortfolioOptimizationEngine()
        self.scenario_manager = PortfolioScenarioManager(optimization_engine=self.optimization_engine)

        self.governance_engine = PortfolioGovernanceEngine()
        self.investment_manager = InvestmentManager(approval_engine=self.governance_engine.approval_engine)
        self.funding_manager = FundingManager()

        self.value_manager = ValueManager()
        self.benefits_manager = BenefitsManager()
        self.portfolio_manager = PortfolioManager()

        self.execution_manager = PortfolioExecutionManager()
        self.outcome_evaluator = OutcomeEvaluator()
        self.learning_manager = PortfolioLearningManager()
        self.trust_engine = PortfolioTrustEngine()

        self.metrics_collector = PortfolioMetricsCollector()
        self.analytics_engine = PortfolioAnalyticsEngine(
            strategy_manager=self.strategy_manager,
            initiative_manager=self.initiative_manager,
            investment_manager=self.investment_manager,
            funding_manager=self.funding_manager,
            trust_engine=self.trust_engine,
        )
        self.billing_tracker = PortfolioBillingTracker()

        logger.info("[PORTFOLIO MASTER] PortfolioPlatformManager initialized cleanly with all 23 domain subsystems.")

    def run_full_portfolio_flow(
        self,
        tenant_id: str,
        strategy_name: str = "Enterprise AI Acceleration",
        initiative_title: str = "Automated Customer Intelligence Agent",
    ) -> Dict[str, Any]:
        """Runs end-to-end portfolio flow: Strategy -> Objective -> Opportunity -> Initiative -> BC -> Prioritize -> Optimize -> Investment -> Funding -> Execute -> Outcomes -> Benefits -> Learning."""
        # 1. Strategy & Objective
        strat = self.strategy_manager.create_strategy(tenant_id, strategy_name, "Strategic AI Acceleration")
        obj = self.strategy_manager.add_objective(strat.strategy_id, tenant_id, "Customer Satisfaction Boost", "Increase CSAT via AI")

        # 2. Opportunity & Initiative
        opp = self.opportunity_manager.discover_opportunity(tenant_id, "Customer Insights Discovery", "Discover CSAT drivers")
        self.opportunity_manager.qualify_opportunity(opp.opportunity_id, tenant_id, True)

        init = self.initiative_manager.create_initiative(tenant_id, initiative_title, "Deploy agent for insights", opp.opportunity_id, obj.objective_id)
        self.opportunity_manager.mark_converted(opp.opportunity_id, tenant_id, init.initiative_id)

        # 3. Business Case
        bc = self.business_case_manager.create_business_case(
            tenant_id=tenant_id,
            initiative_id=init.initiative_id,
            problem_statement="Manual CSAT analysis is slow.",
            costs=CostEstimate(implementation_cost_usd=50000.0, annual_operating_cost_usd=10000.0),
            benefits=BenefitEstimate(annual_cost_savings_usd=80000.0, productivity_value_usd=40000.0),
        )

        # 4. Prioritize & Optimize
        prio_res = self.prioritization_engine.score_initiatives(tenant_id, [init], [bc])
        opt_res = self.optimization_engine.optimize_portfolio(tenant_id, prio_res, [bc])
        self.metrics_collector.increment("ai_portfolio_optimization_total")

        # 5. Investment & Funding
        proposal = self.investment_manager.propose_investment(tenant_id, init.initiative_id, 60000.0, risk_level=InvestmentRisk.LOW)
        decision = self.investment_manager.finalize_decision(proposal.proposal_id, tenant_id)

        alloc = self.funding_manager.allocate_funding(tenant_id, init.initiative_id, f"idemp_fund_{init.initiative_id}", 60000.0)
        self.metrics_collector.increment("ai_portfolio_funding_requests_total")

        # 6. Delegated Execution
        exec_plan = self.execution_manager.create_execution_plan(tenant_id, init.initiative_id, ExecutionTarget.APPLICATION_PLATFORM)
        del_plan = self.execution_manager.delegate_execution(exec_plan.execution_plan_id, tenant_id, "ApplicationPlatformManager")

        # 7. Value & Outcomes & Benefits
        vm = self.value_manager.record_expected_value(tenant_id, init.initiative_id, ValueDimension.COST_SAVINGS, 80000.0)
        vm_act = self.value_manager.record_realized_value(tenant_id, init.initiative_id, ValueDimension.COST_SAVINGS, 85000.0)

        outcome = self.outcome_evaluator.evaluate_outcome(tenant_id, init.initiative_id, 60000.0, 58000.0, 120000.0, 125000.0)
        benefit = self.benefits_manager.create_benefit_plan(tenant_id, init.initiative_id, "CSAT Efficiency", 120000.0)
        self.benefits_manager.record_realized_benefit(benefit.benefit_id, tenant_id, 125000.0)

        # 8. Learning Feedback
        rec = self.learning_manager.process_outcome_learning(tenant_id, outcome)

        return {
            "strategy": strat.model_dump(),
            "objective": obj.model_dump(),
            "opportunity": opp.model_dump(),
            "initiative": init.model_dump(),
            "business_case": bc.model_dump(),
            "prioritization": prio_res.model_dump(),
            "optimization": opt_res.model_dump(),
            "investment_decision": decision.model_dump(),
            "funding_allocation": alloc.model_dump(),
            "execution_plan": del_plan.model_dump(),
            "outcome": outcome.model_dump(),
            "recommendation": rec.model_dump(),
        }

    def get_summary(self, tenant_id: str = "global") -> Dict[str, Any]:
        """Aggregate master summary for control plane and CLI."""
        report = self.analytics_engine.generate_report(tenant_id)
        metrics = self.metrics_collector.get_metrics_summary()
        return {
            "status": "OPERATIONAL",
            "report": report.model_dump(),
            "metrics": metrics,
        }
