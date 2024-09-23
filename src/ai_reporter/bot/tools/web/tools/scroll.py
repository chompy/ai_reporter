from .....bot.property import PropertyDefinition
from ...response import ToolMessageResponse
from .base import BaseWebTool
from ..browser import WIDTH, HEIGHT

class WebScrollTool(BaseWebTool):

    @staticmethod
    def name() -> str:
        return "web-scroll"

    @staticmethod
    def description(**kwargs):
        return "Scroll the the web browser."

    @staticmethod
    def properties(**kwargs):
        return  [
            PropertyDefinition("direction", description="The direction to scroll the browser viewport.", required=True, choices=["up", "down", "left", "right"]),
        ]

    def execute(self, direction : str, *args, **kwargs):
        sx, sy = self.browser.get_scroll_position()
        match direction:
            case "down":
                self.browser.scroll_to(0, sy+HEIGHT)
            case "up":
                self.browser.scroll_to(0, sy-HEIGHT)
            case "left":
                self.browser.scroll_to(sx-WIDTH, 0)
            case "right":
                self.browser.scroll_to(sx+WIDTH, 0)
        return ToolMessageResponse(
            self._get_browser_window_info_text(), [self._screenshot()]
        )
