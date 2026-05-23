"""Drift event table definition."""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class DriftEvent(Base):
    """Drift event table."""
    __tablename__ = "drift_events"
    
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, nullable=False)
    detector = Column(String)  # psi, ks_test, etc.
    score = Column(Float)
    drift_type = Column(String)  # data_drift, concept_drift
    shap_attribution = Column(JSON)  # Feature importance
    created_at = Column(DateTime, default=datetime.utcnow)
