from typing import Optional
from openai.types.chat import ChatCompletionMessageToolCall, ChatCompletionToolMessageParam
from ..input.prompt import Prompt
from ..input.property import PropertyDefinition

class ToolResponseBase:

    """ The response of a tool call. """

    def __init__(self):
        self.call : Optional[ChatCompletionMessageToolCall] = None

    def to_dict(self) -> dict:
        return {
            "name": self.call.function.name if self.call else "(unknown)",
            "request_args": self.call.function.arguments if self.call else {},
            "done": False
        }

class ToolMessageResponse(ToolResponseBase):
    
    """ Tool response for replying to original tool call. """

    def __init__(self, message : str):
        """
        :param message: Message to reply to the bot with.
        """
        super().__init__()
        self.message = message

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "message": self.message
        }

    def to_bot(self) -> ChatCompletionToolMessageParam:
        return ChatCompletionToolMessageParam(
            role="tool",
            tool_call_id=self.call.id if self.call else "-",
            content=self.message
        )

class ToolDoneResponse(ToolResponseBase):

    """ Tool response that signifies completion of the report. """

    def __init__(self, **kwargs):
        super().__init__()
        self.values = kwargs

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "done": True,
            "values": self.values
        }

class ToolPromptResponse(ToolResponseBase):

    """ Tool response for prompting the bot with a sub-request. """

    def __init__(self, **kwargs):
        super().__init__()
        self.prompt = Prompt(
            report_properties=[PropertyDefinition("report", description="A report of your analysis.", required=True)],
            **kwargs
        )

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "prompt": self.prompt
        }

class ToolBotResponse(ToolMessageResponse):
    """ Tool response for replying with the results of a sub-request from a ToolPromptResponse. """
    pass