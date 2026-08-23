"""Personalization & Experience Context (Phase 5.22 - Component 6).

Provides user & role personalization while enforcing explicit consent boundaries:
- Consent scopes: USER_PROFILE, SESSION, APPLICATION, ORGANIZATION, MEMORY, BEHAVIORAL_ANALYTICS
- Consent statuses: GRANTED, DENIED, PENDING, REVOKED
- Memory scope check & tenant isolation (never bypasses memory or identity authorization)
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.application_platform.exceptions import ConsentDeniedException

logger = logging.getLogger(__name__)


class ConsentScope(str, Enum):
    USER_PROFILE = "USER_PROFILE"
    SESSION = "SESSION"
    APPLICATION = "APPLICATION"
    ORGANIZATION = "ORGANIZATION"
    MEMORY = "MEMORY"
    BEHAVIORAL_ANALYTICS = "BEHAVIORAL_ANALYTICS"


class ConsentStatus(str, Enum):
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    PENDING = "PENDING"
    REVOKED = "REVOKED"


class PersonalizationConsent(BaseModel):
    """Explicit consent grant for a user."""

    consent_id: str = Field(default_factory=lambda: f"cns_{uuid.uuid4().hex[:12]}")
    user_id: str
    tenant_id: str
    scope: ConsentScope
    status: ConsentStatus = ConsentStatus.GRANTED
    granted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


class PersonalizationProfile(BaseModel):
    """User/Role personalization settings."""

    profile_id: str = Field(default_factory=lambda: f"prof_{uuid.uuid4().hex[:12]}")
    user_id: str
    tenant_id: str
    preferences: Dict[str, Any] = Field(default_factory=dict)
    role_settings: Dict[str, Any] = Field(default_factory=dict)
    locale: str = "en-US"
    theme: str = "DARK"
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExperienceContext(BaseModel):
    """Constructed user experience context for runtime prompt & UI formatting."""

    context_id: str = Field(default_factory=lambda: f"expctx_{uuid.uuid4().hex[:12]}")
    user_id: str
    tenant_id: str
    application_id: str
    allowed_preferences: Dict[str, Any] = Field(default_factory=dict)
    authorized_memory_scopes: List[str] = Field(default_factory=list)
    consent_summary: Dict[str, str] = Field(default_factory=dict)


class PersonalizationEngine:
    """Manages profiles, consents, and experience context resolution."""

    def __init__(self) -> None:
        self._profiles: Dict[str, PersonalizationProfile] = {}  # key: f"{tenant_id}:{user_id}"
        self._consents: Dict[str, PersonalizationConsent] = {}  # key: f"{tenant_id}:{user_id}:{scope}"

    def grant_consent(
        self,
        tenant_id: str,
        user_id: str,
        scope: ConsentScope,
        status: ConsentStatus = ConsentStatus.GRANTED,
    ) -> PersonalizationConsent:
        key = f"{tenant_id}:{user_id}:{scope.value}"
        cns = PersonalizationConsent(
            user_id=user_id,
            tenant_id=tenant_id,
            scope=scope,
            status=status,
        )
        self._consents[key] = cns
        logger.info(f"[PERSONALIZATION] Set consent '{scope.value}' to '{status.value}' for user '{user_id}'")
        return cns

    def set_profile(
        self,
        tenant_id: str,
        user_id: str,
        preferences: Dict[str, Any],
        role_settings: Optional[Dict[str, Any]] = None,
    ) -> PersonalizationProfile:
        key = f"{tenant_id}:{user_id}"
        prof = PersonalizationProfile(
            user_id=user_id,
            tenant_id=tenant_id,
            preferences=preferences,
            role_settings=role_settings or {},
        )
        self._profiles[key] = prof
        return prof

    def check_consent(self, tenant_id: str, user_id: str, scope: ConsentScope) -> bool:
        key = f"{tenant_id}:{user_id}:{scope.value}"
        if key not in self._consents:
            return False
        return self._consents[key].status == ConsentStatus.GRANTED

    def construct_experience_context(
        self,
        tenant_id: str,
        user_id: str,
        application_id: str,
        requested_scopes: Optional[List[ConsentScope]] = None,
    ) -> ExperienceContext:
        """Construct personalization experience context after checking consent boundaries."""
        scopes = requested_scopes or [ConsentScope.USER_PROFILE, ConsentScope.MEMORY]
        consent_summary = {}

        for scope in scopes:
            granted = self.check_consent(tenant_id, user_id, scope)
            consent_summary[scope.value] = "GRANTED" if granted else "DENIED"

        prof_key = f"{tenant_id}:{user_id}"
        profile = self._profiles.get(prof_key)

        allowed_prefs = {}
        if consent_summary.get(ConsentScope.USER_PROFILE.value) == "GRANTED" and profile:
            allowed_prefs = profile.preferences

        memory_scopes = []
        if consent_summary.get(ConsentScope.MEMORY.value) == "GRANTED":
            memory_scopes.append(f"user:{user_id}:private")

        return ExperienceContext(
            user_id=user_id,
            tenant_id=tenant_id,
            application_id=application_id,
            allowed_preferences=allowed_prefs,
            authorized_memory_scopes=memory_scopes,
            consent_summary=consent_summary,
        )
