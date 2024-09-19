from abc import abstractmethod
import logging
from typing import Optional

from ..tools.handler import ToolHandler
from ..prompt import Prompt
from ..results import BotResults

class BaseClient:

    def __init__(self, logger : Optional[logging.Logger] = None, **kwargs):
        self.logger = logger
        self._kwargs = kwargs

    def _log(self, message : str, params : dict, level : int = logging.INFO):
        params["_module"] = "bot"
        if self.logger: self.logger.log(level, message, extra=params)

    @staticmethod
    @abstractmethod
    def name() -> str: ...

    @abstractmethod
    def run(self, prompt : Prompt) -> BotResults:
        """
        Run the AI/LLM with given prompt data.
        
        :param prompt: The prompt.
        """
        ...

    def _get_tool_handler(self, prompt : Prompt, is_final_iteration : bool = False):
        return ToolHandler({
            **(prompt.tools if not is_final_iteration else {}),
            "done": {"properties": prompt.report_properties}
        }, self.logger)