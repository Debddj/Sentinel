"""Calibration curve table definition."""
from sqlalchemy import Column, Integer, DateTime, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class CalibrationCurve(Base):
    """Calibration curve for FP rate analysis."""
    __tablename__ = "calibration_curves"
    
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, nullable=False)
    curve_data = Column(JSON)  # ROC-style points
    threshold_recommendations = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
