from dataclasses import dataclass
from tomcam.config import theme
from tomcam.ui.drawing import rounded_rect


@dataclass
class Button:
    key: str
    label: str
    rect: tuple
    description: str = ""

    def contains(self, x, y):
        rx, ry, rw, rh = self.rect
        return rx <= x <= rx + rw and ry <= y <= ry + rh

    def draw(self, app, selected=False, compact=False):
        x, y, w, h = self.rect
        if selected:
            rounded_rect(app.renderer, x - 3, y - 3, w + 6, h + 6, 20, theme.ACCENT)
            rounded_rect(app.renderer, x, y, w, h, 17, theme.SURFACE_RAISED)
        else:
            rounded_rect(app.renderer, x, y, w, h, 17, theme.SURFACE)

        if compact:
            app.render_text(self.label, x + 22, y + (h - 26) // 2, theme.TEXT, 22)
        else:
            app.render_text(self.label, x + 22, y + 17, theme.TEXT, 26)
            if self.description:
                app.render_text(self.description, x + 22, y + 53, theme.MUTED, 18)


