"""Phase 5.9 Enterprise Identity & Security Package."""

from app.security.api_keys import APIKey, APIKeyManager, APIKeyPolicy
from app.security.authentication import AuthenticationManager
from app.security.authorization import AuthorizationEngine
from app.security.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ExpiredTokenError,
    InvalidAPIKeyError,
    InvalidTokenError,
    PermissionDeniedError,
    QuotaExceededError,
    RateLimitExceededError,
    SecretAccessDeniedError,
    SecurityException,
    SecurityPolicyViolation,
    TenantAccessDeniedError,
)
from app.security.identity import (
    APIKeyIdentity,
    AuthenticationMethod,
    Identity,
    ServiceIdentity,
    SystemIdentity,
    UserIdentity,
)
from app.security.secrets import EnvironmentSecretProvider, SecretManager, SecretProvider

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
