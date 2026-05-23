"""Reference baseline table definition."""
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class ReferenceBaseline(Base):
    """Reference baseline table."""
    __tablename__ = "reference_baselines"
    
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, nullable=False)
    version = Column(Integer, default=1)
    feature_stats = Column(JSON)  # mean, std, quantiles, histograms
    created_at = Column(DateTime, default=datetime.utcnow)
