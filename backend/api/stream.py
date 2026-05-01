import asyncio
import logging
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from core.state_manager import state

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_frames_from_state():

    last_jpeg = None

    while True:
        jpeg = state.get_stream_frame()

        if jpeg:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')

        await asyncio.sleep(0.1)

@router.get("/api/stream")
async def video_stream():

    return StreamingResponse(
        get_frames_from_state(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
