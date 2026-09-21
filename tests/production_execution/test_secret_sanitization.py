from app.deployment.secrets import SecretsSanitizer


def test_secrets_sanitizer_masks_canary_secrets():
    payload = {
        "db_pass": "password123",
        "api_key": "admin123",
        "jwt_secret": "canary_secret",
        "normal_key": "enterprise-ai-platform",
    }
    sanitized = SecretsSanitizer.sanitize_structure(payload)

    assert "[REDACTED" in str(sanitized["db_pass"])
    assert "password123" not in str(sanitized["db_pass"])
    assert "[REDACTED" in str(sanitized["api_key"])
    assert "admin123" not in str(sanitized["api_key"])
    assert "[REDACTED" in str(sanitized["jwt_secret"])
    assert "canary_secret" not in str(sanitized["jwt_secret"])
    assert sanitized["normal_key"] == "enterprise-ai-platform"
