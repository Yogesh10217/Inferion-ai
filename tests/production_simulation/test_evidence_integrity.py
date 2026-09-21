from app.deployment.deployment_simulation import ProductionSimulationEngine
from app.deployment.secrets import SecretsSanitizer


def test_evidence_fingerprint_deterministic_and_secret_safe():
    engine = ProductionSimulationEngine()
    evidence = engine.run_simulation()

    fingerprint1 = evidence.calculate_evidence_fingerprint()
    fingerprint2 = evidence.calculate_evidence_fingerprint()

    assert len(fingerprint1) == 64
    assert fingerprint1 == fingerprint2

    # Verify secret sanitization on evidence payload
    raw_payload = {"log": "Connection failed with password=password123"}
    sanitized = SecretsSanitizer.sanitize_structure(raw_payload)
    assert "password123" not in str(sanitized)
    assert "[REDACTED:" in str(sanitized) or "[REDACTED]" in str(sanitized) or "[REDACTED" in str(sanitized)
