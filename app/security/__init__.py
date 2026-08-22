"""Phase 5.9 Enterprise Identity & Security Package."""

from app.security.exceptions import (
    SecurityException, AuthenticationError, AuthorizationError,
    InvalidTokenError, ExpiredTokenError, InvalidAPIKeyError,
    PermissionDeniedError, TenantAccessDeniedError, SecretAccessDeniedError,
    RateLimitExceededError, QuotaExceededError, SecurityPolicyViolation,
)
from app.security.identity import (
    Identity, UserIdentity, ServiceIdentity, APIKeyIdentity, SystemIdentity, AuthenticationMethod
)
from app.security.authentication import AuthenticationManager
from app.security.authorization import AuthorizationEngine
from app.security.api_keys import APIKeyManager, APIKey, APIKeyPolicy
from app.security.secrets import SecretManager, SecretProvider, EnvironmentSecretProvider

__all__ = [
    "SecurityException",
    "AuthenticationError",
    "AuthorizationError",
    "InvalidTokenError",
    "ExpiredTokenError",
    "InvalidAPIKeyError",
    "PermissionDeniedError",
    "TenantAccessDeniedError",
    "SecretAccessDeniedError",
    "RateLimitExceededError",
    "QuotaExceededError",
    "SecurityPolicyViolation",
    "Identity",
    "UserIdentity",
    "ServiceIdentity",
    "APIKeyIdentity",
    "SystemIdentity",
    "AuthenticationMethod",
    "AuthenticationManager",
    "AuthorizationEngine",
    "APIKeyManager",
    "APIKey",
    "APIKeyPolicy",
    "SecretManager",
    "SecretProvider",
    "EnvironmentSecretProvider",
]
