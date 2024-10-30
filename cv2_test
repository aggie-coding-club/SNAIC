import cv2
import time

def test_camera():
    try:
        # Initialize the camera (0 is usually the default camera)
        print("Initializing camera...")
        cap = cv2.VideoCapture(0)
        
        # Check if camera opened successfully
        if not cap.isOpened():
            print("Error: Could not open camera")
            return False
        
        # Wait for camera to initialize
        print("Camera warming up...")
        time.sleep(2)
        
        # Capture a frame
        print("Capturing image...")
        ret, frame = cap.read()
        
        if ret:
            # Save the image
            cv2.imwrite('test_image.jpg', frame)
            print("Image captured successfully! Saved as 'test_image.jpg'")
            
            # Clean up
            cap.release()
            return True
        else:
            print("Error: Could not capture frame")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_camera()
