"""Development Environment Subsystem."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class EnvironmentType(str, Enum):
    LOCAL = "LOCAL"
    REMOTE = "REMOTE"
    CLOUD = "CLOUD"
    EPHEMERAL = "EPHEMERAL"
    CI = "CI"


class DevelopmentEnvironment(BaseModel):
    env_id: str = Field(default_factory=lambda: f"env_{uuid.uuid4().hex[:10]}")
    name: str
    env_type: EnvironmentType = EnvironmentType.CLOUD
    tenant_id: str = "global"
    is_active: bool = True
    created_at: datetime = Field(default_factory=_now)


class EnvironmentManager:
    """Manages cloud, local, remote, and ephemeral development environment templates."""

    def create_environment(self, name: str, env_type: EnvironmentType = EnvironmentType.CLOUD, tenant_id: str = "global") -> DevelopmentEnvironment:
        env = DevelopmentEnvironment(name=name, env_type=env_type, tenant_id=tenant_id)
        logger.info(f"[ENVIRONMENT MANAGER] Created environment '{env.env_id}' ('{name}', {env_type.value})")
        return env
