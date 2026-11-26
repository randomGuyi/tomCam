from tomcam.config import theme
from tomcam.ui.drawing import rounded_rect


class TouchKeyboard:
    def __init__(self):
        self.value = ""
        self.shift = False
        self.numeric = False
        self.visible = False

        self.x = 24
        self.y = 205
        self.width = 752
        self.key_height = 48
        self.gap = 5

    def open(self):
        self.value = ""
        self.shift = False
        self.numeric = False
        self.visible = True

    def close(self):
        self.visible = False

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value

    def _rows(self):
        if self.numeric:
            return [
                list("1234567890"),
                list("@#$%&*-+()"),
                ["_", ".", ",", "?", "!", "'", "⌫"],
                ["ABC", "SPACE", "CLEAR"],
            ]

        rows = [
            list("qwertyuiop"),
            list("asdfghjkl"),
            list("zxcvbnm") + ["⌫"],
            ["123", "SPACE", "CLEAR"],
        ]

        if self.shift:
            rows = [
                [key.upper() for key in row]
                for row in rows
            ]

        return rows

    def _key_rectangles(self):
        rows = self._rows()
        result = []

        for row_index, row in enumerate(rows):
            count = len(row)
            key_width = (
                self.width - (count - 1) * self.gap
            ) / count

            row_width = (
                count * key_width
                + (count - 1) * self.gap
            )

            start_x = self.x + (
                self.width - row_width
            ) / 2

            y = self.y + row_index * (
                self.key_height + self.gap
            )

            for index, key in enumerate(row):
                x = start_x + index * (
                    key_width + self.gap
                )

                result.append((
                    key,
                    int(x),
                    int(y),
                    int(key_width),
                    self.key_height,
                ))

        return result

    def draw(self, app):
        if not self.visible:
            return

        for key, x, y, width, height in self._key_rectangles():
            special = key in {
                "⌫", "SPACE", "CLEAR", "123", "ABC"
            }

            color = (
                theme.SURFACE_RAISED
                if not special
                else theme.SURFACE
            )

            rounded_rect(
                app.renderer,
                x, y, width, height,
                8,
                color,
            )

            label = " " if key == "SPACE" else key

            app.render_text(
                label,
                x + width // 2 - len(label) * 4,
                y + 14,
                theme.TEXT,
                16,
            )

    def handle_touch(self, touch_x, touch_y):
        """Returns True if the touch was handled."""
        if not self.visible:
            return False

        for key, x, y, width, height in self._key_rectangles():
            if (
                x <= touch_x <= x + width
                and y <= touch_y <= y + height
            ):
                self._activate_key(key)
                return True

        return False

    def _activate_key(self, key):
        if key == "⌫":
            self.value = self.value[:-1]

        elif key == "SPACE":
            self.value += " "

        elif key == "CLEAR":
            self.value = ""

        elif key == "123":
            self.numeric = True

        elif key == "ABC":
            self.numeric = False

        elif len(key) == 1:
            self.value += key

            if self.shift and not self.numeric:
                self.shift = False

