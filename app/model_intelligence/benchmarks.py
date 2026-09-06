"""Model Benchmarking Intelligence (Phase 5.44)."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException

logger = logging.getLogger(__name__)


class BenchmarkMetric(BaseModel):
    metric_name: str
    score: float
    unit: str = "percentage"


class BenchmarkSuite(BaseModel):
    suite_id: str
    name: str
    category: str = "general_reasoning"
    description: Optional[str] = None


class BenchmarkResult(BaseModel):
    model_id: str
    model_name: str
    version_tag: str
    suite_name: str
    score: float
    metrics: List[BenchmarkMetric] = Field(default_factory=list)


class BenchmarkComparison(BaseModel):
    suite_name: str
    baseline_model_id: str
    candidate_model_id: str
    baseline_score: float
    candidate_score: float
    diff_score: float
    winner: str


class ModelBenchmark(BaseModel):
    benchmark_id: str
    tenant_id: str
    suite: BenchmarkSuite
    results: List[BenchmarkResult] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelBenchmarkManager:
    """Manages model benchmarking intelligence."""

    def __init__(self) -> None:
        self._benchmarks: Dict[str, ModelBenchmark] = {}

    def run_benchmark(
        self,
        tenant_id: str,
        suite_name: str,
        results: List[BenchmarkResult],
    ) -> ModelBenchmark:
        bm_id = f"bm-{uuid.uuid4().hex[:8]}"
        suite = BenchmarkSuite(suite_id=f"suite-{uuid.uuid4().hex[:6]}", name=suite_name)
        bm = ModelBenchmark(benchmark_id=bm_id, tenant_id=tenant_id, suite=suite, results=results)
        self._benchmarks[bm_id] = bm
        return bm

    def compare_models(
        self,
        tenant_id: str,
        suite_name: str,
        baseline_model_id: str,
        candidate_model_id: str,
        baseline_score: float,
        candidate_score: float,
    ) -> BenchmarkComparison:
        diff = candidate_score - baseline_score
        winner = candidate_model_id if diff > 0 else (baseline_model_id if diff < 0 else "TIE")
        return BenchmarkComparison(
            suite_name=suite_name,
            baseline_model_id=baseline_model_id,
            candidate_model_id=candidate_model_id,
            baseline_score=baseline_score,
            candidate_score=candidate_score,
            diff_score=diff,
            winner=winner,
        )

    def list_benchmarks(self, tenant_id: str) -> List[ModelBenchmark]:
        return [b for b in self._benchmarks.values() if b.tenant_id == tenant_id]
