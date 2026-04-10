"""
api/stream.py — HIGH-PERFORMANCE MJPEG STREAM (DECOUPLED)
=========================================================
Reads pre-encoded and pre-annotated frames from the Global State Manager.
Extremely lightweight: No AI or OpenCV logic here.
"""
import asyncio
import logging
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from core.state_manager import state

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_frames_from_state():
    """Async generator that yields latest state-cached frames."""
    # This loop is ultra-fast as it only reads from memory.
    # It ensures the API thread is never blocked by camera I/O or AI.
    last_jpeg = None
    
    while True:
        jpeg = state.get_stream_frame()
        
        if jpeg:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')
        
        # Consistent FPS for the client stream (approx 10 FPS to match engine)
        await asyncio.sleep(0.1)

@router.get("/api/stream")
async def video_stream():
    """Non-blocking MJPEG video stream endpoint."""
    return StreamingResponse(
        get_frames_from_state(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
