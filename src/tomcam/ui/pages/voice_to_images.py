import textwrap

from tomcam.config import theme
from tomcam.ui.pages.base_page import BasePage
from tomcam.ui.components.button import Button
from tomcam.ui.components.header import draw_header




class VoiceToImagePage(BasePage):
    def __init__(self, app):
        super().__init__(app)


        self.status = "Press to start recording"

        self._controls = [
            Button("back", "Return", (42, 365, 190, 70)),
            Button("record", "Start Recording", (270, 365, 260, 70)),
            Button("generate", "Generate Image", (550, 365, 208, 70)),
        ]

    @property
    def controls(self):
        return self._controls


    def activate(self, key):
        if key == "back":
            self.app.navigation.show_home()

        elif key == "record":
            self.status = "Mic-Service has to be implemented"

        elif key == "generate":
            self.status = "Generate Image has to be implemented"

    def go_back(self):
        self.app.navigation.show_home()

    def on_hide(self):
        pass

    def draw(self, app):
        draw_header(app, "Voice to Image")



        status_lines = textwrap.wrap(
            self.status, width=68, max_lines=4, placeholder="..."
        )
        status_y = 275

        for index, line in enumerate(status_lines):
            app.render_text(
                line,
                40, status_y + index * 20,
                theme.MUTED,
                18,
            )

        for index, button in enumerate(self.controls):
            button.draw(
                app,
                selected=index == self.focus_index,
                compact=True,
            )

"""
    def draw_visualizer(self, app):
        center_x = 400
        center_y = 235

        ### TODO: Ask Mic-Service if it's buzzy recording
        if self.is_recording():
            elapsed = time.monotonic() - self.start_time

            # Animated concentric circles.
            for i in range(4):
                radius = 55 + i * 15 + abs(
                    math.sin(elapsed * 2 + i) * 10
                )

                color = (
                    90,
                    130 + i * 20,
                    240,
                    255,
                )

                sdl2.SDL_SetRenderDrawColor(
                    app.renderer, *color
                )

                sdl2.SDL_RenderDrawLine(
                    app.renderer,
                    center_x - int(radius),
                    center_y,
                    center_x + int(radius),
                    center_y,
                )

            app.render_text(
                "LISTENING",
                350, 310,
                theme.MUTED,
                18,
            )

        else:
            if self.transcript:
                app.render_text(
                    "IMAGE REQUEST",
                    60, 180,
                    theme.TEXT,
                    18,
                )
                lines = textwrap.wrap(
                    self.transcript, width=72, max_lines=4,
                    placeholder="...",
                )
                for index, line in enumerate(lines):
                    app.render_text(
                        line,
                        60, 210 + index * 24,
                        theme.TEXT,
                        18,
                    )
            else:
                rounded_rect(
                    app.renderer,
                    center_x - 40,
                    center_y - 40,
                    80,
                    80,
                    40,
                    theme.SURFACE_RAISED,
                )

                app.render_text(
                    "MIC",
                    center_x - 17,
                    center_y - 10,
                    theme.MUTED,
                    18,
                )
"""


