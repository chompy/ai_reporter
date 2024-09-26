# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

from ai_reporter import bot as _bot
from ai_reporter.report import Report

if TYPE_CHECKING:
    from logging import Logger

    from ai_reporter.report_type import ReportType

get_bot_client = _bot.get_bot_client
BotResults = _bot.BotResults
Prompt = _bot.Prompt
PropertyDefinition = _bot.PropertyDefinition
PropertyType = _bot.PropertyType
Image = _bot.Image


def run_bot(prompt: Prompt, config: dict | None = None, logger: Logger | None = None) -> BotResults:
    """
    Run the report bot with the given prompt.
    :param prompt: Prompt for bot.
    :param config: Bot client configuration.
    :param logger: Optional logger.
    """
    bot_client_config = config.get("bot_client", "openai") if config else {}
    return get_bot_client(bot_client_config, config if config else {}, logger).run(prompt)


def run_report(report_type: ReportType, config: dict | None = None, logger: Logger | None = None) -> Iterator[Report]:
    """
    Run report bot with prompt from given report type, keep generating new reports as long as `ReportType:next`
    returns a `ReportType` instance. Return an iterator where each iteration is the next report in the chain.
    :param report_type: Report type of report to generate.
    :param config: Bot client configuration.
    :param logger: Optional logger.
    """
    report_values = {}
    current_report_type: ReportType | None = report_type
    while current_report_type:
        if logger:
            logger.info(
                "Run report.", extra={"report_type": report_type, "report_prompt": current_report_type.prompt.to_dict()}
            )
        bot_results = run_bot(current_report_type.prompt, config, logger)
        report = Report(current_report_type, bot_results)
        yield report
        report_values[report.type.name] = report.values
        current_report_type = current_report_type.next(report_values)
