from .....bot.property import PropertyDefinition
from ...response import ToolMessageResponse
from .base import BaseWebTool

class WebGotoTool(BaseWebTool):

    @staticmethod
    def name() -> str:
        return "web-goto"

    @staticmethod
    def description(**kwargs):
        return "Navigate the web browser to the given URL."

    @staticmethod
    def properties(**kwargs):
        return  [
            PropertyDefinition("url", description="The URL to navigate to.", required=True)
        ]

    def execute(self, url : str, *args, **kwargs):
        self.browser.goto(url)
        return ToolMessageResponse(
            self._get_browser_window_info_text(), [self._screenshot()]
        )