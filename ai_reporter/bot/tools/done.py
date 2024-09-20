from typing import Iterable

from ..property import PropertyDefinition
from .base import BaseTool
from .response import ToolDoneResponse
from ...utils import check_config_type

class DoneTool(BaseTool):

    @staticmethod
    def name() -> str:
        return "done"

    @staticmethod
    def description(**kwargs):
        return "Finish your analysis."

    @staticmethod
    def properties(properties : Iterable[PropertyDefinition]):
        out = list(properties)
        for i in range(len(out)): check_config_type(out[i], PropertyDefinition, "prompt:report_properties.%d" % i)
        return out

    def execute(self, **kwargs):
        return ToolDoneResponse(**kwargs)
