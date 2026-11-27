from pathlib import Path
import signal
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
        self._recording_error = None

    def start_recording(self, destination: str) -> None:
        if self.is_recording():
            raise RuntimeError("Recording is already running")

        self.recording_error()

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
        self._recording_error = None

    def stop_recording(self) -> Path:
        if self._process is None:
            raise RuntimeError("No recording is running")

        process = self._process
        if process.poll() is None:
            process.send_signal(signal.SIGINT)
        try:
            _, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                _, stderr = process.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                _, stderr = process.communicate()

        path = self._output_path
        self._process = None
        self._output_path = None

        stopped_by_interrupt = (
            process.returncode == -signal.SIGINT
            or (
                process.returncode == 1
                and b"Aborted by signal Interrupt" in stderr
            )
        )
        if process.returncode != 0 and not stopped_by_interrupt:
            message = stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(
                message or f"arecord exited with status {process.returncode}"
            )
        if path is None or not path.exists():
            raise RuntimeError("Recording file was not created")

        return path

    def recording_error(self):
        if self._process is None or self._process.poll() is None:
            return self._recording_error

        process = self._process
        _, stderr = process.communicate()
        self._process = None
        self._output_path = None

        if process.returncode:
            message = stderr.decode("utf-8", errors="replace").strip()
            self._recording_error = (
                message or f"arecord exited with status {process.returncode}"
            )

        return self._recording_error

    def is_recording(self) -> bool:
        return (
            self._process is not None
            and self._process.poll() is None
        )

