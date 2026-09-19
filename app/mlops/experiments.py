"""Experimentation & A/B / Multi-Variant Testing Engine."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ExperimentVariant(BaseModel):
    variant_id: str = Field(default_factory=lambda: f"var_{uuid.uuid4().hex[:10]}")
    name: str  # e.g. "Control (GPT-4)", "Treatment A (Claude-3)", "Treatment B (Prompt V2)"
    asset_id: str
    version_number: str
    traffic_weight: float = 50.0  # Percentage allocation


class ExperimentMetricScore(BaseModel):
    success_rate: float = 95.0
    latency_ms: float = 110.0
    cost_dollars: float = 0.0012
    token_usage: int = 450
    quality_score: float = 92.5
    hallucination_rate: float = 0.01
    user_feedback_score: float = 4.8
    tool_success_rate: float = 98.0
    plan_confidence: float = 0.94


class ExperimentRun(BaseModel):
    run_id: str = Field(default_factory=lambda: f"run_{uuid.uuid4().hex[:10]}")
    experiment_id: str
    variant_id: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    scores: ExperimentMetricScore = Field(default_factory=ExperimentMetricScore)
    created_at: datetime = Field(default_factory=_now)


class Experiment(BaseModel):
    experiment_id: str = Field(default_factory=lambda: f"exp_{uuid.uuid4().hex[:10]}")
    name: str
    tenant_id: str = "global"
    description: str = ""
    status: str = "DRAFT"  # DRAFT, RUNNING, PAUSED, COMPLETED, CANCELLED
    variants: List[ExperimentVariant] = Field(default_factory=list)
    winner_variant_id: Optional[str] = None

    created_at: datetime = Field(default_factory=_now)
    completed_at: Optional[datetime] = None


class ExperimentManager:
    """Manages A/B and multi-variant experiments across models, prompts, agents, and strategies."""

    def __init__(self) -> None:
        self._experiments: Dict[str, Experiment] = {}
        self._runs: List[ExperimentRun] = []

    def create_experiment(self, name: str, tenant_id: str = "global", description: str = "") -> Experiment:
        exp = Experiment(name=name, tenant_id=tenant_id, description=description)
        self._experiments[exp.experiment_id] = exp
        logger.info(f"[EXPERIMENT ENGINE] Created experiment '{name}' (ID: {exp.experiment_id})")
        return exp

    def add_variant(
        self, experiment_id: str, name: str, asset_id: str, version_number: str, traffic_weight: float = 50.0
    ) -> ExperimentVariant:
        exp = self.get_experiment(experiment_id)
        var = ExperimentVariant(
            name=name, asset_id=asset_id, version_number=version_number, traffic_weight=traffic_weight
        )
        exp.variants.append(var)
        logger.info(f"[EXPERIMENT ENGINE] Added variant '{name}' to experiment '{exp.name}'")
        return var

    def start_experiment(self, experiment_id: str) -> Experiment:
        exp = self.get_experiment(experiment_id)
        exp.status = "RUNNING"
        logger.info(f"[EXPERIMENT ENGINE] Started experiment '{exp.name}'")
        return exp

    def record_run(
        self,
        experiment_id: str,
        variant_id: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        scores: Optional[ExperimentMetricScore] = None,
    ) -> ExperimentRun:
        run = ExperimentRun(
            experiment_id=experiment_id,
            variant_id=variant_id,
            input_data=input_data,
            output_data=output_data,
            scores=scores or ExperimentMetricScore(),
        )
        self._runs.append(run)
        return run

    def select_winner(self, experiment_id: str, winner_variant_id: str) -> Experiment:
        exp = self.get_experiment(experiment_id)
        exp.winner_variant_id = winner_variant_id
        exp.status = "COMPLETED"
        exp.completed_at = _now()
        logger.info(f"[EXPERIMENT ENGINE] Completed experiment '{exp.name}': Winner = '{winner_variant_id}'")
        return exp

    def select_variant_for_request(self, experiment_id: str, request_id: str) -> Optional[ExperimentVariant]:
        """Deterministically select a variant for a request based on traffic weight distribution."""
        exp = self._experiments.get(experiment_id)
        if not exp or exp.status != "RUNNING" or not exp.variants:
            return None

        # Calculate total weight
        total_weight = sum(v.traffic_weight for v in exp.variants)
        if total_weight <= 0:
            return exp.variants[0]

        import hashlib

        h = int(hashlib.md5(f"{experiment_id}:{request_id}".encode()).hexdigest(), 16)
        bucket = (h % 10000) / 100.0  # Float 0.00 - 99.99

        cumulative = 0.0
        for variant in exp.variants:
            cumulative += (variant.traffic_weight / total_weight) * 100.0
            if bucket <= cumulative:
                return variant
        return exp.variants[0]

    def get_experiment(self, experiment_id: str) -> Experiment:
        exp = self._experiments.get(experiment_id)
        if not exp:
            raise KeyError(f"Experiment '{experiment_id}' not found")
        return exp
