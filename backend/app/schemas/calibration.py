"""Calibration schemas."""
from pydantic import BaseModel
from typing import List

class CalibrationPoint(BaseModel):
    """Single calibration point."""
    threshold: float
    fp_rate: float
    tp_rate: float

class CalibrationResponse(BaseModel):
    """Calibration response."""
    model_id: int
    points: List[CalibrationPoint]
