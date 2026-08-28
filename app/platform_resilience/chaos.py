"""Controlled Resilience Experiment Governance Subsystem (Phase 5.37)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget
from app.platform_resilience.exceptions import (
    CrossTenantResilienceAccessException,
    ResilienceResourceNotFoundException,
    HighRiskRecoveryRequiresApprovalException,
)


class ExperimentScenario(str, Enum):
    LATENCY_INJECTION = "LATENCY_INJECTION"
    PACKET_LOSS = "PACKET_LOSS"
    RESOURCE_EXHAUSTION = "RESOURCE_EXHAUSTION"
    PROCESS_KILL = "PROCESS_KILL"
    DEPENDENCY_OUTAGE = "DEPENDENCY_OUTAGE"


class ExperimentScope(str, Enum):
    SINGLE_INSTANCE = "SINGLE_INSTANCE"
    SERVICE = "SERVICE"
    ZONE = "ZONE"
    REGION = "REGION"


class ExperimentRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ExperimentStatus(str, Enum):
    PLANNED = "PLANNED"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


class ExperimentResult(BaseModel):
    is_resilient: bool = True
    steady_state_preserved: bool = True
    observations: List[str] = Field(default_factory=list)


class ResilienceExperiment(BaseModel):
    experiment_id: str = Field(default_factory=lambda: f"exp_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    scenario: ExperimentScenario = ExperimentScenario.LATENCY_INJECTION
    scope: ExperimentScope = ExperimentScope.SERVICE
    risk: ExperimentRisk = ExperimentRisk.HIGH
    target_service_id: str
    duration_seconds: int = 60
    delegation_id: Optional[str] = None
    status: ExperimentStatus = ExperimentStatus.PLANNED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChaosExperimentManager:
    """Controlled Resilience Experiment Governance Manager.
    
    Ensures chaos experiments never directly disrupt infrastructure, requiring approval and delegation.
    """

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._experiments: Dict[str, ResilienceExperiment] = {}

    def plan_experiment(
        self,
        tenant_id: str,
        name: str,
        target_service_id: str,
        scenario: ExperimentScenario = ExperimentScenario.LATENCY_INJECTION,
        scope: ExperimentScope = ExperimentScope.SERVICE,
        risk: ExperimentRisk = ExperimentRisk.HIGH,
        duration_seconds: int = 60,
    ) -> ResilienceExperiment:
        exp = ResilienceExperiment(
            tenant_id=tenant_id,
            name=name,
            target_service_id=target_service_id,
            scenario=scenario,
            scope=scope,
            risk=risk,
            duration_seconds=duration_seconds,
        )
        self._experiments[exp.experiment_id] = exp

        if risk in (ExperimentRisk.HIGH, ExperimentRisk.CRITICAL):
            raise HighRiskRecoveryRequiresApprovalException(f"Chaos experiment '{name}' (ID: {exp.experiment_id}) is high-risk ({risk.value}) and requires human approval.")

        return exp

    def approve_and_delegate_experiment(self, experiment_id: str, tenant_id: str) -> ResilienceExperiment:
        exp = self.get_experiment(experiment_id, tenant_id)
        exp.status = ExperimentStatus.APPROVED

        del_req = DelegationRequest(
            tenant_id=tenant_id,
            target=DelegationTarget.PLATFORM_OPERATIONS,
            action="run_chaos_experiment",
            payload={"experiment_id": experiment_id, "scenario": exp.scenario.value, "target_service_id": exp.target_service_id},
            requester_id="chaos_manager",
        )
        exp.delegation_id = del_req.delegation_id
        exp.status = ExperimentStatus.DELEGATED
        exp.status = ExperimentStatus.COMPLETED
        return exp

    def get_experiment(self, experiment_id: str, tenant_id: str) -> ResilienceExperiment:
        exp = self._experiments.get(experiment_id)
        if not exp:
            raise ResilienceResourceNotFoundException(experiment_id)
        
        try:
            self.tenant_guard.enforce_isolation(tenant_id, exp.tenant_id)
        except Exception:
            raise CrossTenantResilienceAccessException(tenant_id, exp.tenant_id)
            
        return exp
