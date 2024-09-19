class MalformedBotResponseError(Exception):
    """
    Raised when LLM produces a malformed response. When this is
    raised we should ask the LLM to retry.
    """
    
    def retry_message(self) -> str:
        return "I'm sorry, I couldn't understand your response, or something was missing. Please try again."

class ToolPropertyInvalidError(ValueError, MalformedBotResponseError):
    
    def __init__(self, tool_name : str, property_name : str) -> None:
        self.tool_name = tool_name
        self.property_name = property_name
        super().__init__("property '%s' is invalid for tool '%s'" % (self.property_name, self.tool_name))

    def retry_message(self):
        return "Property '%s' was invalid in your call to the '%s' tool.  Please try again." % (
                self.property_name, self.tool_name)

class ToolPropertyMissingError(AttributeError, MalformedBotResponseError):
    
    def __init__(self, tool_name : str, property_name : str) -> None:
        self.tool_name = tool_name
        self.property_name = property_name
        super().__init__("required property '%s' is missing for tool '%s'" % (self.property_name, self.tool_name))

    def retry_message(self):
        return "A required property, '%s', was missing in your call to the '%s' tool. Please try again." % (
                self.property_name, self.tool_name)

class ToolNotDefinedError(MalformedBotResponseError):
    def __init__(self, tool_name : str) -> None:
        self.tool_name = tool_name
        super().__init__("tool '%s' is not defined" % self.tool_name)

    def retry_message(self):
        return "You tried to call a non-existent tool, '%s'. Please try again." % self.tool_name

class BotMaxIterationsError(Exception):
    """ Bot reached the maximum amount of iterations without completing the report. """
    pass

class BotClientNotExistError(ValueError):
    """ Specified bot client does not exist. """
    pass