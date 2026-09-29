from openai import OpenAI
from typing import override
from services.interfaces.GeneratedImage import GeneratedImage
from services.interfaces.ImageProvider import ImageProvider


class OpenAIProvider(ImageProvider):

    def __init__(self) -> None:
        super().__init__()
        self.__client = OpenAI()

    @property
    def name(self) -> str:
        return "openai"

    @override
    def generate(self, prompt: str) -> GeneratedImage | None:
        return None

    @override
    def updateQuotaExpired(self) -> None:
        pass


    

