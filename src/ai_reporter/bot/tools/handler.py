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
    from ai_reporter.bot.tools.base import BaseTool
    from ai_reporter.bot.tools.response import ToolResponseBase

TOOLS = {"git": GIT_TOOLS, "web": WEB_TOOLS, "done": [DoneTool]}


class ToolHandler:
    """
    Handles tool calling based on requests from the bot.
    """

    def __init__(self, tools: dict[str, dict], logger: logging.Logger | None = None):
        self.tools_config = tools
        self.logger = logger
        self.state: dict[str, object] = {}

    @property
    def tools(self) -> list[type[BaseTool]]:
        """List of tools available to the bot."""
        out = []
        for name in self.tools_config:
            for collection_name, classes in TOOLS.items():
                if name == collection_name:
                    out += classes
        return [*out, DoneTool]

    def get_tool_config(self, tool: type[BaseTool]) -> dict:
        """
        The configuration for the given tool.

        :param tool: The tool to get configuration for.
        """
        for collection_name, classes in TOOLS.items():
            for _class in classes:
                if tool is _class:
                    return self.tools_config.get(collection_name, {})
        return {}

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
            for tool_class in self.tools:
                this_tool_name = tool_class.name()
                if not this_tool_name:
                    continue
                if this_tool_name == name:
                    tool_config = self.get_tool_config(tool_class)
                    tool_props = tool_class.properties(**tool_config)
                    # check for required properties
                    for prop in tool_props:
                        e = None
                        if not prop.check_type(args.get(prop.name)):
                            e = ToolPropertyInvalidError(this_tool_name, prop.name, "Unexpected value type.")
                        elif not prop.check_required(args.get(prop.name)):
                            e = ToolPropertyMissingError(this_tool_name, prop.name)
                        elif not prop.check_choices(args.get(prop.name)):
                            e = ToolPropertyInvalidError(
                                this_tool_name, prop.name, "Value is not one of the provided options."
                            )
                        elif not prop.check_range(args.get(prop.name)):
                            e = ToolPropertyInvalidError(this_tool_name, prop.name, "Value is out of range.")
                        if e:
                            self._log_error(name, e)
                            raise e
                    # call tool
                    tool_obj = tool_class(state=self.state, logger=self.logger, **tool_config)
                    resp = tool_obj.execute(**args)
                    self._log(
                        f"Response from {tool_obj!s}.",
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
