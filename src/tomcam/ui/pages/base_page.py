from tomcam.input.input_manager import InputManager
from tomcam.config import theme


class BasePage:
    def __init__(self, app):
        self.app = app
        self.focus_index = 0
        self.active_finger = None

    @property
    def controls(self):
        return []

    def on_show(self):
        self.focus_index = min(self.focus_index, max(0, len(self.controls) - 1))

    def on_hide(self):
        pass

    def handle_action(self, action):
        count = len(self.controls)
        if not count:
            return
        if action == InputManager.ROTATE_NEXT:
            self.focus_index = (self.focus_index + 1) % count
        elif action == InputManager.ROTATE_PREVIOUS:
            self.focus_index = (self.focus_index - 1) % count
        elif action == InputManager.CONFIRM:
            self.activate(self.controls[self.focus_index].key)
        elif action == InputManager.BACK:
            self.go_back()

    def activate(self, key):
        pass

    def go_back(self):
        pass

    def handle_touch(self, event):
        finger_id = event.tfinger.fingerId
        x = int(event.tfinger.x * theme.WIDTH)
        y = int(event.tfinger.y * theme.HEIGHT)

        if event.type == 1792:  # SDL_FINGERDOWN
            self.active_finger = finger_id
            for index, control in enumerate(self.controls):
                if control.contains(x, y):
                    self.focus_index = index
                    self.activate(control.key)
                    break
        elif event.type == 1794:  # SDL_FINGERUP
            if self.active_finger == finger_id:
                self.active_finger = None


