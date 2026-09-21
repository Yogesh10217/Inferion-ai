import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional

from sqlalchemy import select

from app.admin.exceptions import ResourceNotFoundException
from app.admin.models import ReportJob


class ReportAdminService:
    def __init__(self, db: Any):
        self.db = db

    async def create_report_job(self, type: str, created_by: str, parameters: Optional[dict] = None) -> ReportJob:
        job = ReportJob(
            id=str(uuid.uuid4()),
            type=type,
            status="pending",
            created_by=created_by,
            parameters=parameters,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        # Note: In a production system, this is where we would trigger a background task (e.g. Celery, ARQ, or asyncio.create_task)
        # to actually process the report and update the job status later.
        return job

    async def get_report_job(self, job_id: str) -> ReportJob:
        job = await self.db.get(ReportJob, job_id)
        if not job:
            raise ResourceNotFoundException(f"Report Job {job_id} not found")
        return job

    async def list_report_jobs(
        self, created_by: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[ReportJob]:
        stmt = select(ReportJob)
        if created_by:
            stmt = stmt.where(ReportJob.created_by == created_by)
        stmt = stmt.order_by(ReportJob.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
