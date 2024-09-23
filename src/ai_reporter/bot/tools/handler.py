import logging
from typing import Optional

from ...error.bot import (
    MalformedBotResponseError,
    ToolNotDefinedError,
    ToolPropertyInvalidError,
    ToolPropertyMissingError,
)
from .base import BaseTool
from .done import DoneTool
from .git import TOOLS as GIT_TOOLS
from .response import ToolResponseBase
from .web import TOOLS as WEB_TOOLS

TOOLS = {
    "git": GIT_TOOLS,
    "web": WEB_TOOLS,
    "done": [DoneTool]
}

class ToolHandler:

    """
    Handles tool calling based on requests from the bot.
    """

    def __init__(
        self,
        tools : dict[str,dict],
        logger : Optional[logging.Logger] = None
    ):
        self.tools_config = tools
        self.logger = logger
        self.state : dict[str,object] = {}

    @property
    def tools(self) -> list[type[BaseTool]]:
        """ List of tools available to the bot. """
        out = []
        for name in self.tools_config.keys():
            for collection_name, classes in TOOLS.items():
                if name == collection_name: out += classes
        return out + [DoneTool]

    def get_tool_config(self, tool : type[BaseTool]) -> dict:
        """
        The configuration for the given tool.

        :param tool: The tool to get configuration for.
        """
        for collection_name, classes in TOOLS.items():
            for _class in classes:
                if tool is _class:
                    return self.tools_config.get(collection_name, {})
        return {}

    def call(self, name : str, args : dict) -> ToolResponseBase:
        """
        Execute the given tool with the given arguments.

        :param name: Name of tool to execute.
        :param args: The arguments to pass.
        """
        self._log("Call tool '%s'." % name, {"action": "call", "object": "tool '%s'" % name, "tool_name": name, "tool_args": args})
        try:
            for tool_class in self.tools:
                this_tool_name = tool_class.name()
                if not this_tool_name: continue
                if this_tool_name == name:
                    tool_config = self.get_tool_config(tool_class)
                    tool_props = tool_class.properties(**tool_config)
                    # check for required properties
                    for prop in tool_props:
                        if not prop.check_type(args.get(prop.name)):
                            raise ToolPropertyInvalidError(this_tool_name, prop.name, "Unexpected value type.")
                        if not prop.check_required(args.get(prop.name)):
                            raise ToolPropertyMissingError(this_tool_name, prop.name)
                        if not prop.check_choices(args.get(prop.name)):
                            raise ToolPropertyInvalidError(this_tool_name, prop.name, "Value is not one of the provided options.")
                        if not prop.check_range(args.get(prop.name)):
                            raise ToolPropertyInvalidError(this_tool_name, prop.name, "Value is out of range.")
                    # call tool
                    tool_obj = tool_class(state=self.state, logger=self.logger, **tool_config)
                    resp = tool_obj.execute(**args)
                    self._log("Response from %s." % tool_obj, {"action": "response", "object": "tool '%s'" % name, 
                        "tool_response": resp.to_dict(), "tool_name": name, "tool_args": args})
                    return resp
        except TypeError as e:
            self._log_error(name, e)
            raise MalformedBotResponseError()
        except Exception as e:
            self._log_error(name, e)
            raise e
        raise ToolNotDefinedError(name)

    def _log(self, message : str, params : dict = {}, level : int = logging.INFO):
        params["_module"] = "tool"
        if self.logger: self.logger.log(level, message, extra=params)

    def _log_error(self, tool_name : str, e : Exception):
        self._log("Error when calling tool '%s'." % tool_name, {"action": "error", "object": "tool '%s'" % tool_name, 
            "tool_name": tool_name, "error_class": e.__class__.__name__, "error": str(e)}, level=logging.ERROR)