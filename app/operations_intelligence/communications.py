"""Operational Communication Intelligence & Sanitization (Phase 5.41)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import CrossTenantOperationsAccessException
from app.platform_contracts.redaction import SensitiveDataSanitizer


class CommunicationAudience(str, Enum):
    INTERNAL_OPS = "INTERNAL_OPS"
    EXEC_STAKEHOLDERS = "EXEC_STAKEHOLDERS"
    PUBLIC_STATUS_PAGE = "PUBLIC_STATUS_PAGE"
    CUSTOMER_SUPPORT = "CUSTOMER_SUPPORT"


class CommunicationStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    SENT = "SENT"


class OperationalCommunication(BaseModel):
    communication_id: str = Field(default_factory=lambda: f"comm_op_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    incident_id: str
    audience: CommunicationAudience = CommunicationAudience.INTERNAL_OPS
    status: CommunicationStatus = CommunicationStatus.DRAFT
    sanitized_message: str
    sent_at: Optional[datetime] = None


class CommunicationManager:
    """Manages operational communications with sensitive data sanitization."""

    def __init__(self) -> None:
        self._communications: Dict[str, OperationalCommunication] = {}
        self.sanitizer = SensitiveDataSanitizer()

    def create_communication(
        self,
        tenant_id: str,
        incident_id: str,
        raw_message: str,
        audience: CommunicationAudience = CommunicationAudience.INTERNAL_OPS,
    ) -> OperationalCommunication:
        import re

        sanitized_msg = raw_message
        # Sanitize sensitive patterns in text string
        sanitized_msg = re.sub(
            r"(password|secret|token|api_key|credential)['\"\s:=]+['\"]?([^'\"\s]+)['\"]?",
            r"\1: '[REDACTED]'",
            sanitized_msg,
            flags=re.IGNORECASE,
        )
        self.sanitizer.sanitize({"password": raw_message})

        comm = OperationalCommunication(
            tenant_id=tenant_id,
            incident_id=incident_id,
            audience=audience,
            sanitized_message=sanitized_msg,
        )
        self._communications[comm.communication_id] = comm
        return comm

    def send_communication(self, tenant_id: str, communication_id: str) -> OperationalCommunication:
        comm = self.get_communication(tenant_id, communication_id)
        comm.status = CommunicationStatus.SENT
        comm.sent_at = datetime.now(timezone.utc)
        return comm

    def get_communication(self, tenant_id: str, communication_id: str) -> OperationalCommunication:
        comm = self._communications.get(communication_id)
        if not comm or comm.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return comm
