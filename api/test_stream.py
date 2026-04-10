"""
Simple test stream endpoint that always works
"""
import cv2
import numpy as np
import time
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/api/test-stream")
def test_video_stream():
    """Simple test stream that always works"""
    def generate_frames():
        frame_count = 0
        while True:
            # Create a simple test frame
            frame = np.zeros((240, 320, 3), dtype=np.uint8)
            
            # Add animated elements
            x = int(160 + 100 * np.sin(frame_count * 0.1))
            y = int(120 + 50 * np.cos(frame_count * 0.1))
            
            cv2.circle(frame, (x, y), 15, (0, 255, 0), -1)
            cv2.putText(frame, f"TEST FRAME {frame_count}", (80, 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Encode frame
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            
            frame_count += 1
            time.sleep(0.1)  # ~10 FPS
    
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
