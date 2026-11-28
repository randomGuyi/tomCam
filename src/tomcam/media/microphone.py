from pathlib import Path
import os
import signal
import shutil
import subprocess
import sys


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
        self._stop_requested = False
        self._process = None
        self._output_path = None
        self._recording_error = None

    def start_recording(self, destination: str) -> None:
        if self.is_recording():
            raise RuntimeError("Recording is already running")

        self.recording_error()

        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)

        if sys.platform == "darwin":
            executable = shutil.which("ffmpeg")
            if not executable:
                raise RuntimeError(
                    "ffmpeg is required for Mac microphone recording. "
                    "Install it with `brew install ffmpeg`."
                )
            command = [
                executable,
                "-hide_banner",
                "-loglevel", "error",
                "-nostdin",
                "-y",
                "-f", "avfoundation",
                "-i", os.getenv("TOMCAM_AUDIO_DEVICE", ":0"),
                "-ac", str(self.channels),
                "-ar", str(self.sample_rate),
                "-c:a", "pcm_s16le",
                str(path),
            ]
        else:
            command = [
                "arecord",
                "-D", os.getenv("TOMCAM_AUDIO_DEVICE", self.device),
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
        self._stop_requested = False

    def stop_recording(self) -> Path:
        if self._process is None:
            raise RuntimeError("No recording is running")

        process = self._process
        if process.poll() is None:
            self._stop_requested = True
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

        stopped_by_interrupt = self._stop_requested and (
            process.returncode == -signal.SIGINT
            or (
                process.returncode == 1
                and b"Aborted by signal Interrupt" in stderr
            )
            or process.returncode == 255
        )
        if process.returncode != 0 and not stopped_by_interrupt:
            message = stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(
                message or f"arecord exited with status {process.returncode}"
            )
        if path is None or not path.exists() or path.stat().st_size <= 44:
            raise RuntimeError("Recording did not produce a usable audio file")

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

