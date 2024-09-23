from .....bot.property import PropertyDefinition
from .....error.bot import ToolPropertyInvalidError
from ...response import ToolMessageResponse
from .base import BaseWebTool

class WebPasswordTool(BaseWebTool):

    @staticmethod
    def name() -> str:
        return "web-password"

    @staticmethod
    def description(**kwargs):
        return "Input a password in to a password type input element in the web browser."

    @staticmethod
    def properties(**kwargs):
        return  [
            PropertyDefinition("label", description="The two character element label.", required=True),
            PropertyDefinition("username", description="The username for the password.", required=True),
        ]

    def execute(self, label : str, username : str, *args, **kwargs):
        info = self.browser.get_element_info(label)
        if info.get("INPUT TYPE") != "password": raise ToolPropertyInvalidError(self.name(), "label", "it's not a password type input element")
        secrets = self.browser.get_secrets_for_current_url()
        for secret in secrets:
            if secret.key == username:
                self.browser.input(label, secret.value)
                return ToolMessageResponse(
                    self._get_browser_window_info_text(), [self._screenshot()]
                )
        raise ToolPropertyInvalidError(self.name(), "username", "no password found for the username")
