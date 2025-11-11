from celery import Celery
from app.config import settings

celery_app = Celery(
    "cryptscan",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.SCAN_TIMEOUT_SECONDS,
    task_soft_time_limit=settings.SCAN_TIMEOUT_SECONDS - 30,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Import tasks to register them with Celery
# This must be imported after celery_app is created
import app.tasks  # noqa: F401

