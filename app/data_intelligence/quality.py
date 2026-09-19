"""Enterprise data quality intelligence (Phase 5.43)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import (
    CrossTenantDataIntelligenceException,
    DataQualityEvaluationException,
)


class DataQualityDimension(str, Enum):
    COMPLETENESS = "COMPLETENESS"
    ACCURACY = "ACCURACY"
    CONSISTENCY = "CONSISTENCY"
    VALIDITY = "VALIDITY"
    UNIQUENESS = "UNIQUENESS"
    TIMELINESS = "TIMELINESS"
    INTEGRITY = "INTEGRITY"


class DataQualityStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"
    SKIPPED = "SKIPPED"


class DataQualityRule(BaseModel):
    rule_id: str
    dataset_id: str
    tenant_id: str
    name: str
    dimension: DataQualityDimension
    target_field: Optional[str] = None
    min_threshold: float = 0.95
    max_threshold: float = 1.0
    rule_expression: str = ""
    is_critical: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataQualityScore(BaseModel):
    dimension: DataQualityDimension
    score: float
    passed_rules: int
    failed_rules: int
    explanation: str


class DataQualityResult(BaseModel):
    result_id: str
    dataset_id: str
    tenant_id: str
    status: DataQualityStatus
    overall_quality_score: float
    dimension_scores: Dict[DataQualityDimension, DataQualityScore]
    evaluated_rules_count: int
    passed_rules_count: int
    failed_rules_count: int
    explanation: str
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataQualityManager:
    """Manages rules and deterministic evaluation of data quality."""

    def __init__(self) -> None:
        self._rules: Dict[str, DataQualityRule] = {}
        self._results: Dict[str, DataQualityResult] = {}

    def create_rule(
        self,
        dataset_id: str,
        tenant_id: str,
        name: str,
        dimension: DataQualityDimension,
        target_field: Optional[str] = None,
        min_threshold: float = 0.95,
        rule_expression: str = "",
        is_critical: bool = False,
        rule_id: Optional[str] = None,
    ) -> DataQualityRule:
        rid = rule_id or f"dqr-{uuid.uuid4().hex[:8]}"
        rule = DataQualityRule(
            rule_id=rid,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            name=name,
            dimension=dimension,
            target_field=target_field,
            min_threshold=min_threshold,
            rule_expression=rule_expression,
            is_critical=is_critical,
        )
        self._rules[rid] = rule
        return rule

    def list_rules(self, dataset_id: str, tenant_id: str) -> List[DataQualityRule]:
        return [r for r in self._rules.values() if r.dataset_id == dataset_id and r.tenant_id == tenant_id]

    def evaluate_quality(
        self,
        dataset_id: str,
        tenant_id: str,
        observations: Optional[Dict[DataQualityDimension, float]] = None,
    ) -> DataQualityResult:
        rules = self.list_rules(dataset_id, tenant_id)

        # Deterministic evaluation using provided observations or default thresholds
        dim_scores: Dict[DataQualityDimension, DataQualityScore] = {}
        total_passed = 0
        total_failed = 0
        scores_list = []

        obs = observations or {dim: 0.98 for dim in DataQualityDimension}

        for dim in DataQualityDimension:
            dim_val = obs.get(dim, 0.98)
            dim_rules = [r for r in rules if r.dimension == dim]

            passed = 0
            failed = 0
            if dim_rules:
                for r in dim_rules:
                    if dim_val >= r.min_threshold:
                        passed += 1
                    else:
                        failed += 1
            else:
                if dim_val >= 0.90:
                    passed += 1
                else:
                    failed += 1

            total_passed += passed
            total_failed += failed
            scores_list.append(dim_val)

            dim_scores[dim] = DataQualityScore(
                dimension=dim,
                score=round(dim_val, 4),
                passed_rules=passed,
                failed_rules=failed,
                explanation=f"Dimension {dim.value} score {dim_val:.2f} ({passed} passed, {failed} failed)",
            )

        avg_score = round(sum(scores_list) / max(1, len(scores_list)), 4)
        overall_status = (
            DataQualityStatus.PASSED
            if avg_score >= 0.90 and total_failed == 0
            else (DataQualityStatus.WARNING if avg_score >= 0.75 else DataQualityStatus.FAILED)
        )

        res_id = f"dqr-res-{uuid.uuid4().hex[:8]}"
        result = DataQualityResult(
            result_id=res_id,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            status=overall_status,
            overall_quality_score=avg_score,
            dimension_scores=dim_scores,
            evaluated_rules_count=total_passed + total_failed,
            passed_rules_count=total_passed,
            failed_rules_count=total_failed,
            explanation=f"Evaluated {len(scores_list)} quality dimensions for dataset {dataset_id}. Status: {overall_status.value} (Score: {avg_score})",
        )
        self._results[res_id] = result
        return result

    def get_result(self, result_id: str, tenant_id: str) -> DataQualityResult:
        res = self._results.get(result_id)
        if not res:
            raise DataQualityEvaluationException(f"Quality result '{result_id}' not found.")
        if res.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return res
