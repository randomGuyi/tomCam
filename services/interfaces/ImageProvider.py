from abc import ABC, abstractmethod
from services.interfaces.GeneratedImage import GeneratedImage

class ImageProvider(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def isQuotaExpired(self) -> bool:
        return self.isQuotaExpired

    @isQuotaExpired.setter
    def isQuotaExpired(self, expired : bool) -> None:
        self.isQuotaExpired = expired

    @abstractmethod
    def generate(self, prompt: str) -> GeneratedImage | None:
        pass

    @abstractmethod
    def updateQuotaExpired(self) -> None:
        pass



