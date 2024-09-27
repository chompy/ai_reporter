# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT


from ai_reporter.bot.tools.response import ToolMessageResponse
from ai_reporter.bot.tools.web.tools.base import BaseWebTool


class WebSubmitTool(BaseWebTool):
    @staticmethod
    def name() -> str:
        return "web-submit"

    def description(self):
        return "Submit the current form in the web browser."

    def properties(self):
        return []

    def execute(self):
        success = self.browser.submit()
        return ToolMessageResponse(
            self._get_browser_window_info_text("(success)" if success else "(warning: no form was found)"),
            [self._screenshot()],
        )
