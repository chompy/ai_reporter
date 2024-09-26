# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT


from ai_reporter.bot.property import PropertyDefinition
from ai_reporter.bot.tools.response import ToolMessageResponse
from ai_reporter.bot.tools.web.tools.base import BaseWebTool
from ai_reporter.error.bot import ToolPropertyInvalidError


class WebSelectTool(BaseWebTool):
    @staticmethod
    def name() -> str:
        return "web-select"

    @staticmethod
    def description():
        return "Change the selection in a SELECT element in the web browser."

    @staticmethod
    def properties():
        return [
            PropertyDefinition("label", description="The two character element label.", required=True),
            PropertyDefinition(
                "option",
                description="The option to pick. (Use the `web-element` tool to get a list of options.)",
                required=True,
            ),
        ]

    def execute(self, label: str, option: str):
        info = self.browser.get_element_info(label)
        if info.get("TAG NAME") != "select":
            raise ToolPropertyInvalidError(self.name(), "label", "Cannot change the selection of a non SELECT element.")
        self.browser.select(label, option)
        return ToolMessageResponse(self._get_browser_window_info_text(), [self._screenshot()])
