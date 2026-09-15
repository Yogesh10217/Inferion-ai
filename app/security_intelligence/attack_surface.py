"""Attack Surface Intelligence Subsystem (Phase 5.32)."""

from enum import Enum
from typing import Dict, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.security_intelligence.exceptions import CrossTenantSecurityAccessException


class AttackSurfaceExposure(str, Enum):
    INTERNET_FACING = "INTERNET_FACING"
    PARTNER_FACING = "PARTNER_FACING"
    INTERNAL_NETWORK = "INTERNAL_NETWORK"
    ISOLATED_VPC = "ISOLATED_VPC"


class AttackSurfaceEntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: f"entry_{uuid.uuid4().hex[:12]}")
    asset_id: str
    entry_point_name: str
    exposure: AttackSurfaceExposure = AttackSurfaceExposure.INTERNET_FACING
    requires_auth: bool = True
    privileged_access: bool = False


class AttackSurfaceRisk(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AttackSurface(BaseModel):
    surface_id: str = Field(default_factory=lambda: f"surf_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    entries: List[AttackSurfaceEntry] = Field(default_factory=list)
    overall_risk: AttackSurfaceRisk = AttackSurfaceRisk.MEDIUM
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AttackSurfaceManager:
    """Tracks and evaluates attack surface exposure across public APIs, external integrations, and agent permissions."""

    def __init__(self) -> None:
        self._surfaces: Dict[str, AttackSurface] = {}

    def register_attack_surface(
        self,
        tenant_id: str,
        entries: List[AttackSurfaceEntry],
    ) -> AttackSurface:
        has_public_unauth = any(e.exposure == AttackSurfaceExposure.INTERNET_FACING and not e.requires_auth for e in entries)
        has_privileged = any(e.privileged_access for e in entries)

        if has_public_unauth or has_privileged:
            overall_risk = AttackSurfaceRisk.CRITICAL
        elif any(e.exposure == AttackSurfaceExposure.INTERNET_FACING for e in entries):
            overall_risk = AttackSurfaceRisk.HIGH
        else:
            overall_risk = AttackSurfaceRisk.MEDIUM

        surf = AttackSurface(
            tenant_id=tenant_id,
            entries=entries,
            overall_risk=overall_risk,
        )
        self._surfaces[surf.surface_id] = surf
        return surf

    def get_attack_surface(self, surface_id: str, tenant_id: str) -> AttackSurface:
        surf = self._surfaces.get(surface_id)
        if not surf:
            raise KeyError(f"Attack surface '{surface_id}' not found.")
        if tenant_id != "global" and surf.tenant_id != "global" and tenant_id != surf.tenant_id:
            raise CrossTenantSecurityAccessException(tenant_id, surf.tenant_id)
        return surf
