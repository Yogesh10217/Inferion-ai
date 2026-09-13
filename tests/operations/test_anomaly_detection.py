from app.operations.anomaly_detection import AnomalyType, RuleBasedAnomalyDetector
from app.operations.observability_engine import ObservabilityEngine


def test_anomaly_detection_none():
    obs = ObservabilityEngine().collect_observations()
    anomalies = RuleBasedAnomalyDetector().detect_anomalies(obs)
    assert len(anomalies) == 0


def test_anomaly_detection_latency_spike():
    obs = ObservabilityEngine().collect_observations(
        app_data={"latency_p95": 1200.0, "error_rate": 0.001},
    )
    anomalies = RuleBasedAnomalyDetector().detect_anomalies(obs)
    assert any(a.anomaly_type == AnomalyType.LATENCY_SPIKE for a in anomalies)
