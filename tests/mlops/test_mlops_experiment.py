"""Unit tests for ExperimentManager and A/B Testing."""

from app.mlops.experiments import ExperimentManager


def test_experiment_creation_variants_and_winner_selection():
    mgr = ExperimentManager()

    exp = mgr.create_experiment("Model Routing Experiment", tenant_id="tenant_exp")
    v1 = mgr.add_variant(exp.experiment_id, "GPT-4 Baseline", "asset_gpt4", "1.0.0", traffic_weight=50.0)
    v2 = mgr.add_variant(exp.experiment_id, "Claude-3 Candidate", "asset_claude3", "1.0.0", traffic_weight=50.0)

    mgr.start_experiment(exp.experiment_id)
    mgr.record_run(exp.experiment_id, v1.variant_id, {"q": "hi"}, {"a": "hello"})
    mgr.record_run(exp.experiment_id, v2.variant_id, {"q": "hi"}, {"a": "hello there"})

    completed_exp = mgr.select_winner(exp.experiment_id, v2.variant_id)
    assert completed_exp.status == "COMPLETED"
    assert completed_exp.winner_variant_id == v2.variant_id
