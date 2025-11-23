"""Celery application configuration."""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "stock_analysis",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["tasks.import_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_prefetch_multiplier=1,
)
