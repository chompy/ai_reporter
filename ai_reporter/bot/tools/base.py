from abc import abstractmethod
import logging
import os
import tempfile
from typing import Optional

from ..property import PropertyDefinition
from .response import ToolResponseBase

class BaseTool:

    def __init__(self, state : dict[str,object], logger : Optional[logging.Logger] = None, **kwargs):
        self.state = state
        self.logger = logger
        self.args = kwargs
        self.work_path = os.path.join(tempfile.gettempdir(), "_ai_reporter_work")
        os.makedirs(self.work_path, exist_ok=True)

    @staticmethod
    @abstractmethod
    def name() -> str: ...

    @staticmethod
    @abstractmethod
    def description(*args, **kwargs) -> str: ...

    @staticmethod
    @abstractmethod
    def properties(*args, **kwargs) -> list[PropertyDefinition]: ...

    @abstractmethod
    def execute(self, *args, **kwargs) -> ToolResponseBase: ...

    def __str__(self):
        return "tool '%s'" % self.name()