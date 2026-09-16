"""Tenant-Isolated Repositories for Model Intelligence (Phase 5.44)."""

import logging
from typing import Any, Dict, List

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException, ModelReferenceNotFoundException
from app.platform_contracts.redaction import SensitiveDataSanitizer

logger = logging.getLogger(__name__)


class ModelReferenceRepository:
    """Tenant-isolated repository for model references."""

    def __init__(self) -> None:
        self.sanitizer = SensitiveDataSanitizer()
        self._data: Dict[str, Dict[str, Any]] = {}

    def save(self, record_id: str, tenant_id: str, record: Dict[str, Any]) -> Dict[str, Any]:
        clean_record = self.sanitizer.sanitize(record)
        clean_record["_tenant_id"] = tenant_id
        self._data[record_id] = clean_record
        return clean_record

    def get(self, record_id: str, tenant_id: str) -> Dict[str, Any]:
        rec = self._data.get(record_id)
        if not rec:
            raise ModelReferenceNotFoundException(f"Record '{record_id}' not found.")
        if rec.get("_tenant_id") != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return rec

    def list(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [r for r in self._data.values() if r.get("_tenant_id") == tenant_id]


class ModelIncidentRepository:
    """Tenant-isolated repository for model incidents."""

    def __init__(self) -> None:
        self.sanitizer = SensitiveDataSanitizer()
        self._data: Dict[str, Dict[str, Any]] = {}

    def save(self, record_id: str, tenant_id: str, record: Dict[str, Any]) -> Dict[str, Any]:
        clean_record = self.sanitizer.sanitize(record)
        clean_record["_tenant_id"] = tenant_id
        self._data[record_id] = clean_record
        return clean_record

    def get(self, record_id: str, tenant_id: str) -> Dict[str, Any]:
        rec = self._data.get(record_id)
        if not rec:
            raise ValueError(f"Incident record '{record_id}' not found.")
        if rec.get("_tenant_id") != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return rec

    def list(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [r for r in self._data.values() if r.get("_tenant_id") == tenant_id]


class ModelEvidenceRepository:
    """Tenant-isolated repository for immutable model evidence."""

    def __init__(self) -> None:
        self.sanitizer = SensitiveDataSanitizer()
        self._data: Dict[str, Dict[str, Any]] = {}

    def save(self, record_id: str, tenant_id: str, record: Dict[str, Any]) -> Dict[str, Any]:
        clean_record = self.sanitizer.sanitize(record)
        clean_record["_tenant_id"] = tenant_id
        self._data[record_id] = clean_record
        return clean_record

    def get(self, record_id: str, tenant_id: str) -> Dict[str, Any]:
        rec = self._data.get(record_id)
        if not rec:
            raise ValueError(f"Evidence record '{record_id}' not found.")
        if rec.get("_tenant_id") != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return rec
