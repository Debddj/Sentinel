"""backend/app/models/calibration_curve.py — Calibration curve table."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base   # ← must use the shared Base, NOT declarative_base()


class CalibrationCurve(Base):
    """ROC-style FP-rate / detection-rate calibration curve per model per detector."""
    __tablename__ = "calibration_curves"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("model_registry.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    detector: Mapped[Optional[str]] = mapped_column(String(64))
    # List of {threshold, fp_rate, detection_rate} dicts
    curve_data: Mapped[Optional[dict]] = mapped_column(JSON)
    # Recommended thresholds at common FP budgets (1%, 5%, 10%)
    threshold_recommendations: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )