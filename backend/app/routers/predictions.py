"""Prediction ingestion routes: POST /api/predictions/ingest (batch)."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.post("/ingest")
async def ingest_predictions(db: AsyncSession = Depends(get_db)):
    """Ingest batch predictions."""
    return {"ingested": 0}
