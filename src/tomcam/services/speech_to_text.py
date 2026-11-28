from pathlib import Path

import speech_recognition as sr


class SpeechToTextError(Exception):
    """Raised when a recording cannot be transcribed."""


class SpeechToText:
    def __init__(self, language="en-US"):
        self.language = language
        self.recognizer = sr.Recognizer()
        self.recognizer.operation_timeout = 30

    def transcribe(self, audio_path: Path) -> str:
        try:
            with sr.AudioFile(str(audio_path)) as source:
                audio = self.recognizer.record(source)
        except (OSError, ValueError) as exc:
            raise SpeechToTextError(
                f"Could not read recording: {exc}"
            ) from exc

        try:
            text = self.recognizer.recognize_google(
                audio,
                language=self.language,
            ).strip()
        except sr.UnknownValueError as exc:
            raise SpeechToTextError(
                "The recording could not be understood. Please try again."
            ) from exc
        except sr.RequestError as exc:
            raise SpeechToTextError(
                f"Speech recognition service is unavailable: {exc}"
            ) from exc

        if not text:
            raise SpeechToTextError(
                "The speech recognition service returned no text."
            )
        return text
