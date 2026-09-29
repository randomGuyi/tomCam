from services.ImageGenerator import ImageGenerator
from services.providers.GeminiProvider import GeminiProvider
from services.providers.OpenAIProvider import OpenAIProvider


def main():
    generator = ImageGenerator([
        OpenAIProvider(),
        GeminiProvider()
    ])

    image = generator.generate(
        prompt= "A medival castle floating above clouds"
    )

    


if __name__ == "__main__":
    main()
