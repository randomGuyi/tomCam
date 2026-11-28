import os
from pathlib import Path

import cv2
import numpy as np
import requests
from dotenv import load_dotenv


class ImageGeneratorError(Exception):
    """Raised when image generation fails."""


class ImageGenerator:
    def __init__(self):
        # Project root: <project>/src/tomcam/services/image_generator.py
        project_root = Path(__file__).resolve().parents[3]
        for env_path in (project_root / ".env", project_root / "src" / ".env"):
            if env_path.is_file():
                load_dotenv(env_path)

        self.api_url = os.getenv("IMAGE_API_URL")
        self.api_key = os.getenv("IMAGE_API_KEY")

        if not self.api_url:
            raise ImageGeneratorError("IMAGE_API_URL is missing.")

        if not self.api_key:
            raise ImageGeneratorError("IMAGE_API_KEY is missing.")

        self.timeout = 180

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "image/*",
        })

    def generate(self, prompt: str) -> np.ndarray:
        """
        Send a prompt to the Cloudflare Worker.

        Returns:
            OpenCV image as a NumPy array in BGR format.
        """
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("The image prompt must not be empty.")

        try:
            response = self.session.post(
                self.api_url,
                json={"prompt": prompt.strip()},
                timeout=self.timeout,
            )

            response.raise_for_status()

        except requests.Timeout as exc:
            raise ImageGeneratorError(
                "Image generation timed out."
            ) from exc

        except requests.RequestException as exc:
            raise ImageGeneratorError(
                f"Could not contact image backend: {exc}"
            ) from exc

        content_type = response.headers.get("Content-Type", "")

        if not content_type.lower().startswith("image/"):
            raise ImageGeneratorError(
                f"Backend did not return an image. "
                f"Content-Type: {content_type or 'unknown'}"
            )

        image_data = np.frombuffer(response.content, dtype=np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

        if image is None:
            raise ImageGeneratorError(
                "The backend response could not be decoded as an image."
            )

        return image

    def generate_to_file(self, prompt: str, destination: str) -> str:
        """
        Generate an image and save it to disk.

        Returns:
            The destination path.
        """
        image = self.generate(prompt)

        destination_path = Path(destination)
        destination_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        success = cv2.imwrite(str(destination_path), image)

        if not success:
            raise ImageGeneratorError(
                f"Could not save image to {destination_path}"
            )

        return str(destination_path)


