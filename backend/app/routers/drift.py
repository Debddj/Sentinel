"""Drift detection routes: GET /api/drift, /api/drift/{id}/attribution."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.get("/")
async def get_drift(db: AsyncSession = Depends(get_db)):
    """Get drift detection results."""
    return []

@router.get("/{drift_id}/attribution")
async def get_drift_attribution(drift_id: int, db: AsyncSession = Depends(get_db)):
    """Get SHAP attribution for drift event."""
    return {"attribution": []}
