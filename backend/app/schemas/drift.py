"""Drift detection schemas."""
from pydantic import BaseModel
from typing import Optional

class DriftEventResponse(BaseModel):
    """Drift event response."""
    id: int
    model_id: int
    detector: str
    score: float
    drift_type: str
