"""Tests for AnomalyDetector statistical checks."""

from app.observability.anomaly_detection import AnomalyDetector


def test_cost_spike_detection():
    detector = AnomalyDetector(cost_spike_multiplier=2.0)
    detector.establish_baseline("agent.cost", [0.01, 0.01, 0.01, 0.01])

    evt = detector.detect_cost_spike("agent", current_cost=0.05, historical_costs=[0.01, 0.01, 0.01, 0.01])
    assert evt is not None
    assert evt.anomaly_type == "COST_SPIKE"
    assert evt.current_value == 0.05


def test_execution_loop_detection():
    detector = AnomalyDetector()
    history = ["tool_search", "tool_call", "tool_call", "tool_call", "tool_call", "tool_call"]

    evt = detector.detect_execution_loop(history, max_repeats=5, component="agent")
    assert evt is not None
    assert evt.anomaly_type == "EXECUTION_LOOP"
    assert evt.component == "agent"
