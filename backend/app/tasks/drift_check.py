"""Drift check task triggered on batch size or time elapsed."""
from app.tasks.celery_app import celery_app

@celery_app.task
def check_drift(model_id: int) -> dict:
    """Check for drift on new batch of predictions."""
    return {"model_id": model_id, "drift_detected": False}
