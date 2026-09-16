"""
Tool Policy Rules & Configuration Models
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class PolicyEffect(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


class PolicyRule(BaseModel):
    rule_id: str
    description: str = ""
    effect: PolicyEffect = PolicyEffect.ALLOW
    target_tools: List[str] = Field(default_factory=lambda: ["*"])
    target_categories: List[str] = Field(default_factory=list)
    roles: List[str] = Field(default_factory=list)
    scopes: List[str] = Field(default_factory=list)
    max_cost_per_call: Optional[float] = None


class ToolPolicy(BaseModel):
    policy_id: str
    tenant_id: str = "default_tenant"
    organization_id: str = "default_org"
    name: str
    description: str = ""
    rules: List[PolicyRule] = Field(default_factory=list)
    is_active: bool = True
