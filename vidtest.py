import cv2
import time
import numpy as np
from datetime import datetime

def test_camera():
    """
    Test program for Raspberry Pi camera using OpenCV
    Displays live feed, captures images, and demonstrates basic features
    """
    # Initialize camera
    # Use 0 for default camera (usually Pi Camera)
    cap = cv2.VideoCapture(0)
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    print("Camera initialized successfully")
    print("Press 'q' to quit")
    print("Press 's' to save a photo")
    print("Press 'g' to convert to grayscale")
    
    # Initialize variables
    grayscale_mode = False
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Can't receive frame")
                break
            
            # Calculate FPS
            frame_count += 1
            if frame_count % 30 == 0:
                end_time = time.time()
                fps = 30 / (end_time - start_time)
                start_time = time.time()
                print(f"FPS: {fps:.2f}")
            
            # Process frame
            if grayscale_mode:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Convert back to BGR for consistent display
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            
            # Add timestamp to frame
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, timestamp, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display the frame
            cv2.imshow('Raspberry Pi Camera Test', frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("Quitting...")
                break
            elif key == ord('s'):
                # Save image
                filename = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Saved image: {filename}")
            elif key == ord('g'):
                # Toggle grayscale mode
                grayscale_mode = not grayscale_mode
                print(f"Grayscale mode: {'On' if grayscale_mode else 'Off'}")
                
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    
    finally:
        # Release camera and close windows
        cap.release()
        cv2.destroyAllWindows()
        print("Camera released and windows closed")

if __name__ == "__main__":
    test_camera()
