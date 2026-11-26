from tomcam.ui.pages.home_page import HomePage
from tomcam.ui.pages.library_page import LibraryPage
from tomcam.ui.pages.settings_page import SettingsPage
from tomcam.ui.pages.take_picture_page import TakePicturePage
from tomcam.ui.pages.voice_to_images import VoiceToImagePage
from tomcam.ui.pages.wifi_page import WifiPage


class Navigation:
    def __init__(self, app):
        self.app = app
        self.current_page = None
        self.show_home()

    def _show(self, page):
        if self.current_page:
            self.current_page.on_hide()
        self.current_page = page
        self.current_page.on_show()

    def show_home(self):
        self._show(HomePage(self.app))

    def show_take_picture(self):
        self._show(TakePicturePage(self.app))

    def show_voice_to_image(self):
        self._show(VoiceToImagePage(self.app))

    def show_library(self):
        self._show(LibraryPage(self.app))

    def show_settings(self):
        self._show(SettingsPage(self.app))

    def show_wifi(self):
        self._show(WifiPage(self.app))

