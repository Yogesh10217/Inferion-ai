"""Unified Enterprise Decision Context Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.decision_intelligence.exceptions import CrossTenantDecisionAccessException, DecisionContextException


class DecisionContextType(str, Enum):
    ARCHITECTURE = "ARCHITECTURE"
    DATA_GOVERNANCE = "DATA_GOVERNANCE"
    COMPLIANCE = "COMPLIANCE"
    INVESTMENT = "INVESTMENT"
    PORTFOLIO = "PORTFOLIO"
    OPERATIONS = "OPERATIONS"
    SECURITY = "SECURITY"
    APPLICATION = "APPLICATION"
    MODEL = "MODEL"
    WORKFLOW = "WORKFLOW"
    CROSS_DOMAIN = "CROSS_DOMAIN"


class DecisionScope(str, Enum):
    LOCAL = "LOCAL"
    APPLICATION = "APPLICATION"
    DEPARTMENT = "DEPARTMENT"
    ENTERPRISE = "ENTERPRISE"


class DecisionPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DecisionContext(BaseModel):
    context_id: str = Field(default_factory=lambda: f"ctx_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    description: str
    context_type: DecisionContextType = DecisionContextType.CROSS_DOMAIN
    scope: DecisionScope = DecisionScope.ENTERPRISE
    priority: DecisionPriority = DecisionPriority.HIGH
    source_references: Dict[str, Any] = Field(default_factory=dict)
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionContextBuilder:
    """Assembles decision context references from existing enterprise managers."""

    def assemble_context(
        self,
        tenant_id: str,
        title: str,
        description: str,
        context_type: DecisionContextType = DecisionContextType.CROSS_DOMAIN,
        scope: DecisionScope = DecisionScope.ENTERPRISE,
        priority: DecisionPriority = DecisionPriority.HIGH,
        architecture_ref: Optional[str] = None,
        data_gov_ref: Optional[str] = None,
        compliance_ref: Optional[str] = None,
        portfolio_ref: Optional[str] = None,
        ops_ref: Optional[str] = None,
    ) -> DecisionContext:
        refs = {}
        if architecture_ref:
            refs["architecture_ref"] = architecture_ref
        if data_gov_ref:
            refs["data_governance_ref"] = data_gov_ref
        if compliance_ref:
            refs["compliance_ref"] = compliance_ref
        if portfolio_ref:
            refs["portfolio_ref"] = portfolio_ref
        if ops_ref:
            refs["operations_ref"] = ops_ref

        return DecisionContext(
            tenant_id=tenant_id,
            title=title,
            description=description,
            context_type=context_type,
            scope=scope,
            priority=priority,
            source_references=refs,
        )


class DecisionContextManager:
    """Manages creation and retrieval of tenant-isolated decision contexts."""

    def __init__(self) -> None:
        self._contexts: Dict[str, DecisionContext] = {}

    def create_context(self, context: DecisionContext) -> DecisionContext:
        self._contexts[context.context_id] = context
        return context

    def get_context(self, context_id: str, tenant_id: str) -> DecisionContext:
        ctx = self._contexts.get(context_id)
        if not ctx:
            raise DecisionContextException(f"Context '{context_id}' not found.")
        if ctx.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantDecisionAccessException(tenant_id, ctx.tenant_id)
        return ctx
