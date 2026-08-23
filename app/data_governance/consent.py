"""User Data Consent Management & Enforcement Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.data_governance.exceptions import ConsentViolationException


class ConsentStatus(str, Enum):
    PENDING = "PENDING"
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    WITHDRAWN = "WITHDRAWN"
    EXPIRED = "EXPIRED"


class ConsentPurpose(str, Enum):
    AI_CONTEXT = "AI_CONTEXT"
    PERSONALIZATION = "PERSONALIZATION"
    ANALYTICS = "ANALYTICS"
    TRAINING = "TRAINING"
    KNOWLEDGE_GENERATION = "KNOWLEDGE_GENERATION"
    AGENT_EXECUTION = "AGENT_EXECUTION"
    EXTERNAL_INTEGRATIONS = "EXTERNAL_INTEGRATIONS"


class ConsentScope(BaseModel):
    allowed_purposes: List[ConsentPurpose] = Field(default_factory=list)
    allowed_asset_ids: Optional[List[str]] = None
    expiration_date: Optional[datetime] = None


class DataConsent(BaseModel):
    consent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    subject_id: str
    status: ConsentStatus = ConsentStatus.GRANTED
    scope: ConsentScope
    granted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    withdrawn_at: Optional[datetime] = None
    consent_version: str = "1.0.0"


class ConsentManager:
    """Manages consent grants, withdrawals, and purpose-based validation."""

    def __init__(self) -> None:
        self._consents: Dict[str, Dict[str, DataConsent]] = {}  # tenant_id -> {subject_id -> DataConsent}
        self._withdrawn_keys: Dict[str, DataConsent] = {}

    def grant_consent(
        self,
        tenant_id: str,
        subject_id: str,
        purposes: List[ConsentPurpose],
        allowed_asset_ids: Optional[List[str]] = None,
        consent_version: str = "1.0.0",
    ) -> DataConsent:
        if tenant_id not in self._consents:
            self._consents[tenant_id] = {}

        consent = DataConsent(
            tenant_id=tenant_id,
            subject_id=subject_id,
            status=ConsentStatus.GRANTED,
            scope=ConsentScope(allowed_purposes=purposes, allowed_asset_ids=allowed_asset_ids),
            consent_version=consent_version,
        )
        self._consents[tenant_id][subject_id] = consent
        return consent

    def withdraw_consent(
        self,
        tenant_id: str,
        subject_id: str,
        idempotency_key: Optional[str] = None,
    ) -> DataConsent:
        ikey = idempotency_key or f"withdraw:{tenant_id}:{subject_id}"
        if ikey in self._withdrawn_keys:
            return self._withdrawn_keys[ikey]

        if tenant_id not in self._consents or subject_id not in self._consents[tenant_id]:
            # Create a withdrawn marker
            consent = DataConsent(
                tenant_id=tenant_id,
                subject_id=subject_id,
                status=ConsentStatus.WITHDRAWN,
                scope=ConsentScope(allowed_purposes=[]),
                withdrawn_at=datetime.now(timezone.utc),
            )
        else:
            consent = self._consents[tenant_id][subject_id]
            consent.status = ConsentStatus.WITHDRAWN
            consent.withdrawn_at = datetime.now(timezone.utc)

        self._withdrawn_keys[ikey] = consent
        return consent

    def evaluate_consent(
        self,
        tenant_id: str,
        subject_id: str,
        purpose: ConsentPurpose,
        asset_id: Optional[str] = None,
    ) -> bool:
        """Evaluate if active consent exists for the requested purpose and asset."""
        tenant_consents = self._consents.get(tenant_id, {})
        consent = tenant_consents.get(subject_id)

        if not consent or consent.status != ConsentStatus.GRANTED:
            return False

        if consent.scope.expiration_date and consent.scope.expiration_date < datetime.now(timezone.utc):
            consent.status = ConsentStatus.EXPIRED
            return False

        if purpose not in consent.scope.allowed_purposes:
            return False

        if asset_id and consent.scope.allowed_asset_ids is not None:
            if asset_id not in consent.scope.allowed_asset_ids:
                return False

        return True

    def validate_consent_or_raise(
        self,
        tenant_id: str,
        subject_id: str,
        purpose: ConsentPurpose,
        asset_id: Optional[str] = None,
    ) -> None:
        if not self.evaluate_consent(tenant_id, subject_id, purpose, asset_id):
            raise ConsentViolationException(
                f"Consent Violation: Subject '{subject_id}' has no valid granted consent for purpose '{purpose.value}'.",
                tenant_id=tenant_id,
            )
