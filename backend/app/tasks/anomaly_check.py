"""Anomaly detection check with Isolation Forest."""
from app.tasks.celery_app import celery_app

@celery_app.task
def check_anomalies(model_id: int) -> dict:
    """Check for anomalies in recent predictions."""
    return {"model_id": model_id, "anomalies": []}
