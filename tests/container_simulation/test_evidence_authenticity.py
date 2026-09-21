from app.deployment.deployment_simulation import ProductionSimulationEngine
from app.deployment.secrets import SecretsSanitizer


def test_evidence_fingerprint_sha256_authenticity():
    engine = ProductionSimulationEngine()
    evidence = engine.run_simulation()
    fingerprint = evidence.calculate_evidence_fingerprint()

    assert len(fingerprint) == 64
    assert all(c in "0123456789abcdef" for c in fingerprint)

    raw_secrets = ["password123", "123456", "admin123", "placeholder", "canary_secret"]
    for s in raw_secrets:
        assert s not in fingerprint
        sanitized = SecretsSanitizer.sanitize_text(f"log with secret={s}")
        assert s not in sanitized
        assert "[REDACTED:" in sanitized or "[REDACTED" in sanitized
