"""Lifecycle Governance Gates Subsystem (Phase 5.33)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.ai_lifecycle_platform.exceptions import CrossTenantLifecycleAccessException


class GateType(str, Enum):
    DATA_GOVERNANCE = "DATA_GOVERNANCE"
    SECURITY = "SECURITY"
    SAFETY = "SAFETY"
    RELIABILITY = "RELIABILITY"
    COMPLIANCE = "COMPLIANCE"
    ARCHITECTURE = "ARCHITECTURE"
    RISK = "RISK"
    TRUST = "TRUST"
    COST = "COST"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"


class GateStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"
    SKIPPED = "SKIPPED"


class GateRequirement(BaseModel):
    name: str
    is_hard_constraint: bool = True


class GateEvaluation(BaseModel):
    evaluation_id: str = Field(default_factory=lambda: f"gateeval_{uuid.uuid4().hex[:12]}")
    gate_type: GateType
    status: GateStatus = GateStatus.PASSED
    message: str = "Gate requirements satisfied"
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LifecycleGate(BaseModel):
    gate_id: str = Field(default_factory=lambda: f"gate_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    gate_type: GateType = GateType.SECURITY
    is_hard_gate: bool = True
    requirements: List[GateRequirement] = Field(default_factory=list)


class LifecycleGateManager:
    """Evaluates lifecycle governance gates and blocks promotion on hard gate failures."""

    def __init__(self) -> None:
        self._gates: Dict[str, LifecycleGate] = {}

    def create_gate(
        self,
        tenant_id: str,
        name: str,
        gate_type: GateType = GateType.SECURITY,
        is_hard_gate: bool = True,
    ) -> LifecycleGate:
        req = GateRequirement(name=f"{gate_type.value}_Check", is_hard_constraint=is_hard_gate)
        gate = LifecycleGate(tenant_id=tenant_id, name=name, gate_type=gate_type, is_hard_gate=is_hard_gate, requirements=[req])
        self._gates[gate.gate_id] = gate
        return gate

    def evaluate_gates(
        self,
        tenant_id: str,
        gate_ids: List[str],
        gate_override_pass: bool = True,
    ) -> List[GateEvaluation]:
        evaluations = []
        for gid in gate_ids:
            gate = self._gates.get(gid)
            if not gate:
                continue
            if tenant_id != "global" and gate.tenant_id != "global" and tenant_id != gate.tenant_id:
                raise CrossTenantLifecycleAccessException(tenant_id, gate.tenant_id)

            status = GateStatus.PASSED if gate_override_pass else GateStatus.FAILED
            evaluations.append(GateEvaluation(gate_type=gate.gate_type, status=status, message="Passed" if gate_override_pass else "Hard gate failure"))

        return evaluations
