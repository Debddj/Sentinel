"""Alert table definition."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Alert(Base):
    """Alert table."""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True)
    drift_event_id = Column(Integer, nullable=False)
    severity = Column(String)  # low, medium, high, critical
    status = Column(String, default="open")  # open, acknowledged, resolved
    cooldown = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
