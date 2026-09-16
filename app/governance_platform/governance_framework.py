"""Governance Framework & Multi-Domain Control Specification Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class GovernanceDomain(str, Enum):
    SECURITY = "SECURITY"
    PRIVACY = "PRIVACY"
    DATA_GOVERNANCE = "DATA_GOVERNANCE"
    MODEL_GOVERNANCE = "MODEL_GOVERNANCE"
    AGENT_GOVERNANCE = "AGENT_GOVERNANCE"
    TOOL_GOVERNANCE = "TOOL_GOVERNANCE"
    WORKFLOW_GOVERNANCE = "WORKFLOW_GOVERNANCE"
    HUMAN_OVERSIGHT = "HUMAN_OVERSIGHT"
    EXPLAINABILITY = "EXPLAINABILITY"
    FAIRNESS = "FAIRNESS"
    SAFETY = "SAFETY"
    RELIABILITY = "RELIABILITY"
    FINANCIAL_GOVERNANCE = "FINANCIAL_GOVERNANCE"
    COMPLIANCE = "COMPLIANCE"
    OPERATIONAL_RISK = "OPERATIONAL_RISK"


class GovernanceScope(str, Enum):
    PLATFORM = "PLATFORM"
    TENANT = "TENANT"
    ORGANIZATION = "ORGANIZATION"
    WORKSPACE = "WORKSPACE"
    PROJECT = "PROJECT"
    APPLICATION = "APPLICATION"
    RESOURCE = "RESOURCE"
    MODEL = "MODEL"
    AGENT = "AGENT"
    AGENT_TEAM = "AGENT_TEAM"
    WORKFLOW = "WORKFLOW"
    TOOL = "TOOL"
    MCP_SERVER = "MCP_SERVER"
    EXTENSION = "EXTENSION"
    DATASET = "DATASET"
    DEPLOYMENT = "DEPLOYMENT"
    EXECUTION = "EXECUTION"


class GovernanceControl(BaseModel):
    control_id: str = Field(default_factory=lambda: f"ctrl_{uuid.uuid4().hex[:10]}")
    name: str
    domain: GovernanceDomain = GovernanceDomain.SECURITY
    scope: GovernanceScope = GovernanceScope.TENANT
    tenant_id: str = "global"

    description: str = ""
    is_active: bool = True
    enforcement_action: str = "WARN"  # ALLOW, WARN, REQUIRE_APPROVAL, THROTTLE, RESTRICT, BLOCK, ESCALATE
    created_at: datetime = Field(default_factory=_now)


class GovernanceFramework(BaseModel):
    framework_id: str = Field(default_factory=lambda: f"gw_fw_{uuid.uuid4().hex[:10]}")
    name: str
    tenant_id: str = "global"
    description: str = ""
    controls: List[GovernanceControl] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)
