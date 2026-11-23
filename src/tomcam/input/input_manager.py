from queue import SimpleQueue, Empty


class InputManager:
    ROTATE_NEXT = "rotate_next"
    ROTATE_PREVIOUS = "rotate_previous"
    CONFIRM = "confirm"
    BACK = "back"

    def __init__(self):
        self._events = SimpleQueue()

    def post(self, event):
        self._events.put(event)

    def drain(self):
        result = []
        while True:
            try:
                result.append(self._events.get_nowait())
            except Empty:
                return result


