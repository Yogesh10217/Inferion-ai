"""Tests for EvaluationEngine metrics."""

from app.observability.context import ObservabilityContext
from app.observability.evaluation import EvaluationEngine


def test_evaluation_engine_metrics():
    ee = EvaluationEngine()
    ctx = ObservabilityContext(agent_id="agent-eval-1", model_id="gpt-4o")

    score = ee.evaluate_execution(
        execution_id="exec-e1",
        is_success=True,
        steps_completed=5,
        total_steps=5,
        planning_confidence=0.9,
        critique_score=0.95,
        context=ctx,
    )

    assert score.overall_quality_score > 0.8
    assert score.task_completion_rate == 1.0

    ag_score = ee.calculate_agent_score("agent-eval-1")
    assert ag_score["agent_success_rate"] == 1.0
    assert ag_score["count"] == 1
