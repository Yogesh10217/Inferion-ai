"""Repositories for Security Assurance Persistence."""

from typing import Any, Dict, Optional


class SecurityAssuranceRepository:
    """In-memory repository for tenant-scoped security assurance records."""

    def __init__(self) -> None:
        self._records: Dict[str, Dict[str, Any]] = {}

    def save(self, tenant_id: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        key = f"{tenant_id}:{record_id}"
        self._records[key] = data
        return data

    def get(self, tenant_id: str, record_id: str) -> Optional[Dict[str, Any]]:
        key = f"{tenant_id}:{record_id}"
        return self._records.get(key)
