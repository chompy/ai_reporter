# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from ai_reporter.bot.property import PropertyDefinition
from ai_reporter.bot.tools.response import ToolMessageResponse
from ai_reporter.bot.tools.web.tools.base import BaseWebTool


class WebGotoTool(BaseWebTool):
    @staticmethod
    def name() -> str:
        return "web-goto"

    @staticmethod
    def description():
        return "Navigate the web browser to the given URL."

    @staticmethod
    def properties():
        return [PropertyDefinition("url", description="The URL to navigate to.", required=True)]

    def execute(self, url: str):
        self.browser.goto(url)
        return ToolMessageResponse(self._get_browser_window_info_text(), [self._screenshot()])
