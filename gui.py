import kivy
kivy.require("2.3.0")

import time
import threading
import cv2
import math
import csv

from linkfinding import link_find

from sys import platform

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDTextButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (
    OneLineListItem
)

from kivy.app import App
from kivy.factory import Factory
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.camera import Camera
from kivy.config import Config
from kivy.base import Builder
from kivy.graphics.texture import Texture
from kivy.properties import ListProperty, NumericProperty, BooleanProperty

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
        print("Camera available: ", camera_available())
        self.capture = cv2.VideoCapture(0)
        cv2.namedWindow("CV2 Image")
        Clock.schedule_interval(self.update, 1.0 / FRAMERATE)

        return super().on_enter(*args)
    
    def update(self, *args):
        success, frame = self.capture.read()
        # print("Read frame: ", success)

        buf1 = frame # cv2.rotate(frame, cv2.ROTATE_180)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(640, 480), colorfmt="bgr")
        # On the PI, colorfmt="rgba"
        if platform == "win32":
            texture1.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        elif platform == "linux":
            texture1.blit_buffer(buf, colorfmt="rgba", bufferfmt="ubyte")
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

def sample_get_products(csv_file):
    products = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            products.append({'name': row['Domain'], 'link': row['Link']})
    return products

loaded_products = threading.Condition()

class ProductsList(Screen):
    loading_active = BooleanProperty(True)
    loading_thread = None
    products = []

    def load_products(self):
        link_find()
        loaded_products.acquire()
        self.products = sample_get_products('links.csv')
        self.update_product_list()
        loaded_products.notify_all()

        
        # self.loading_active = False

        # self.ids.loading.active = False
        # for product in products:
        #     list_item = OneLineListItem(text=f"{product}")

        #     self.ids.container.add_widget(list_item)

        print("done")

    def update_product_list(self):
        self.ids.container.clear_widgets()
        
        for product in self.products:
            list_item = OneLineListItem(
                text=product['link']
            )
            self.ids.container.add_widget(list_item)

    def on_enter(self, *args):
        # self.loading_thread = threading.Thread(target=self.load_products)

        self.load_products()
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