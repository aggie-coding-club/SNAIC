# Dependencies:
# 
# python-opencv
# kivy
# kivymd
# picamera2 (only on raspberry pi)

import kivy
kivy.require("2.3.0")

import time
import threading
import math
import cv2

from sys import platform

if platform == "linux":
    import picamera2

from kivymd.app import MDApp
from kivymd.uix.list import (
    TwoLineAvatarListItem,
    ImageLeftWidget
)

from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.config import Config
from kivy.base import Builder
from kivy.graphics.texture import Texture
from kivy.properties import BooleanProperty
from kivy.properties import BooleanProperty

# https://stackoverflow.com/questions/37749378/integrate-opencv-webcam-into-a-kivy-user-interface

def camera_available():
    cap = cv2.VideoCapture(0)
    available = cap is not None and cap.isOpened()
    
    cap.release()
    
    return available

FRAMERATE = 33.0

last_x = 0
last_y = 0

# Screen that shows the camera feed + scan button
class CamTab(Screen):
    double_touch = False

    def on_enter(self, *args):
        # Setup capture
        if platform == "win32":
            self.capture = cv2.VideoCapture(0)
            cv2.namedWindow("CV2 Image")
        elif platform == "linux":
            self.capture = picamera2.Picamera2()
            self.capture.configure(
                self.capture.create_video_configuration(main={"format": "RGB888", "size": (640, 480)})
            )
            self.capture.start()
        Clock.schedule_interval(self.update, 1.0 / FRAMERATE)

        return super().on_enter(*args)
    
    def update(self, *args):
        if platform == "win32":
            _, frame = self.capture.read()
        elif platform == "linux":
            frame = self.capture.capture_array()

        buf1 = cv2.rotate(frame, cv2.ROTATE_180)
        self.cur_frame = buf1
        buf = buf1.tostring()

        # On the PI, colorfmt="rgba"
        if platform == "win32":
            texture1 = Texture.create(size=(640, 480), colorfmt="bgr")
            texture1 = Texture.create(size=(640, 480), colorfmt="bgr")
            texture1 = Texture.create(size=(640, 480), colorfmt="bgr")
            texture1.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        elif platform == "linux":
            texture1 = Texture.create(size=(640, 480), colorfmt="bgr")
            texture1.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        else:
            print(f"unrecognized operating system: {platform}")
        self.show_camera.texture = texture1

    def image_press(self, *args):
        global last_x, last_y

        if self.show_camera.collide_point(*args[1].pos) and not self.double_touch:
            x = math.floor(args[1].spos[0] * 640)
            y = math.floor(args[1].spos[1] * 480)
            last_x = x
            last_y = y

            frame = cv2.flip(self.cur_frame, 0)
            cv2.imwrite("frame.png", frame)
            self.manager.current = "products"
            
        self.double_touch = not self.double_touch

        return True

def sample_get_products():
    time.sleep(1)

    return [
        "Product 1", 
        "Product 2", 
        "Product 3", 
        "Product 4", 
        "Product 5", 
        "Product 6" 
    ]

loaded_products = threading.Condition()

class ProductsList(Screen):
    loading_active = BooleanProperty(True)
    loading_thread = None
    products = []

    def populate_products_list(self):
        for product in self.products:
            list_item = TwoLineAvatarListItem(
                # TODO: Change this to the relevant avatar
                ImageLeftWidget(
                    source="gui/unknown.png"
                ),
                text=f"{product}",
                secondary_text="price"
            )

            self.ids.container.add_widget(list_item)

    def update(self, *args):
        # Wait for product loading thread to finish and populate 
        if self.loading_thread is not None and not self.loading_thread.is_alive():
            self.loading_active = False
            self.loading_thread = None
            self.ids.loading.active = False
            self.populate_products_list()

    def load_products(self):
        # TODO: Call ML function here
        # Make sure that item preview images go into gui folder
        print(f"Looking for products at ({last_x}, {last_y})")
        time.sleep(5)
        self.products = ["Product 1", "Hello World"]

    def on_enter(self, *args):
        # Start loading thread and schedule update
        self.loading_thread = threading.Thread(target=self.load_products)
        self.loading_thread.start()

        Clock.schedule_interval(self.update, 1 / 60)

        return super().on_enter(*args)

class SNAICApp(MDApp):
    def build(self):
        return Builder.load_file("snaic.kv")

def start():
    SNAICApp().run()

if __name__ == "__main__":
    start()