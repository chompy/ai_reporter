import json
import logging
from typing import Iterable, Optional, Tuple

import openai
from openai.types.chat import (
    ChatCompletionContentPartImageParam,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionToolParam
)
from openai.types.chat.chat_completion_content_part_image_param import ImageURL
from openai.types.shared_params.function_definition import FunctionDefinition

from ...error.bot import BotMaxIterationsError, MalformedBotResponseError
from ..image import Image
from ..prompt import Prompt
from ..results import BotResults
from ..tools.handler import ToolHandler
from ..tools.response import ToolDoneResponse, ToolMessageResponse, ToolResponseBase
from .base_client import BaseClient

class OpenAIClient(BaseClient):

    def __init__(self, api_key : Optional[str] = None, base_url : Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )

    @staticmethod
    def name():
        return "openai"

    def _prepare_image_attachments(self, images : Iterable[Image]) -> ChatCompletionUserMessageParam:
        messages = []
        # TODO preface attachments with information about what they are?
        #messages.append({ "type": "text", 
        #    "text": "The following are images (they should be screenshots of the application) that have been attached to the issue." })
        for image in images:
            data = image.to_base64()
            if not data: raise ValueError("cannot process image with no data")
            messages.append(
                ChatCompletionContentPartImageParam(
                    image_url=ImageURL(url=data, detail="high"),
                    type="image_url"
                )
            )
        return ChatCompletionUserMessageParam(role="user", content=messages)

    def run(self, prompt : Prompt) -> BotResults:

        tool_handler = self._get_tool_handler(prompt)

        # prepare initial messages for ai
        messages : list[ChatCompletionMessageParam] = [
            ChatCompletionSystemMessageParam(content=prompt.system_prompt, role="system"),
            ChatCompletionUserMessageParam(content=prompt.user_prompt, role="user")
        ]
        if prompt.images: messages.append(self._prepare_image_attachments(prompt.images))

        self._log("Start bot.", {"action": "start", "object": "bot", "parameters": prompt.to_dict()})

        # make iterations until bot/llm completes task or max iterations are reached
        for iteration in range(1, prompt.max_iterations+1):
            self._log("Bot pass #%d." % iteration, {"action": "pass", "object": "#%d" % iteration})

            # after max iteration reached make only the 'done' tool available, and tell bot to finish its report
            if iteration == prompt.max_iterations:
                self._log("Bot has reached maximum allowed passes. Asking it to complete analysis.", {
                    "action": "max pass", "object": "#%d" % iteration
                })
                tool_handler = self._get_tool_handler(prompt, is_final_iteration=True)
                messages.append({"role": "user", "content": prompt.max_iteration_prompt})

            # contact llm, allow it to retry if a malformed response is returned
            tool_response = None
            err_retry_iter = prompt.max_error_retry
            while err_retry_iter >= 0:
                try:
                    chat_resp_messages, tool_response = self._handle_chat_completion(prompt.model, tool_handler, messages)
                    messages += chat_resp_messages
                    err_retry_iter = -1
                except MalformedBotResponseError as e:
                    err_retry_iter -= 1
                    if err_retry_iter <= 0: raise e
                    messages.append(ChatCompletionUserMessageParam(content=e.retry_message(), role="user"))
                    if err_retry_iter >= 0:
                        retry_no = prompt.max_error_retry - err_retry_iter
                        self._log("Retry #%d after '%s' error." % (retry_no, e.__class__.__name__), {
                            "action": "retry", "object": "%d" % retry_no, "parameters": {
                                "error_class": e.__class__.__name__, "error": str(e), "retry_message": messages[-1].get("content", "(n/a)")
                            }}, level=logging.WARNING)

            # done response recieved, finish report
            if isinstance(tool_response, ToolDoneResponse): 
                self._log("Finished report via '%s' tool call." % (tool_response.call.function.name if tool_response.call else "(unknown)"), {
                    "action": "finish", "object": "report", "parameters": tool_response.to_dict()
                })
                return BotResults(tool_response.values)

        # failed to complete task
        self._log("Maximum iterations reached.", {"action": "pass", "object": "maximum exceeded"}, level=logging.ERROR)
        raise BotMaxIterationsError("max iterations reached")

    def _handle_chat_completion(
        self, 
        model : str,
        tool_handler : ToolHandler,
        messages : list[ChatCompletionMessageParam]
    ) -> Tuple[list[ChatCompletionMessageParam], Optional[ToolResponseBase]]:
        response = self.client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=0.2,
            top_p=0.1,
            tools=self._tool_definitions(tool_handler),
            tool_choice="required"
        )
        if len(response.choices) == 0: raise Exception("unexpected response from chat completitions api")
        out = []
        response_message = response.choices[0].message
        out.append(response_message.to_dict())
        if response_message.tool_calls:
            for call in response_message.tool_calls:
                resp = self._tool_call(tool_handler, call)
                if isinstance(resp, ToolDoneResponse):
                    return [], resp
                if isinstance(resp, ToolMessageResponse): out.append(resp.to_bot())
            return out, None
        return [], None

    def _tool_call(self, tool_handler : ToolHandler, tool_call : ChatCompletionMessageToolCall) -> ToolResponseBase:
        function_args = json.loads(tool_call.function.arguments)
        out = tool_handler.call(tool_call.function.name, function_args)
        out.call = tool_call
        return out

    def _tool_definitions(self, tool_handler : ToolHandler) -> list[ChatCompletionToolParam]:
        out = []
        for tool in tool_handler.tools:
            tool_config = tool_handler.get_tool_config(tool)
            out.append(ChatCompletionToolParam(
                function=FunctionDefinition(
                    name=tool.name(),
                    description=tool.description(**tool_config),
                    parameters={
                        "type": "object",
                        "properties": dict(map(lambda p: (p.name, p.to_dict()), tool.properties(**tool_config))),
                        "required": list(map(lambda p: p.name, filter(lambda p: p.required, tool.properties(**tool_config))))
                    }
                ),
                type="function"
            ))
        return out