from pathlib import Path
import subprocess


class Microphone:
    def __init__(
        self,
        device: str = "plughw:1,0",
        sample_rate: int = 16000,
        channels: int = 1,
    ):
        self.device = device
        self.sample_rate = sample_rate
        self.channels = channels
        self._process = None
        self._output_path = None

    def start_recording(self, destination: str) -> None:
        if self.is_recording():
            raise RuntimeError("Recording is already running")

        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)

        command = [
            "arecord",
            "-D", self.device,
            "-f", "S16_LE",
            "-r", str(self.sample_rate),
            "-c", str(self.channels),
            "-t", "wav",
            str(path),
        ]

        self._process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

        self._output_path = path

    def stop_recording(self) -> Path:
        if not self.is_recording():
            raise RuntimeError("No recording is running")

        self._process.terminate()

        try:
            self._process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait()

        path = self._output_path
        self._process = None
        self._output_path = None

        if path is None or not path.exists():
            raise RuntimeError("Recording file was not created")

        return path

    def is_recording(self) -> bool:
        return (
            self._process is not None
            and self._process.poll() is None
        )

