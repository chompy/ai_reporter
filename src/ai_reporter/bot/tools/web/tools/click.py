# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from ai_reporter.bot.property import PropertyDefinition
from ai_reporter.bot.tools.response import ToolMessageResponse
from ai_reporter.bot.tools.web.tools.base import BaseWebTool


class WebClickTool(BaseWebTool):
    @staticmethod
    def name() -> str:
        return "web-click"

    def description(self):
        return "Click on an element in the web browser."

    def properties(self):
        return [PropertyDefinition("label", description="The two character element label.", required=True)]

    def execute(self, label: str):
        self.browser.click(label)
        return ToolMessageResponse(self._get_browser_window_info_text(), [self._screenshot()])
