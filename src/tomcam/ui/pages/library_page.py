from tomcam.config import theme
from tomcam.services.image_library import ImageLibrary
from tomcam.ui.components.button import Button
from tomcam.ui.components.header import draw_header
from tomcam.ui.pages.base_page import BasePage


class LibraryPage(BasePage):
    def __init__(self, app):
        super().__init__(app)
        self.library = ImageLibrary()
        self.images = []
        self.status = ""
        self._controls = [Button("back", "Return to Home", (42, 390, 716, 70))]

    @property
    def controls(self):
        return self._controls

    def on_show(self):
        super().on_show()
        try:
            self.images = self.library.get_images()
            self.status = (
                f"{len(self.images)} saved image(s)"
                if self.images
                else "No saved images yet"
            )
        except OSError as exc:
            self.images = []
            self.status = f"Could not read image library: {exc}"

    def activate(self, key):
        if key == "back":
            self.app.navigation.show_home()

    def go_back(self):
        self.app.navigation.show_home()

    def draw(self, app):
        draw_header(app, "Library")
        app.render_text(self.status, 44, 112, theme.MUTED, 18)
        for index, path in enumerate(self.images[:9]):
            app.render_text(
                path.name[:54],
                48,
                151 + index * 25,
                theme.TEXT,
                18,
            )
        for index, button in enumerate(self.controls):
            button.draw(app, selected=index == self.focus_index)
