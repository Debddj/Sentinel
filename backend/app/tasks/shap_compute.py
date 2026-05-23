"""Async SHAP computation task."""
from app.tasks.celery_app import celery_app

@celery_app.task
def compute_shap(drift_event_id: int) -> dict:
    """Compute SHAP attribution for drift event (< 5s target)."""
    return {"drift_event_id": drift_event_id, "attribution": {}}
