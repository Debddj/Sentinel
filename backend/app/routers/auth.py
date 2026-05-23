"""Authentication routes: login, refresh, logout."""
from fastapi import APIRouter, Depends
from app.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()

@router.post("/login")
async def login(username: str, password: str):
    """User login endpoint."""
    return {"access_token": "token", "token_type": "bearer"}

@router.post("/refresh")
async def refresh(refresh_token: str):
    """Refresh access token."""
    return {"access_token": "new_token", "token_type": "bearer"}

@router.post("/logout")
async def logout():
    """User logout endpoint."""
    return {"message": "logged out"}
