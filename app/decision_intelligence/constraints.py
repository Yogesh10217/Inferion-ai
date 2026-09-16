"""Unified Decision Constraint Evaluation Subsystem."""

import uuid
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field


class ConstraintType(str, Enum):
    FINANCIAL = "FINANCIAL"
    RISK = "RISK"
    COMPLIANCE = "COMPLIANCE"
    DATA_GOVERNANCE = "DATA_GOVERNANCE"
    ARCHITECTURE = "ARCHITECTURE"
    SECURITY = "SECURITY"
    CAPACITY = "CAPACITY"
    PERFORMANCE = "PERFORMANCE"
    TRUST = "TRUST"
    POLICY = "POLICY"
    TIME = "TIME"
    RESOURCE = "RESOURCE"


class ConstraintSeverity(str, Enum):
    SOFT = "SOFT"
    HARD = "HARD"
    CRITICAL = "CRITICAL"


class DecisionConstraint(BaseModel):
    constraint_id: str = Field(default_factory=lambda: f"const_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    constraint_type: ConstraintType
    title: str
    severity: ConstraintSeverity = ConstraintSeverity.HARD
    threshold_value: float
    is_active: bool = True


class ConstraintEvaluation(BaseModel):
    constraint_id: str
    constraint_type: ConstraintType
    passed: bool
    observed_value: float
    threshold_value: float
    severity: ConstraintSeverity
    message: str


class ConstraintResult(BaseModel):
    tenant_id: str
    context_id: str
    passed_all: bool
    hard_violations_count: int
    evaluations: List[ConstraintEvaluation] = Field(default_factory=list)


class ConstraintManager:
    """Evaluates decision constraints and blocks recommendations on hard constraint violations."""

    def __init__(self) -> None:
        self._constraints: Dict[str, List[DecisionConstraint]] = {}

    def add_constraint(self, constraint: DecisionConstraint) -> DecisionConstraint:
        if constraint.tenant_id not in self._constraints:
            self._constraints[constraint.tenant_id] = []
        self._constraints[constraint.tenant_id].append(constraint)
        return constraint

    def evaluate_constraints(
        self,
        tenant_id: str,
        context_id: str,
        observed_values: Dict[ConstraintType, float],
    ) -> ConstraintResult:
        tenant_consts = self._constraints.get(tenant_id, [])
        evaluations = []
        hard_violations = 0

        for const in tenant_consts:
            if not const.is_active:
                continue
            obs = observed_values.get(const.constraint_type, 0.0)

            # Rule logic: e.g. for RISK, obs <= threshold; for TRUST/COMPLIANCE/VALUE, obs >= threshold
            if const.constraint_type in (ConstraintType.RISK, ConstraintType.FINANCIAL, ConstraintType.CAPACITY):
                passed = obs <= const.threshold_value
            else:
                passed = obs >= const.threshold_value

            if not passed and const.severity in (ConstraintSeverity.HARD, ConstraintSeverity.CRITICAL):
                hard_violations += 1

            evaluations.append(
                ConstraintEvaluation(
                    constraint_id=const.constraint_id,
                    constraint_type=const.constraint_type,
                    passed=passed,
                    observed_value=obs,
                    threshold_value=const.threshold_value,
                    severity=const.severity,
                    message=f"{const.title}: Observed {obs} vs threshold {const.threshold_value} (Passed: {passed}).",
                )
            )

        return ConstraintResult(
            tenant_id=tenant_id,
            context_id=context_id,
            passed_all=(hard_violations == 0),
            hard_violations_count=hard_violations,
            evaluations=evaluations,
        )
