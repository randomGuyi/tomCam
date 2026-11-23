import os
import sys
import sdl2
import sdl2.sdlttf as ttf

from tomcam.config import theme
from tomcam.input.input_manager import InputManager
from tomcam.input.rotary_encoder import RotaryInput
from tomcam.app.navigation import Navigation


class Application:
    def __init__(self):
        os.environ.setdefault(
            "SDL_VIDEODRIVER",
            os.environ.get("TOMCAM_VIDEO_DRIVER", theme.DEFAULT_VIDEO_DRIVER)
        )

        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_EVENTS) != 0:
            raise RuntimeError(self.sdl_error())

        if ttf.TTF_Init() != 0:
            sdl2.SDL_Quit()
            raise RuntimeError("SDL_ttf initialization failed")

        self.window = sdl2.SDL_CreateWindow(
            b"TomCam",
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            theme.WIDTH, theme.HEIGHT,
            sdl2.SDL_WINDOW_FULLSCREEN
        )
        if not self.window:
            self.shutdown_sdl()
            raise RuntimeError(self.sdl_error())

        # Software rendering is a conservative compatibility choice for Pi 3.
        self.renderer = sdl2.SDL_CreateRenderer(
            self.window, -1, sdl2.SDL_RENDERER_SOFTWARE
        )
        if not self.renderer:
            self.shutdown_sdl()
            raise RuntimeError(self.sdl_error())

        sdl2.SDL_ShowCursor(sdl2.SDL_DISABLE)
        sdl2.SDL_SetHint(sdl2.SDL_HINT_TOUCH_MOUSE_EVENTS, b"0")
        sdl2.SDL_SetHint(sdl2.SDL_HINT_MOUSE_TOUCH_EVENTS, b"0")

        self.fonts = {}
        self.load_fonts()
        self.input_manager = InputManager()
        self.rotary = None
        if theme.ENABLE_ROTARY_ENCODER:
            try:
                self.rotary = RotaryInput(
                    self.input_manager, theme.ENCODER_PIN_A,
                    theme.ENCODER_PIN_B, theme.ENCODER_BUTTON_PIN
                )
            except Exception as exc:
                print(f"Rotary encoder unavailable: {exc}", file=sys.stderr)

        self.status_message = ""
        self.navigation = Navigation(self)
        self.running = True

    @staticmethod
    def sdl_error():
        error = sdl2.SDL_GetError()
        return error.decode("utf-8", errors="replace") if error else "Unknown SDL error"

    def load_fonts(self):
        path = next((p for p in theme.FONT_PATHS if os.path.exists(p)), None)
        if not path:
            raise RuntimeError("No font found; install fonts-dejavu-core")
        for size in (18, 22, 26, 40):
            font = ttf.TTF_OpenFont(path.encode(), size)
            if not font:
                raise RuntimeError(self.sdl_error())
            self.fonts[size] = font

    def render_text(self, text, x, y, color=theme.TEXT, size=22):
        surface = ttf.TTF_RenderUTF8_Blended(
            self.fonts[size], text.encode("utf-8"), sdl2.SDL_Color(*color)
        )
        if not surface:
            return
        texture = sdl2.SDL_CreateTextureFromSurface(self.renderer, surface)
        if texture:
            rect = sdl2.SDL_Rect(x, y, surface.contents.w, surface.contents.h)
            sdl2.SDL_RenderCopy(self.renderer, texture, None, rect)
            sdl2.SDL_DestroyTexture(texture)
        sdl2.SDL_FreeSurface(surface)

    def run(self):
        event = sdl2.SDL_Event()
        try:
            while self.running:
                for action in self.input_manager.drain():
                    self.navigation.current_page.handle_action(action)

                while sdl2.SDL_PollEvent(event):
                    if event.type == sdl2.SDL_QUIT:
                        self.running = False
                    elif event.type == sdl2.SDL_KEYDOWN:
                        key = event.key.keysym.sym
                        if key == sdl2.SDLK_ESCAPE:
                            self.navigation.current_page.handle_action(InputManager.BACK)
                        elif key in (sdl2.SDLK_DOWN, sdl2.SDLK_RIGHT):
                            self.navigation.current_page.handle_action(InputManager.ROTATE_NEXT)
                        elif key in (sdl2.SDLK_UP, sdl2.SDLK_LEFT):
                            self.navigation.current_page.handle_action(InputManager.ROTATE_PREVIOUS)
                        elif key in (sdl2.SDLK_RETURN, sdl2.SDLK_SPACE):
                            self.navigation.current_page.handle_action(InputManager.CONFIRM)
                    elif event.type in (
                        sdl2.SDL_FINGERDOWN, sdl2.SDL_FINGERMOTION, sdl2.SDL_FINGERUP
                    ):
                        self.navigation.current_page.handle_touch(event)
                    # Mouse events are deliberately ignored.

                sdl2.SDL_SetRenderDrawColor(self.renderer, *theme.BACKGROUND)
                sdl2.SDL_RenderClear(self.renderer)
                self.navigation.current_page.draw(self)
                sdl2.SDL_RenderPresent(self.renderer)
                sdl2.SDL_Delay(1000 // theme.FPS)
        finally:
            self.close()

    def close(self):
        if self.rotary:
            self.rotary.close()
            self.rotary = None
        self.shutdown_sdl()

    def shutdown_sdl(self):
        if getattr(self, "renderer", None):
            sdl2.SDL_DestroyRenderer(self.renderer)
            self.renderer = None
        if getattr(self, "window", None):
            sdl2.SDL_DestroyWindow(self.window)
            self.window = None
        for font in getattr(self, "fonts", {}).values():
            ttf.TTF_CloseFont(font)
        self.fonts = {}
        ttf.TTF_Quit()
        sdl2.SDL_Quit()


