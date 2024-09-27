# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT


from ai_reporter.bot.property import PropertyDefinition
from ai_reporter.bot.tools.response import ToolMessageResponse
from ai_reporter.bot.tools.web.tools.base import BaseWebTool
from ai_reporter.error.bot import ToolPropertyInvalidError


class WebPasswordTool(BaseWebTool):
    @staticmethod
    def name() -> str:
        return "web-password"

    def description(self):
        return "Input a password in to a password type input element in the web browser."

    def properties(self):
        return [
            PropertyDefinition("label", description="The two character element label.", required=True),
            PropertyDefinition("username", description="The username for the password.", required=True),
        ]

    def execute(self, label: str, username: str):
        info = self.browser.get_element_info(label)
        if info.get("INPUT TYPE") != "password":
            raise ToolPropertyInvalidError(self.name(), "label", "it's not a password type input element")
        secrets = self.browser.get_secrets_for_current_url()
        for secret in secrets:
            if secret.key == username:
                self.browser.input(label, secret.value)
                return ToolMessageResponse(self._get_browser_window_info_text(), [self._screenshot()])
        raise ToolPropertyInvalidError(self.name(), "username", "no password found for the username")
