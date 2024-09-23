from .....bot.property import PropertyDefinition
from ...response import ToolMessageResponse
from .base import BaseWebTool

class WebHoverTool(BaseWebTool):

    @staticmethod
    def name() -> str:
        return "web-hover"

    @staticmethod
    def description(**kwargs):
        return "Hover over an element in the web browser."

    @staticmethod
    def properties(**kwargs):
        return  [
            PropertyDefinition("label", description="The two character element label.", required=True)
        ]

    def execute(self, label : str, option : str, *args, **kwargs):
        self.browser.hover(label)
        return ToolMessageResponse(
            self._get_browser_window_info_text(), [self._screenshot()]
        )
