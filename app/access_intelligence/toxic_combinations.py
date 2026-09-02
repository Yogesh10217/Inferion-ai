"""Toxic Combination & Segregation of Duties (SoD) Analysis (Phase 5.39)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import CrossTenantAccessIntelligenceException


class ToxicCombinationSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ToxicCombinationRule(BaseModel):
    """Rule defining a conflicting set of entitlements or actions."""
    rule_id: str = Field(default_factory=lambda: f"sod_rule_{uuid.uuid4().hex[:8]}")
    code: str
    name: str
    description: str
    conflicting_entitlements: List[str]  # entitlement codes or actions
    severity: ToxicCombinationSeverity = ToxicCombinationSeverity.HIGH


class ToxicCombinationEvidence(BaseModel):
    """Evidence documenting detected toxic combination."""
    evidence_id: str = Field(default_factory=lambda: f"tc_evid_{uuid.uuid4().hex[:8]}")
    identity_id: str
    matched_entitlements: List[str]
    rule_code: str


class ToxicCombination(BaseModel):
    """Identified toxic combination finding."""
    combination_id: str = Field(default_factory=lambda: f"tc_find_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    identity_id: str
    rule_id: str
    rule_code: str
    severity: ToxicCombinationSeverity
    description: str
    recommendation: str
    evidence: ToxicCombinationEvidence
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ToxicCombinationManager:
    """Manages Segregation of Duties (SoD) rules and generates findings."""

    def __init__(self) -> None:
        self._rules: Dict[str, ToxicCombinationRule] = {}
        self._findings: Dict[str, ToxicCombination] = {}
        self._init_default_rules()

    def _init_default_rules(self) -> None:
        defaults = [
            ToxicCombinationRule(code="SOD-001", name="Deploy + Approve Own Deployment", description="Identity possesses capability to deploy and self-approve deployment", conflicting_entitlements=["DEPLOY_RELEASE", "APPROVE_DEPLOYMENT"], severity=ToxicCombinationSeverity.CRITICAL),
            ToxicCombinationRule(code="SOD-002", name="Modify Policy + Approve Policy", description="Identity can modify authorization policy and approve policy changes", conflicting_entitlements=["MODIFY_POLICY", "APPROVE_POLICY"], severity=ToxicCombinationSeverity.CRITICAL),
            ToxicCombinationRule(code="SOD-003", name="Access Sensitive Data + Disable Auditing", description="Identity can read sensitive datasets and disable audit logging", conflicting_entitlements=["READ_SENSITIVE_DATA", "DISABLE_AUDIT_LOGGING"], severity=ToxicCombinationSeverity.CRITICAL),
            ToxicCombinationRule(code="SOD-004", name="Create Identity + Assign Privileges", description="Identity can create new users/service accounts and assign admin roles", conflicting_entitlements=["CREATE_IDENTITY", "ASSIGN_PRIVILEGES"], severity=ToxicCombinationSeverity.HIGH),
        ]
        for r in defaults:
            self._rules[r.rule_id] = r

    def add_rule(self, code: str, name: str, description: str, conflicting_entitlements: List[str], severity: ToxicCombinationSeverity = ToxicCombinationSeverity.HIGH) -> ToxicCombinationRule:
        rule = ToxicCombinationRule(
            code=code,
            name=name,
            description=description,
            conflicting_entitlements=conflicting_entitlements,
            severity=severity,
        )
        self._rules[rule.rule_id] = rule
        return rule

    def evaluate_identity_entitlements(self, tenant_id: str, identity_id: str, active_entitlements: List[str]) -> List[ToxicCombination]:
        results: List[ToxicCombination] = []
        for rule in self._rules.values():
            matches = [e for e in rule.conflicting_entitlements if e in active_entitlements]
            if len(matches) == len(rule.conflicting_entitlements):
                evid = ToxicCombinationEvidence(
                    identity_id=identity_id,
                    matched_entitlements=matches,
                    rule_code=rule.code,
                )
                tc = ToxicCombination(
                    tenant_id=tenant_id,
                    identity_id=identity_id,
                    rule_id=rule.rule_id,
                    rule_code=rule.code,
                    severity=rule.severity,
                    description=f"Segregation of Duties violation: {rule.name} ({', '.join(matches)}).",
                    recommendation=f"Revoke one of conflicting entitlements ({', '.join(matches)}) from identity '{identity_id}'.",
                    evidence=evid,
                )
                self._findings[tc.combination_id] = tc
                results.append(tc)
        return results

    def list_findings(self, tenant_id: str, identity_id: Optional[str] = None) -> List[ToxicCombination]:
        results = [f for f in self._findings.values() if f.tenant_id == tenant_id]
        if identity_id:
            results = [f for f in results if f.identity_id == identity_id]
        return results
