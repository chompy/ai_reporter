from typing import Iterable

from ..input.property import PropertyDefinition
from .base import BaseTool
from .response import ToolResponse

class DoneTool(BaseTool):

    @staticmethod
    def name() -> str:
        return "done"

    @classmethod
    def definition(cls, properties : Iterable[PropertyDefinition], **kwargs) -> dict:
        return {
            "name": cls.name(),
            "description": "Finish your analysis.",
            "parameters": {
                "type": "object",
                "properties": dict(map(lambda p: (p.name, p.to_dict()), properties)),
                "required": list(map(lambda p: p.name, filter(lambda p: p.required, properties)))
            }
        }

    def execute(self, **kwargs):
        self._check_properties(kwargs)
        return ToolResponse(values=kwargs, done=True)
