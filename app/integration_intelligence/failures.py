"""Integration Failure Intelligence (Phase 5.40)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import CrossTenantIntegrationAccessException


class FailureType(str, Enum):
    TIMEOUT = "TIMEOUT"
    UNREACHABLE = "UNREACHABLE"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    RATE_LIMITED = "RATE_LIMITED"
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class FailureSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FailureEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"fail_evid_{uuid.uuid4().hex[:8]}")
    error_code: str
    error_message: str
    sanitized_stacktrace: Optional[str] = None


class IntegrationFailure(BaseModel):
    """Integration Failure Representation."""
    failure_id: str = Field(default_factory=lambda: f"fail_int_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    execution_id: str
    connector_id: str
    failure_type: FailureType
    severity: FailureSeverity = FailureSeverity.HIGH
    evidence: FailureEvidence
    failed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IntegrationFailureManager:
    """Manages integration failure telemetry and emits references to reliability and event intelligence."""

    def __init__(self) -> None:
        self._failures: Dict[str, IntegrationFailure] = {}

    def record_failure(
        self,
        tenant_id: str,
        execution_id: str,
        connector_id: str,
        failure_type: FailureType,
        error_code: str,
        error_message: str,
        severity: FailureSeverity = FailureSeverity.HIGH,
        sanitized_stacktrace: Optional[str] = None,
    ) -> IntegrationFailure:
        evid = FailureEvidence(
            error_code=error_code,
            error_message=error_message,
            sanitized_stacktrace=sanitized_stacktrace,
        )
        fail = IntegrationFailure(
            tenant_id=tenant_id,
            execution_id=execution_id,
            connector_id=connector_id,
            failure_type=failure_type,
            severity=severity,
            evidence=evid,
        )
        self._failures[fail.failure_id] = fail
        return fail

    def get_failure(self, tenant_id: str, failure_id: str) -> IntegrationFailure:
        fail = self._failures.get(failure_id)
        if not fail or fail.tenant_id != tenant_id:
            raise CrossTenantIntegrationAccessException()
        return fail

    def list_failures(self, tenant_id: str) -> List[IntegrationFailure]:
        return [f for f in self._failures.values() if f.tenant_id == tenant_id]
