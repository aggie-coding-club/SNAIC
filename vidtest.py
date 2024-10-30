# import cv2
# from picamera2 import Picamera2
# import time

# def setup_camera():
#     """Initialize and configure the Picamera2."""
#     picam2 = Picamera2()
    
#     # Configure the camera
#     config = picam2.create_preview_configuration(
#         main={"size": (1280, 720)},
#         lores={"size": (640, 480)},
#         display="lores"
#     )
#     picam2.configure(config)
    
#     return picam2

# def display_live_feed():
#     """Display live feed from the camera with FPS counter."""
#     try:
#         # Initialize camera
#         picam2 = setup_camera()
#         picam2.start()
        
#         # Allow camera to warm up
#         print("Warming up camera...")
#         time.sleep(2)
        
#         # Variables for FPS calculation
#         fps_start_time = time.time()
#         fps_counter = 0
#         fps = 0
        
#         print("Press 'q' to quit")
        
#         while True:
#             # Capture frame
#             frame = picam2.capture_array()
            
#             # Calculate FPS
#             fps_counter += 1
#             if (time.time() - fps_start_time) > 1:
#                 fps = fps_counter
#                 fps_counter = 0
#                 fps_start_time = time.time()
            
#             # Add FPS text to frame
#             cv2.putText(frame, f"FPS: {fps}", (30, 30),
#                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
#             # Display frame
#             cv2.imshow("Raspberry Pi Camera", frame)
            
#             # Check for 'q' key to quit
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
    
#     except Exception as e:
#         print(f"Error: {str(e)}")
    
#     finally:
#         # Cleanup
#         cv2.destroyAllWindows()
#         picam2.stop()
#         print("Camera stopped and resources released")

# if __name__ == "__main__":
#     display_live_feed()

from picamera2 import Picamera2
from picamera2.previews import Preview
import time

def setup_camera():
    """Initialize and configure the Raspberry Pi camera"""
    try:
        # Initialize the camera
        picam2 = Picamera2()
        
        # Configure the camera
        preview_config = picam2.create_preview_configuration()
        picam2.configure(preview_config)
        
        return picam2
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return None

def start_live_feed(duration=0):
    """
    Start the live camera feed
    Args:
        duration: Time in seconds to run the feed (0 for continuous until keyboard interrupt)
    """
    picam2 = setup_camera()
    
    if picam2 is None:
        return
    
    try:
        # Start the camera
        picam2.start_preview(Preview.QTGL)  # Use Qt preview window
        picam2.start()
        
        print("Live feed started. Press CTRL+C to stop.")
        
        if duration > 0:
            # Run for specified duration
            time.sleep(duration)
        else:
            # Run until keyboard interrupt
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\nStopping live feed...")
    except Exception as e:
        print(f"Error during live feed: {e}")
    finally:
        # Clean up
        picam2.stop_preview()
        picam2.stop()
        print("Camera stopped")

if __name__ == "__main__":
    # Start the live feed indefinitely
    start_live_feed()
