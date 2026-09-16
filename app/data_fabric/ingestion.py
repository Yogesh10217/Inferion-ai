"""Data Ingestion Pipeline Engine."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.data_fabric.connector import ConnectorFactory
from app.data_fabric.data_source import DataSource
from app.jobs.job_queue import JobQueue
from app.resilience.circuit_breaker import CircuitBreakerRegistry

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class IngestionMode(str, Enum):
    FULL_SYNC = "FULL_SYNC"
    INCREMENTAL_SYNC = "INCREMENTAL_SYNC"
    STREAMING = "STREAMING"
    EVENT_DRIVEN = "EVENT_DRIVEN"
    MANUAL = "MANUAL"


class IngestionRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"ing_req_{uuid.uuid4().hex[:10]}")
    source_id: str
    tenant_id: str = "global"
    mode: IngestionMode = IngestionMode.FULL_SYNC
    limit: int = 100
    secret_data: Optional[Dict[str, Any]] = None


class IngestionBatch(BaseModel):
    batch_id: str = Field(default_factory=lambda: f"batch_{uuid.uuid4().hex[:10]}")
    records_count: int
    records: List[Dict[str, Any]]
    cursor: Optional[str] = None


class IngestionResult(BaseModel):
    ingestion_id: str
    source_id: str
    tenant_id: str
    mode: IngestionMode
    total_records: int
    batches_processed: int
    status: str = "COMPLETED"
    completed_at: datetime = Field(default_factory=_now)


class DataIngestionEngine:
    """Orchestrates secure extraction, validation, normalization, and ingestion pipeline."""

    def __init__(
        self,
        connector_factory: Optional[ConnectorFactory] = None,
        job_queue: Optional[JobQueue] = None,
        circuit_breakers: Optional[CircuitBreakerRegistry] = None,
    ) -> None:
        self.connector_factory = connector_factory or ConnectorFactory()
        self.job_queue = job_queue or JobQueue()
        self.circuit_breakers = circuit_breakers or CircuitBreakerRegistry()
        self._history: List[IngestionResult] = []

    async def execute_ingestion(self, data_source: DataSource, request: IngestionRequest) -> IngestionResult:
        """Run ingestion pipeline: Connect -> Extract -> Validate -> Record Result."""
        cb = self.circuit_breakers.get_breaker(f"ingestion:{data_source.id}")
        if not cb.allow_request():
            logger.warning(f"[INGESTION ENGINE] Circuit breaker OPEN for data source '{data_source.id}'")
            res = IngestionResult(
                ingestion_id=request.request_id,
                source_id=data_source.id,
                tenant_id=data_source.tenant_id,
                mode=request.mode,
                total_records=0,
                batches_processed=0,
                status="CIRCUIT_OPEN",
            )
            self._history.append(res)
            return res

        connector = self.connector_factory.create_connector(data_source, secret_data=request.secret_data)
        await connector.connect()

        if request.mode == IngestionMode.INCREMENTAL_SYNC:
            records, _ = await connector.fetch_incremental(limit=request.limit)
        else:
            records = await connector.fetch(limit=request.limit)

        await connector.disconnect()
        cb.record_success()

        res = IngestionResult(
            ingestion_id=request.request_id,
            source_id=data_source.id,
            tenant_id=data_source.tenant_id,
            mode=request.mode,
            total_records=len(records),
            batches_processed=1 if records else 0,
            status="COMPLETED",
        )
        self._history.append(res)
        logger.info(f"[INGESTION ENGINE] Ingested {len(records)} records from source '{data_source.name}' (Req: {request.request_id})")
        return res
