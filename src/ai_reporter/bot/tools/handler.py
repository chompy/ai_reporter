# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT


from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ai_reporter.bot.tools.done import DoneTool
from ai_reporter.bot.tools.git import TOOLS as GIT_TOOLS
from ai_reporter.bot.tools.web import TOOLS as WEB_TOOLS
from ai_reporter.error.bot import (
    MalformedBotResponseError,
    ToolNotDefinedError,
    ToolPropertyInvalidError,
    ToolPropertyMissingError,
)

if TYPE_CHECKING:
    from ai_reporter.bot.tools.response import ToolResponseBase

TOOLS = {"git": GIT_TOOLS, "web": WEB_TOOLS, "done": [DoneTool]}


class ToolHandler:
    """
    Handles tool calling based on requests from the bot.
    """

    def __init__(self, tools: dict[str, dict], logger: logging.Logger | None = None):
        self.state: dict[str, object] = {}
        self.tools = []
        for name, config in tools.items():
            self.tools += [t(state=self.state, logger=logger, **config) for t in TOOLS[name]]
        self.logger = logger

    def call(self, name: str, args: dict) -> ToolResponseBase:
        """
        Execute the given tool with the given arguments.

        :param name: Name of tool to execute.
        :param args: The arguments to pass.
        """
        self._log(
            f"Call tool '{name}'.", {"action": "call", "object": f"tool '{name}'", "tool_name": name, "tool_args": args}
        )
        try:
            for tool in self.tools:
                if tool.name() == name:
                    tool_props = tool.properties()
                    # check for required properties
                    for prop in tool_props:
                        e = None
                        if not prop.check_type(args.get(prop.name)):
                            e = ToolPropertyInvalidError(tool.name(), prop.name, "Unexpected value type.")
                        elif not prop.check_required(args.get(prop.name)):
                            e = ToolPropertyMissingError(tool.name(), prop.name)
                        elif not prop.check_choices(args.get(prop.name)):
                            e = ToolPropertyInvalidError(
                                tool.name(), prop.name, "Value is not one of the provided options."
                            )
                        elif not prop.check_range(args.get(prop.name)):
                            e = ToolPropertyInvalidError(tool.name(), prop.name, "Value is out of range.")
                        if e:
                            self._log_error(name, e)
                            raise e
                    # call tool
                    resp = tool.execute(**args)
                    self._log(
                        f"Response from {tool!s}.",
                        {
                            "action": "response",
                            "object": f"tool '{name}'",
                            "tool_response": resp.to_dict(),
                            "tool_name": name,
                            "tool_args": args,
                        },
                    )
                    return resp
        except TypeError as e:
            self._log_error(name, e)
            raise MalformedBotResponseError from e
        raise ToolNotDefinedError(name)

    def _log(self, message: str, params: dict | None = None, level: int = logging.INFO):
        params["_module"] = "tool"
        if self.logger:
            self.logger.log(level, message, extra=params)

    def _log_error(self, tool_name: str, e: Exception):
        self._log(
            f"Error when calling tool '{tool_name}'.",
            {
                "action": "error",
                "object": f"tool '{tool_name}'",
                "tool_name": tool_name,
                "error_class": e.__class__.__name__,
                "error": str(e),
            },
            level=logging.ERROR,
        )
