from abc import abstractmethod
import logging
from typing import Optional

from ..prompt import Prompt
from ..results import BotResults
from ..tools.handler import ToolHandler
from ..tools.response import ToolDoneResponse
from ...error.bot import MalformedBotResponseError

class BaseClient:

    def __init__(self, logger : Optional[logging.Logger] = None, **kwargs):
        self.logger = logger
        self._kwargs = kwargs

    def _log(self, message : str, params : dict, level : int = logging.INFO):
        params["_module"] = "bot"
        params["bot_client"] = self.name()
        if self.logger: self.logger.log(level, message, extra=params)

    @staticmethod
    @abstractmethod
    def name() -> str:
        """ The name of the bot client. """
        ...

    @abstractmethod
    def run(self, prompt : Prompt) -> BotResults:
        """
        Submit the prompt the AI/LLM and return the results.
        
        :param prompt: The prompt.
        """
        ...

    def __str__(self):
        return "bot client '%s'" % self.name()

    def _get_tool_handler(self, prompt : Prompt, is_final_iteration : bool = False):
        return ToolHandler({
            **(prompt.tools if not is_final_iteration else {}),
            "done": {"properties": prompt.report_properties}
        }, self.logger)

    def _log_start(self, prompt : Prompt):
        self._log("Start %s." % self.name(), {
            "action": "start", "object": self, "bot_prompt": prompt.to_dict()})

    def _log_iteration(self, iteration : int):
        self._log("Bot iteration #%d." % iteration, {"action": "interation", "object": self, "bot_iteration": iteration})

    def _log_max_iterations(self, iteration : int):
        self._log("Bot has reached maximum allowed iterations. Asking it to complete analysis.", {
            "action": "max interations", "object": self, "bot_iteration": iteration})

    def _log_error_retry(self, e : MalformedBotResponseError, retry_no : int):
        self._log("Retry #%d after '%s' error." % (retry_no, e.__class__.__name__), {
            "action": "retry", "object": self, "error_class": e.__class__.__name__, 
            "error": str(e), "bot_retry_message": e.retry_message()}, level=logging.WARNING)

    def _log_done(self, tool_response : ToolDoneResponse):
        self._log("Finished report via '%s' tool call." % (tool_response.tool_name if tool_response.tool_name else "(unknown)"), {
            "action": "done", "object": self, "tool_response": tool_response.to_dict()
        })