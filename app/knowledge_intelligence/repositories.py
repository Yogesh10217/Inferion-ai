"""Tenant-Scoped Repositories for Knowledge Intelligence Platform (Phase 5.35)."""

from typing import Dict, Any, Optional, List
from app.platform_contracts.repositories import TenantScopedRepository
from app.knowledge_intelligence.knowledge import KnowledgeItem
from app.knowledge_intelligence.sources import KnowledgeSource
from app.knowledge_intelligence.provenance import ProvenanceRecord
from app.knowledge_intelligence.relationships import KnowledgeRelationship
from app.knowledge_intelligence.investigations import KnowledgeInvestigation
from app.knowledge_intelligence.memory import OrganizationalMemory


class KnowledgeRepository(TenantScopedRepository[KnowledgeItem]):
    def __init__(self) -> None:
        self._store: Dict[str, KnowledgeItem] = {}

    def save(self, entity: KnowledgeItem) -> KnowledgeItem:
        self._store[entity.item_id] = entity
        return entity

    def get_by_id(self, entity_id: str) -> Optional[KnowledgeItem]:
        return self._store.get(entity_id)

    def get_by_id_and_tenant(self, entity_id: str, tenant_id: str) -> Optional[KnowledgeItem]:
        item = self._store.get(entity_id)
        if item and item.tenant_id == tenant_id:
            return item
        return None

    def list_by_tenant(self, tenant_id: str) -> List[KnowledgeItem]:
        return [i for i in self._store.values() if i.tenant_id == tenant_id]


class KnowledgeSourceRepository(TenantScopedRepository[KnowledgeSource]):
    def __init__(self) -> None:
        self._store: Dict[str, KnowledgeSource] = {}

    def save(self, entity: KnowledgeSource) -> KnowledgeSource:
        self._store[entity.source_id] = entity
        return entity

    def get_by_id(self, entity_id: str) -> Optional[KnowledgeSource]:
        return self._store.get(entity_id)

    def get_by_id_and_tenant(self, entity_id: str, tenant_id: str) -> Optional[KnowledgeSource]:
        src = self._store.get(entity_id)
        if src and src.tenant_id == tenant_id:
            return src
        return None

    def list_by_tenant(self, tenant_id: str) -> List[KnowledgeSource]:
        return [s for s in self._store.values() if s.tenant_id == tenant_id]


class ProvenanceRepository(TenantScopedRepository[ProvenanceRecord]):
    def __init__(self) -> None:
        self._store: Dict[str, ProvenanceRecord] = {}

    def save(self, entity: ProvenanceRecord) -> ProvenanceRecord:
        self._store[entity.record_id] = entity
        return entity

    def get_by_id(self, entity_id: str) -> Optional[ProvenanceRecord]:
        return self._store.get(entity_id)

    def get_by_id_and_tenant(self, entity_id: str, tenant_id: str) -> Optional[ProvenanceRecord]:
        rec = self._store.get(entity_id)
        if rec and rec.tenant_id == tenant_id:
            return rec
        return None

    def list_by_tenant(self, tenant_id: str) -> List[ProvenanceRecord]:
        return [r for r in self._store.values() if r.tenant_id == tenant_id]


class KnowledgeRelationshipRepository(TenantScopedRepository[KnowledgeRelationship]):
    def __init__(self) -> None:
        self._store: Dict[str, KnowledgeRelationship] = {}

    def save(self, entity: KnowledgeRelationship) -> KnowledgeRelationship:
        self._store[entity.relationship_id] = entity
        return entity

    def get_by_id(self, entity_id: str) -> Optional[KnowledgeRelationship]:
        return self._store.get(entity_id)

    def get_by_id_and_tenant(self, entity_id: str, tenant_id: str) -> Optional[KnowledgeRelationship]:
        rel = self._store.get(entity_id)
        if rel and rel.tenant_id == tenant_id:
            return rel
        return None

    def list_by_tenant(self, tenant_id: str) -> List[KnowledgeRelationship]:
        return [r for r in self._store.values() if r.tenant_id == tenant_id]


class KnowledgeInvestigationRepository(TenantScopedRepository[KnowledgeInvestigation]):
    def __init__(self) -> None:
        self._store: Dict[str, KnowledgeInvestigation] = {}

    def save(self, entity: KnowledgeInvestigation) -> KnowledgeInvestigation:
        self._store[entity.investigation_id] = entity
        return entity

    def get_by_id(self, entity_id: str) -> Optional[KnowledgeInvestigation]:
        return self._store.get(entity_id)

    def get_by_id_and_tenant(self, entity_id: str, tenant_id: str) -> Optional[KnowledgeInvestigation]:
        inv = self._store.get(entity_id)
        if inv and inv.tenant_id == tenant_id:
            return inv
        return None

    def list_by_tenant(self, tenant_id: str) -> List[KnowledgeInvestigation]:
        return [i for i in self._store.values() if i.tenant_id == tenant_id]


class MemoryRepository(TenantScopedRepository[OrganizationalMemory]):
    def __init__(self) -> None:
        self._store: Dict[str, OrganizationalMemory] = {}

    def save(self, entity: OrganizationalMemory) -> OrganizationalMemory:
        self._store[entity.memory_id] = entity
        return entity

    def get_by_id(self, entity_id: str) -> Optional[OrganizationalMemory]:
        return self._store.get(entity_id)

    def get_by_id_and_tenant(self, entity_id: str, tenant_id: str) -> Optional[OrganizationalMemory]:
        mem = self._store.get(entity_id)
        if mem and mem.tenant_id == tenant_id:
            return mem
        return None

    def list_by_tenant(self, tenant_id: str) -> List[OrganizationalMemory]:
        return [m for m in self._store.values() if m.tenant_id == tenant_id]
