from tomcam.config import theme
from tomcam.ui.pages.base_page import BasePage
from tomcam.ui.components.button import Button
from tomcam.ui.components.header import draw_header
from tomcam.ui.drawing import rounded_rect
from tomcam.media.camera import Camera

import ctypes
import cv2
import sdl2


class TakePicturePage(BasePage):
    def __init__(self, app):
        super().__init__(app)

        self.CAMERA_WIDTH = 640 
        self.CAMERA_HEIGHT = 450
        self.CAMERA_FPS = 15

        self.PREVIEW_BORDER_WIDTH = 16

        self.status = "Camera preview will appear here"
        self.camera = Camera(
            device="/dev/video0",
            width=self.CAMERA_WIDTH,
            height=self.CAMERA_HEIGHT,
            fps= self.CAMERA_FPS
        )
        self.camera_texture = None
        self.camera_texture_size = None
        if not self.camera.is_running():
            self.camera.start()

        self._controls = [
            Button("back", "Return", (
                42 + self.PREVIEW_BORDER_WIDTH, 
                365, 
                190, 
                70)
            ),
            Button("shoot", "Shoot Picture", (
                540, 
                365, 
                218 - self.PREVIEW_BORDER_WIDTH,
                70)),
        ]

    @property
    def controls(self):
        return self._controls

    def on_shoot_picture(self):
        return self.camera.capture_image("data/images/capture.jpg")

    def activate(self, key):
        if key == "back":
            self.app.navigation.show_home()
        elif key == "shoot":
            self.status = "Capture requested — camera integration comes next."

    def go_back(self):
        self.camera.stop()

        if self.camera_texture is not None:
            sdl2.SDL_DestroyTexture(self.camera_texture)
            self.camera_texture = None
            self.camera_texture_size = None

        self.app.navigation.show_home()

    def draw_camera_preview(self, app):
        frame = self.camera.get_frame()

        if frame is None:
            app.render_text(
                "Waiting for camera...",
                270, 220,
                theme.MUTED,
                18,
            )
            return
    
        height, width, _ = frame.shape
    
        # Convert OpenCV BGR to RGB for SDL2.
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = rgb.copy()
    
        # Create the texture once, or recreate it if the frame size changes.
        if self.camera_texture_size != (width, height):
            if self.camera_texture is not None:
                sdl2.SDL_DestroyTexture(self.camera_texture)
    
            self.camera_texture = sdl2.SDL_CreateTexture(
                app.renderer,
                sdl2.SDL_PIXELFORMAT_RGB24,
                sdl2.SDL_TEXTUREACCESS_STREAMING,
                width,
                height,
            )
    
            if not self.camera_texture:
                self.camera_texture_size = None
                raise RuntimeError("Could not create camera texture")
    
            self.camera_texture_size = (width, height)
    
        # Update the texture with the newest camera frame.
        pixels = rgb.ctypes.data_as(
            ctypes.POINTER(ctypes.c_uint8)
        )
    
        result = sdl2.SDL_UpdateTexture(
            self.camera_texture,
            None,
            pixels,
            width * 3,
        )
    
        if result != 0:
            raise RuntimeError("Could not update camera texture")
    
        # Render the image inside the preview rectangle.
        destination = sdl2.SDL_Rect(
            54,
            117,
            682,
            340,
        )
    
        sdl2.SDL_RenderCopy(
            app.renderer,
            self.camera_texture,
            None,
            ctypes.byref(destination),
        )

    def draw(self, app):
        draw_header(
            app,
            "Take Picture"
        )
   
        # light gray
        rounded_rect(
            app.renderer,
            42,
            105,
            704, 
            362,
            22,
            theme.SURFACE,
        )
   
        # Live webcam preview
        self.draw_camera_preview(app)
    
        for index, button in enumerate(self.controls):
            button.draw(
                app,
                selected=index == self.focus_index,
                compact=True,
            )

