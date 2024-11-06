import cv2
import numpy as np
from picamera2 import Picamera2

cam = Picamera2()
height = 480
width = 640
middle = (int(width / 2), int(height / 2))
cam.configure(cam.create_video_configuration(main={"format": 'RGB888', "size": (width, height)}))

cam.start()

while True:
        frame = cam.capture_array()
        cv2.circle(frame, middle, 10, (255, 0 , 255), -1)
        cv2.imshow('f', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
                break
