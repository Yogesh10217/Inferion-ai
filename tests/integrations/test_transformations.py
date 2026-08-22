"""Unit tests for TransformationPipeline, field mappings, and sensitive data redaction."""

import pytest
from app.integrations.transformation import TransformationPipeline, FieldMapping


def test_payload_transformation_and_redaction():
    tp = TransformationPipeline()
    raw_payload = {"user_name": "Alice", "api_key": "sk-secret-token-12345", "city": "NYC"}
    mappings = [
        FieldMapping(source_field="user_name", target_field="username"),
        FieldMapping(source_field="api_key", target_field="auth_key", redact_sensitive=True),
    ]

    transformed = tp.transform(raw_payload, mappings)
    assert transformed["username"] == "Alice"
    assert "sk-secret-token-12345" not in transformed["auth_key"]
