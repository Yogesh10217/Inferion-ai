"""Data Catalog & Business Glossary Management Subsystem."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.data_governance.assets import DataAssetManager, DataAssetType, DataDomain


class SchemaFieldMetadata(BaseModel):
    name: str
    data_type: str
    nullable: bool = True
    description: Optional[str] = None
    sensitive_data_type: Optional[str] = None


class SchemaMetadata(BaseModel):
    schema_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: str = "1.0.0"
    fields: List[SchemaFieldMetadata] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CatalogMetadata(BaseModel):
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    custom_attributes: Dict[str, Any] = Field(default_factory=dict)
    classification_level: str = "CONFIDENTIAL"


class CatalogEntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    asset_id: str
    asset_name: str
    asset_type: DataAssetType
    domain: DataDomain
    owner_id: str
    metadata: CatalogMetadata
    schema_info: Optional[SchemaMetadata] = None
    glossary_terms: List[str] = Field(default_factory=list)
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GlossaryTerm(BaseModel):
    term_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str
    definition: str
    domain: DataDomain
    steward_id: str
    synonyms: List[str] = Field(default_factory=list)
    related_asset_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BusinessGlossary(BaseModel):
    tenant_id: str
    terms: Dict[str, GlossaryTerm] = Field(default_factory=dict)


class DataCatalog(BaseModel):
    tenant_id: str
    entries: Dict[str, CatalogEntry] = Field(default_factory=dict)


class DataCatalogManager:
    """Manages Data Catalog entries, schema tracking, business definitions, and search."""

    def __init__(self, asset_manager: DataAssetManager) -> None:
        self.asset_manager = asset_manager
        self._catalogs: Dict[str, DataCatalog] = {}
        self._glossaries: Dict[str, BusinessGlossary] = {}

    def _get_or_create_catalog(self, tenant_id: str) -> DataCatalog:
        if tenant_id not in self._catalogs:
            self._catalogs[tenant_id] = DataCatalog(tenant_id=tenant_id)
        return self._catalogs[tenant_id]

    def _get_or_create_glossary(self, tenant_id: str) -> BusinessGlossary:
        if tenant_id not in self._glossaries:
            self._glossaries[tenant_id] = BusinessGlossary(tenant_id=tenant_id)
        return self._glossaries[tenant_id]

    def register_catalog_entry(
        self,
        tenant_id: str,
        asset_id: str,
        description: str,
        tags: Optional[List[str]] = None,
        schema_fields: Optional[List[SchemaFieldMetadata]] = None,
        glossary_terms: Optional[List[str]] = None,
    ) -> CatalogEntry:
        asset = self.asset_manager.get_asset(asset_id, tenant_id)
        catalog = self._get_or_create_catalog(tenant_id)

        meta = CatalogMetadata(
            description=description,
            tags=tags or [],
            classification_level=asset.classification,
        )

        schema_info = None
        if schema_fields:
            schema_info = SchemaMetadata(fields=schema_fields)

        entry = CatalogEntry(
            tenant_id=tenant_id,
            asset_id=asset.asset_id,
            asset_name=asset.name,
            asset_type=asset.type,
            domain=asset.domain,
            owner_id=asset.owner.owner_id,
            metadata=meta,
            schema_info=schema_info,
            glossary_terms=glossary_terms or [],
        )
        catalog.entries[asset_id] = entry
        return entry

    def search_catalog(
        self,
        tenant_id: str,
        query: str,
        domain: Optional[DataDomain] = None,
        asset_type: Optional[DataAssetType] = None,
    ) -> List[CatalogEntry]:
        catalog = self._get_or_create_catalog(tenant_id)
        q = query.lower()
        results = []
        for entry in catalog.entries.values():
            if domain and entry.domain != domain:
                continue
            if asset_type and entry.asset_type != asset_type:
                continue
            if q in entry.asset_name.lower() or q in entry.metadata.description.lower() or any(q in t.lower() for t in entry.metadata.tags):
                results.append(entry)
        return results

    def add_glossary_term(
        self,
        tenant_id: str,
        name: str,
        definition: str,
        domain: DataDomain,
        steward_id: str,
        synonyms: Optional[List[str]] = None,
    ) -> GlossaryTerm:
        glossary = self._get_or_create_glossary(tenant_id)
        term = GlossaryTerm(
            tenant_id=tenant_id,
            name=name,
            definition=definition,
            domain=domain,
            steward_id=steward_id,
            synonyms=synonyms or [],
        )
        glossary.terms[term.term_id] = term
        return term

    def list_glossary_terms(self, tenant_id: str) -> List[GlossaryTerm]:
        glossary = self._get_or_create_glossary(tenant_id)
        return list(glossary.terms.values())
