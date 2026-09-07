"""
Decision Options Identification Subsystem.
Identifies, enumerates, and structures candidate decision options across cross-domain context.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.decision_intelligence.exceptions import (
    DecisionNotFoundException,
    CrossTenantDecisionIntelligenceException,
    DecisionOptionNotFoundException,
)


class DecisionOption(BaseModel):
    option_id: str = Field(default_factory=lambda: f"opt_{uuid.uuid4().hex[:12]}")
    decision_id: str
    tenant_id: str
    title: str
    description: Optional[str] = None
    action_type: str = "DELEGATE"
    target_system: str = "OPERATIONS"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    estimated_cost: float = 0.0
    reversibility: str = "REVERSIBLE"
    score: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionOptionsRegistry:
    """Manages candidate decision options for a decision."""

    def __init__(self) -> None:
        self._options: Dict[str, List[DecisionOption]] = {}

    def add_option(
        self,
        decision_id: str,
        tenant_id: str,
        title: str,
        description: Optional[str] = None,
        action_type: str = "DELEGATE",
        target_system: str = "OPERATIONS",
        parameters: Optional[Dict[str, Any]] = None,
        estimated_cost: float = 0.0,
        reversibility: str = "REVERSIBLE",
    ) -> DecisionOption:
        opt = DecisionOption(
            decision_id=decision_id,
            tenant_id=tenant_id,
            title=title,
            description=description,
            action_type=action_type,
            target_system=target_system,
            parameters=parameters or {},
            estimated_cost=estimated_cost,
            reversibility=reversibility,
        )
        if decision_id not in self._options:
            self._options[decision_id] = []
        self._options[decision_id].append(opt)
        return opt

    def list_options(self, decision_id: str, tenant_id: str) -> List[DecisionOption]:
        opts = self._options.get(decision_id, [])
        for opt in opts:
            if opt.tenant_id != tenant_id and tenant_id != "global":
                raise CrossTenantDecisionIntelligenceException(f"Unauthorized access to decision options for decision '{decision_id}'")
        return opts

    def get_option(self, option_id: str, tenant_id: str) -> DecisionOption:
        for opts in self._options.values():
            for opt in opts:
                if opt.option_id == option_id:
                    if opt.tenant_id != tenant_id and tenant_id != "global":
                        raise CrossTenantDecisionIntelligenceException(f"Unauthorized access to decision option '{option_id}'")
                    return opt
        raise DecisionOptionNotFoundException(f"Decision option '{option_id}' not found.")
