"""Enterprise Budget Governance (Phase 5.42)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import (
    CrossTenantFinOpsIntelligenceException,
    BudgetExceededException,
)


class BudgetPeriod(str, Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUALLY = "ANNUALLY"


class BudgetThreshold(str, Enum):
    WARNING = "WARNING"      # 75%
    CRITICAL = "CRITICAL"    # 90%
    HARD_LIMIT = "HARD_LIMIT" # 100%


class BudgetStatus(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EXCEEDED = "EXCEEDED"


class Budget(BaseModel):
    budget_id: str = Field(default_factory=lambda: f"bdg_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    amount_usd: float
    warning_threshold_pct: float = 75.0
    critical_threshold_pct: float = 90.0
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    current_spend_usd: float = 0.0
    status: BudgetStatus = BudgetStatus.NORMAL
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BudgetAssessment(BaseModel):
    budget_id: str
    tenant_id: str
    limit_usd: float
    current_spend_usd: float
    utilization_pct: float
    status: BudgetStatus
    requires_escalation: bool = False


class BudgetManager:
    """Manages enterprise budget limits, thresholds, and governance assessments."""

    def __init__(self) -> None:
        self._budgets: Dict[str, Budget] = {}

    def create_budget(
        self,
        tenant_id: str,
        name: str,
        amount_usd: float,
        warning_threshold_pct: float = 75.0,
        critical_threshold_pct: float = 90.0,
        period: BudgetPeriod = BudgetPeriod.MONTHLY,
    ) -> Budget:
        bdg = Budget(
            tenant_id=tenant_id,
            name=name,
            amount_usd=amount_usd,
            warning_threshold_pct=warning_threshold_pct,
            critical_threshold_pct=critical_threshold_pct,
            period=period,
        )
        self._budgets[bdg.budget_id] = bdg
        return bdg

    def evaluate_budget(self, tenant_id: str, budget_id: str, current_spend_usd: float) -> BudgetAssessment:
        bdg = self.get_budget(tenant_id, budget_id)
        bdg.current_spend_usd = current_spend_usd
        utilization = round((current_spend_usd / bdg.amount_usd) * 100.0, 2)

        if utilization >= 100.0:
            bdg.status = BudgetStatus.EXCEEDED
            escalation = True
        elif utilization >= bdg.critical_threshold_pct:
            bdg.status = BudgetStatus.CRITICAL
            escalation = True
        elif utilization >= bdg.warning_threshold_pct:
            bdg.status = BudgetStatus.WARNING
            escalation = False
        else:
            bdg.status = BudgetStatus.NORMAL
            escalation = False

        asm = BudgetAssessment(
            budget_id=bdg.budget_id,
            tenant_id=tenant_id,
            limit_usd=bdg.amount_usd,
            current_spend_usd=current_spend_usd,
            utilization_pct=utilization,
            status=bdg.status,
            requires_escalation=escalation,
        )
        return asm

    def get_budget(self, tenant_id: str, budget_id: str) -> Budget:
        bdg = self._budgets.get(budget_id)
        if not bdg or bdg.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return bdg

    def list_budgets(self, tenant_id: str) -> List[Budget]:
        return [b for b in self._budgets.values() if b.tenant_id == tenant_id]
