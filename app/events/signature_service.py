from datetime import datetime, timezone
import hmac
import hashlib
import time
from typing import Dict, Optional
from app.events.exceptions import InvalidSignatureException


class SignatureService:
    """Handles HMAC-SHA256 signature generation and verification for webhooks."""

    DEFAULT_TOLERANCE_SECONDS = 300  # 5 minutes

    @classmethod
    def generate_signature(cls, secret: str, timestamp: str, payload: str) -> str:
        """
        Generate HMAC-SHA256 signature.
        Format: v1=<hex_digest>
        String to sign: {timestamp}.{payload}
        """
        to_sign = f"{timestamp}.{payload}".encode("utf-8")
        digest = hmac.new(secret.encode("utf-8"), to_sign, hashlib.sha256).hexdigest()
        return f"v1={digest}"

    @classmethod
    def generate_headers(
        cls,
        event_id: str,
        event_type: str,
        secret: str,
        payload: str,
        timestamp: Optional[str] = None,
    ) -> Dict[str, str]:
        """Generate standard security headers for outgoing webhook requests."""
        if not timestamp:
            timestamp = str(int(time.time()))

        sig = cls.generate_signature(secret, timestamp, payload)

        return {
            "X-Event-ID": event_id,
            "X-Event-Type": event_type,
            "X-Timestamp": timestamp,
            "X-Signature": f"t={timestamp},{sig}",
            "Content-Type": "application/json",
        }

    @classmethod
    def verify_signature(
        cls,
        signature_header: str,
        payload: str,
        primary_secret: str,
        secondary_secret: Optional[str] = None,
        tolerance_seconds: int = DEFAULT_TOLERANCE_SECONDS,
    ) -> bool:
        """
        Verify incoming webhook signature header.
        Supports dual secrets for rotation and timestamp tolerance window for replay protection.
        Header format: t=<timestamp>,v1=<hash>
        """
        if not signature_header:
            raise InvalidSignatureException("Missing X-Signature header")

        parts = dict(pair.split("=", 1) for pair in signature_header.split(",") if "=" in pair)
        timestamp = parts.get("t")
        received_sig = parts.get("v1")

        if not timestamp or not received_sig:
            raise InvalidSignatureException("Invalid X-Signature header format")

        # Verify timestamp freshness (replay protection)
        try:
            ts_int = int(timestamp)
            now_int = int(time.time())
            if abs(now_int - ts_int) > tolerance_seconds:
                raise InvalidSignatureException("Webhook timestamp outside allowed tolerance window")
        except ValueError:
            raise InvalidSignatureException("Invalid timestamp in signature header")

        # Try primary secret
        expected_sig = cls.generate_signature(primary_secret, timestamp, payload)
        primary_sig = expected_sig.split("v1=")[-1]
        
        if hmac.compare_digest(received_sig, primary_sig):
            return True

        # Fallback to secondary secret if present (secret rotation support)
        if secondary_secret:
            expected_sec_sig = cls.generate_signature(secondary_secret, timestamp, payload)
            secondary_sig = expected_sec_sig.split("v1=")[-1]
            if hmac.compare_digest(received_sig, secondary_sig):
                return True

        raise InvalidSignatureException("Signature verification failed")
