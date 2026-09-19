"""Authentication Assurance & Multi-Factor Verification Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.identity.exceptions import AuthenticationAssuranceException
from app.security.authentication import AuthenticationManager as BaseAuthManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AuthenticationMethod(str, Enum):
    PASSWORD = "PASSWORD"  # nosec B105
    API_KEY = "API_KEY"
    OAUTH2 = "OAUTH2"
    OIDC = "OIDC"
    JWT = "JWT"
    SAML = "SAML"
    SERVICE_TOKEN = "SERVICE_TOKEN"  # nosec B105
    CLIENT_CERTIFICATE = "CLIENT_CERTIFICATE"
    MFA = "MFA"
    PASSKEY = "PASSKEY"
    WORKLOAD_IDENTITY = "WORKLOAD_IDENTITY"


class AuthenticationAssuranceLevel(str, Enum):
    LOW = "LOW"
    STANDARD = "STANDARD"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class AuthenticationResult(BaseModel):
    auth_id: str = Field(default_factory=lambda: f"auth_{uuid.uuid4().hex[:10]}")
    identity_id: str
    tenant_id: str = "global"
    method: AuthenticationMethod = AuthenticationMethod.JWT
    assurance_level: AuthenticationAssuranceLevel = AuthenticationAssuranceLevel.STANDARD
    is_authenticated: bool = True
    session_id: str = Field(default_factory=lambda: f"sess_{uuid.uuid4().hex[:10]}")
    authenticated_at: datetime = Field(default_factory=_now)


class AuthenticationManager:
    """Evaluates authentication assurance levels and integrates with base AuthenticationManager."""

    def __init__(self, base_auth_manager: Optional[BaseAuthManager] = None) -> None:
        self.base_auth_manager = base_auth_manager or BaseAuthManager(secret_key="zero_trust_secret")  # nosec B106
        self._auth_sessions: Dict[str, AuthenticationResult] = {}

    def authenticate(
        self,
        identity_id: str,
        method: AuthenticationMethod = AuthenticationMethod.JWT,
        tenant_id: str = "global",
        mfa_verified: bool = False,
    ) -> AuthenticationResult:
        # Determine assurance level
        if mfa_verified or method in (AuthenticationMethod.PASSKEY, AuthenticationMethod.CLIENT_CERTIFICATE):
            assurance = AuthenticationAssuranceLevel.HIGH
        elif method in (AuthenticationMethod.JWT, AuthenticationMethod.OIDC, AuthenticationMethod.SAML):
            assurance = AuthenticationAssuranceLevel.STANDARD
        else:
            assurance = AuthenticationAssuranceLevel.LOW

        res = AuthenticationResult(
            identity_id=identity_id,
            tenant_id=tenant_id,
            method=method,
            assurance_level=assurance,
            is_authenticated=True,
        )
        self._auth_sessions[res.session_id] = res
        logger.info(f"[AUTH MANAGER] Authenticated '{identity_id}' ({method.value}): Assurance = {assurance.value}")
        return res

    def verify_assurance(self, session_id: str, required_level: AuthenticationAssuranceLevel) -> bool:
        sess = self._auth_sessions.get(session_id)
        if not sess or not sess.is_authenticated:
            raise AuthenticationAssuranceException(required=required_level.value, provided="NONE")

        # Level hierarchy: VERY_HIGH > HIGH > STANDARD > LOW
        hierarchy = {
            AuthenticationAssuranceLevel.LOW: 1,
            AuthenticationAssuranceLevel.STANDARD: 2,
            AuthenticationAssuranceLevel.HIGH: 3,
            AuthenticationAssuranceLevel.VERY_HIGH: 4,
        }

        if hierarchy[sess.assurance_level] < hierarchy[required_level]:
            raise AuthenticationAssuranceException(required=required_level.value, provided=sess.assurance_level.value)

        return True
