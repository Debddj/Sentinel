"""Prediction table definition."""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Prediction(Base):
    """Prediction table."""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, nullable=False)
    features = Column(JSON)  # features as JSONB
    prediction = Column(Float)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
