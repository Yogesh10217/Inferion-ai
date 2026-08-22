"""Synchronization & Change Data Capture Engine."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.data_fabric.data_source import DataSource, DataSourceManager
from app.data_fabric.ingestion import DataIngestionEngine, IngestionRequest, IngestionMode
from app.data_fabric.exceptions import DataSynchronizationError

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SyncStrategy(str, Enum):
    FULL = "FULL"
    INCREMENTAL = "INCREMENTAL"
    CHANGE_DATA_CAPTURE = "CHANGE_DATA_CAPTURE"
    WEBHOOK = "WEBHOOK"
    SCHEDULED = "SCHEDULED"
    EVENT_DRIVEN = "EVENT_DRIVEN"


class SyncStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PARTIAL = "PARTIAL"


class SyncJob(BaseModel):
    """Synchronization job tracking execution lifecycle."""

    job_id: str = Field(default_factory=lambda: f"sync_{uuid.uuid4().hex[:10]}")
    source_id: str
    tenant_id: str = "global"
    idempotency_key: str = Field(default_factory=lambda: f"idemp_{uuid.uuid4().hex[:10]}")
    strategy: SyncStrategy = SyncStrategy.FULL
    status: SyncStatus = SyncStatus.PENDING

    checkpoint_cursor: Optional[str] = None
    processed_records: int = 0
    error_message: Optional[str] = None

    started_at: datetime = Field(default_factory=_now)
    completed_at: Optional[datetime] = None


class DataSyncManager:
    """Manages multi-tenant synchronization jobs, checkpointing, retries, pause/resume, and cancellation."""

    def __init__(
        self,
        source_manager: Optional[DataSourceManager] = None,
        ingestion_engine: Optional[DataIngestionEngine] = None,
    ) -> None:
        self.source_manager = source_manager or DataSourceManager()
        self.ingestion_engine = ingestion_engine or DataIngestionEngine()
        self._jobs: Dict[str, SyncJob] = {}

    def create_sync_job(
        self,
        source_id: str,
        tenant_id: str = "global",
        strategy: SyncStrategy = SyncStrategy.FULL,
        idempotency_key: Optional[str] = None,
    ) -> SyncJob:
        """Create a sync job with idempotency deduplication."""
        if idempotency_key:
            existing = [j for j in self._jobs.values() if j.idempotency_key == idempotency_key and j.status in (SyncStatus.PENDING, SyncStatus.RUNNING)]
            if existing:
                logger.info(f"[DATA SYNC] Returned existing idempotent job '{existing[0].job_id}'")
                return existing[0]

        job = SyncJob(
            source_id=source_id,
            tenant_id=tenant_id,
            strategy=strategy,
            idempotency_key=idempotency_key or f"idemp_{uuid.uuid4().hex[:10]}",
        )
        self._jobs[job.job_id] = job
        logger.info(f"[DATA SYNC] Created sync job '{job.job_id}' for source '{source_id}' (Strategy: {strategy.value})")
        return job

    async def run_sync_job(self, job_id: str, secret_data: Optional[Dict[str, Any]] = None) -> SyncJob:
        """Execute sync job with progress checkpointing."""
        job = self.get_sync_job(job_id)
        if job.status == SyncStatus.CANCELLED:
            logger.warning(f"[DATA SYNC] Cannot run cancelled job '{job_id}'")
            return job

        job.status = SyncStatus.RUNNING
        try:
            ds = self.source_manager.get_source(job.source_id)
            ing_mode = IngestionMode.INCREMENTAL_SYNC if job.strategy == SyncStrategy.INCREMENTAL else IngestionMode.FULL_SYNC

            req = IngestionRequest(source_id=job.source_id, tenant_id=job.tenant_id, mode=ing_mode, secret_data=secret_data)
            res = await self.ingestion_engine.execute_ingestion(ds, req)

            job.processed_records = res.total_records
            job.checkpoint_cursor = f"cursor_{job.job_id}"
            job.status = SyncStatus.COMPLETED if res.status == "COMPLETED" else SyncStatus.FAILED
            job.completed_at = _now()
            self.source_manager.update_sync_timestamp(job.source_id)

            logger.info(f"[DATA SYNC] Job '{job.job_id}' finished with status '{job.status.value}' ({job.processed_records} records)")
            return job
        except Exception as e:
            job.status = SyncStatus.FAILED
            job.error_message = str(e)
            job.completed_at = _now()
            logger.error(f"[DATA SYNC ERROR] Sync job '{job_id}' failed: {e}")
            raise DataSynchronizationError(job_id, str(e))

    def pause_sync_job(self, job_id: str) -> SyncJob:
        job = self.get_sync_job(job_id)
        if job.status == SyncStatus.RUNNING:
            job.status = SyncStatus.PAUSED
            logger.info(f"[DATA SYNC] Paused sync job '{job_id}'")
        return job

    def resume_sync_job(self, job_id: str) -> SyncJob:
        job = self.get_sync_job(job_id)
        if job.status in (SyncStatus.PAUSED, SyncStatus.FAILED):
            job.status = SyncStatus.PENDING
            logger.info(f"[DATA SYNC] Resumed sync job '{job_id}'")
        return job

    def cancel_sync_job(self, job_id: str) -> SyncJob:
        job = self.get_sync_job(job_id)
        job.status = SyncStatus.CANCELLED
        job.completed_at = _now()
        logger.info(f"[DATA SYNC] Cancelled sync job '{job_id}'")
        return job

    def get_sync_job(self, job_id: str) -> SyncJob:
        job = self._jobs.get(job_id)
        if not job:
            raise DataSynchronizationError(job_id, "Job not found")
        return job

    def list_jobs(self, tenant_id: Optional[str] = None, source_id: Optional[str] = None) -> List[SyncJob]:
        res = list(self._jobs.values())
        if tenant_id:
            res = [j for j in res if j.tenant_id == tenant_id]
        if source_id:
            res = [j for j in res if j.source_id == source_id]
        return res
