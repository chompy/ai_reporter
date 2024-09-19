from typing import Iterable

from ..property import PropertyDefinition
from .base import BaseTool
from .response import ToolDoneResponse

class DoneTool(BaseTool):

    @staticmethod
    def name() -> str:
        return "done"

    @staticmethod
    def description():
        return "Finish your analysis."

    @staticmethod
    def properties(properties : Iterable[PropertyDefinition]):
        return list(properties)

    def execute(self, **kwargs):
        return ToolDoneResponse(**kwargs)
