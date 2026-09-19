"""AI Quality and Evaluation Metrics Subsystem."""

from __future__ import annotations

import logging
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from app.observability.context import ObservabilityContext, get_current_context

logger = logging.getLogger(__name__)


@dataclass
class EvaluationScore:
    """Holds computed quality and evaluation metrics for an execution or model."""

    execution_id: str
    agent_id: Optional[str]
    workflow_id: Optional[str]
    model_id: Optional[str]
    task_completion_rate: float  # 0.0 to 1.0
    planning_confidence: float  # 0.0 to 1.0
    critique_score: float  # 0.0 to 1.0
    user_feedback_score: Optional[float] = None  # 1.0 to 5.0
    hallucination_signal: Optional[float] = None  # 0.0 to 1.0 (None if ground truth missing)
    overall_quality_score: float = 0.0
    evaluated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EvaluationEngine:
    """Evaluates agent, workflow, and model execution quality, task completion, and quality scores."""

    def __init__(self) -> None:
        self._evaluations: List[EvaluationScore] = []

    def evaluate_execution(
        self,
        execution_id: str,
        is_success: bool,
        steps_completed: int,
        total_steps: int,
        planning_confidence: float = 0.85,
        critique_score: float = 0.90,
        user_feedback_score: Optional[float] = None,
        reference_answer: Optional[str] = None,
        actual_output: Optional[str] = None,
        context: Optional[ObservabilityContext] = None,
    ) -> EvaluationScore:
        """Evaluate an execution and calculate composite quality metrics."""
        ctx = context or get_current_context()

        completion_rate = (steps_completed / total_steps) if total_steps > 0 else (1.0 if is_success else 0.0)
        completion_rate = min(1.0, max(0.0, completion_rate))

        # Calculate hallucination signal only if ground truth reference is provided
        hallucination_signal = None
        if reference_answer and actual_output:
            ref_words = set(reference_answer.lower().split())
            act_words = set(actual_output.lower().split())
            overlap = len(ref_words.intersection(act_words)) / len(ref_words) if ref_words else 1.0
            hallucination_signal = round(1.0 - overlap, 4)

        # Composite overall quality score (0.0 - 1.0)
        weighted_score = (completion_rate * 0.4) + (planning_confidence * 0.3) + (critique_score * 0.3)
        if user_feedback_score is not None:
            norm_feedback = (user_feedback_score - 1.0) / 4.0
            weighted_score = (weighted_score * 0.7) + (norm_feedback * 0.3)

        overall_score = round(min(1.0, max(0.0, weighted_score)), 4)

        eval_res = EvaluationScore(
            execution_id=execution_id,
            agent_id=ctx.agent_id,
            workflow_id=ctx.workflow_id,
            model_id=ctx.model_id,
            task_completion_rate=round(completion_rate, 4),
            planning_confidence=round(planning_confidence, 4),
            critique_score=round(critique_score, 4),
            user_feedback_score=user_feedback_score,
            hallucination_signal=hallucination_signal,
            overall_quality_score=overall_score,
        )

        self._evaluations.append(eval_res)
        return eval_res

    def calculate_agent_score(self, agent_id: str) -> Dict[str, Any]:
        """Calculate aggregate scores and success rates for an agent."""
        matching = [e for e in self._evaluations if e.agent_id == agent_id]
        if not matching:
            return {
                "agent_id": agent_id,
                "count": 0,
                "agent_success_rate": 0.0,
                "avg_task_completion": 0.0,
                "avg_quality_score": 0.0,
            }

        avg_completion = sum(e.task_completion_rate for e in matching) / len(matching)
        avg_quality = sum(e.overall_quality_score for e in matching) / len(matching)
        success_count = sum(1 for e in matching if e.task_completion_rate >= 0.99)
        success_rate = success_count / len(matching)

        return {
            "agent_id": agent_id,
            "count": len(matching),
            "agent_success_rate": round(success_rate, 4),
            "avg_task_completion": round(avg_completion, 4),
            "avg_quality_score": round(avg_quality, 4),
        }

    def calculate_workflow_score(self, workflow_id: str) -> Dict[str, Any]:
        """Calculate aggregate scores and completion rates for a workflow."""
        matching = [e for e in self._evaluations if e.workflow_id == workflow_id]
        if not matching:
            return {
                "workflow_id": workflow_id,
                "count": 0,
                "workflow_success_rate": 0.0,
                "avg_task_completion": 0.0,
                "avg_quality_score": 0.0,
            }

        avg_completion = sum(e.task_completion_rate for e in matching) / len(matching)
        avg_quality = sum(e.overall_quality_score for e in matching) / len(matching)
        success_count = sum(1 for e in matching if e.task_completion_rate >= 0.99)

        return {
            "workflow_id": workflow_id,
            "count": len(matching),
            "workflow_success_rate": round(success_count / len(matching), 4),
            "avg_task_completion": round(avg_completion, 4),
            "avg_quality_score": round(avg_quality, 4),
        }

    def compare_agent_versions(self, agent_v1_id: str, agent_v2_id: str) -> Dict[str, Any]:
        """Compare performance and quality benchmarks between two agent versions."""
        score_v1 = self.calculate_agent_score(agent_v1_id)
        score_v2 = self.calculate_agent_score(agent_v2_id)

        quality_diff = round(score_v2["avg_quality_score"] - score_v1["avg_quality_score"], 4)
        success_diff = round(score_v2["agent_success_rate"] - score_v1["agent_success_rate"], 4)

        return {
            "agent_v1": score_v1,
            "agent_v2": score_v2,
            "quality_difference": quality_diff,
            "success_rate_difference": success_diff,
            "better_version": agent_v2_id if quality_diff >= 0 else agent_v1_id,
        }

    def compare_model_performance(self, model_a: str, model_b: str) -> Dict[str, Any]:
        """Compare quality score aggregates across two AI model identifiers."""
        m_a = [e for e in self._evaluations if e.model_id == model_a]
        m_b = [e for e in self._evaluations if e.model_id == model_b]

        avg_a = (sum(e.overall_quality_score for e in m_a) / len(m_a)) if m_a else 0.0
        avg_b = (sum(e.overall_quality_score for e in m_b) / len(m_b)) if m_b else 0.0

        return {
            "model_a": {"model_id": model_a, "count": len(m_a), "avg_quality_score": round(avg_a, 4)},
            "model_b": {"model_id": model_b, "count": len(m_b), "avg_quality_score": round(avg_b, 4)},
            "quality_delta": round(avg_b - avg_a, 4),
            "top_performing_model": model_b if avg_b >= avg_a else model_a,
        }
