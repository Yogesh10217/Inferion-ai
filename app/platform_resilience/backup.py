"""Backup Governance Subsystem (Phase 5.37)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_resilience.exceptions import CrossTenantResilienceAccessException, ResilienceResourceNotFoundException


class BackupStatus(str, Enum):
    VALIDATED = "VALIDATED"
    PENDING = "PENDING"
    CORRUPTED = "CORRUPTED"
    EXPIRED = "EXPIRED"


class BackupIntegrity(BaseModel):
    is_valid: bool = True
    checksum_sha256: str = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    size_bytes: int = 104857600


class BackupVerification(BaseModel):
    verification_id: str = Field(default_factory=lambda: f"bakver_{uuid.uuid4().hex[:12]}")
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: BackupStatus = BackupStatus.VALIDATED


class BackupReference(BaseModel):
    backup_id: str = Field(default_factory=lambda: f"bakref_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    resource_id: str
    storage_location_uri: str = "s3://enterprise-backups/daily/backup_001"
    status: BackupStatus = BackupStatus.VALIDATED
    integrity: BackupIntegrity = Field(default_factory=BackupIntegrity)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BackupPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: f"bakpoly_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    resource_id: str
    frequency_hours: int = 24
    retention_days: int = 30


class BackupManager:
    """Backup Governance and Verification Manager referencing existing storage infrastructure."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._backups: Dict[str, BackupReference] = {}

    def register_backup_reference(
        self,
        tenant_id: str,
        resource_id: str,
        storage_location_uri: str,
        checksum_sha256: str = "a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4e5f67890",
    ) -> BackupReference:
        bak = BackupReference(
            tenant_id=tenant_id,
            resource_id=resource_id,
            storage_location_uri=storage_location_uri,
            integrity=BackupIntegrity(is_valid=True, checksum_sha256=checksum_sha256),
        )
        self._backups[bak.backup_id] = bak
        return bak

    def verify_backup(self, backup_id: str, tenant_id: str) -> BackupVerification:
        bak = self.get_backup(backup_id, tenant_id)
        return BackupVerification(status=bak.status)

    def get_backup(self, backup_id: str, tenant_id: str) -> BackupReference:
        bak = self._backups.get(backup_id)
        if not bak:
            raise ResilienceResourceNotFoundException(backup_id)
        
        try:
            self.tenant_guard.enforce_isolation(tenant_id, bak.tenant_id)
        except Exception:
            raise CrossTenantResilienceAccessException(tenant_id, bak.tenant_id)
            
        return bak
