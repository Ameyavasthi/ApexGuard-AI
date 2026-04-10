import cv2
print('OpenCV version:', cv2.__version__)
cap = cv2.VideoCapture(0)
print('Camera opened:', cap.isOpened())
if cap.isOpened():
    ret, frame = cap.read()
    print('Frame captured:', ret)
    print('Frame shape:', frame.shape if ret else 'None')
    cap.release()
else:
    print('Failed to open camera')
