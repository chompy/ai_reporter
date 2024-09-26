# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT


from typing import Iterable

from ai_reporter.bot.property import PropertyDefinition
from ai_reporter.bot.tools.base import BaseTool
from ai_reporter.bot.tools.response import ToolDoneResponse
from ai_reporter.utils import check_config_type


class DoneTool(BaseTool):
    """Tool that the bot should call when it has completed its analysis."""

    @staticmethod
    def name() -> str:
        return "done"

    @staticmethod
    def description():
        return "Finish your analysis."

    @staticmethod
    def properties(properties: Iterable[PropertyDefinition]):
        out = list(properties)
        for i in range(len(out)):
            check_config_type(out[i], PropertyDefinition, "prompt:report_properties.%d" % i)
        return out

    def execute(self, **kwargs):
        return ToolDoneResponse(**kwargs)
