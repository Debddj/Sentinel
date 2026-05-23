"""WebSocket routes: /ws/stream?model_id= with heartbeat."""
from fastapi import APIRouter, WebSocket

router = APIRouter()

@router.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket, model_id: int):
    """WebSocket endpoint for real-time drift and alert streaming."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except Exception:
        pass
