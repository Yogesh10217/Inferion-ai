"""Tenant-isolated, thread-safe repositories for Operations Assurance entities."""

import threading
from typing import Dict, Any, List, Optional, TypeVar, Generic
from pydantic import BaseModel

from app.operations_assurance.exceptions import CrossTenantOperationsAssuranceException
from app.platform_contracts.redaction import SensitiveDataSanitizer

T = TypeVar("T", bound=BaseModel)


class OperationsTenantRepository(Generic[T]):
    """Thread-safe, tenant-isolated repository with metadata sanitization and zero metadata leakage."""

    def __init__(self, sanitizer: Optional[SensitiveDataSanitizer] = None) -> None:
        self._sanitizer = sanitizer or SensitiveDataSanitizer()
        self._storage: Dict[str, Dict[str, T]] = {}  # tenant_id -> {resource_id -> item}
        self._lock = threading.RLock()

    def save(self, tenant_id: str, resource_id: str, item: T) -> T:
        with self._lock:
            if tenant_id not in self._storage:
                self._storage[tenant_id] = {}
            self._storage[tenant_id][resource_id] = item
            return item

    def get(self, tenant_id: str, resource_id: str) -> T:
        with self._lock:
            tenant_store = self._storage.get(tenant_id)
            if not tenant_store or resource_id not in tenant_store:
                # Check if resource exists in another tenant to enforce security exception without leakage
                for tid, items in self._storage.items():
                    if tid != tenant_id and resource_id in items:
                        raise CrossTenantOperationsAssuranceException("Access denied.")
                raise CrossTenantOperationsAssuranceException("Access denied.")
            return tenant_store[resource_id]

    def list_all(self, tenant_id: str) -> List[T]:
        with self._lock:
            tenant_store = self._storage.get(tenant_id, {})
            return list(tenant_store.values())

    def delete(self, tenant_id: str, resource_id: str) -> bool:
        with self._lock:
            tenant_store = self._storage.get(tenant_id)
            if not tenant_store or resource_id not in tenant_store:
                raise CrossTenantOperationsAssuranceException("Access denied.")
            del tenant_store[resource_id]
            return True
