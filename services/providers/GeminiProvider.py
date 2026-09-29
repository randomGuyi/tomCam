
from typing import override
from services.interfaces.GeneratedImage import GeneratedImage
from services.interfaces.ImageProvider import ImageProvider


class GeminiProvider(ImageProvider):

    @property
    def name(self) -> str:
        return "gemini"

    @override
    def generate(self, prompt: str) -> GeneratedImage | None:
        return None

    @override
    def updateQuotaExpired(self) -> None:
        pass
