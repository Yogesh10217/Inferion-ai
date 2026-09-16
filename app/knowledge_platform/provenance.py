"""Knowledge Provenance, Citation & Lineage Traceability Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class KnowledgeProvenance(BaseModel):
    provenance_id: str = Field(default_factory=lambda: f"kprv_{uuid.uuid4().hex[:10]}")
    item_id: str
    source_system: str = "DataFabric"


class CitationReference(BaseModel):
    citation_id: str = Field(default_factory=lambda: f"cit_{uuid.uuid4().hex[:10]}")
    source_id: str
    text_snippet: str


class ProvenanceChain(BaseModel):

    chain_id: str = Field(default_factory=lambda: f"prov_{uuid.uuid4().hex[:10]}")
    item_id: str
    tenant_id: str = "global"

    source_system: str = "DataFabric"
    connector_type: str = "REST_API"
    ingestion_job_id: str = "job_init"
    transformation_applied: str = "CHUNKING_EMBEDDING"
    version_number: int = 1

    created_at: datetime = Field(default_factory=_now)


class ProvenanceManager:
    """Tracks complete knowledge lineage and citation references."""

    def __init__(self) -> None:
        self._chains: Dict[str, ProvenanceChain] = {}

    def create_chain(self, item_id: str, tenant_id: str = "global", source_system: str = "DataFabric", connector_type: str = "REST_API") -> ProvenanceChain:
        chain = ProvenanceChain(item_id=item_id, tenant_id=tenant_id, source_system=source_system, connector_type=connector_type)
        self._chains[item_id] = chain
        logger.info(f"[PROVENANCE MANAGER] Created provenance chain '{chain.chain_id}' for item '{item_id}'")
        return chain

    def get_chain(self, item_id: str) -> Optional[ProvenanceChain]:
        return self._chains.get(item_id)
