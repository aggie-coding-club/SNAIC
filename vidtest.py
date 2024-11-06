import cv2
import datetime
import os
from pathlib import Path
from picamera2 import Picamera2
import time

class PiVideoRecorder:
    def __init__(self, output_dir="recordings", resolution=(1920, 1080)):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize PiCamera
        self.picam = Picamera2()
        self.width, self.height = resolution
        
        # Configure the camera
        config = self.picam.create_preview_configuration(
            main={"size": resolution},
            lores={"size": (640, 480)},
            display="lores"
        )
        self.picam.configure(config)
        self.picam.start()
        
        # Allow camera to warm up
        time.sleep(2)
        
        # Initialize recording state
        self.is_recording = False
        self.out = None
        self.fps = 30

    def start_recording(self):
        if not self.is_recording:
            # Generate filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.output_dir / f"recording_{timestamp}.mp4"
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.out = cv2.VideoWriter(
                str(filename),
                fourcc,
                self.fps,
                (self.width, self.height)
            )
            self.is_recording = True
            print(f"Started recording: {filename}")
            return True
        return False

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            if self.out:
                self.out.release()
                self.out = None
            print("Stopped recording")
            return True
        return False

    def run(self):
        try:
            print("Recording controls:")
            print("Press 'r' to start/stop recording")
            print("Press 'q' to quit")
            
            while True:
                # Capture frame
                frame = self.picam.capture_array()
                
                # Convert frame from BGR to RGB (PiCamera uses BGR by default)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Add recording indicator
                if self.is_recording:
                    cv2.circle(frame, (30, 30), 10, (0, 0, 255), -1)
                    cv2.putText(
                        frame,
                        "Recording...",
                        (50, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2
                    )

                # Display frame
                cv2.imshow('PiCamera Recording', frame)

                # Write frame if recording
                if self.is_recording and self.out:
                    self.out.write(frame)

                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):  # Quit
                    break
                elif key == ord('r'):  # Start/stop recording
                    if self.is_recording:
                        self.stop_recording()
                    else:
                        self.start_recording()

        finally:
            # Clean up
            if self.out:
                self.out.release()
            self.picam.stop()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    recorder = PiVideoRecorder()
    recorder.run()
