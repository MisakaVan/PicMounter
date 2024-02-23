from src.Processor.ProcessorUnit import ProcessorUnit
from src.Canvas.Canvas import Canvas
from typing import override, final


class ProcessorChain(ProcessorUnit):
    """
    A processor unit that contains a list of subunits to be called in order.
    """
    _sub_units: list[ProcessorUnit]
    _description = "A ProcessorUnit that contains a list of subunits to be called in order."

    def __init__(self,
                 config: dict | None = None,
                 name: str | None = None,
                 sub_units: list[ProcessorUnit] | None = None):
        super().__init__(config)
        self._sub_units = sub_units if sub_units is not None else []

    @override
    def forward(self, canvas: Canvas):
        for sub_unit in self._sub_units:
            canvas = sub_unit.forward(canvas)
        return canvas

    @override
    def recipe(self) -> str:
        return ", \n".join([sub_unit.__str__() for sub_unit in self.sub_units])

    @property
    def sub_units(self):
        return self._sub_units

    @override
    @final
    def _recipe_as_list(self) -> list[str]:
        ret = []
        for sub_unit in self.sub_units:
            ret.extend(sub_unit._beautify_str())
        return ret


if __name__ == '__main__':
    units = [
        ProcessorUnit(config={"test1": "abc"}, name="test_base_unit", description="First things first"),
        ProcessorUnit(config={"test2": "def"}, name="another_base_unit", description="Second things second"),
        ProcessorUnit(config={"test3": "ghi"}, name="unit_114514", description=None),
    ]

    chain = ProcessorChain(sub_units=units, name="test_chain")
    print(chain.beautify_str())
