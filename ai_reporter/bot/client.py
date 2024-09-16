import logging
from typing import Iterable, Optional, Tuple

import openai
from openai.types.chat import (
    ChatCompletionContentPartImageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_content_part_image_param import ImageURL

from ..error.bot import BotMaxIterationsError, MalformedBotResponseError
from ..input.image import Image
from ..input.prompt import Prompt
from ..tools.handler import ToolHandler
from ..tools.response import (
    ToolDoneResponse,
    ToolMessageResponse,
    ToolPromptResponse,
    ToolResponseBase,
    ToolBotResponse,
)
from ..utils import dict_get_type

class BotClient:

    def __init__(self, api_key : Optional[str] = None, base_url : Optional[str] = None, logger : Optional[logging.Logger] = None):
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.logger = logger

    def _log(self, message : str, params : dict, level : int = logging.INFO):
        params["_module"] = "bot"
        if self.logger: self.logger.log(level, message, extra=params)

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

    def run(self, prompt : Prompt) -> dict[str,object]:
        """ Run the AI/LLM with given prompt data. """

        tool_handler = ToolHandler({
            **prompt.tools,
            "done": {"properties": prompt.report_properties}
        }, self.logger)

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

            # make callback if provided from prompt
            if prompt.iteration_callback:
                messages += prompt.iteration_callback(iteration, messages)

            # after max iteration reached make only the 'done' tool available, and tell bot to finish its report
            if iteration == prompt.max_iterations:
                self._log("Bot has reached maximum allowed passes. Asking it to complete analysis.", {
                    "action": "max pass", "object": "#%d" % iteration
                })
                tool_handler = ToolHandler({"done": {"properties": prompt.report_properties}})
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
                    messages.append(e.retry_message())
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
                return tool_response.values

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
            tools=tool_handler.definitions(),
            tool_choice="required"
        )
        if len(response.choices) == 0: raise Exception("unexpected response from chat completitions api")
        out = []
        response_message = response.choices[0].message
        out.append(response_message.to_dict())
        if response_message.tool_calls:
            for call in response_message.tool_calls:
                resp = tool_handler.call_openai(call)
                if isinstance(resp, ToolPromptResponse):
                    self._log("Start '%s' bot sub-request." % call.function.name, {"action": "start", "object": "sub-request '%s'" % call.function.name})
                    sub_req_values = self.run(resp.prompt)
                    resp = ToolBotResponse(message=dict_get_type(sub_req_values, "report", str))
                elif isinstance(resp, ToolDoneResponse):
                    return [], resp
                if isinstance(resp, ToolMessageResponse): out.append(resp.to_bot())
            return out, None
        return [], None

