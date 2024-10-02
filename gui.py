import kivy
kivy.require("2.3.0")

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.config import Config

Config.set("graphics", "resizable", True)

class ScanScreen(Screen):
    def __init__(self, **kw):
        super(ScanScreen, self).__init__(**kw)

        self.button.bind(on_press=self.load)

    def load(self, *args):
        self.manager.current = "load"

class LoadingScreen(Screen):
    pass

class SNAICApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ScanScreen(name="scan"))
        sm.add_widget(LoadingScreen(name="load"))

        return sm
    
def start():
    SNAICApp().run()

if __name__ == "__main__":
    start()