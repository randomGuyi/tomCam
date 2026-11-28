from pathlib import Path
import threading
import time

import cv2


class Camera:
    def __init__(
        self,
        device: str = "/dev/video0",
        width: int = 640,
        height: int = 480,
        fps: int = 15,
    ):
        self.device = device
        self.width = width
        self.height = height
        self.fps = fps

        self._capture = None
        self._thread = None
        self._running = False
        self._lock = threading.Lock()
        self._latest_frame = None

    def start(self) -> None:
        if self._running:
            return

        self._capture = cv2.VideoCapture(
            self.device,
            cv2.CAP_V4L2,
        )

        if not self._capture.isOpened():
            self._capture.release()
            self._capture = None
            raise RuntimeError(
                f"Could not open camera: {self.device}"
            )

        self._capture.set(
            cv2.CAP_PROP_FRAME_WIDTH, self.width
        )
        self._capture.set(
            cv2.CAP_PROP_FRAME_HEIGHT, self.height
        )
        self._capture.set(
            cv2.CAP_PROP_FPS, self.fps
        )

        self._running = True
        self._thread = threading.Thread(
            target=self._capture_loop,
            daemon=True,
        )
        self._thread.start()

    def _capture_loop(self) -> None:
        while self._running:
            success, frame = self._capture.read()

            if success:
                with self._lock:
                    self._latest_frame = frame
            else:
                time.sleep(0.05)

    def get_frame(self):
        # Return the most recent frame in OpenCV BGR format.
        with self._lock:
            if self._latest_frame is None:
                return None

            return self._latest_frame.copy()


    def stop(self) -> None:
        self._running = False

        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None

        if self._capture is not None:
            self._capture.release()
            self._capture = None

        with self._lock:
            self._latest_frame = None

    def is_running(self) -> bool:
        return self._running

