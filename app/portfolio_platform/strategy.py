"""Enterprise AI Strategy & Objective Management Subsystem."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.portfolio_platform.exceptions import (
    CrossTenantPortfolioAccessException,
    StrategyAlignmentException,
)


class StrategyStatus(str, Enum):
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    ARCHIVED = "ARCHIVED"


class StrategyHorizon(str, Enum):
    NEAR_TERM = "NEAR_TERM"      # 1 Year
    MEDIUM_TERM = "MEDIUM_TERM"  # 2-3 Years
    LONG_TERM = "LONG_TERM"      # 5+ Years


class StrategicTheme(str, Enum):
    OPERATIONAL_EXCELLENCE = "OPERATIONAL_EXCELLENCE"
    CUSTOMER_EXPERIENCE = "CUSTOMER_EXPERIENCE"
    PRODUCT_INNOVATION = "PRODUCT_INNOVATION"
    RISK_AND_COMPLIANCE = "RISK_AND_COMPLIANCE"
    COST_OPTIMIZATION = "COST_OPTIMIZATION"


class ObjectiveStatus(str, Enum):
    PLANNED = "PLANNED"
    ON_TRACK = "ON_TRACK"
    AT_RISK = "AT_RISK"
    ACHIEVED = "ACHIEVED"


class KeyResult(BaseModel):
    kr_id: str = Field(default_factory=lambda: f"kr_{uuid.uuid4().hex[:12]}")
    title: str
    target_value: float
    current_value: float = 0.0
    unit: str = "percentage"


class BusinessObjective(BaseModel):
    objective_id: str = Field(default_factory=lambda: f"obj_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    strategy_id: str
    title: str
    description: str
    theme: StrategicTheme = StrategicTheme.PRODUCT_INNOVATION
    status: ObjectiveStatus = ObjectiveStatus.PLANNED
    key_results: List[KeyResult] = Field(default_factory=list)
    weight: float = 1.0


class EnterpriseStrategy(BaseModel):
    strategy_id: str = Field(default_factory=lambda: f"strat_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    version: str = "1.0.0"
    name: str
    description: str
    horizon: StrategyHorizon = StrategyHorizon.NEAR_TERM
    status: StrategyStatus = StrategyStatus.ACTIVE
    objectives: List[BusinessObjective] = Field(default_factory=list)
    strategy_fingerprint: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def compute_fingerprint(self) -> str:
        canonical_str = json.dumps(
            {
                "tenant_id": self.tenant_id,
                "version": self.version,
                "name": self.name,
                "horizon": self.horizon.value,
                "objectives_count": len(self.objectives),
            },
            sort_keys=True,
        )
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()


class StrategyAlignment(BaseModel):
    alignment_id: str = Field(default_factory=lambda: f"align_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    objective_id: str
    initiative_id: str
    alignment_score: float = 100.0  # 0.0 to 100.0
    rationale: str = "Direct alignment"


class StrategyManager:
    """Manages enterprise AI strategies, objectives, and initiative alignments."""

    def __init__(self) -> None:
        self._strategies: Dict[str, EnterpriseStrategy] = {}
        self._alignments: Dict[str, StrategyAlignment] = {}

    def create_strategy(
        self,
        tenant_id: str,
        name: str,
        description: str,
        horizon: StrategyHorizon = StrategyHorizon.NEAR_TERM,
        version: str = "1.0.0",
    ) -> EnterpriseStrategy:
        strat = EnterpriseStrategy(
            tenant_id=tenant_id,
            name=name,
            description=description,
            horizon=horizon,
            version=version,
        )
        strat.strategy_fingerprint = strat.compute_fingerprint()
        self._strategies[strat.strategy_id] = strat
        return strat

    def add_objective(
        self,
        strategy_id: str,
        tenant_id: str,
        title: str,
        description: str,
        theme: StrategicTheme = StrategicTheme.PRODUCT_INNOVATION,
        key_results: Optional[List[KeyResult]] = None,
    ) -> BusinessObjective:
        strat = self.get_strategy(strategy_id, tenant_id)
        obj = BusinessObjective(
            tenant_id=tenant_id,
            strategy_id=strategy_id,
            title=title,
            description=description,
            theme=theme,
            key_results=key_results or [],
        )
        strat.objectives.append(obj)
        strat.strategy_fingerprint = strat.compute_fingerprint()
        return obj

    def get_strategy(self, strategy_id: str, tenant_id: str) -> EnterpriseStrategy:
        strat = self._strategies.get(strategy_id)
        if not strat:
            raise StrategyAlignmentException(f"Strategy '{strategy_id}' not found.")
        if strat.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantPortfolioAccessException(request_tenant=tenant_id, target_tenant=strat.tenant_id, resource_id=strategy_id)
        return strat

    def list_strategies(self, tenant_id: str) -> List[EnterpriseStrategy]:
        return [s for s in self._strategies.values() if s.tenant_id in (tenant_id, "global")]
