import math
import os
import textwrap
import time
from concurrent.futures import ThreadPoolExecutor

import sdl2
import speech_recognition as sr

from tomcam.config import theme
from tomcam.ui.pages.base_page import BasePage
from tomcam.ui.components.button import Button
from tomcam.ui.components.header import draw_header
from tomcam.ui.drawing import rounded_rect
from tomcam.media.microphone import Microphone


TRANSCRIPTION_EXECUTOR = ThreadPoolExecutor(max_workers=1)


class VoiceToImagePage(BasePage):
    def __init__(self, app):
        super().__init__(app)

        self.microphone = Microphone(
            device=os.environ.get("TOMCAM_AUDIO_DEVICE", "plughw:1,0")
        )

        self.status = "Press to start recording"
        self.audio_path = None
        self.transcript = None
        self._transcription_future = None
        self.start_time = None

        self._controls = [
            Button("back", "Return", (42, 365, 190, 70)),
            Button("record", "Start Recording", (270, 365, 260, 70)),
            Button("generate", "Generate Image", (550, 365, 208, 70)),
        ]

    @property
    def controls(self):
        return self._controls

    def is_recording(self):
        return self.microphone.is_recording()

    def activate(self, key):
        if key == "back":
            self.stop_recording()
            self.app.navigation.show_home()

        elif key == "record":
            if self.is_recording():
                self.stop_recording()
            elif (
                self._transcription_future is not None
                and not self._transcription_future.done()
            ):
                self.status = "Wait for transcription to finish"
            else:
                self.start_recording()

        elif key == "generate":
            if self.audio_path is not None:
                self.status = "Image generation is not configured yet"
            elif self.is_recording():
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

            self.start_time = time.monotonic()
            self.audio_path = None
            self.transcript = None
            self._transcription_future = None
            self.status = "Listening..."

            self._controls[1].label = "Stop Recording"

        except Exception as exc:
            self.status = f"Microphone error: {exc}"

    def stop_recording(self):
        if not self.is_recording():
            return

        try:
            self.audio_path = self.microphone.stop_recording()
            self.status = "Transcribing audio..."
            self._transcription_future = TRANSCRIPTION_EXECUTOR.submit(
                self.transcribe_audio, self.audio_path
            )

        except Exception as exc:
            self.status = f"Recording error: {exc}"

        finally:
            self.start_time = None
            self._controls[1].label = "Start Recording"

    @staticmethod
    def transcribe_audio(audio_path):
        recognizer = sr.Recognizer()
        recognizer.operation_timeout = 15
        with sr.AudioFile(str(audio_path)) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)

    def update_transcription(self):
        future = self._transcription_future
        if future is None or not future.done():
            return

        self._transcription_future = None
        try:
            self.transcript = future.result()
            self.status = "Recording completed"
        except sr.UnknownValueError:
            self.status = "Could not understand the recording"
        except sr.RequestError as exc:
            self.status = f"Speech service error: {exc}"
        except Exception as exc:
            self.status = f"Transcription error: {exc}"

    def draw_visualizer(self, app):
        center_x = 400
        center_y = 235

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

    def draw(self, app):
        draw_header(app, "Voice to Image")
        self.update_transcription()

        recording = self.is_recording()
        if not recording and self.start_time is not None:
            self.start_time = None
            self._controls[1].label = "Start Recording"
            error = self.microphone.recording_error()
            self.status = (
                f"Microphone error: {error}"
                if error
                else "Recording stopped unexpectedly"
            )

        self.draw_visualizer(app)

        if not recording and self.status.startswith(
            ("Recording error:", "Microphone error:")
        ):
            status_lines = textwrap.wrap(
                self.status, width=68, max_lines=4, placeholder="..."
            )
            status_y = 275
        else:
            status_lines = textwrap.wrap(
                self.status, width=68, max_lines=2, placeholder="..."
            )
            status_y = 315

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
