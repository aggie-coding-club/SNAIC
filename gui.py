import kivy
kivy.require("2.3.0")

import time
import threading
import cv2

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
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.config import Config
from kivy.base import Builder
from kivy.properties import ListProperty, NumericProperty, BooleanProperty

# https://stackoverflow.com/questions/37749378/integrate-opencv-webcam-into-a-kivy-user-interface

def camera_available():
    cap = cv2.VideoCapture(0)
    available = cap is not None and cap.isOpened()
    
    cap.release()
    
    return available

class Scan(Screen):
    def on_enter(self, *args):
        # if camera_available():
        #     self.add_widget(Camera(
        #         resolution=(1920, 1080),
        #         play=False,
        #         size_hint=(1, 0.75),
        #         index=0
        #     ))
        # else:
        #     self.add_widget(MDLabel(
        #         text="No camera detected",
        #         size_hint=(1, 0.75),
        #         halign="center"
        #     ))

        return super().on_enter(*args)

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