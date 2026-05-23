"""Model registry routes: CRUD for /api/models, baseline upload."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.get("/")
async def list_models(db: AsyncSession = Depends(get_db)):
    """List all models."""
    return []

@router.post("/")
async def create_model(db: AsyncSession = Depends(get_db)):
    """Create a new model."""
    return {"id": 1}

@router.get("/{model_id}")
async def get_model(model_id: int, db: AsyncSession = Depends(get_db)):
    """Get model by ID."""
    return {"id": model_id}
