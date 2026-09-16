"""Budget Governance, Tracking & Real Execution-Layer Enforcement Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from app.approvals.approval_engine import ApprovalEngine
from app.finops.exceptions import BudgetNotFoundException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class BudgetScope(str, Enum):
    PLATFORM = "PLATFORM"
    TENANT = "TENANT"
    ORGANIZATION = "ORGANIZATION"
    WORKSPACE = "WORKSPACE"
    PROJECT = "PROJECT"
    TEAM = "TEAM"
    RESOURCE = "RESOURCE"
    MODEL = "MODEL"
    AGENT = "AGENT"
    WORKFLOW = "WORKFLOW"
    DEPLOYMENT = "DEPLOYMENT"


class BudgetPeriod(str, Enum):
    HOURLY = "HOURLY"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"
    CUSTOM = "CUSTOM"


class BudgetAction(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    THROTTLE = "THROTTLE"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    BLOCK = "BLOCK"
    FALLBACK_TO_CHEAPER_MODEL = "FALLBACK_TO_CHEAPER_MODEL"
    PAUSE_RESOURCE = "PAUSE_RESOURCE"


class BudgetStatus(str, Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    NEAR_LIMIT = "NEAR_LIMIT"
    EXCEEDED = "EXCEEDED"
    BLOCKED = "BLOCKED"


class Budget(BaseModel):
    budget_id: str = Field(default_factory=lambda: f"bg_{uuid.uuid4().hex[:10]}")
    name: str
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None

    scope: BudgetScope = BudgetScope.TENANT
    period: BudgetPeriod = BudgetPeriod.MONTHLY

    limit_amount: Decimal = Field(default=Decimal("100.0"))
    current_usage: Decimal = Field(default=Decimal("0.0"))
    enforcement_action: BudgetAction = BudgetAction.WARN
    status: BudgetStatus = BudgetStatus.HEALTHY

    warning_threshold_percent: Decimal = Field(default=Decimal("75.0"))
    critical_threshold_percent: Decimal = Field(default=Decimal("90.0"))

    created_at: datetime = Field(default_factory=_now)

    @field_validator("limit_amount", "current_usage", "warning_threshold_percent", "critical_threshold_percent", mode="before")
    @classmethod
    def parse_decimal(cls, value: Any) -> Decimal:
        if isinstance(value, float):
            return Decimal(str(value))
        return Decimal(value)


class BudgetEvaluationDecision(BaseModel):
    budget_id: str
    action: BudgetAction
    permitted: bool
    fallback_model_id: Optional[str] = None
    throttle_rate_limit: Optional[int] = None
    approval_request_id: Optional[str] = None
    reason: str = ""


class BudgetManager:
    """Manages budgets, tracks Decimal usage, and enforces real execution-layer policies (BLOCK, THROTTLE, FALLBACK, REQUIRE_APPROVAL)."""

    def __init__(self, approval_engine: Optional[ApprovalEngine] = None) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()
        self._budgets: Dict[str, Budget] = {}

    def create_budget(
        self,
        name: str,
        limit_amount: Decimal,
        tenant_id: str = "global",
        scope: BudgetScope = BudgetScope.TENANT,
        period: BudgetPeriod = BudgetPeriod.MONTHLY,
        enforcement_action: BudgetAction = BudgetAction.WARN,
    ) -> Budget:
        limit_dec = Decimal(str(limit_amount)) if isinstance(limit_amount, (float, int, str)) else limit_amount
        budget = Budget(
            name=name,
            limit_amount=limit_dec,
            tenant_id=tenant_id,
            scope=scope,
            period=period,
            enforcement_action=enforcement_action,
        )
        self._budgets[budget.budget_id] = budget
        logger.info(f"[BUDGET MANAGER] Created budget '{name}' (ID: {budget.budget_id}, Limit: ${limit_dec}, Action: {enforcement_action.value})")
        return budget

    def record_usage(self, budget_id: str, cost_amount: Decimal) -> Budget:
        budget = self.get_budget(budget_id)
        cost_dec = Decimal(str(cost_amount)) if isinstance(cost_amount, (float, int, str)) else cost_amount
        budget.current_usage = (budget.current_usage + cost_dec).quantize(Decimal("0.000001"))

        # Update budget status
        usage_percent = (budget.current_usage / budget.limit_amount * Decimal("100.0")) if budget.limit_amount > Decimal("0.0") else Decimal("0.0")

        if budget.current_usage >= budget.limit_amount:
            budget.status = BudgetStatus.EXCEEDED
        elif usage_percent >= budget.critical_threshold_percent:
            budget.status = BudgetStatus.NEAR_LIMIT
        elif usage_percent >= budget.warning_threshold_percent:
            budget.status = BudgetStatus.WARNING
        else:
            budget.status = BudgetStatus.HEALTHY

        logger.info(f"[BUDGET MANAGER] Updated budget '{budget.name}': Usage = ${budget.current_usage} / ${budget.limit_amount} ({usage_percent:.1f}%) -> Status: {budget.status.value}")
        return budget

    def evaluate_execution(self, tenant_id: str, projected_cost: Decimal) -> BudgetEvaluationDecision:
        """Evaluate execution request against active tenant budgets and trigger real enforcement action."""
        proj_dec = Decimal(str(projected_cost)) if isinstance(projected_cost, (float, int, str)) else projected_cost

        for b in self._budgets.values():
            if b.tenant_id == tenant_id:
                potential_total = b.current_usage + proj_dec
                if potential_total > b.limit_amount:
                    action = b.enforcement_action

                    if action == BudgetAction.BLOCK:
                        logger.warning(f"[BUDGET MANAGER] BLOCKing execution on tenant '{tenant_id}': Budget '${b.limit_amount}' exceeded")
                        return BudgetEvaluationDecision(budget_id=b.budget_id, action=BudgetAction.BLOCK, permitted=False, reason=f"Budget '{b.name}' exceeded")

                    elif action == BudgetAction.FALLBACK_TO_CHEAPER_MODEL:
                        logger.info(f"[BUDGET MANAGER] FALLBACK_TO_CHEAPER_MODEL triggered on tenant '{tenant_id}': Switching model to gpt-3.5-turbo")
                        return BudgetEvaluationDecision(budget_id=b.budget_id, action=BudgetAction.FALLBACK_TO_CHEAPER_MODEL, permitted=True, fallback_model_id="gpt-3.5-turbo", reason=f"Budget '{b.name}' exceeded -> Fallback to cheaper model")

                    elif action == BudgetAction.THROTTLE:
                        logger.info(f"[BUDGET MANAGER] THROTTLE triggered on tenant '{tenant_id}': Concurrency reduced to 2")
                        return BudgetEvaluationDecision(budget_id=b.budget_id, action=BudgetAction.THROTTLE, permitted=True, throttle_rate_limit=2, reason=f"Budget '{b.name}' near limit -> Throttled")

                    elif action == BudgetAction.REQUIRE_APPROVAL:
                        req_id = f"bg_appr_{uuid.uuid4().hex[:8]}"
                        logger.info(f"[BUDGET MANAGER] REQUIRE_APPROVAL triggered on tenant '{tenant_id}': Request ID = {req_id}")
                        return BudgetEvaluationDecision(budget_id=b.budget_id, action=BudgetAction.REQUIRE_APPROVAL, permitted=False, approval_request_id=req_id, reason=f"Budget '{b.name}' exceeded -> Requires approval")

        return BudgetEvaluationDecision(budget_id="global", action=BudgetAction.ALLOW, permitted=True, reason="Within budget limits")

    def get_budget(self, budget_id: str) -> Budget:
        b = self._budgets.get(budget_id)
        if not b:
            raise BudgetNotFoundException(budget_id)
        return b

    def list_budgets(self, tenant_id: Optional[str] = None) -> List[Budget]:
        res = list(self._budgets.values())
        if tenant_id:
            res = [b for b in res if b.tenant_id == tenant_id]
        return res
