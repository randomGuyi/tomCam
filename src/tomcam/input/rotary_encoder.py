from gpiozero import RotaryEncoder, Button


class RotaryInput:
    """GPIO callbacks only enqueue actions; SDL stays on the main thread."""

    def __init__(self, input_manager, pin_a, pin_b, button_pin):
        self.input_manager = input_manager
        self.encoder = RotaryEncoder(pin_a, pin_b, max_steps=0)
        self.button = Button(button_pin, bounce_time=0.08)
        self.encoder.when_rotated_clockwise = lambda: self.input_manager.post(
            self.input_manager.ROTATE_NEXT
        )
        self.encoder.when_rotated_anticlockwise = lambda: self.input_manager.post(
            self.input_manager.ROTATE_PREVIOUS
        )
        self.button.when_pressed = lambda: self.input_manager.post(
            self.input_manager.CONFIRM
        )

    def close(self):
        self.encoder.close()
        self.button.close()


