# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT


class MalformedBotResponseError(Exception):
    """Bot produces a malformed response."""

    def retry_message(self) -> str:
        """Retry message for the bot."""
        return "I'm sorry, I couldn't understand your response, or something was missing. Please try again."


class ToolPropertyInvalidError(ValueError, MalformedBotResponseError):
    """Bot returned an invalid property value."""

    def __init__(self, tool_name: str, property_name: str, why: str = "") -> None:
        self.tool_name = tool_name
        self.property_name = property_name
        self.why = why
        super().__init__(f"property '{self.property_name!s}' is invalid for tool '{self.tool_name!s}'")

    def retry_message(self):
        why_str = (self.why.capitalize() + ".") if self.why else ""
        return f"Property '{self.property_name!s}' was invalid in your call to the '{self.tool_name!s}' tool. {why_str!s}Please try again."


class ToolPropertyMissingError(AttributeError, MalformedBotResponseError):
    """Bot didn't provide a required property."""

    def __init__(self, tool_name: str, property_name: str) -> None:
        self.tool_name = tool_name
        self.property_name = property_name
        super().__init__(f"required property '{self.property_name!s}' is missing for tool '{self.tool_name!s}'")

    def retry_message(self):
        return f"A required property, '{self.property_name!s}', was missing in your call to the '{self.tool_name!s}' tool. Please try again."


class ToolNotDefinedError(MalformedBotResponseError):
    """Bot tried to call a tool that doesn't exist."""

    def __init__(self, tool_name: str) -> None:
        self.tool_name = tool_name
        super().__init__(f"tool '{self.tool_name!s}' is not defined")

    def retry_message(self):
        return f"You tried to call a non-existent tool, '{self.tool_name!s}'. Please try again."


class BotMaxIterationsError(Exception):
    """Bot reached the maximum amount of iterations without completing the report."""


class BotClientNotExistError(ValueError):
    """Specified bot client does not exist."""
