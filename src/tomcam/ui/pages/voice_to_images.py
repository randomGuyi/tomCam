import math
import time

import sdl2

from tomcam.config import theme
from tomcam.ui.pages.base_page import BasePage
from tomcam.ui.components.button import Button
from tomcam.ui.components.header import draw_header
from tomcam.ui.drawing import rounded_rect
from tomcam.media.microphone import Microphone


class VoiceToImagePage(BasePage):
    def __init__(self, app):
        super().__init__(app)

        self.microphone = Microphone(
            device="plughw:1,0"
        )

        self.status = "Press to start recording"
        self.recording = False
        self.audio_path = None
        self.start_time = None

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
            self.stop_recording()
            self.app.navigation.show_home()

        elif key == "record":
            if self.recording:
                self.stop_recording()
            else:
                self.start_recording()

        elif key == "generate":
            if self.audio_path is not None:
                self.status = "Image generation is not configured yet"
            elif self.recording:
                self.status = "Stop recording before generating"
            else:
                self.status = "Record audio before generating an image"

    def go_back(self):
        self.stop_recording()
        self.app.navigation.show_home()

    def on_hide(self):
        self.stop_recording()

    def start_recording(self):
        try:
            self.microphone.start_recording(
                "data/audio/voice_input.wav"
            )

            self.recording = True
            self.start_time = time.monotonic()
            self.audio_path = None
            self.status = "Listening..."

            self._controls[1].label = "Stop Recording"

        except Exception as exc:
            self.status = f"Microphone error: {exc}"

    def stop_recording(self):
        if not self.recording:
            return

        try:
            self.audio_path = self.microphone.stop_recording()
            self.status = "Recording completed"

        except Exception as exc:
            self.status = f"Recording error: {exc}"

        finally:
            self.recording = False
            self.start_time = None
            self._controls[1].label = "Start Recording"

    def draw_visualizer(self, app):
        center_x = 400
        center_y = 235

        if self.recording:
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

    def draw(self, app):
        draw_header(app, "Voice to Image")

        self.draw_visualizer(app)

        app.render_text(
            self.status,
            240, 325,
            theme.MUTED,
            18,
        )

        for index, button in enumerate(self.controls):
            button.draw(
                app,
                selected=index == self.focus_index,
                compact=True,
            )
