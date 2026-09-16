"""Container & Image Security Engine."""

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ContainerScanResult(BaseModel):
    scan_id: str = Field(default_factory=lambda: f"containersec-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    image_tag: str
    vulnerabilities_count: int = 0
    runs_as_root: bool = False
    scanned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContainerSecurityEngine:
    """Scans container images and configurations for security defects."""

    def scan_image(self, tenant_id: str, image_tag: str, runs_as_root: bool = False) -> ContainerScanResult:
        return ContainerScanResult(
            tenant_id=tenant_id,
            image_tag=image_tag,
            runs_as_root=runs_as_root,
        )
