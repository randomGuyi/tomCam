import ctypes
from datetime import datetime
from pathlib import Path
import queue
import textwrap
import threading

import cv2
import sdl2

from tomcam.config import theme
from tomcam.media.microphone import Microphone
from tomcam.services.image_generator import ImageGenerator
from tomcam.services.speech_to_text import SpeechToText
from tomcam.ui.components.button import Button
from tomcam.ui.components.header import draw_header
from tomcam.ui.drawing import rounded_rect
from tomcam.ui.pages.base_page import BasePage


class VoiceToImagePage(BasePage):
    def __init__(self, app):
        super().__init__(app)
        project_root = Path(__file__).resolve().parents[4]
        self.audio_directory = project_root / "data" / "audio"
        self.images_directory = project_root / "data" / "images"
        self.microphone = Microphone()
        self.transcriber = SpeechToText()
        self.status = "Press Start Recording and describe an image"
        self.transcript = ""
        self.image_path = None
        self.image_texture = None
        self.image_texture_size = None
        self._image_texture_path = None
        self._operation = None
        self._results = queue.Queue()
        self._worker = None
        self._controls = [
            Button("back", "Return", (42, 378, 190, 64)),
            Button("record", "Start Recording", (264, 378, 260, 64)),
            Button("generate", "Generate Image", (556, 378, 202, 64)),
        ]

    @property
    def controls(self):
        return self._controls

    def activate(self, key):
        if key == "back":
            self.app.navigation.show_home()
        elif key == "record":
            self.toggle_recording()
        elif key == "generate":
            self.generate_image()

    def go_back(self):
        self.app.navigation.show_home()

    def on_hide(self):
        if self.microphone.is_recording():
            try:
                self.microphone.stop_recording()
            except (OSError, RuntimeError) as exc:
                self.app.status_message = f"Could not stop recording: {exc}"
        self.destroy_image_texture()

    def toggle_recording(self):
        if self._operation:
            return
        if self.microphone.is_recording():
            try:
                audio_path = self.microphone.stop_recording()
            except (OSError, RuntimeError) as exc:
                self._controls[1].label = "Start Recording"
                self.status = f"Could not stop recording: {exc}"
                return
            self._start_worker(
                "transcription",
                lambda: self.transcriber.transcribe(audio_path),
                "Transcribing recording...",
            )
            self._controls[1].label = "Transcribing..."
            return

        self.transcript = ""
        self.image_path = None
        self.destroy_image_texture()
        try:
            self.audio_path = self.audio_directory / (
                f"voice_{datetime.now():%Y%m%d_%H%M%S_%f}.wav"
            )
            self.microphone.start_recording(str(self.audio_path))
        except (OSError, RuntimeError) as exc:
            self.status = f"Could not start recording: {exc}"
            return

        self._controls[1].label = "Stop Recording"
        self.status = "Recording... Press Stop Recording when finished."

    def generate_image(self):
        if self._operation:
            return
        if self.microphone.is_recording():
            self.status = "Stop recording before generating an image."
            return
        if not self.transcript:
            self.status = "Record a description before generating an image."
            return

        self._start_worker(
            "generation",
            self._generate_image,
            "Generating image... This may take a few minutes.",
        )
        self._controls[2].label = "Generating..."

    def _generate_image(self):
        generator = ImageGenerator()
        filename = f"voice_{datetime.now():%Y%m%d_%H%M%S_%f}.jpg"
        destination = self.images_directory / filename
        return generator.generate_to_file(self.transcript, str(destination))

    def _start_worker(self, operation, function, status):
        self._operation = operation
        self.status = status

        def run():
            try:
                result = function()
            except Exception as exc:
                self._results.put((operation, None, exc))
            else:
                self._results.put((operation, result, None))

        self._worker = threading.Thread(target=run, daemon=True)
        self._worker.start()

    def _update_operation(self):
        while True:
            try:
                operation, result, error = self._results.get_nowait()
            except queue.Empty:
                break

            self._operation = None
            self._worker = None
            if operation == "transcription":
                self._controls[1].label = "Start Recording"
                if error:
                    self.status = f"Transcription failed: {error}"
                else:
                    self.transcript = result
                    self.status = "Description captured. Select Generate Image."
            else:
                self._controls[2].label = "Generate Image"
                if error:
                    self.status = f"Image generation failed: {error}"
                else:
                    self.image_path = Path(result)
                    self.status = "Image generated."

        if not self._operation and not self.microphone.is_recording():
            recording_error = self.microphone.recording_error()
            if recording_error:
                self._controls[1].label = "Start Recording"
                self.status = f"Recording failed: {recording_error}"

    def destroy_image_texture(self):
        if self.image_texture is not None:
            sdl2.SDL_DestroyTexture(self.image_texture)
            self.image_texture = None
            self.image_texture_size = None
            self._image_texture_path = None

    def draw_image_preview(self, app):
        image_path = str(self.image_path)
        if self._image_texture_path != image_path:
            image = cv2.imread(image_path)
            if image is None:
                raise RuntimeError(f"Could not load generated image: {image_path}")
            height, width, _ = image.shape
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).copy()
            self.destroy_image_texture()
            self.image_texture = sdl2.SDL_CreateTexture(
                app.renderer,
                sdl2.SDL_PIXELFORMAT_RGB24,
                sdl2.SDL_TEXTUREACCESS_STATIC,
                width,
                height,
            )
            if not self.image_texture:
                raise RuntimeError("Could not create image preview texture")
            pixels = rgb_image.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
            if sdl2.SDL_UpdateTexture(
                self.image_texture, None, pixels, width * 3
            ) != 0:
                self.destroy_image_texture()
                raise RuntimeError("Could not update image preview texture")
            self.image_texture_size = (width, height)
            self._image_texture_path = image_path

        width, height = self.image_texture_size
        scale = min(680 / width, 204 / height)
        preview_width = int(width * scale)
        preview_height = int(height * scale)
        destination = sdl2.SDL_Rect(
            400 - preview_width // 2,
            226 - preview_height // 2,
            preview_width,
            preview_height,
        )
        sdl2.SDL_RenderCopy(
            app.renderer,
            self.image_texture,
            None,
            ctypes.byref(destination),
        )

    def draw(self, app):
        self._update_operation()
        draw_header(app, "Voice to Image")
        rounded_rect(app.renderer, 42, 108, 716, 250, 18, theme.SURFACE)

        if self.image_path:
            self.draw_image_preview(app)
            app.render_text(
                textwrap.shorten(self.transcript, width=78, placeholder="..."),
                48,
                341,
                theme.MUTED,
                18,
            )
        else:
            status_lines = textwrap.wrap(
                self.status, width=70, max_lines=2, placeholder="..."
            )
            for index, line in enumerate(status_lines):
                app.render_text(
                    line,
                    60,
                    126 + index * 22,
                    theme.MUTED,
                    18,
                )
            if self.transcript:
                app.render_text("DESCRIPTION", 60, 174, theme.ACCENT, 18)
                lines = textwrap.wrap(
                    self.transcript, width=68, max_lines=7, placeholder="..."
                )
                for index, line in enumerate(lines):
                    app.render_text(
                        line,
                        60,
                        200 + index * 22,
                        theme.TEXT,
                        18,
                    )

        for index, button in enumerate(self.controls):
            button.draw(
                app,
                selected=index == self.focus_index,
                compact=True,
            )
