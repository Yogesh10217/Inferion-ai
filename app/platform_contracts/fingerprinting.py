"""Deterministic SHA-256 Fingerprinting & Canonical Serialization (Phase 5.30)."""

import hashlib
import json
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel


class FingerprintAlgorithm(str, Enum):
    SHA256 = "SHA256"


class Fingerprint(BaseModel):
    value: str
    algorithm: FingerprintAlgorithm = FingerprintAlgorithm.SHA256
    schema_version: str = "1.0.0"


class FingerprintValidationResult(BaseModel):
    is_valid: bool
    expected_fingerprint: str
    observed_fingerprint: str


class CanonicalSerializer:
    """Recursively converts objects into deterministic canonical JSON data structures."""

    @classmethod
    def serialize_obj(cls, obj: Any) -> Any:
        if obj is None:
            return None
        if isinstance(obj, (int, float, bool, str)):
            return obj
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, (datetime, date)):
            if isinstance(obj, datetime):
                if obj.tzinfo is None:
                    obj = obj.replace(tzinfo=timezone.utc)
                else:
                    obj = obj.astimezone(timezone.utc)
                return obj.isoformat()
            return obj.isoformat()
        if isinstance(obj, dict):
            return {str(k): cls.serialize_obj(v) for k, v in sorted(obj.items(), key=lambda x: str(x[0]))}
        if isinstance(obj, set):
            serialized_items = [cls.serialize_obj(i) for i in obj]
            return sorted(serialized_items, key=lambda x: str(x))
        if isinstance(obj, (list, tuple)):
            return [cls.serialize_obj(i) for i in obj]
        if hasattr(obj, "model_dump"):
            return cls.serialize_obj(obj.model_dump())
        if hasattr(obj, "__dict__"):
            return cls.serialize_obj({k: v for k, v in obj.__dict__.items() if not k.startswith("_")})
        return str(obj)

    @classmethod
    def to_canonical_json(cls, obj: Any) -> str:
        canonical_struct = cls.serialize_obj(obj)
        return json.dumps(canonical_struct, sort_keys=True, separators=(",", ":"))


class FingerprintGenerator:
    """Generates and verifies deterministic SHA-256 fingerprints."""

    @staticmethod
    def generate(obj: Any, contract_version: str = "1.0.0") -> str:
        canonical_json = CanonicalSerializer.to_canonical_json({"contract_version": contract_version, "payload": obj})
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    @staticmethod
    def verify(obj: Any, expected_fingerprint: str, contract_version: str = "1.0.0") -> FingerprintValidationResult:
        computed = FingerprintGenerator.generate(obj, contract_version)
        is_valid = computed == expected_fingerprint
        return FingerprintValidationResult(
            is_valid=is_valid,
            expected_fingerprint=expected_fingerprint,
            observed_fingerprint=computed,
        )
