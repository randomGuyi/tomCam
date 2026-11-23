from tomcam.config import theme
from tomcam.ui.pages.base_page import BasePage
from tomcam.ui.components.button import Button
from tomcam.ui.components.header import draw_header
from tomcam.ui.drawing import rounded_rect


class HomePage(BasePage):
    def __init__(self, app):
        super().__init__(app)
        self._controls = [
            Button("take_picture", "Take Picture", (42, 155, 345, 82), "Capture a new photo"),
            Button("voice_to_image", "Voice to Image", (413, 155, 345, 82), "Create an image using your voice"),
            Button("library", "Library", (42, 260, 345, 82), "View saved images"),
            Button("settings", "Settings", (413, 260, 345, 82), "Configure TomCam"),
        ]

    @property
    def controls(self):
        return self._controls

    def activate(self, key):
        if key == "take_picture":
            self.app.navigation.show_take_picture()
        else:
            self.app.status_message = f"{key.replace('_', ' ').title()} is not implemented yet."

    def draw(self, app):
        draw_header(app, "What would you like to do?",
                    "Choose an option using touch or the rotary encoder")
        for index, button in enumerate(self.controls):
            button.draw(app, selected=index == self.focus_index)
        rounded_rect(app.renderer, 42, 390, 716, 48, 14, theme.SURFACE)
        app.render_text("Rotate to navigate   •   Press to select",
                        62, 403, theme.MUTED, 18)
        if app.status_message:
            app.render_text(app.status_message, 430, 403, theme.SUCCESS, 18)


