"""Integration Authentication Profile & Session Subsystem."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AuthenticationType(str, Enum):
    API_KEY = "API_KEY"
    BEARER_TOKEN = "BEARER_TOKEN"
    OAUTH2 = "OAUTH2"
    SERVICE_ACCOUNT = "SERVICE_ACCOUNT"
    BASIC_AUTH = "BASIC_AUTH"
    CUSTOM_HEADER = "CUSTOM_HEADER"
    SIGNED_REQUEST = "SIGNED_REQUEST"


class AuthenticationProfile(BaseModel):
    profile_id: str = Field(default_factory=lambda: f"authp_{uuid.uuid4().hex[:10]}")
    auth_type: AuthenticationType = AuthenticationType.OAUTH2
    secret_id: str
    tenant_id: str = "global"
    is_valid: bool = True
    created_at: datetime = Field(default_factory=_now)


class AuthenticationSession(BaseModel):
    session_id: str = Field(default_factory=lambda: f"asec_{uuid.uuid4().hex[:10]}")
    profile_id: str
    tenant_id: str = "global"
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=_now)
