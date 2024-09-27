# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
import os
import tempfile
from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from ai_reporter.utils import check_config_type

if TYPE_CHECKING:
    from ai_reporter.bot.property import PropertyDefinition
    from ai_reporter.bot.tools.response import ToolResponseBase


class BaseTool:
    """Base class for tool."""

    def __init__(self, state: dict[str, object], logger: logging.Logger | None = None, **kwargs):
        self.state = state
        self.logger = logger
        self.kwargs = kwargs
        self.work_path = os.path.join(tempfile.gettempdir(), "_ai_reporter_work")
        os.makedirs(self.work_path, exist_ok=True)

    @staticmethod
    @abstractmethod
    def name() -> str:
        """The name of the tool."""
        ...

    @abstractmethod
    def description(self) -> str:
        """A description to tell the bot what the tool does."""
        ...

    @abstractmethod
    def properties(self) -> list[PropertyDefinition]:
        """The parameters of the arguments to call the tool with."""
        ...

    @abstractmethod
    def execute(self, *args, **kwargs) -> ToolResponseBase:
        """Execute the tool."""
        ...

    def __str__(self):
        return f"tool '{self.name()}'"

    def _log(self, message, params: dict | None = None, level: int = logging.INFO):
        params["_module"] = "tool"
        params["tool_name"] = self.name()
        if self.logger:
            self.logger.log(level, message, extra=params)

    def _log_error(self, message, error: Exception, params: dict | None = None, level: int = logging.ERROR):
        params["error_class"] = error.__class__.__name__
        params["error"] = str(error)
        params["action"] = "error"
        params["object"] = self
        self._log(message, params, level)

    def _check_config_type(self, value: Any, expected_type: type, name: str | None = None):
        check_config_type(value, expected_type, name)
