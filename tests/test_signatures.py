import time

import pytest

from app.events.exceptions import InvalidSignatureException
from app.events.signature_service import SignatureService


def test_signature_generation_and_verification():
    secret = "test_webhook_secret_key"
    payload = '{"event":"inference.completed","status":"ok"}'
    timestamp = str(int(time.time()))

    headers = SignatureService.generate_headers(
        event_id="evt_123",
        event_type="inference.completed",
        secret=secret,
        payload=payload,
        timestamp=timestamp,
    )

    assert headers["X-Event-ID"] == "evt_123"
    assert headers["X-Event-Type"] == "inference.completed"
    assert headers["X-Timestamp"] == timestamp
    assert "X-Signature" in headers

    # Verify signature
    is_valid = SignatureService.verify_signature(
        signature_header=headers["X-Signature"],
        payload=payload,
        primary_secret=secret,
    )
    assert is_valid is True


def test_signature_secret_rotation():
    primary_secret = "new_rotated_secret"
    secondary_secret = "old_previous_secret"
    payload = '{"test":"rotation"}'
    timestamp = str(int(time.time()))

    # Generate header with OLD secret
    old_headers = SignatureService.generate_headers(
        event_id="evt_rot",
        event_type="organization.created",
        secret=secondary_secret,
        payload=payload,
        timestamp=timestamp,
    )

    # Verification with dual secrets should pass because secondary_secret matches!
    is_valid = SignatureService.verify_signature(
        signature_header=old_headers["X-Signature"],
        payload=payload,
        primary_secret=primary_secret,
        secondary_secret=secondary_secret,
    )
    assert is_valid is True


def test_signature_timestamp_replay_protection():
    secret = "secret123"
    payload = '{"data":1}'
    old_timestamp = str(int(time.time()) - 600)  # 10 minutes ago

    headers = SignatureService.generate_headers(
        event_id="evt_old",
        event_type="user.created",
        secret=secret,
        payload=payload,
        timestamp=old_timestamp,
    )

    # Should raise InvalidSignatureException due to timestamp window expired (default 300s)
    with pytest.raises(InvalidSignatureException, match="outside allowed tolerance window"):
        SignatureService.verify_signature(
            signature_header=headers["X-Signature"],
            payload=payload,
            primary_secret=secret,
            tolerance_seconds=300,
        )


def test_invalid_signature_fails():
    secret = "correct_secret"
    wrong_secret = "wrong_secret"
    payload = '{"data":1}'
    timestamp = str(int(time.time()))

    headers = SignatureService.generate_headers(
        event_id="evt_err",
        event_type="user.created",
        secret=secret,
        payload=payload,
        timestamp=timestamp,
    )

    with pytest.raises(InvalidSignatureException):
        SignatureService.verify_signature(
            signature_header=headers["X-Signature"],
            payload=payload,
            primary_secret=wrong_secret,
        )
