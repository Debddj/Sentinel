"""Celery Beat: periodic tasks for sequential detectors."""
from celery.schedules import crontab
from app.tasks.celery_app import celery_app

celery_app.conf.beat_schedule = {
    "check-drift-every-30s": {
        "task": "app.tasks.drift_check.check_drift",
        "schedule": 30.0,
    },
}
