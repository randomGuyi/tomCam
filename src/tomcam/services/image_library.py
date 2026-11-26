from pathlib import Path


class ImageLibrary:
    SUPPORTED_FORMATS = {
        ".jpg", ".jpeg", ".png", ".bmp"
    }

    def __init__(self, directory="data/images"):
        self.directory = Path(directory)
        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def get_images(self):
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
        images = self.get_images()
        return images[0] if images else None
