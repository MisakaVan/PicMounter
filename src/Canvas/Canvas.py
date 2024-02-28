import pathlib

import PIL.Image
from PIL import Image


class Canvas:
    """
    A class that holds the picture to be edited and is passed to Processors to be modified.
    """

    raw_image: PIL.Image.Image
    current_image: PIL.Image.Image

    def __init__(self, img_path: str | pathlib.Path):
        self.raw_image = Image.open(img_path)
        self.current_image = self.raw_image.copy()

    def save(self, path: str | pathlib.Path):
        self.current_image.save(path, exif=self.raw_image.getexif())
        return path
