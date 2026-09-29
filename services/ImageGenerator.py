from services.exceptions.QuotaExeededError import QuotaExeededError
from services.exceptions.RateLimitError import RateLimitError
from services.interfaces.GeneratedImage import GeneratedImage
from services.exceptions.AllProvidersUnavailabe import AllProvidersUnavailable


class ImageGenerator:

    def __init__(self, providers) -> None:
        self.providers = providers

    def generate(self, prompt: str) -> GeneratedImage:
        
        errors = []

        for provider in self.providers:
            if not provider.isQuotaExpired:
                try:
                    return provider.generate(prompt)

                except QuotaExeededError as e:
                    errors.append({provider.name, e})
                    continue

                except RateLimitError as e:
                    errors.append({provider.name, e})
                    continue

        raise AllProvidersUnavailable(errors)








