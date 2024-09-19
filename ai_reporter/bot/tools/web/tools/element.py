from ...response import ToolMessageResponse
from .....bot.property import PropertyDefinition
from .base import BaseWebTool

class WebElementTool(BaseWebTool):

    @staticmethod
    def name() -> str:
        return "web-element"

    @staticmethod
    def description(**kwargs):
        return "Retrieve information about an element in the web browser."

    @staticmethod
    def properties(**kwargs):
        return  [
            PropertyDefinition("label", description="The two character element label.", required=True)
        ]

    def execute(self, label : str, **kwargs):
        info = self.browser.get_element_info(label)
        out = ""
        for k, v in info.items():
            if type(v) is list: v = ",".join(v)
            out += "%s: %s, " % (k, str(v))
        return ToolMessageResponse(out.strip().strip(","))
