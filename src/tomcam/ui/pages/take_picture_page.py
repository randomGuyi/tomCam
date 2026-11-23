from tomcam.config import theme
from tomcam.ui.pages.base_page import BasePage
from tomcam.ui.components.button import Button
from tomcam.ui.components.header import draw_header
from tomcam.ui.drawing import rounded_rect


class TakePicturePage(BasePage):
    def __init__(self, app):
        super().__init__(app)
        self.status = "Camera preview will appear here"
        self._controls = [
            Button("back", "Return", (42, 365, 190, 70)),
            Button("shoot", "Shoot Picture", (540, 365, 218, 70)),
        ]

    @property
    def controls(self):
        return self._controls

    def activate(self, key):
        if key == "back":
            self.app.navigation.show_home()
        elif key == "shoot":
            self.status = "Capture requested — camera integration comes next."

    def go_back(self):
        self.app.navigation.show_home()

    def draw(self, app):
        draw_header(app, "Take Picture", "Frame your photo, then press Shoot Picture")
        rounded_rect(app.renderer, 42, 135, 716, 205, 22, theme.SURFACE)
        rounded_rect(app.renderer, 54, 147, 692, 181, 16, (15, 19, 26, 255))
        # Call the Camere-Manager here to render the current cam content.
        rounded_rect(app.renderer, 350, 198, 100, 62, 14, theme.SURFACE_RAISED)
        app.render_text("CAMERA", 365, 270, theme.MUTED, 18)
        app.render_text(self.status, 225, 310, theme.MUTED, 18)
        for index, button in enumerate(self.controls):
            button.draw(app, selected=index == self.focus_index, compact=True)


