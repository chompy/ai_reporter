from ...response import ToolMessageResponse
from .....bot.property import PropertyDefinition, PropertyType
from .base import BaseWebTool

class WebSwitchTabTool(BaseWebTool):

    @staticmethod
    def name() -> str:
        return "web-switch-tab"

    @staticmethod
    def description(**kwargs):
        return "Switch to a different tab in the web browser."

    @staticmethod
    def properties(**kwargs):
        return  [
            PropertyDefinition("tab_number", type=PropertyType.INT, description="The tab to switch to.", min=1)
        ]

    def execute(self, tab_number : int, *args, **kwargs):
        tab_list = self.browser.get_open_windows()
        self.browser.switch_window(tab_list[tab_number-1]["handle"])
        return ToolMessageResponse(
            self._get_browser_window_info_text(), [self._screenshot()]
        )

