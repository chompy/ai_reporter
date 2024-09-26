# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from ai_reporter.utils import check_config_type

if TYPE_CHECKING:
    from ai_reporter.bot.image import Image
    from ai_reporter.bot.property import PropertyDefinition

DEFAULT_SYSTEM_PROMPT = """
Using the tools available to you, perform an analysis of the user's message. Use the `done` tool to signal the completion of your analysis.
""".strip()

DEFAULT_MAX_ITERATION_PROMPT = """
Please complete your analysis to the best of your ability with the `done` tool.
"""


class Prompt:
    """
    The prompt for the AI model as well as the desired properties to include in the report
    """

    def __init__(
        self,
        user_prompt: str,
        report_properties: Iterable[PropertyDefinition],
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        images: Iterable[Image] | None = None,
        tools: dict[str, dict] | None = None,
        model: str = "gpt-4o-mini",
        max_iterations: int = 20,
        max_error_retry: int = 3,
        max_iteration_prompt: str = DEFAULT_MAX_ITERATION_PROMPT,
    ):
        """
        :param user_prompt: The query for the bot.
        :param report_properties: Definition of the values the bot should return.
        :param system_prompt: The parameters in which the bot should analyze the query.
        :param images: Images for the bot to analyze (in additional to the prompt).
        :param tools: The tools the bot is allowed to use and their configuration.
        :param model: The LLM to generate the report with.
        :param max_iterations: The maximum number of loops to take before forcing the bot to finish.
        :param max_error_retry: The maximum number of retries before giving up after the bot returns an erroneous response.
        :param max_iteration_prompt: The prompt to send to the bot when the maximum number of loops has been reached and it is forced to finish.
        """
        check_config_type(user_prompt, str, "prompt:user_prompt")
        self.user_prompt = user_prompt
        check_config_type(report_properties, Iterable, "prompt:report_properties")
        self.report_properties = report_properties
        check_config_type(system_prompt, str, "prompt:system_prompt")
        self.system_prompt = system_prompt
        if images:
            check_config_type(images, Iterable, "prompt:images")
        self.images = images if images else []
        if tools:
            check_config_type(tools, dict, "prompt:tools")
        self.tools = tools if tools else {}
        check_config_type(model, str, "prompt:model")
        self.model = model
        check_config_type(max_iterations, int, "prompt:max_iterations")
        self.max_iterations = max_iterations
        check_config_type(max_error_retry, int, "prompt:max_error_retry")
        self.max_error_retry = max_error_retry
        check_config_type(max_iteration_prompt, str, "prompt:max_iteration_prompt")
        self.max_iteration_prompt = max_iteration_prompt

    def to_dict(self) -> dict:
        return {**self.__dict__, "images": [i.mime for i in self.images]}
