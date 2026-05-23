"""Alert request/response schemas."""
from pydantic import BaseModel

class AlertResponse(BaseModel):
    """Alert response."""
    id: int
    severity: str
    status: str
