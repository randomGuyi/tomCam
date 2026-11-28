""" 
This Library-Class is used to store the Images in a ring buffer
as well as retrieving the paths of all the captured images 
in order to preview them properly.
"""

from pathlib import Path
import cv2


class ImageLibrary:
    SUPPORTED_FORMATS = {
        ".jpg", ".jpeg", ".png", ".bmp"
    }

    def __init__(self, directory="data/images"):
        self.directory = Path(directory)
        # Create the directory in case it's still not present
        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def get_images(self):
        # Return the Images filtered and sorted by format
        return sorted(
            [
                path
                for path in self.directory.iterdir()
                if path.is_file()
                and path.suffix.lower() in self.SUPPORTED_FORMATS
            ],
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

    def get_latest(self):
        # Return the latest image for preview or
        # to perform operations...
        images = self.get_images()
        return images[0] if images else None

    def save_img(self, frame ):
        # Save the image.
        # TODO: Use a ring buffer to save storage
        if frame is None:
            raise RuntimeError("No camera frame available")

        path = Path(self.directory)
        path.parent.mkdir(parents=True, exist_ok=True)

        if not cv2.imwrite(str(path), frame):
            raise RuntimeError(f"Could not save image: {path}")

        return path





