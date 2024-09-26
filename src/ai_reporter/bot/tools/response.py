# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from ai_reporter.bot.image import Image


class ToolResponseBase:
    """The response of a tool call."""

    def __init__(self):
        self.tool_name: str | None = None
        self.tool_call_id: str | None = None

    def to_dict(self) -> dict:
        return {"name": self.tool_name, "tool_call_id": self.tool_call_id, "done": False}


class ToolMessageResponse(ToolResponseBase):
    """Tool response for replying with requested information."""

    def __init__(self, message: str, images: Iterable[Image] = []):
        """
        :param message: Message to reply to the bot with.
        """
        super().__init__()
        self.message = message
        self.images = images

    def to_dict(self) -> dict:
        return {**super().to_dict(), "message": self.message}


class ToolDoneResponse(ToolResponseBase):
    """Tool response that signifies completion of the report."""

    def __init__(self, **kwargs):
        super().__init__()
        self.values = kwargs

    def to_dict(self) -> dict:
        return {**super().to_dict(), "done": True, "values": self.values}
