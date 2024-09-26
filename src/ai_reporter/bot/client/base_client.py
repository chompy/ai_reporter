# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from abc import abstractmethod
from typing import TYPE_CHECKING

from ai_reporter.bot.tools.handler import ToolHandler

if TYPE_CHECKING:
    from ai_reporter.bot.prompt import Prompt
    from ai_reporter.bot.results import BotResults
    from ai_reporter.bot.tools.response import ToolDoneResponse
    from ai_reporter.error.bot import MalformedBotResponseError


class BaseClient:
    def __init__(self, logger: logging.Logger | None = None, **kwargs):
        self.logger = logger
        self._kwargs = kwargs

    def _log(self, message: str, params: dict, level: int = logging.INFO):
        params["_module"] = "bot"
        params["bot_client"] = self.name()
        if self.logger:
            self.logger.log(level, message, extra=params)

    @staticmethod
    @abstractmethod
    def name() -> str:
        """The name of the bot client."""
        ...

    @abstractmethod
    def run(self, prompt: Prompt) -> BotResults:
        """
        Submit the prompt the AI/LLM and return the results.
        :param prompt: The prompt.
        """
        ...

    def __str__(self):
        return f"bot client '{self.name()}'"

    def _get_tool_handler(self, prompt: Prompt, *, is_final_iteration: bool = False):
        return ToolHandler(
            {**(prompt.tools if not is_final_iteration else {}), "done": {"properties": prompt.report_properties}},
            self.logger,
        )

    def _log_start(self, prompt: Prompt):
        self._log(f"Start '{self.name()}'.", {"action": "start", "object": self, "bot_prompt": prompt.to_dict()})

    def _log_iteration(self, iteration: int):
        self._log(f"Bot iteration #{iteration}.", {"action": "interation", "object": self, "bot_iteration": iteration})

    def _log_max_iterations(self, iteration: int):
        self._log(
            "Bot has reached maximum allowed iterations. Asking it to complete analysis.",
            {"action": "max interations", "object": self, "bot_iteration": iteration},
        )

    def _log_error_retry(self, e: MalformedBotResponseError, retry_no: int):
        self._log(
            f"Retry #{retry_no} after '{e.__class__.__name__}' error.",
            {
                "action": "retry",
                "object": self,
                "error_class": e.__class__.__name__,
                "error": str(e),
                "bot_retry_message": e.retry_message(),
            },
            level=logging.WARNING,
        )

    def _log_done(self, tool_response: ToolDoneResponse):
        self._log(
            f"Finished report via '{tool_response.tool_name if tool_response.tool_name else "(unknown)"}' tool call."
            % (),
            {"action": "done", "object": self, "tool_response": tool_response.to_dict()},
        )
