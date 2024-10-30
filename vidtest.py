import cv2
from picamera2 import Picamera2
import time

def setup_camera():
    """Initialize and configure the Picamera2."""
    picam2 = Picamera2()
    
    # Configure the camera
    config = picam2.create_preview_configuration(
        main={"size": (1280, 720)},
        lores={"size": (640, 480)},
        display="lores"
    )
    picam2.configure(config)
    
    return picam2

def display_live_feed():
    """Display live feed from the camera with FPS counter."""
    try:
        # Initialize camera
        picam2 = setup_camera()
        picam2.start()
        
        # Allow camera to warm up
        print("Warming up camera...")
        time.sleep(2)
        
        # Variables for FPS calculation
        fps_start_time = time.time()
        fps_counter = 0
        fps = 0
        
        print("Press 'q' to quit")
        
        while True:
            # Capture frame
            frame = picam2.capture_array()
            
            # Calculate FPS
            fps_counter += 1
            if (time.time() - fps_start_time) > 1:
                fps = fps_counter
                fps_counter = 0
                fps_start_time = time.time()
            
            # Add FPS text to frame
            cv2.putText(frame, f"FPS: {fps}", (30, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display frame
            cv2.imshow("Raspberry Pi Camera", frame)
            
            # Check for 'q' key to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        # Cleanup
        cv2.destroyAllWindows()
        picam2.stop()
        print("Camera stopped and resources released")

if __name__ == "__main__":
    display_live_feed()
