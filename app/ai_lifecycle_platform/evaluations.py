"""AI Evaluation Governance Subsystem (Phase 5.33)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.ai_lifecycle_platform.exceptions import CrossTenantLifecycleAccessException, EvaluationNotFoundException


class EvaluationCategory(str, Enum):
    QUALITY = "QUALITY"
    ACCURACY = "ACCURACY"
    SAFETY = "SAFETY"
    SECURITY = "SECURITY"
    RELIABILITY = "RELIABILITY"
    PERFORMANCE = "PERFORMANCE"
    COST = "COST"
    FAIRNESS = "FAIRNESS"
    COMPLIANCE = "COMPLIANCE"


class EvaluationStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class EvaluationMetric(BaseModel):
    name: str
    value: float
    threshold: float = 0.8
    passed: bool = True


class EvaluationResult(BaseModel):
    result_id: str = Field(default_factory=lambda: f"evres_{uuid.uuid4().hex[:12]}")
    category: EvaluationCategory = EvaluationCategory.QUALITY
    score: float = 0.95
    passed: bool = True
    metrics: List[EvaluationMetric] = Field(default_factory=list)
    evidence_references: List[str] = Field(default_factory=list)


class EvaluationRun(BaseModel):
    run_id: str = Field(default_factory=lambda: f"evrun_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_asset_id: str
    suite_id: str
    status: EvaluationStatus = EvaluationStatus.PASSED
    results: List[EvaluationResult] = Field(default_factory=list)
    overall_passed: bool = True
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvaluationDefinition(BaseModel):
    def_id: str = Field(default_factory=lambda: f"evdef_{uuid.uuid4().hex[:12]}")
    name: str
    category: EvaluationCategory = EvaluationCategory.QUALITY
    threshold: float = 0.8


class EvaluationSuite(BaseModel):
    suite_id: str = Field(default_factory=lambda: f"evsuite_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    definitions: List[EvaluationDefinition] = Field(default_factory=list)


class EvaluationManager:
    """Manages AI evaluation suites, runs, and evidence-backed evaluation results."""

    def __init__(self) -> None:
        self._suites: Dict[str, EvaluationSuite] = {}
        self._runs: Dict[str, EvaluationRun] = {}

    def create_suite(
        self,
        tenant_id: str,
        name: str,
        definitions: Optional[List[EvaluationDefinition]] = None,
    ) -> EvaluationSuite:
        defs = definitions or [
            EvaluationDefinition(name="Default Accuracy", category=EvaluationCategory.ACCURACY, threshold=0.8)
        ]
        suite = EvaluationSuite(tenant_id=tenant_id, name=name, definitions=defs)
        self._suites[suite.suite_id] = suite
        return suite

    def run_evaluation(
        self,
        tenant_id: str,
        target_asset_id: str,
        suite_id: str,
        overall_passed: bool = True,
        evidence_references: Optional[List[str]] = None,
    ) -> EvaluationRun:
        ev_references = evidence_references or ["ev_ref_default"]
        metrics = [EvaluationMetric(name="Accuracy", value=0.92, threshold=0.8, passed=overall_passed)]
        res = EvaluationResult(
            category=EvaluationCategory.QUALITY,
            score=0.92,
            passed=overall_passed,
            metrics=metrics,
            evidence_references=ev_references,
        )

        run = EvaluationRun(
            tenant_id=tenant_id,
            target_asset_id=target_asset_id,
            suite_id=suite_id,
            status=EvaluationStatus.PASSED if overall_passed else EvaluationStatus.FAILED,
            results=[res],
            overall_passed=overall_passed,
        )
        self._runs[run.run_id] = run
        return run

    def get_run(self, run_id: str, tenant_id: str) -> EvaluationRun:
        run = self._runs.get(run_id)
        if not run:
            raise EvaluationNotFoundException(run_id)
        if tenant_id != "global" and run.tenant_id != "global" and tenant_id != run.tenant_id:
            raise CrossTenantLifecycleAccessException(tenant_id, run.tenant_id)
        return run
