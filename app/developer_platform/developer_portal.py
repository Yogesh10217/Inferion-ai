"""Developer Portal, Onboarding & Application Subscriptions Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.security.secrets import SecretManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DeveloperApplication(BaseModel):
    app_id: str = Field(default_factory=lambda: f"dapp_{uuid.uuid4().hex[:10]}")
    name: str
    developer_id: str
    tenant_id: str = "global"
    api_key_id: str
    created_at: datetime = Field(default_factory=_now)


class DeveloperSubscription(BaseModel):
    subscription_id: str = Field(default_factory=lambda: f"dsub_{uuid.uuid4().hex[:10]}")
    app_id: str
    service_id: str
    tenant_id: str = "global"
    subscribed_at: datetime = Field(default_factory=_now)


class DeveloperPortalManager:
    """Manages developer onboarding, application registrations, and API catalog subscriptions."""

    def __init__(self, secret_manager: Optional[SecretManager] = None) -> None:
        self.secret_manager = secret_manager or SecretManager()
        self._applications: Dict[str, DeveloperApplication] = {}
        self._subscriptions: Dict[str, DeveloperSubscription] = {}

    def register_application(self, name: str, developer_id: str, tenant_id: str = "global") -> DeveloperApplication:
        key_id = f"key_{uuid.uuid4().hex[:8]}"
        app_obj = DeveloperApplication(name=name, developer_id=developer_id, tenant_id=tenant_id, api_key_id=key_id)
        self._applications[app_obj.app_id] = app_obj
        logger.info(f"[DEVELOPER PORTAL] Registered application '{app_obj.app_id}' ('{name}') for developer '{developer_id}'")
        return app_obj

    def subscribe_to_api(self, app_id: str, service_id: str, tenant_id: str = "global") -> DeveloperSubscription:
        sub = DeveloperSubscription(app_id=app_id, service_id=service_id, tenant_id=tenant_id)
        self._subscriptions[sub.subscription_id] = sub
        logger.info(f"[DEVELOPER PORTAL] Application '{app_id}' subscribed to API service '{service_id}'")
        return sub
