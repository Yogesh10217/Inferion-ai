"""Shared Secret & Sensitive Data Redaction Subsystem (Phase 5.30)."""

import copy
from enum import Enum
from typing import Dict, Any, Optional, List, Set
from pydantic import BaseModel, Field

from app.security.secrets import SecretManager


class RedactionRule(BaseModel):
    sensitive_keys: Set[str] = Field(
        default_factory=lambda: {
            "secret",
            "key",
            "token",
            "password",
            "credential",
            "auth",
            "authorization",
            "api_key",
            "private_key",
        }
    )
    redaction_replacement: str = "[REDACTED]"


class RedactionPolicy(BaseModel):
    rule: RedactionRule = Field(default_factory=RedactionRule)
    redact_in_place: bool = False


class RedactionResult(BaseModel):
    sanitized_data: Any
    fields_redacted_count: int = 0


class SensitiveDataSanitizer:
    """Sanitizes sensitive values in data structures without mutating original domain objects."""

    def __init__(
        self,
        secret_manager: Optional[SecretManager] = None,
        policy: Optional[RedactionPolicy] = None,
    ) -> None:
        self.secret_manager = secret_manager or SecretManager()
        self.policy = policy or RedactionPolicy()

    @classmethod
    def sanitize(cls, data: Any) -> Any:
        return cls().sanitize_copy(data)

    @classmethod
    def sanitize_metadata(cls, data: Any) -> Any:
        return cls().sanitize_copy(data)

    def sanitize_copy(self, data: Any) -> Any:

        copied = copy.deepcopy(data)
        return self._sanitize_recursive(copied)

    def sanitize_for_logging(self, data: Any) -> Any:
        return self.sanitize_copy(data)

    def _sanitize_recursive(self, obj: Any) -> Any:
        if isinstance(obj, dict):
            new_dict = {}
            for k, v in obj.items():
                if any(s in str(k).lower() for s in self.policy.rule.sensitive_keys):
                    new_dict[k] = self.policy.rule.redaction_replacement
                else:
                    new_dict[k] = self._sanitize_recursive(v)
            return new_dict
        elif isinstance(obj, list):
            return [self._sanitize_recursive(i) for i in obj]
        elif isinstance(obj, set):
            return {self._sanitize_recursive(i) for i in obj}
        elif hasattr(obj, "model_dump"):
            dumped = obj.model_dump()
            sanitized_dump = self._sanitize_recursive(dumped)
            try:
                return type(obj)(**sanitized_dump)
            except Exception:
                return sanitized_dump
        return obj
