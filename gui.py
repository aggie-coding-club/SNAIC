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
    OneLineListItem
)

from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.base import Builder
from kivy.graphics.texture import Texture
from kivy.properties import BooleanProperty

# https://stackoverflow.com/questions/37749378/integrate-opencv-webcam-into-a-kivy-user-interface

def camera_available():
    cap = cv2.VideoCapture(0)
    available = cap is not None and cap.isOpened()
    
    cap.release()
    
    return available

FRAMERATE = 33.0

# Screen that shows the camera feed + scan button
class CamTab(Screen):
    double_touch = False

    def on_enter(self, *args):
        # Setup capture
        # print("Camera available: ", camera_available())

        if platform == "win32":
            self.capture = cv2.VideoCapture(0)
            cv2.namedWindow("CV2 Image")
        elif platform == "linux":
            self.capture = picamera2.Picamera2()
            self.capture.configure(
                self.capture.create_video_configuration(main={"format": "RGB8888", "size": (640, 480)})
            )
            self.capture.start()
        Clock.schedule_interval(self.update, 1.0 / FRAMERATE)

        return super().on_enter(*args)
    
    def update(self, *args):
        if platform == "win32":
            success, frame = self.capture.read()
        elif platform == "linux":
            frame = self.capture.capture_array()
        # print("Read frame: ", success)

        buf1 = frame # cv2.rotate(frame, cv2.ROTATE_180)
        buf = buf1.tostring()
        # On the PI, colorfmt="rgba"
        if platform == "win32":
            texture1 = Texture.create(size=(640, 480), colorfmt="bgr")
            texture1.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        elif platform == "linux":
            texture1 = Texture.create(size=(640, 480), colorfmt="rgb")
            texture1.blit_buffer(buf, colorfmt="rgb", bufferfmt="ubyte")
        else:
            print(f"unrecognized operating system: {platform}")
        # texture1 = cv2.rotate(texture1, cv2.ROTATE_180)
        self.show_camera.texture = texture1

    def image_press(self, *args):
        # TODO: See if the bottom of the image should report 0.1 or 0
        if self.show_camera.collide_point(*args[1].pos) and not self.double_touch:
            x = math.floor(args[1].spos[0] * 640)
            y = math.floor(args[1].spos[1] * 480)
            print(f"Image touched: x: {x}, y: {y}")
            
        self.double_touch = not self.double_touch

            # TODO: Here is where the ML function would be called

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
    products = [
        "Product 1", 
        "Product 2", 
        "Product 3", 
        "Product 4", 
        "Product 5", 
        "Product 6"
    ]

    def load_products(self):
        loaded_products.acquire()
        products = sample_get_products()
        loaded_products.notify_all()

        # self.loading_active = False

        # self.ids.loading.active = False
        # for product in products:
        #     list_item = OneLineListItem(text=f"{product}")

        #     self.ids.container.add_widget(list_item)

        print("done")

    def on_enter(self, *args):
        # self.loading_thread = threading.Thread(target=self.load_products)

        self.loading_active = False
        # self.ids.loading.active = False
        for product in self.products:
            list_item = OneLineListItem(text=f"{product}")

            self.ids.container.add_widget(list_item)

        return super().on_enter(*args)

class SNAICApp(MDApp):
    def build(self):
        return Builder.load_file("snaic.kv")

def start():
    SNAICApp().run()

if __name__ == "__main__":
    start()