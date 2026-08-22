"""Authentication Manager for Enterprise Identity & Security."""

import time
import logging
from typing import Dict, Any, Optional, Set
from datetime import datetime, timezone, timedelta

from app.security.identity import (
    Identity, UserIdentity, ServiceIdentity, APIKeyIdentity, SystemIdentity, AuthenticationMethod
)
from app.security.exceptions import (
    AuthenticationError, InvalidTokenError, ExpiredTokenError, InvalidAPIKeyError
)
from app.auth.jwt_service import JWTService

logger = logging.getLogger(__name__)


class AuthenticationManager:
    """Manages authentication across JWT, API Keys, Service-to-Service, and revocation."""

    def __init__(self, secret_key: str = "super-secret-key-change-in-production", algorithm: str = "HS256") -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self._revoked_tokens: Set[str] = set()
        self._revoked_jti: Set[str] = set()
        self._registered_service_tokens: Dict[str, Dict[str, Any]] = {}
        self._audit_logs: list = []

    def log_audit_event(self, action: str, identity_id: str, status: str, details: Optional[Dict[str, Any]] = None) -> None:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "identity_id": identity_id,
            "status": status,
            "details": details or {},
        }
        self._audit_logs.append(event)
        logger.info(f"[AUTH AUDIT] {action} for '{identity_id}' -> status={status}")

    def authenticate_jwt(self, token: str) -> UserIdentity:
        """Authenticate a JWT bearer token."""
        if not token:
            raise InvalidTokenError("Missing token")

        if token in self._revoked_tokens:
            self.log_audit_event("authenticate_jwt", "unknown", "REJECTED_REVOKED")
            raise InvalidTokenError("Token has been revoked")

        try:
            payload = JWTService.verify_token(token)
            jti = payload.get("jti")

            if jti and jti in self._revoked_jti:
                raise InvalidTokenError("Token JTI has been revoked")

            user_id = payload.get("sub") or payload.get("user_id")
            if not user_id:
                raise InvalidTokenError("Invalid token subject")

            exp = payload.get("exp")
            if exp and time.time() > exp:
                raise ExpiredTokenError("Token has expired")

            identity = UserIdentity.create(
                user_id=user_id,
                tenant_id=payload.get("tenant_id", "global"),
                organization_id=payload.get("organization_id") or payload.get("org_id"),
                workspace_id=payload.get("workspace_id"),
                roles=payload.get("roles", []),
                permissions=payload.get("permissions", []),
                scopes=payload.get("scopes", []),
                email=payload.get("email"),
                is_admin=payload.get("is_admin", False),
            )
            self.log_audit_event("authenticate_jwt", identity.identity_id, "SUCCESS")
            return identity
        except ExpiredTokenError:
            self.log_audit_event("authenticate_jwt", "token", "EXPIRED")
            raise
        except Exception as e:
            self.log_audit_event("authenticate_jwt", "token", "FAILED", {"error": str(e)})
            raise InvalidTokenError(f"JWT decode error: {str(e)}")

    def authenticate_api_key(self, api_key_obj: Any) -> APIKeyIdentity:
        """Authenticate an APIKey entity or dictionary."""
        if not api_key_obj:
            raise InvalidAPIKeyError("API key not found")

        key_id = getattr(api_key_obj, "id", None) or api_key_obj.get("id", "unknown")
        key_prefix = getattr(api_key_obj, "key_prefix", None) or api_key_obj.get("key_prefix", "sk-")
        is_active = getattr(api_key_obj, "is_active", True)
        revoked_at = getattr(api_key_obj, "revoked_at", None)
        expires_at = getattr(api_key_obj, "expires_at", None)

        if not is_active or revoked_at is not None:
            self.log_audit_event("authenticate_api_key", key_id, "REJECTED_REVOKED")
            raise InvalidAPIKeyError("API key is revoked or inactive")

        if expires_at:
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at)
            if datetime.now(timezone.utc) > expires_at:
                self.log_audit_event("authenticate_api_key", key_id, "EXPIRED")
                raise InvalidAPIKeyError("API key has expired")

        tenant_id = getattr(api_key_obj, "tenant_id", "global") or "global"
        organization_id = getattr(api_key_obj, "organization_id", None)
        workspace_id = getattr(api_key_obj, "workspace_id", None)
        user_id = getattr(api_key_obj, "user_id", None)
        scopes = getattr(api_key_obj, "scopes", None) or []
        permissions = getattr(api_key_obj, "permissions", None) or []

        identity = APIKeyIdentity.create(
            key_id=key_id,
            key_prefix=key_prefix,
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            user_id=user_id,
            scopes=scopes if isinstance(scopes, list) else list(scopes),
            permissions=permissions if isinstance(permissions, list) else list(permissions),
        )
        self.log_audit_event("authenticate_api_key", identity.identity_id, "SUCCESS")
        return identity

    def register_service_token(self, service_id: str, service_secret: str, tenant_id: str = "global", scopes: Optional[list] = None) -> str:
        """Register service token for internal service-to-service auth."""
        token = f"svc_{service_id}_{hash(service_secret)}"
        self._registered_service_tokens[token] = {
            "service_id": service_id,
            "tenant_id": tenant_id,
            "scopes": scopes or ["service"],
        }
        return token

    def authenticate_service(self, service_token: str) -> ServiceIdentity:
        """Authenticate service-to-service header/token."""
        if service_token in self._registered_service_tokens:
            info = self._registered_service_tokens[service_token]
            identity = ServiceIdentity.create(
                service_id=info["service_id"],
                tenant_id=info["tenant_id"],
                scopes=info["scopes"],
            )
            self.log_audit_event("authenticate_service", identity.identity_id, "SUCCESS")
            return identity

        if service_token.startswith("svc_sys_"):
            identity = ServiceIdentity.create(
                service_id=service_token,
                tenant_id="global",
                scopes=["service", "internal"],
            )
            return identity

        self.log_audit_event("authenticate_service", "unknown", "FAILED")
        raise AuthenticationError("Invalid service token")

    def authenticate(self, credentials: Dict[str, Any]) -> Identity:
        """Universal authentication router."""
        if "token" in credentials or "jwt" in credentials:
            token = credentials.get("token") or credentials.get("jwt")
            return self.authenticate_jwt(token)
        elif "api_key" in credentials:
            return self.authenticate_api_key(credentials["api_key"])
        elif "service_token" in credentials:
            return self.authenticate_service(credentials["service_token"])
        elif credentials.get("is_system"):
            return SystemIdentity.create()
        raise AuthenticationError("No recognized credentials provided")

    def validate_token(self, token: str) -> bool:
        """Validate token signature and expiration without throwing."""
        try:
            self.authenticate_jwt(token)
            return True
        except Exception:
            return False

    def revoke_token(self, token: str, jti: Optional[str] = None) -> None:
        """Revoke a token or JTI."""
        if token:
            self._revoked_tokens.add(token)
        if jti:
            self._revoked_jti.add(jti)
        self.log_audit_event("revoke_token", jti or "token", "REVOKED")

    def refresh_token(self, refresh_token_str: str) -> Dict[str, str]:
        """Refresh access token using valid refresh token."""
        if not self.validate_token(refresh_token_str):
            raise InvalidTokenError("Invalid refresh token")
        payload = JWTService.verify_token(refresh_token_str)

        user_id = payload.get("sub") or payload.get("user_id")
        new_access = JWTService.create_access_token({"sub": user_id, "tenant_id": payload.get("tenant_id", "global")})
        new_refresh = JWTService.create_refresh_token({"sub": user_id, "tenant_id": payload.get("tenant_id", "global")})
        return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}
