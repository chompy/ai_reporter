import json
import logging
from typing import Optional

from openai.types.chat import ChatCompletionMessageToolCall, ChatCompletionToolParam
from openai.types.shared_params.function_definition import FunctionDefinition

from ..error.bot import ToolNotDefinedError
from ..utils import dict_get_type
from .base import BaseTool
from .done import DoneTool
from .code import CodeTool
from .code.tools import AVAILABLE_TOOLS as AVAILABLE_CODE_TOOLS
from .response import ToolResponseBase

AVAILABLE_TOOLS : list[type[BaseTool]] = [DoneTool, CodeTool] + AVAILABLE_CODE_TOOLS

class ToolHandler:

    def __init__(
        self,
        tools : dict[str,dict],
        logger : Optional[logging.Logger] = None
    ):
        self.tools_config = tools
        self.tools = list(filter(lambda t: t.name() in tools.keys(), AVAILABLE_TOOLS))
        self.logger = logger

    def _log(self, params : dict, message : str = "", level : int = logging.INFO):
        params["_module"] = "tool"
        if self.logger: self.logger.log(level, message, extra=params)

    def definitions(self) -> list[ChatCompletionToolParam]:
        """ Build tools parameter list. """
        defs = []
        for tool in self.tools:
            def_dict = tool.definition(**self.tools_config.get(tool.name(), {}))
            defs.append(ChatCompletionToolParam(
                function=FunctionDefinition(
                    name=tool.name(),
                    description=dict_get_type(def_dict, "description", str),
                    parameters=dict_get_type(def_dict, "parameters", dict, {})
                ),
                type="function"
            ))
        return defs

    def call(self, name : str, args : dict) -> ToolResponseBase:
        """ Call tool from its name and args dictionary. """
        self._log({"action": "call", "object": "tool '%s'" % name, "parameters": args})
        try:
            for tool_class in self.tools:
                this_tool_name = tool_class.name()
                if not this_tool_name: continue
                if this_tool_name == name:
                    tool_obj = tool_class(logger=self.logger, **self.tools_config.get(this_tool_name, {}))
                    resp = tool_obj.execute(**args)
                    self._log({"action": "response", "object": "tool '%s'" % name, "parameters": {
                        "response": resp.to_dict()}})
                    return resp
        except Exception as e:
            self._log({"action": "error", "object": "tool '%s'" % name, "parameters": {
                "error_class": e.__class__.__name__, "error": str(e)
            }}, level=logging.ERROR)
            raise e
        raise ToolNotDefinedError(name)

    def call_openai(self, tool_call : ChatCompletionMessageToolCall) -> ToolResponseBase:
        """ Call tool from a OpenAI tool request. """
        function_args = json.loads(tool_call.function.arguments)
        out = self.call(tool_call.function.name, function_args)
        out.call = tool_call
        return out
