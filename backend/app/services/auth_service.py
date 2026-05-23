"""Authentication service with JWT and password hashing."""
from passlib.context import CryptContext
from jose import jwt
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Handles JWT creation/verification and password hashing."""
    
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt."""
        return pwd_context.hash(password)
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(password, hashed)
