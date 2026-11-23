from tomcam.ui.pages.home_page import HomePage
from tomcam.ui.pages.take_picture_page import TakePicturePage


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


