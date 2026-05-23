"""Prediction request/response schemas."""
from pydantic import BaseModel
from typing import Optional

class PredictionRequest(BaseModel):
    """Prediction ingest request."""
    model_id: int
    features: dict
    prediction: float
    confidence: Optional[float] = None

class PredictionResponse(BaseModel):
    """Prediction response."""
    id: int
    model_id: int
    prediction: float
