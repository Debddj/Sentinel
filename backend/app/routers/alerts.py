"""Alert routes: GET/PATCH /api/alerts."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.get("/")
async def list_alerts(db: AsyncSession = Depends(get_db)):
    """List all alerts."""
    return []

@router.patch("/{alert_id}")
async def update_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """Update alert status."""
    return {"id": alert_id}
