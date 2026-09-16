"""Known Error Intelligence (Phase 5.41)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import CrossTenantOperationsAccessException


class KnownErrorStatus(str, Enum):
    PUBLISHED = "PUBLISHED"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"


class KnownError(BaseModel):
    known_error_id: str = Field(default_factory=lambda: f"ke_op_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    problem_id: Optional[str] = None
    workaround: str
    remediation_reference: Optional[str] = None
    status: KnownErrorStatus = KnownErrorStatus.PUBLISHED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnownErrorManager:
    """Manages known error registry and workaround lookup."""

    def __init__(self) -> None:
        self._known_errors: Dict[str, KnownError] = {}

    def publish_known_error(
        self,
        tenant_id: str,
        title: str,
        workaround: str,
        problem_id: Optional[str] = None,
        remediation_reference: Optional[str] = None,
    ) -> KnownError:
        ke = KnownError(
            tenant_id=tenant_id,
            title=title,
            workaround=workaround,
            problem_id=problem_id,
            remediation_reference=remediation_reference,
        )
        self._known_errors[ke.known_error_id] = ke
        return ke

    def get_known_error(self, tenant_id: str, known_error_id: str) -> KnownError:
        ke = self._known_errors.get(known_error_id)
        if not ke or ke.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return ke

    def list_known_errors(self, tenant_id: str) -> List[KnownError]:
        return [k for k in self._known_errors.values() if k.tenant_id == tenant_id]
