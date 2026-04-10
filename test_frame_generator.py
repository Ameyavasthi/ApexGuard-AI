import cv2
import numpy as np
import time

def create_test_stream():
    """Create a test video stream that always works"""
    frame_count = 0
    
    while True:
        # Create a test frame with moving elements
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        
        # Add animated test pattern
        x = int(160 + 100 * np.sin(frame_count * 0.1))
        y = int(120 + 50 * np.cos(frame_count * 0.1))
        
        cv2.circle(frame, (x, y), 20, (0, 255, 0), -1)
        cv2.rectangle(frame, (x-30, y-30), (x+30, y+30), (255, 255, 255), 2)
        
        # Add text
        cv2.putText(frame, f"TEST FEED - Frame {frame_count}", (50, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, "Camera Simulation", (80, 200),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        # Encode and yield
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
        if ret:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        frame_count += 1
        time.sleep(0.066)  # ~15 FPS

if __name__ == "__main__":
    print("Testing frame generator...")
    for i, chunk in enumerate(create_test_stream()):
        print(f"Frame {i}: {len(chunk)} bytes")
        if i >= 5:
            break
