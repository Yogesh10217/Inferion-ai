"""Application Registry & Lifecycle Management (Phase 5.22 - Component 1).

Enforces:
- Tenant isolation
- Immutable production application versions (DEPLOYED / ACTIVE)
- SHA-256 Version fingerprinting
- Explicit state transitions
"""

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.application_platform.exceptions import (
    ApplicationNotFoundException,
    ApplicationVersionNotFoundException,
    ImmutableVersionException,
    InvalidLifecycleTransitionException,
)
from app.application_platform.repositories import ApplicationRepository, InMemoryApplicationRepository

logger = logging.getLogger(__name__)


class ApplicationType(str, Enum):
    CHAT_APPLICATION = "CHAT_APPLICATION"
    COPILOT = "COPILOT"
    AGENT_APPLICATION = "AGENT_APPLICATION"
    WORKFLOW_APPLICATION = "WORKFLOW_APPLICATION"
    KNOWLEDGE_APPLICATION = "KNOWLEDGE_APPLICATION"
    ANALYTICS_APPLICATION = "ANALYTICS_APPLICATION"
    AUTOMATION_APPLICATION = "AUTOMATION_APPLICATION"
    CUSTOMER_SUPPORT = "CUSTOMER_SUPPORT"
    INTERNAL_ENTERPRISE = "INTERNAL_ENTERPRISE"
    DEVELOPER_TOOL = "DEVELOPER_TOOL"
    CUSTOM = "CUSTOM"


class ApplicationStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIGURED = "CONFIGURED"
    VALIDATED = "VALIDATED"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    DEPLOYED = "DEPLOYED"
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    SUSPENDED = "SUSPENDED"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"
    ARCHIVED = "ARCHIVED"


# Immutable production states where version content cannot be modified directly
IMMUTABLE_STATUSES = {ApplicationStatus.DEPLOYED, ApplicationStatus.ACTIVE}

# Allowed lifecycle state transitions
VALID_TRANSITIONS: Dict[ApplicationStatus, List[ApplicationStatus]] = {
    ApplicationStatus.DRAFT: [ApplicationStatus.CONFIGURED, ApplicationStatus.VALIDATED, ApplicationStatus.ARCHIVED],
    ApplicationStatus.CONFIGURED: [ApplicationStatus.VALIDATED, ApplicationStatus.DRAFT, ApplicationStatus.ARCHIVED],
    ApplicationStatus.VALIDATED: [ApplicationStatus.REVIEW, ApplicationStatus.DRAFT, ApplicationStatus.ARCHIVED],
    ApplicationStatus.REVIEW: [ApplicationStatus.APPROVED, ApplicationStatus.DRAFT, ApplicationStatus.ARCHIVED],
    ApplicationStatus.APPROVED: [ApplicationStatus.DEPLOYED, ApplicationStatus.DRAFT, ApplicationStatus.ARCHIVED],
    ApplicationStatus.DEPLOYED: [ApplicationStatus.ACTIVE, ApplicationStatus.DEGRADED, ApplicationStatus.SUSPENDED, ApplicationStatus.DEPRECATED],
    ApplicationStatus.ACTIVE: [ApplicationStatus.DEGRADED, ApplicationStatus.SUSPENDED, ApplicationStatus.DEPRECATED],
    ApplicationStatus.DEGRADED: [ApplicationStatus.ACTIVE, ApplicationStatus.SUSPENDED, ApplicationStatus.DEPRECATED],
    ApplicationStatus.SUSPENDED: [ApplicationStatus.ACTIVE, ApplicationStatus.DEPRECATED, ApplicationStatus.ARCHIVED],
    ApplicationStatus.DEPRECATED: [ApplicationStatus.RETIRED, ApplicationStatus.ARCHIVED],
    ApplicationStatus.RETIRED: [ApplicationStatus.ARCHIVED],
    ApplicationStatus.ARCHIVED: [],
}


class ApplicationConfiguration(BaseModel):
    """Configuration associated with an application version."""

    config_id: str = Field(default_factory=lambda: f"cfg_{uuid.uuid4().hex[:12]}")
    environment: str = "PRODUCTION"
    model_references: Dict[str, str] = Field(default_factory=dict)
    prompt_references: Dict[str, str] = Field(default_factory=dict)
    workflow_references: Dict[str, str] = Field(default_factory=dict)
    knowledge_references: List[str] = Field(default_factory=list)
    tool_permissions: List[str] = Field(default_factory=list)
    integration_references: List[str] = Field(default_factory=list)
    feature_flags: Dict[str, Any] = Field(default_factory=dict)
    policies: List[str] = Field(default_factory=list)
    runtime_limits: Dict[str, Any] = Field(default_factory=dict)
    secrets_references: Dict[str, str] = Field(default_factory=dict)


class ApplicationVersion(BaseModel):
    """Application version definition with fingerprinting and immutability rules."""

    version_id: str = Field(default_factory=lambda: f"appver_{uuid.uuid4().hex[:12]}")
    application_id: str
    tenant_id: str
    version: str = "1.0.0"
    status: ApplicationStatus = ApplicationStatus.DRAFT
    configuration: ApplicationConfiguration = Field(default_factory=ApplicationConfiguration)
    composition_references: List[str] = Field(default_factory=list)
    version_fingerprint: str = ""
    created_by: str = "system"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def compute_fingerprint(self) -> str:
        """Compute SHA-256 version fingerprint hash."""
        fingerprint_data = {
            "application_id": self.application_id,
            "version": self.version,
            "configuration": self.configuration.model_dump(),
            "compositions": sorted(self.composition_references),
        }
        serialized = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def is_immutable(self) -> bool:
        """Return True if this version is promoted to an immutable state."""
        return self.status in IMMUTABLE_STATUSES


