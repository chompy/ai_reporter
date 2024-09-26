# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from ai_reporter.bot.results import BotResults
    from ai_reporter.report_type import ReportType


class Report:
    """
    The results of a report produced by the bot.
    """

    def __init__(self, report_type: ReportType, bot_results: BotResults):
        self.type = report_type
        self.results = bot_results

    @property
    def values(self) -> dict[str, object]:
        """The values returned by the bot as configured in the prompt (report_properties)."""
        return self.results.values

    def to_dict(self) -> dict:
        return {"type": self.type.to_dict(), "values": self.values}

    @staticmethod
    def reports_to_dict(reports: Iterable[Report]) -> dict:
        """
        Converts a list of reports to dict where the key is the report type name and
        the values are the bot result values.
        :param reports: The list of reports.
        """
        return {r.type.name: r.values for r in reports}
