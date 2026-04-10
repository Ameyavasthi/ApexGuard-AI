from fastapi import APIRouter

router = APIRouter()

@router.get("/api/test-simple")
def test_simple():
    """Simple non-streaming endpoint to test basic connectivity"""
    return {"status": "working", "message": "Basic API endpoint functioning"}

@router.get("/api/test-frame")
def test_frame():
    """Return a single test frame as image"""
    import cv2
    import numpy as np
    import base64
    
    # Create test frame
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    cv2.putText(frame, "TEST FRAME", (80, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Encode to JPEG
    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
    if ret:
        img_str = base64.b64encode(buffer.tobytes()).decode()
        return {"image": f"data:image/jpeg;base64,{img_str}"}
    
    return {"error": "Failed to generate frame"}
