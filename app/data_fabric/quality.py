"""Data Quality Platform Engine."""

from datetime import datetime, timezone
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DataQualityRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: f"rule_{uuid.uuid4().hex[:10]}")
    name: str
    rule_type: str  # COMPLETENESS, UNIQUENESS, FRESHNESS, SCHEMA_VALIDITY
    target_field: Optional[str] = None
    min_score: float = 80.0


class DataQualityResult(BaseModel):
    result_id: str = Field(default_factory=lambda: f"qr_{uuid.uuid4().hex[:10]}")
    asset_id: str
    tenant_id: str = "global"

    overall_score: float
    completeness_score: float
    uniqueness_score: float
    freshness_score: float
    schema_validity_score: float

    warnings: List[str] = Field(default_factory=list)
    failures: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

    evaluated_at: datetime = Field(default_factory=_now)


class DataQualityEngine:
    """Evaluates data quality metrics and produces comprehensive scorecards."""

    def evaluate_quality(self, asset_id: str, records: List[Dict[str, Any]], tenant_id: str = "global") -> DataQualityResult:
        if not records:
            return DataQualityResult(
                asset_id=asset_id,
                tenant_id=tenant_id,
                overall_score=100.0,
                completeness_score=100.0,
                uniqueness_score=100.0,
                freshness_score=100.0,
                schema_validity_score=100.0,
            )

        total = len(records)
        null_count = 0
        ids = []

        for r in records:
            null_count += sum(1 for v in r.values() if v is None)
            if "id" in r:
                ids.append(r["id"])

        total_fields = total * max(1, len(records[0]))
        completeness = max(0.0, 100.0 - (null_count / total_fields * 100.0))

        unique_ratio = len(set(ids)) / len(ids) if ids else 1.0
        uniqueness = unique_ratio * 100.0

        freshness = 95.0
        schema_validity = 100.0

        overall = (completeness + uniqueness + freshness + schema_validity) / 4.0

        warnings = []
        if completeness < 90.0:
            warnings.append(f"Completeness ({completeness:.1f}%) below 90%")
        if uniqueness < 100.0:
            warnings.append(f"Duplicate records detected ({uniqueness:.1f}% unique)")

        res = DataQualityResult(
            asset_id=asset_id,
            tenant_id=tenant_id,
            overall_score=overall,
            completeness_score=completeness,
            uniqueness_score=uniqueness,
            freshness_score=freshness,
            schema_validity_score=schema_validity,
            warnings=warnings,
        )
        logger.info(f"[DATA QUALITY] Evaluated asset '{asset_id}': Overall Score = {overall:.2f}")
        return res
