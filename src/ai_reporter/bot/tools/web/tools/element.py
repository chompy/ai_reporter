# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from ai_reporter.bot.property import PropertyDefinition
from ai_reporter.bot.tools.response import ToolMessageResponse
from ai_reporter.bot.tools.web.tools.base import BaseWebTool


class WebElementTool(BaseWebTool):
    @staticmethod
    def name() -> str:
        return "web-element"

    @staticmethod
    def description():
        return "Retrieve information about an element in the web browser."

    @staticmethod
    def properties():
        return [PropertyDefinition("label", description="The two character element label.", required=True)]

    def execute(self, label: str):
        info = self.browser.get_element_info(label)
        out = ""
        for k, v in info.items():
            out_value = v
            if isinstance(v, list):
                out_value = ",".join(v)
            out += f"{k!s}: {out_value}, "
        return ToolMessageResponse(out.strip().strip(","))
