from ..prompt import Prompt
from ..results import BotResults
from ..token_count import TokenCount
from ..tools.response import ToolDoneResponse
from .base_client import BaseClient

class NullClient(BaseClient):

    """ Null client for testing. """

    @staticmethod
    def name():
        return "null"

    def run(self, prompt : Prompt) -> BotResults:
        self._log_start(prompt)
        self._log_iteration(1)
        tool_response = ToolDoneResponse(test=True, null=True, prompt=prompt.to_dict())
        self._log_done(tool_response)
        return BotResults(values=tool_response.values, tokens=TokenCount())
