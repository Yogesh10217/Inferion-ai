"""Deterministic data validation intelligence (Phase 5.43)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import CrossTenantDataIntelligenceException


class ValidationType(str, Enum):
    SCHEMA = "SCHEMA"
    TYPE = "TYPE"
    FORMAT = "FORMAT"
    RANGE = "RANGE"
    RELATIONSHIP = "RELATIONSHIP"
    CONSTRAINT = "CONSTRAINT"


class ValidationStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"


class DataValidationRule(BaseModel):
    rule_id: str
    dataset_id: str
    tenant_id: str
    name: str
    validation_type: ValidationType
    target_field: str
    validation_spec: Dict[str, Any] = Field(default_factory=dict)
    is_blocking: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataValidationResult(BaseModel):
    validation_id: str
    dataset_id: str
    tenant_id: str
    status: ValidationStatus
    evaluated_rules: int
    passed_rules: int
    failed_rules: int
    failure_reasons: List[str] = Field(default_factory=list)
    explanation: str
    validated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataValidationManager:
    """Manages deterministic data validation checks (read-only, never mutates data)."""

    def __init__(self) -> None:
        self._rules: Dict[str, DataValidationRule] = {}
        self._results: Dict[str, DataValidationResult] = {}

    def create_rule(
        self,
        dataset_id: str,
        tenant_id: str,
        name: str,
        validation_type: ValidationType,
        target_field: str,
        validation_spec: Optional[Dict[str, Any]] = None,
        is_blocking: bool = True,
        rule_id: Optional[str] = None,
    ) -> DataValidationRule:
        rid = rule_id or f"dvr-{uuid.uuid4().hex[:8]}"
        rule = DataValidationRule(
            rule_id=rid,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            name=name,
            validation_type=validation_type,
            target_field=target_field,
            validation_spec=validation_spec or {},
            is_blocking=is_blocking,
        )
        self._rules[rid] = rule
        return rule

    def validate_data(
        self,
        dataset_id: str,
        tenant_id: str,
        data_sample: Optional[List[Dict[str, Any]]] = None,
    ) -> DataValidationResult:
        rules = [r for r in self._rules.values() if r.dataset_id == dataset_id and r.tenant_id == tenant_id]

        failures = []
        passed = 0
        failed = 0

        sample = data_sample or []

        if not rules:
            # Default validation if no custom rules exist
            if sample:
                passed = len(sample)
            else:
                passed = 1
        else:
            for rule in rules:
                rule_failed = False
                for idx, row in enumerate(sample):
                    val = row.get(rule.target_field)
                    if rule.validation_type == ValidationType.TYPE:
                        expected_type = rule.validation_spec.get("expected_type", "str")
                        if expected_type == "int" and not isinstance(val, int):
                            rule_failed = True
                            failures.append(f"Row {idx}: field '{rule.target_field}' value {val} is not int")
                        elif expected_type == "str" and not isinstance(val, str):
                            rule_failed = True
                            failures.append(f"Row {idx}: field '{rule.target_field}' value {val} is not str")
                    elif rule.validation_type == ValidationType.RANGE:
                        min_v = rule.validation_spec.get("min")
                        max_v = rule.validation_spec.get("max")
                        if val is not None:
                            if min_v is not None and val < min_v:
                                rule_failed = True
                                failures.append(f"Row {idx}: field '{rule.target_field}' value {val} < min {min_v}")
                            if max_v is not None and val > max_v:
                                rule_failed = True
                                failures.append(f"Row {idx}: field '{rule.target_field}' value {val} > max {max_v}")
                    elif rule.validation_type == ValidationType.CONSTRAINT:
                        if rule.validation_spec.get("not_null") and val is None:
                            rule_failed = True
                            failures.append(f"Row {idx}: field '{rule.target_field}' violates NOT NULL constraint")

                if rule_failed:
                    failed += 1
                else:
                    passed += 1

        status = ValidationStatus.PASSED if failed == 0 else ValidationStatus.FAILED
        vid = f"val-{uuid.uuid4().hex[:8]}"

        result = DataValidationResult(
            validation_id=vid,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            status=status,
            evaluated_rules=passed + failed,
            passed_rules=passed,
            failed_rules=failed,
            failure_reasons=failures,
            explanation=f"Validation {status.value} for dataset {dataset_id}. Passed: {passed}, Failed: {failed}.",
        )
        self._results[vid] = result
        return result

    def get_result(self, validation_id: str, tenant_id: str) -> DataValidationResult:
        res = self._results.get(validation_id)
        if not res:
            raise Exception(f"Validation result '{validation_id}' not found.")
        if res.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return res
