# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT


from ai_reporter.bot.property import PropertyDefinition
from ai_reporter.bot.tools.response import ToolMessageResponse
from ai_reporter.bot.tools.web.browser import HEIGHT, WIDTH
from ai_reporter.bot.tools.web.tools.base import BaseWebTool


class WebScrollTool(BaseWebTool):
    @staticmethod
    def name() -> str:
        return "web-scroll"

    def description(self):
        return "Scroll the the web browser."

    def properties(self):
        return [
            PropertyDefinition(
                "direction",
                description="The direction to scroll the browser viewport.",
                required=True,
                choices=["up", "down", "left", "right"],
            ),
        ]

    def execute(self, direction: str):
        sx, sy = self.browser.get_scroll_position()
        match direction:
            case "down":
                self.browser.scroll_to(0, sy + HEIGHT)
            case "up":
                self.browser.scroll_to(0, sy - HEIGHT)
            case "left":
                self.browser.scroll_to(sx - WIDTH, 0)
            case "right":
                self.browser.scroll_to(sx + WIDTH, 0)
        return ToolMessageResponse(self._get_browser_window_info_text(), [self._screenshot()])
