"""
APScheduler setup.
Uses BackgroundScheduler (thread-based) so it works seamlessly with
synchronous FastAPI / SQLAlchemy without any asyncio complexity.
"""
import logging
from uuid import UUID

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(
    jobstores={"default": MemoryJobStore()},
    executors={"default": ThreadPoolExecutor(max_workers=10)},
    job_defaults={"coalesce": True, "max_instances": 1, "misfire_grace_time": 60},
)


def add_monitoring_job(monitoring_id: str, interval_minutes: int) -> None:
    """Register or replace a scheduled monitoring job."""
    from app.services.monitoring_service import run_monitoring_check

    scheduler.add_job(
        func=run_monitoring_check,
        trigger="interval",
        minutes=interval_minutes,
        id=monitoring_id,
        args=[monitoring_id],
        replace_existing=True,
    )
    logger.info(f"[Scheduler] Job added: id={monitoring_id}, every {interval_minutes}m")


def remove_monitoring_job(monitoring_id: str) -> None:
    """Remove a monitoring job if it exists."""
    try:
        scheduler.remove_job(monitoring_id)
        logger.info(f"[Scheduler] Job removed: id={monitoring_id}")
    except Exception:
        pass  # Job may not exist yet


def load_active_jobs() -> None:
    """
    Called at startup — loads all active monitoring requests from the DB
    and schedules them so monitoring is truly persistent.
    """
    from app.database import SessionLocal
    from app.models.monitoring import MonitoringRequest

    db = SessionLocal()
    try:
        active = db.query(MonitoringRequest).filter(MonitoringRequest.is_active == True).all()
        for req in active:
            add_monitoring_job(str(req.id), req.interval_minutes)
        logger.info(f"[Scheduler] Loaded {len(active)} active monitoring jobs from DB")
    except Exception as e:
        logger.error(f"[Scheduler] Failed to load jobs: {e}")
    finally:
        db.close()
