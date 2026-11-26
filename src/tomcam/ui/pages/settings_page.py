from tomcam.config import theme
from tomcam.ui.components.button import Button
from tomcam.ui.components.header import draw_header
from tomcam.ui.pages.base_page import BasePage


class SettingsPage(BasePage):
    def __init__(self, app):
        super().__init__(app)
        self._controls = [
            Button(
                "wifi",
                "Wi-Fi & Networks",
                (42, 155, 716, 82),
                "Connect to and manage wireless networks",
            ),
            Button("back", "Return to Home", (42, 260, 716, 82)),
        ]

    @property
    def controls(self):
        return self._controls

    def activate(self, key):
        if key == "wifi":
            self.app.navigation.show_wifi()
        elif key == "back":
            self.app.navigation.show_home()

    def go_back(self):
        self.app.navigation.show_home()

    def draw(self, app):
        draw_header(app, "Settings", "Configure TomCam")
        for index, button in enumerate(self.controls):
            button.draw(app, selected=index == self.focus_index)
        app.render_text(
            "Network profiles are saved for automatic reconnection.",
            44,
            382,
            theme.MUTED,
            18,
        )
