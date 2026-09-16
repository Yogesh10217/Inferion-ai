"""Extension domain models and manifest specification."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.extensions.exceptions import InvalidExtensionManifestException

logger = logging.getLogger(__name__)


class ExtensionType(str, Enum):
    TOOL = "TOOL"
    AGENT = "AGENT"
    WORKFLOW = "WORKFLOW"
    MODEL_PROVIDER = "MODEL_PROVIDER"
    MCP_SERVER = "MCP_SERVER"
    MEMORY_PROVIDER = "MEMORY_PROVIDER"
    KNOWLEDGE_PROVIDER = "KNOWLEDGE_PROVIDER"
    AUTH_PROVIDER = "AUTH_PROVIDER"
    OBSERVABILITY_EXPORTER = "OBSERVABILITY_EXPORTER"
    UI_EXTENSION = "UI_EXTENSION"
    CUSTOM = "CUSTOM"


class ExtensionRuntimeRequirements(BaseModel):
    """Resource governance limits for extension execution."""

    max_cpu_cores: float = 1.0
    max_memory_mb: int = 512
    max_execution_timeout_sec: int = 30
    allow_network_access: bool = False
    allow_filesystem_access: bool = False
    allowed_external_domains: List[str] = Field(default_factory=list)


class ExtensionManifest(BaseModel):
    """Manifest specification describing extension metadata, permissions, and dependencies."""

    identifier: str
    name: str
    version: str = "1.0.0"
    publisher_id: str
    description: str = ""
    extension_type: ExtensionType
    capabilities: List[str] = Field(default_factory=list)
    required_permissions: List[str] = Field(default_factory=list)
    required_scopes: List[str] = Field(default_factory=list)
    dependencies: Dict[str, str] = Field(default_factory=dict)  # package_name -> semver_range
    runtime_requirements: ExtensionRuntimeRequirements = Field(default_factory=ExtensionRuntimeRequirements)
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    compatibility_versions: List[str] = Field(default_factory=lambda: [">=5.0.0"])
    entrypoint: str = "main.py:ExtensionHandler"

    def validate_manifest(self) -> None:
        """Validate required manifest fields."""
        if not self.identifier or not self.name or not self.publisher_id:
            raise InvalidExtensionManifestException("Missing required metadata fields (identifier, name, or publisher_id)")
        if not self.version:
            raise InvalidExtensionManifestException("Missing extension version")


class ExtensionVersion(BaseModel):
    """Version snapshot of an extension."""

    version_id: str = Field(default_factory=lambda: f"extver_{uuid.uuid4().hex[:10]}")
    version_number: str
    manifest: ExtensionManifest
    package_checksum_sha256: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Extension(BaseModel):
    """Extension entity container."""

    extension_id: str = Field(default_factory=lambda: f"ext_{uuid.uuid4().hex[:10]}")
    manifest: ExtensionManifest
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    developer_id: str = "system"
    current_version: str = "1.0.0"
    status: str = "INSTALLED"
    is_enabled: bool = False
    versions: List[ExtensionVersion] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
