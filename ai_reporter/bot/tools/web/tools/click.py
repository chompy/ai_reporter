from ...response import ToolMessageResponse
from .....bot.property import PropertyDefinition
from .base import BaseWebTool

class WebClickTool(BaseWebTool):

    @staticmethod
    def name() -> str:
        return "web-click"

    @staticmethod
    def description(**kwargs):
        return "Click on an element in the web browser."

    @staticmethod
    def properties(**kwargs):
        return  [
            PropertyDefinition("label", description="The two character element label.", required=True)
        ]

    def execute(self, label : str, **kwargs):
        self.browser.click(label)
        return ToolMessageResponse(
            self._get_browser_window_info_text(), [self._screenshot()]
        )