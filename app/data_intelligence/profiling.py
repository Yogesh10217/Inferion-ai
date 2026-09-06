"""Data profiling intelligence (Phase 5.43)."""

import uuid
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import DatasetNotFoundException, CrossTenantDataIntelligenceException


class ProfileDimension(str, Enum):
    COMPLETENESS = "COMPLETENESS"
    UNIQUENESS = "UNIQUENESS"
    NULL_DISTRIBUTION = "NULL_DISTRIBUTION"
    CARDINALITY = "CARDINALITY"
    VALUE_DISTRIBUTION = "VALUE_DISTRIBUTION"
    FORMAT_CONSISTENCY = "FORMAT_CONSISTENCY"
    SCHEMA_STRUCTURE = "SCHEMA_STRUCTURE"


class ProfileMetric(BaseModel):
    metric_name: str
    dimension: ProfileDimension
    value: float
    description: str = ""
    details: Dict[str, Any] = Field(default_factory=dict)


class ProfileResult(BaseModel):
    profile_id: str
    dataset_id: str
    tenant_id: str
    total_records_analyzed: int
    total_columns_analyzed: int
    overall_completeness: float
    overall_uniqueness: float
    null_rate: float
    metrics: List[ProfileMetric] = Field(default_factory=list)
    profiled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataProfile(BaseModel):
    profile_id: str
    dataset_id: str
    tenant_id: str
    result: ProfileResult
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DataProfilingManager:
    """Manages dataset profiling analysis."""

    def __init__(self) -> None:
        self._profiles: Dict[str, DataProfile] = {}

    def profile_dataset(
        self,
        dataset_id: str,
        tenant_id: str,
        total_records: int = 1000,
        total_columns: int = 10,
        null_count: int = 50,
        duplicate_count: int = 10,
        custom_metrics: Optional[List[ProfileMetric]] = None,
    ) -> DataProfile:
        pid = f"prof-{uuid.uuid4().hex[:8]}"

        completeness = max(0.0, 1.0 - (null_count / max(1, total_records * total_columns)))
        uniqueness = max(0.0, 1.0 - (duplicate_count / max(1, total_records)))
        null_rate = null_count / max(1, total_records * total_columns)

        metrics = custom_metrics or [
            ProfileMetric(
                metric_name="null_rate",
                dimension=ProfileDimension.NULL_DISTRIBUTION,
                value=null_rate,
                description="Ratio of null values across all fields",
            ),
            ProfileMetric(
                metric_name="row_cardinality",
                dimension=ProfileDimension.CARDINALITY,
                value=float(total_records),
                description="Total row count evaluated",
            ),
            ProfileMetric(
                metric_name="completeness_score",
                dimension=ProfileDimension.COMPLETENESS,
                value=completeness,
                description="Ratio of non-null field values",
            ),
            ProfileMetric(
                metric_name="uniqueness_score",
                dimension=ProfileDimension.UNIQUENESS,
                value=uniqueness,
                description="Ratio of unique records",
            ),
        ]

        result = ProfileResult(
            profile_id=pid,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            total_records_analyzed=total_records,
            total_columns_analyzed=total_columns,
            overall_completeness=completeness,
            overall_uniqueness=uniqueness,
            null_rate=null_rate,
            metrics=metrics,
        )

        dp = DataProfile(
            profile_id=pid,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            result=result,
        )
        self._profiles[pid] = dp
        return dp

    def get_profile(self, profile_id: str, tenant_id: str) -> DataProfile:
        dp = self._profiles.get(profile_id)
        if not dp:
            raise DatasetNotFoundException(profile_id)
        if dp.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return dp

    def list_profiles(self, dataset_id: str, tenant_id: str) -> List[DataProfile]:
        return [
            dp for dp in self._profiles.values()
            if dp.dataset_id == dataset_id and dp.tenant_id == tenant_id
        ]
