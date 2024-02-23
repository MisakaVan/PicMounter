"""
A ProcessorUnit that adds a configurable margin to the image.
"""
import os.path
import pathlib
import PIL
import colorsys
from PIL import Image, ImageOps, ImageColor

from src.Processor.ProcessorUnit import ProcessorUnit
from src.Canvas.Canvas import Canvas

from typing import override, Any

import loguru

logger = loguru.logger


class MarginMaker(ProcessorUnit):
    """
    A ProcessorUnit that adds a configurable margin to the image.
    """

    _default_description = "Adds a configurable margin to the image."

    left: int
    right: int
    top: int
    bottom: int
    color: Any

    def __init__(self,
                 config: dict | None = None,
                 name: str | None = None,
                 description: str | None = None,
                 left=0,
                 right=0,
                 top=0,
                 bottom=0,
                 color="white"
                 ):
        """

        :param config:
        :param left:
        :param right:
        :param top:
        :param bottom:
        """

        super().__init__(config, name, description)

        self.recipe_dict = {
            "left": left,
            "right": right,
            "top": top,
            "bottom": bottom,
            "color": color
        }

        self.__dict__.update(self.recipe_dict)

    @override
    def forward(self, canvas: Canvas):
        """
        Adds a margin to the image.
        :param canvas: The canvas to be modified.
        :return:
        """
        logger.info(f"Forwarding: {self.recipe_dict}")

        current_image = canvas.current_image
        new_size = (current_image.width + self.left + self.right, current_image.height + self.top + self.bottom)
        new_image = Image.new('RGB', new_size, color=self.color)
        new_image.paste(current_image, (self.left, self.top))
        canvas.current_image = new_image

        return canvas

    @override
    def _recipe_as_list(self) -> list[str]:
        return [f"""left={self.left}, right={self.right}, top={self.top}, bottom={self.bottom}, color={self.color}"""]


if __name__ == '__main__':
    margin = 500
    margin_maker = MarginMaker(left=margin, right=margin, top=margin, bottom=margin, color="black")
    logger.info(margin_maker)

    img_iphone = pathlib.Path(__file__).resolve().parents[3] / 'pic' / 'example1.jpg'
    logger.info(f"Loading {img_iphone}")

    canvas = Canvas(img_iphone)
    logger.info(f"Original size: {canvas.current_image.size}")

    canvas = margin_maker.forward(canvas)
    logger.info(f"New size: {canvas.current_image.size}")

    target = os.path.splitext(img_iphone)[0] + "_margin_test.jpg"
    canvas.save(target)
    logger.info(f"Saved to {target}")
