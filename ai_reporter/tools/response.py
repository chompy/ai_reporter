from typing import Optional
from openai.types.chat import ChatCompletionMessageToolCall, ChatCompletionToolMessageParam
from ..input.prompt import Prompt

class ToolResponse:

    """ The callback response of a tool. """

    def __init__(self, bot_message : str = "", values : dict = {}, success : bool = True, done : bool = False, prompt : Optional[Prompt] = None):
        self.bot_message = bot_message
        self.values : dict[str,object] = values
        self.success = success
        self.done = done
        self.call : Optional[ChatCompletionMessageToolCall] = None
        self.prompt : Optional[Prompt] = prompt

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "done": self.done,
            "message": self.bot_message,
            "values": self.values,
        }

    def to_bot(self) -> ChatCompletionToolMessageParam:
        return ChatCompletionToolMessageParam(
            role="tool",
            tool_call_id=self.call.id if self.call else "-",
            content=self.bot_message
        )
