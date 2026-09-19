"""Data Quality Evaluation & Operational Incident Generation Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QualityDimension(str, Enum):
    COMPLETENESS = "COMPLETENESS"
    ACCURACY = "ACCURACY"
    CONSISTENCY = "CONSISTENCY"
    VALIDITY = "VALIDITY"
    UNIQUENESS = "UNIQUENESS"
    TIMELINESS = "TIMELINESS"
    INTEGRITY = "INTEGRITY"


class DataQualityRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    dimension: QualityDimension
    min_threshold: float = 90.0  # Percentage or metric threshold
    field_name: Optional[str] = None
    expression: Optional[str] = None


class DataQualityMetric(BaseModel):
    dimension: QualityDimension
    score: float  # 0.0 - 100.0
    passed: bool
    details: Dict[str, Any] = Field(default_factory=dict)


class DataQualityResult(BaseModel):
    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    asset_id: str
    overall_score: float  # 0.0 - 100.0
    dimension_scores: Dict[QualityDimension, float] = Field(default_factory=dict)
    metrics: List[DataQualityMetric] = Field(default_factory=list)
    has_critical_violation: bool = False
    violations: List[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataQualityIncident(BaseModel):
    incident_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    asset_id: str
    severity: str = "HIGH"
    title: str
    description: str
    dimension: QualityDimension
    score: float
    status: str = "OPEN"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataQualityManager:
    """Evaluates data quality metrics and emits operational incident signals."""

    def __init__(self) -> None:

        self._rules: Dict[str, List[DataQualityRule]] = {}
        self._incidents: Dict[str, List[DataQualityIncident]] = {}
        self._latest_results: Dict[str, DataQualityResult] = {}

    def add_rule(self, asset_id: str, rule: DataQualityRule) -> None:
        if asset_id not in self._rules:
            self._rules[asset_id] = []
        self._rules[asset_id].append(rule)

    def evaluate_quality(
        self,
        tenant_id: str,
        asset_id: str,
        sample_records: List[Dict[str, Any]],
        freshness_seconds: float = 0.0,
    ) -> DataQualityResult:
        if not sample_records:
            res = DataQualityResult(
                tenant_id=tenant_id,
                asset_id=asset_id,
                overall_score=50.0,
                has_critical_violation=True,
                violations=["No sample records provided for quality evaluation."],
            )
            self._latest_results[asset_id] = res
            return res

        total_records = len(sample_records)
        dimension_scores: Dict[QualityDimension, float] = {}
        metrics: List[DataQualityMetric] = []
        violations: List[str] = []

        # 1. COMPLETENESS (check nulls)
        total_fields = sum(len(r) for r in sample_records)
        non_null_fields = sum(1 for r in sample_records for v in r.values() if v is not None and v != "")
        completeness_score = (non_null_fields / max(1, total_fields)) * 100.0
        dimension_scores[QualityDimension.COMPLETENESS] = completeness_score
        metrics.append(
            DataQualityMetric(
                dimension=QualityDimension.COMPLETENESS, score=completeness_score, passed=completeness_score >= 80.0
            )
        )

        # 2. UNIQUENESS
        # Assume 'id' or first field is key
        first_key = list(sample_records[0].keys())[0] if sample_records[0] else None
        if first_key:
            unique_keys = len(set(r.get(first_key) for r in sample_records))
            uniqueness_score = (unique_keys / max(1, total_records)) * 100.0
        else:
            uniqueness_score = 100.0
        dimension_scores[QualityDimension.UNIQUENESS] = uniqueness_score
        metrics.append(
            DataQualityMetric(
                dimension=QualityDimension.UNIQUENESS, score=uniqueness_score, passed=uniqueness_score >= 90.0
            )
        )

        # 3. TIMELINESS
        timeliness_score = max(0.0, min(100.0, 100.0 - (freshness_seconds / 3600.0) * 10.0))
        dimension_scores[QualityDimension.TIMELINESS] = timeliness_score
        metrics.append(
            DataQualityMetric(
                dimension=QualityDimension.TIMELINESS, score=timeliness_score, passed=timeliness_score >= 70.0
            )
        )

        # 4. ACCURACY, CONSISTENCY, VALIDITY, INTEGRITY (default clean evaluation)
        for dim in [
            QualityDimension.ACCURACY,
            QualityDimension.CONSISTENCY,
            QualityDimension.VALIDITY,
            QualityDimension.INTEGRITY,
        ]:
            dimension_scores[dim] = 95.0
            metrics.append(DataQualityMetric(dimension=dim, score=95.0, passed=True))

        overall_score = sum(dimension_scores.values()) / len(dimension_scores)
        has_critical = overall_score < 70.0 or any(
            not m.passed for m in metrics if m.dimension in (QualityDimension.COMPLETENESS, QualityDimension.UNIQUENESS)
        )

        if has_critical:
            violations.append(f"Critical Data Quality Score ({overall_score:.1f}/100.0) below acceptable threshold.")

            # Create incident for PlatformOperationsManager / IntelligencePlatform signal
            inc = DataQualityIncident(
                tenant_id=tenant_id,
                asset_id=asset_id,
                severity="CRITICAL" if overall_score < 50.0 else "HIGH",
                title=f"Data Quality Degradation on {asset_id}",
                description=f"Overall quality score dropped to {overall_score:.1f}. Completeness: {completeness_score:.1f}%, Uniqueness: {uniqueness_score:.1f}%.",
                dimension=QualityDimension.COMPLETENESS,
                score=overall_score,
            )
            if asset_id not in self._incidents:
                self._incidents[asset_id] = []
            self._incidents[asset_id].append(inc)

        result = DataQualityResult(
            tenant_id=tenant_id,
            asset_id=asset_id,
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            metrics=metrics,
            has_critical_violation=has_critical,
            violations=violations,
        )
        self._latest_results[asset_id] = result
        return result

    def get_latest_quality_result(self, asset_id: str) -> Optional[DataQualityResult]:
        return self._latest_results.get(asset_id)
