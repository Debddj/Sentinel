"""Drift threshold table definition."""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class DriftThreshold(Base):
    """Drift threshold table for EWMA tracking."""
    __tablename__ = "drift_thresholds"
    
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, nullable=False)
    detector = Column(String)
    ewma_threshold = Column(Float)
    history = Column(JSON)  # Historical thresholds
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
