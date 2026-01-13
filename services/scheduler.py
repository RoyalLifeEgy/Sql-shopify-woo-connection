"""
Sync Scheduler for automatic synchronization
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from database import SessionLocal, get_settings
from models import FieldMapping
from services.sync_engine import SyncEngine

logger = logging.getLogger(__name__)
settings = get_settings()


class SyncScheduler:
    """Scheduler for automatic data synchronization"""

    def __init__(self):
        """Initialize the scheduler"""
        jobstores = {
            'default': SQLAlchemyJobStore(url=settings.database_url)
        }

        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            timezone='UTC'
        )
        self.scheduler.start()
        logger.info("Sync scheduler started")

    def _execute_sync_job(self, field_mapping_id: int):
        """
        Execute a sync job

        Args:
            field_mapping_id: ID of the field mapping to sync
        """
        db = SessionLocal()
        try:
            sync_engine = SyncEngine(db)
            sync_log = sync_engine.execute_sync(field_mapping_id)

            logger.info(
                f"Sync completed for mapping ID {field_mapping_id}: "
                f"{sync_log.records_successful} successful, "
                f"{sync_log.records_failed} failed"
            )
        except Exception as e:
            logger.error(f"Error executing sync job for mapping ID {field_mapping_id}: {str(e)}")
        finally:
            db.close()

    def add_sync_job(self, field_mapping: FieldMapping) -> str:
        """
        Add a sync job to the scheduler

        Args:
            field_mapping: Field mapping to sync

        Returns:
            Job ID
        """
        if not field_mapping.is_active:
            logger.warning(f"Cannot schedule inactive mapping: {field_mapping.name}")
            return None

        job_id = f"sync_mapping_{field_mapping.id}"

        # Remove existing job if it exists
        self.remove_sync_job(job_id)

        # Add new job
        trigger = IntervalTrigger(
            minutes=field_mapping.sync_interval_minutes,
            timezone='UTC'
        )

        self.scheduler.add_job(
            func=self._execute_sync_job,
            trigger=trigger,
            args=[field_mapping.id],
            id=job_id,
            name=f"Sync: {field_mapping.name}",
            replace_existing=True
        )

        logger.info(
            f"Scheduled sync job for mapping '{field_mapping.name}' "
            f"every {field_mapping.sync_interval_minutes} minutes"
        )

        return job_id

    def remove_sync_job(self, job_id: str):
        """
        Remove a sync job from the scheduler

        Args:
            job_id: ID of the job to remove
        """
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed sync job: {job_id}")
        except Exception as e:
            logger.debug(f"Job {job_id} not found or already removed: {str(e)}")

    def update_sync_job(self, field_mapping: FieldMapping) -> str:
        """
        Update an existing sync job

        Args:
            field_mapping: Updated field mapping

        Returns:
            Job ID
        """
        return self.add_sync_job(field_mapping)

    def reschedule_all_jobs(self):
        """Reschedule all active field mappings"""
        db = SessionLocal()
        try:
            active_mappings = db.query(FieldMapping).filter(
                FieldMapping.is_active == True
            ).all()

            logger.info(f"Rescheduling {len(active_mappings)} active mappings")

            for mapping in active_mappings:
                self.add_sync_job(mapping)

        finally:
            db.close()

    def get_scheduled_jobs(self) -> Dict[str, Any]:
        """Get information about all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        return {"jobs": jobs, "total": len(jobs)}

    def pause_job(self, job_id: str):
        """Pause a scheduled job"""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Paused job: {job_id}")
        except Exception as e:
            logger.error(f"Error pausing job {job_id}: {str(e)}")

    def resume_job(self, job_id: str):
        """Resume a paused job"""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Resumed job: {job_id}")
        except Exception as e:
            logger.error(f"Error resuming job {job_id}: {str(e)}")

    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()
        logger.info("Sync scheduler shut down")


# Global scheduler instance
sync_scheduler = SyncScheduler()
