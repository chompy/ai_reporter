# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from ai_reporter.bot.client.base_client import BaseClient
from ai_reporter.bot.prompt import Prompt
from ai_reporter.bot.results import BotResults
from ai_reporter.bot.token_count import TokenCount
from ai_reporter.bot.tools.response import ToolDoneResponse


class NullClient(BaseClient):
    """Null client for testing."""

    @staticmethod
    def name():
        return "null"

    def run(self, prompt: Prompt) -> BotResults:
        self._log_start(prompt)
        self._log_iteration(1)
        tool_response = ToolDoneResponse(test=True, null=True, prompt=prompt.to_dict())
        self._log_done(tool_response)
        return BotResults(values=tool_response.values, tokens=TokenCount())
