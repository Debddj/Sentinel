"""Calibration routes: GET/POST /api/models/{id}/calibration."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.get("/{model_id}/calibration")
async def get_calibration(model_id: int, db: AsyncSession = Depends(get_db)):
    """Get calibration curve for model."""
    return {"calibration": []}

@router.post("/{model_id}/calibration")
async def update_calibration(model_id: int, db: AsyncSession = Depends(get_db)):
    """Update calibration curve."""
    return {"updated": True}
