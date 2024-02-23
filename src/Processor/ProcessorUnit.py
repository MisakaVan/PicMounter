import os
import PIL
from PIL import Image, ExifTags

from src.Canvas.Canvas import Canvas
from typing import override, final


class ProcessorUnit:
    """
    The base class for all processor units.
    """

    __enable_fallback_to_base = True
    # If True, the base class will provide a default implementation for some methods,

    _config: dict
    _name: str
    _description: str

    _default_description = "A ProcessorUnit that does nothing." # Subclasses should override this.

    def __init__(self,
                 config: dict | None = None,
                 name: str | None = None,
                 description: str | None = None,
                 ):
        if config is None:
            config = {}
        self._config = config
        self._name = name
        self._description = description if description is not None else self._default_description

    def forward(self, canvas: Canvas) -> Canvas:
        """
        This virtual function is called to process the canvas.
        :param canvas:
        :return:
        """
        if not self.__enable_fallback_to_base:
            raise NotImplementedError
        return canvas

    def __str__(self):
        return f"""{self.__class__.__name__}(name="{self.name}", description="{self._description}", recipe="{self.recipe()}")"""

    @final
    def beautify_str(self) -> str:
        return "\n".join(self._beautify_str())

    def recipe(self) -> str:
        """
        Returns a one-line string representation of the key information of the processor unit.
        For example, the recipe of a MarginMaker should include the margin width, color, etc.
        This is useful for logging and debugging.
        :return:
        """
        if not self.__enable_fallback_to_base:
            raise NotImplementedError
        return ", ".join(self._recipe_as_list())

    def _recipe_as_list(self) -> list[str]:
        if not self.__enable_fallback_to_base:
            raise NotImplementedError
        return [self._config.__str__()]

    @final
    def _beautify_str(self) -> list[str]:
        indent = " " * 2

        make_indent = lambda s: indent + s

        indented_recipe = list(map(make_indent, self._recipe_as_list()))

        return [
            f"class: {self.__class__.__name__}",
            f"name: {self.name}",
            f"description: {self._description}",
            "recipe: ",
            *indented_recipe
        ]

    @property
    def name(self):
        if self._name is not None:
            return self._name
        else:
            return self.__class__.__name__

    @name.setter
    def name(self, _):
        raise AttributeError("Cannot set the name of a ProcessorUnit")


if __name__ == '__main__':
    unit1 = ProcessorUnit(config={"test": "test"}, name="test_base_unit", )
    print(unit1)
