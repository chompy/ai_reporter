# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT


from ai_reporter.bot.property import PropertyDefinition, PropertyType
from ai_reporter.bot.tools.response import ToolMessageResponse
from ai_reporter.bot.tools.web.tools.base import BaseWebTool


class WebSwitchTabTool(BaseWebTool):
    @staticmethod
    def name() -> str:
        return "web-switch-tab"

    @staticmethod
    def description():
        return "Switch to a different tab in the web browser."

    @staticmethod
    def properties():
        return [PropertyDefinition("tab_number", type=PropertyType.INT, description="The tab to switch to.", min=1)]

    def execute(self, tab_number: int):
        tab_list = self.browser.get_open_windows()
        self.browser.switch_window(tab_list[tab_number - 1]["handle"])
        return ToolMessageResponse(self._get_browser_window_info_text(), [self._screenshot()])
