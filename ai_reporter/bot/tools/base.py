from abc import abstractmethod
import logging
import os
import tempfile
from typing import Any, Optional

from git import exc

from ...utils import check_config_type
from ..property import PropertyDefinition
from .response import ToolResponseBase

class BaseTool:

    """ Base class for tool. """

    def __init__(self, state : dict[str,object], logger : Optional[logging.Logger] = None, **kwargs):
        self.state = state
        self.logger = logger
        self.args = kwargs
        self.work_path = os.path.join(tempfile.gettempdir(), "_ai_reporter_work")
        os.makedirs(self.work_path, exist_ok=True)

    @staticmethod
    @abstractmethod
    def name() -> str:
        """ The name of the tool. """
        ...

    @staticmethod
    @abstractmethod
    def description(*args, **kwargs) -> str:
        """ A description to tell the bot what the tool does. """
        ...

    @staticmethod
    @abstractmethod
    def properties(*args, **kwargs) -> list[PropertyDefinition]:
        """ The parameters of the arguments to call the tool with. """
        ...

    @abstractmethod
    def execute(self, *args, **kwargs) -> ToolResponseBase: 
        """ Execute the tool. """
        ...

    def __str__(self):
        return "tool '%s'" % self.name()

    def _log(self, message, params : dict = {}, level : int = logging.INFO):
        params["_module"] = "tool"
        params["tool_name"] = self.name()
        if self.logger: self.logger.log(level, message, extra=params)

    def _log_error(self, message, error : Exception, params : dict = {}, level : int = logging.ERROR):
        params["error_class"] = error.__class__.__name__
        params["error"] = str(error)
        params["action"] = "error"
        params["object"] = self
        self._log(message, params, level)

    def _check_config_type(self, value : Any, expected_type : type, name : Optional[str] = None):
        check_config_type(value, expected_type, name)