class Application(BaseModel):
    """Core Application entity."""

    application_id: str = Field(default_factory=lambda: f"app_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    name: str
    description: str = ""
    app_type: ApplicationType = ApplicationType.CUSTOM
    current_version_id: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.DRAFT
    owner_id: str = "system"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ApplicationLifecycle:
    """Manages application status transitions and enforces immutability invariant."""

    @staticmethod
    def transition_status(
        current_status: ApplicationStatus,
        target_status: ApplicationStatus,
    ) -> ApplicationStatus:
        if target_status not in VALID_TRANSITIONS.get(current_status, []):
            raise InvalidLifecycleTransitionException(
                f"Invalid lifecycle transition from '{current_status.value}' to '{target_status.value}'."
            )
        return target_status


class ApplicationRegistry:
    """Registry managing application definitions, versions, and lifecycle state."""

    def __init__(self, repository: Optional[ApplicationRepository] = None) -> None:
        self.repository = repository or InMemoryApplicationRepository()

    def create_application(
        self,
        tenant_id: str,
        name: str,
        app_type: ApplicationType = ApplicationType.CUSTOM,
        description: str = "",
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        owner_id: str = "system",
        tags: Optional[List[str]] = None,
    ) -> Application:
        app = Application(
            tenant_id=tenant_id,
            name=name,
            app_type=app_type,
            description=description,
            organization_id=organization_id,
            workspace_id=workspace_id,
            owner_id=owner_id,
            tags=tags or [],
        )
        saved = self.repository.save_application(app.model_dump(mode="json"))
        logger.info(f"[APPLICATION REGISTRY] Created application {app.application_id} for tenant {tenant_id}")
        return Application(**saved)

    def get_application(self, application_id: str, tenant_id: str) -> Application:
        raw = self.repository.get_application(application_id, tenant_id)
        if not raw:
            raise ApplicationNotFoundException(
                f"Application '{application_id}' not found for tenant '{tenant_id}'."
            )
        return Application(**raw)

    def list_applications(self, tenant_id: str) -> List[Application]:
        raw_list = self.repository.list_applications(tenant_id)
        return [Application(**raw) for raw in raw_list]

    def create_version(
        self,
        application_id: str,
        tenant_id: str,
        version_str: str,
        configuration: Optional[ApplicationConfiguration] = None,
        composition_references: Optional[List[str]] = None,
        created_by: str = "system",
    ) -> ApplicationVersion:
        app = self.get_application(application_id, tenant_id)
        cfg = configuration or ApplicationConfiguration()
        ver = ApplicationVersion(
            application_id=app.application_id,
            tenant_id=tenant_id,
            version=version_str,
            status=ApplicationStatus.DRAFT,
            configuration=cfg,
            composition_references=composition_references or [],
            created_by=created_by,
        )
        ver.version_fingerprint = ver.compute_fingerprint()
        saved = self.repository.save_version(ver.model_dump(mode="json"))

        # Link current version if none exists
        if not app.current_version_id:
            app.current_version_id = ver.version_id
            app.status = ApplicationStatus.CONFIGURED
            self.repository.save_application(app.model_dump(mode="json"))

        logger.info(f"[APPLICATION REGISTRY] Created version {ver.version_id} ({ver.version}) for app {application_id}")
        return ApplicationVersion(**saved)

    def get_version(self, version_id: str, tenant_id: str) -> ApplicationVersion:
        raw = self.repository.get_version(version_id, tenant_id)
        if not raw:
            raise ApplicationVersionNotFoundException(
                f"Application version '{version_id}' not found for tenant '{tenant_id}'."
            )
        return ApplicationVersion(**raw)

    def update_version_configuration(
        self,
        version_id: str,
        tenant_id: str,
        new_configuration: ApplicationConfiguration,
    ) -> ApplicationVersion:
        """Update version configuration. Fails if version is in immutable state."""
        version = self.get_version(version_id, tenant_id)
        if version.is_immutable():
            raise ImmutableVersionException(
                f"Version '{version_id}' is in immutable state '{version.status.value}'. "
                "Modification rejected; please create/clone a new version."
            )

        version.configuration = new_configuration
        version.version_fingerprint = version.compute_fingerprint()
        version.updated_at = datetime.now(timezone.utc)
        saved = self.repository.save_version(version.model_dump(mode="json"))
        return ApplicationVersion(**saved)

    def promote_version(
        self,
        version_id: str,
        tenant_id: str,
        target_status: ApplicationStatus,
    ) -> ApplicationVersion:
        """Promote application version state through lifecycle state machine."""
        version = self.get_version(version_id, tenant_id)
        new_status = ApplicationLifecycle.transition_status(version.status, target_status)
        version.status = new_status
        version.version_fingerprint = version.compute_fingerprint()
        version.updated_at = datetime.now(timezone.utc)
        saved = self.repository.save_version(version.model_dump(mode="json"))

        # Update parent application status & active version reference if DEPLOYED or ACTIVE
        if new_status in {ApplicationStatus.DEPLOYED, ApplicationStatus.ACTIVE}:
            app = self.get_application(version.application_id, tenant_id)
            app.current_version_id = version.version_id
            app.status = new_status
            self.repository.save_application(app.model_dump(mode="json"))

        logger.info(f"[APPLICATION REGISTRY] Promoted version {version_id} to {new_status.value}")
        return ApplicationVersion(**saved)

    def list_versions(self, application_id: str, tenant_id: str) -> List[ApplicationVersion]:
        raw_list = self.repository.list_versions(application_id, tenant_id)
        return [ApplicationVersion(**raw) for raw in raw_list]
