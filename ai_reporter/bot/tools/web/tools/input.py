from .....bot.property import PropertyDefinition
from ...response import ToolMessageResponse
from .base import BaseWebTool
from .....error.bot import ToolPropertyInvalidError

class WebInputTool(BaseWebTool):

    @staticmethod
    def name() -> str:
        return "web-input"

    @staticmethod
    def description(**kwargs):
        return "Input text in to an element in the web browser. If you need to enter a password then use the `password` tool instead."

    @staticmethod
    def properties(**kwargs):
        return  [
            PropertyDefinition("label", description="The two character element label.", required=True),
            PropertyDefinition("text", description="Text to input in to the element.", required=True),
        ]

    def execute(self, label : str, text : str, *args, **kwargs):
        info = self.browser.get_element_info(label)
        if info.get("INPUT TYPE") == "password":
            raise ToolPropertyInvalidError(self.name(), "label", "Cannot input in to a password type element, use the `web-password` tool instead.")
        self.browser.input(label, text)
        return ToolMessageResponse(
            self._get_browser_window_info_text(), [self._screenshot()]
        )
