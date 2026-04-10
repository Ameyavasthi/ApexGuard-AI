import cv2

print('Testing different camera backends...')

# Test different backends
backends = [
    cv2.CAP_DSHOW,      # DirectShow (Windows)
    cv2.CAP_MSMF,       # Media Foundation (default, failing)
    cv2.CAP_FFMPEG,     # FFmpeg
]

for i, backend in enumerate(backends):
    print(f'\n--- Testing backend {i}: {backend} ---')
    cap = cv2.VideoCapture(0, backend)
    print(f'Camera opened with backend {backend}: {cap.isOpened()}')
    
    if cap.isOpened():
        # Try to set some properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Try to read a frame
        ret, frame = cap.read()
        print(f'Frame captured: {ret}')
        if ret:
            print(f'Frame shape: {frame.shape}')
            print('SUCCESS: Backend works!')
            cap.release()
            break
        else:
            print('Failed to capture frame')
        cap.release()
    else:
        print('Failed to open camera')

print('\n--- Testing with different camera indices ---')
for i in range(3):
    print(f'\nTesting camera index {i}:')
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cap.isOpened():
        ret, frame = cap.read()
        print(f'Camera {i} - Opened: True, Frame captured: {ret}')
        if ret:
            print(f'Frame shape: {frame.shape}')
        cap.release()
    else:
        print(f'Camera {i} - Opened: False')
