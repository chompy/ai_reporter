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
from ..tools.response import ToolResponse
from ..utils import dict_get_type

class BotClient:

    def __init__(self, api_key : Optional[str] = None, base_url : Optional[str] = None, logger : Optional[logging.Logger] = None):
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.logger = logger

    def _log(self, params : dict, message : str = "", level : int = logging.INFO):
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
            "done": {"properties": prompt.output_properties}
        }, self.logger)

        # prepare initial messages for ai
        messages : list[ChatCompletionMessageParam] = [
            ChatCompletionSystemMessageParam(content=prompt.system_prompt, role="system"),
            ChatCompletionUserMessageParam(content=prompt.user_prompt, role="user")
        ]
        if prompt.images: messages.append(self._prepare_image_attachments(prompt.images))

        self._log({
            "action": "start", "object": "bot", "parameters": {
                "system_prompt": prompt.system_prompt, "user_prompt": prompt.user_prompt, "image_count": len(prompt.images), "available_tools": prompt.tools.keys()}
        })

        # make iterations until bot/llm completes task or max iterations are reached
        for iteration in range(1, prompt.max_iterations+1):
            self._log({"action": "pass", "object": "#%d" % iteration})

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
                        self._log({"action": "retry", "object": "%d" % retry_no, "parameters": {
                                "error_class": e.__class__.__name__, "error": str(e), "retry_message": messages[-1].get("content", "(n/a)")
                            }}, "Retry #%d after '%s' error." % (retry_no, e.__class__.__name__), level=logging.WARNING)

            if tool_response is not None:
                return tool_response.values

        # failed to complete task
        # TODO enforce 'done' tool on last iteration
        self._log({"action": "pass", "object": "maximum exceeded"}, level=logging.ERROR)
        raise BotMaxIterationsError("max iterations reached")

    def _handle_chat_completion(
        self, 
        model : str,
        tool_handler : ToolHandler,
        messages : list[ChatCompletionMessageParam]
    ) -> Tuple[list[ChatCompletionMessageParam], Optional[ToolResponse]]:
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
                if resp.prompt:
                    sub_resp = self.run(resp.prompt)
                    resp.prompt = None
                    resp.bot_message = dict_get_type(sub_resp, "report", str)
                    resp.values = sub_resp
                    resp.success = dict_get_type(sub_resp, "success", bool, True)
                if resp.done: return [], resp
                out.append(resp.to_bot())
            return out, None
        return [], None