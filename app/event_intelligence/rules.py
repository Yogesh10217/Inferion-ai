"""Enterprise Event Automation Rules Subsystem (Phase 5.34)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.event_intelligence.exceptions import CrossTenantEventAccessException, ImmutableEventRecordException
from app.platform_contracts.fingerprinting import FingerprintGenerator
from app.platform_contracts.immutability import ImmutableResource, ImmutableResourceState, ImmutableResourceValidator


class EventRuleStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DISABLED = "DISABLED"


class EventRuleCondition(BaseModel):
    field_name: str
    operator: str = "EQUALS"
    expected_value: str


class EventRuleAction(BaseModel):
    action_name: str
    is_high_risk: bool = False


class EventRuleEvaluation(BaseModel):
    is_matched: bool = True
    matched_rule_id: str = ""


class EventRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: f"rule_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    description: str = ""
    status: EventRuleStatus = EventRuleStatus.ACTIVE
    conditions: List[EventRuleCondition] = Field(default_factory=list)
    actions: List[EventRuleAction] = Field(default_factory=list)
    immutable_record: ImmutableResource = Field(default_factory=lambda: ImmutableResource(resource_id="", tenant_id=""))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def model_post_init(self, __context: Any) -> None:
        if not self.immutable_record.resource_id:
            self.immutable_record = ImmutableResource(resource_id=self.rule_id, tenant_id=self.tenant_id)


class EventRuleManager:
    """Manages enterprise event automation rules and finalizes immutable rule definitions."""

    def __init__(self) -> None:
        self._rules: Dict[str, EventRule] = {}

    def create_rule(
        self,
        tenant_id: str,
        name: str,
        actions: Optional[List[EventRuleAction]] = None,
    ) -> EventRule:
        rule = EventRule(
            tenant_id=tenant_id,
            name=name,
            actions=actions or [EventRuleAction(action_name="REQUEST_INVESTIGATION")],
        )
        self._rules[rule.rule_id] = rule
        return rule

    def finalize_rule(self, rule_id: str, tenant_id: str) -> EventRule:
        rule = self._rules.get(rule_id)
        if not rule:
            raise KeyError(f"Rule '{rule_id}' not found.")
        if tenant_id != "global" and rule.tenant_id != "global" and tenant_id != rule.tenant_id:
            raise CrossTenantEventAccessException(tenant_id, rule.tenant_id)

        if rule.immutable_record.state == ImmutableResourceState.FINALIZED:
            raise ImmutableEventRecordException(rule_id)

        fp = FingerprintGenerator.generate(rule.model_dump(exclude={"immutable_record"}))
        ImmutableResourceValidator.finalize(rule.immutable_record, fingerprint=fp)
        return rule

    def list_rules(self, tenant_id: str) -> List[EventRule]:
        return [r for r in self._rules.values() if r.tenant_id == tenant_id]
