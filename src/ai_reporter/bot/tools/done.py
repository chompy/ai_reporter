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

    def __init__(self, properties: Iterable[PropertyDefinition], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._properties = list(properties)
        self._check_properties()

    @staticmethod
    def name() -> str:
        return "done"

    def description(self):
        return "Finish your analysis."

    def properties(self):
        return self._properties

    def execute(self, **kwargs):
        return ToolDoneResponse(**kwargs)

    def _check_properties(self):
        for i in range(len(self._properties)):
            check_config_type(self._properties[i], PropertyDefinition, f"prompt:report_properties.{i}")
