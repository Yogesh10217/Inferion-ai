from app.deployment.secrets import SecretsSanitizer
from app.deployment.deployment_simulation import ProductionSimulationEngine




def test_security_runtime_headers_and_cors():
    engine = ProductionSimulationEngine()
    evidence = engine.run_simulation()

    sec = evidence.security_results
    assert sec["hsts_present"] is True
    assert sec["x_frame_options"] == "DENY"
    assert sec["x_content_type_options"] == "nosniff"
    assert sec["referrer_policy"] == "strict-origin-when-cross-origin"
    assert "default-src" in sec["content_security_policy"]
    assert sec["cors_wildcard_rejected"] is True
    assert sec["docs_disabled"] is True


def test_secret_canary_safety_in_simulation():
    canary_secrets = [
        "password123",
        "123456",
        "admin123",
        "placeholder",
        "canary_secret",
    ]

    engine = ProductionSimulationEngine()
    evidence = engine.run_simulation()
    fingerprint = evidence.calculate_evidence_fingerprint()

    for secret in canary_secrets:
        sanitized = SecretsSanitizer.sanitize_text(f"log with secret={secret}")
        assert secret not in sanitized
        assert secret not in fingerprint
