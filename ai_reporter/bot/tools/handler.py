import logging
from typing import Optional

from ...error.bot import ToolNotDefinedError, ToolPropertyInvalidError, ToolPropertyMissingError
from .base import BaseTool
from .done import DoneTool
from .git import TOOLS as GIT_TOOLS
from .web import TOOLS as WEB_TOOLS
from .response import ToolResponseBase

TOOLS = {
    "git": GIT_TOOLS,
    "web": WEB_TOOLS
}

class ToolHandler:

    def __init__(
        self,
        tools : dict[str,dict],
        logger : Optional[logging.Logger] = None
    ):
        self.tools_config = tools
        self.logger = logger
        self.state : dict[str,object] = {}

    def _log(self, params : dict, message : str = "", level : int = logging.INFO):
        params["_module"] = "tool"
        if self.logger: self.logger.log(level, message, extra=params)

    @property
    def tools(self) -> list[type[BaseTool]]:
        out = []
        for name in self.tools_config.keys():
            for collection_name, classes in TOOLS.items():
                if name == collection_name: out += classes
        return out + [DoneTool]

    def get_tool_config(self, tool : type[BaseTool]) -> dict:
        for collection_name, classes in TOOLS.items():
            for _class in classes:
                if tool is _class:
                    return self.tools_config.get(collection_name, {})
        return {}

    def call(self, name : str, args : dict) -> ToolResponseBase:
        """ Call tool from its name and args dictionary. """
        self._log({"action": "call", "object": "tool '%s'" % name, "parameters": args})
        try:
            for tool_class in self.tools:
                this_tool_name = tool_class.name()
                if not this_tool_name: continue
                if this_tool_name == name:
                    tool_config = self.get_tool_config(tool_class)
                    tool_props = tool_class.properties(**tool_config)
                    # check for required properties
                    for prop in tool_props:
                        if prop.required and prop.name not in args:
                            raise ToolPropertyMissingError(this_tool_name, prop.name)
                        if prop.choices and args.get(prop.name) not in prop.choices:
                            raise ToolPropertyInvalidError(this_tool_name, prop.name)
                    # call tool
                    tool_obj = tool_class(state=self.state, logger=self.logger, **tool_config)
                    resp = tool_obj.execute(**args)
                    self._log({"action": "response", "object": "tool '%s'" % name, "parameters": {
                        "response": resp.to_dict()}})
                    return resp
        except TypeError as e:
            # TODO invalid tool property error?
            raise e
        except Exception as e:
            self._log({"action": "error", "object": "tool '%s'" % name, "parameters": {
                "error_class": e.__class__.__name__, "error": str(e)
            }}, level=logging.ERROR)
            raise e
        raise ToolNotDefinedError(name)