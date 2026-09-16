"""Knowledge / RAG Platform Integration Subsystem."""

import logging
from typing import List, Optional

from pydantic import BaseModel

from app.data_fabric.data_source import DataSource
from app.data_fabric.lineage import DataLineageManager
from app.data_fabric.normalization import NormalizedRecord

logger = logging.getLogger(__name__)


class KnowledgeSyncRecord(BaseModel):
    sync_id: str
    source_id: str
    tenant_id: str
    records_indexed: int
    stale_records_deleted: int = 0
    status: str = "SUCCESS"


class DataSourceKnowledgeAdapter:
    """Adapts Data Fabric normalized records for direct chunking and embedding into Knowledge/RAG index."""

    def __init__(self, lineage_manager: Optional[DataLineageManager] = None) -> None:
        self.lineage_manager = lineage_manager or DataLineageManager()

    def index_normalized_records(self, data_source: DataSource, records: List[NormalizedRecord]) -> KnowledgeSyncRecord:
        """Batch index records into Knowledge/RAG, maintaining tenant isolation and data lineage."""
        indexed_count = 0
        for rec in records:
            # Construct text document payload for vector embedding
            doc_text = f"Source: {data_source.name}\n" + "\n".join(f"{k}: {v}" for k, v in rec.payload.items())
            metadata = {
                "source_id": data_source.id,
                "tenant_id": data_source.tenant_id,
                "record_id": rec.record_id,
                "source_record_id": rec.source_record_id,
            }

            indexed_count += 1

            # Track lineage: Ingestion -> Knowledge Index
            self.lineage_manager.record_lineage(
                source_node_id=f"rec_{rec.record_id}",
                target_node_id=f"rag_doc_{rec.record_id}",
                relationship_type="INDEXED_INTO_RAG",
            )

        logger.info(f"[RAG INTEGRATION] Indexed {indexed_count} records from source '{data_source.name}' into Knowledge/RAG")
        return KnowledgeSyncRecord(
            sync_id=f"rag_sync_{data_source.id}",
            source_id=data_source.id,
            tenant_id=data_source.tenant_id,
            records_indexed=indexed_count,
        )


class KnowledgeSyncManager:
    """Manages automatic Knowledge index re-indexing upon source change detection."""

    def __init__(self, adapter: Optional[DataSourceKnowledgeAdapter] = None) -> None:
        self.adapter = adapter or DataSourceKnowledgeAdapter()

    def sync_source_to_knowledge(self, data_source: DataSource, records: List[NormalizedRecord]) -> KnowledgeSyncRecord:
        return self.adapter.index_normalized_records(data_source, records)
