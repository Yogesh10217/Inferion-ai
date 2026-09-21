"""Unit tests for Evidence-Backed Insights Engine."""

from app.intelligence_platform.context import ContextBuilder
from app.intelligence_platform.insights import InsightManager, InsightType
from app.intelligence_platform.signals import IntelligenceSignalManager, SignalSource, SignalType


def test_insight_generation_requires_context_evidence():
    sig_mgr = IntelligenceSignalManager()
    sig = sig_mgr.ingest_signal(
        "t1", SignalSource.MLOPS, SignalType.MODEL_DRIFT, "Model accuracy dropped 5%", resource_id="model_v1"
    )

    ctx = ContextBuilder().assemble_context("t1", primary_resource_id="model_v1", signals=[sig])
    mgr = InsightManager()

    ins = mgr.generate_insight_from_context(
        tenant_id="t1",
        insight_type=InsightType.MODEL_BEHAVIOR,
        observation="Model output drift detected",
        recommended_next_step="Retrain model on recent dataset",
        context=ctx,
    )

    assert ins.insight_id.startswith("ins_")
    assert len(ins.evidences) >= 1
