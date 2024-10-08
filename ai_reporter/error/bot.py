class MalformedBotResponseError(Exception):
    """ Bot produces a malformed response. """
    
    def retry_message(self) -> str:
        """ Retry message for the bot. """
        return "I'm sorry, I couldn't understand your response, or something was missing. Please try again."


class ToolPropertyInvalidError(ValueError, MalformedBotResponseError):
    
    """ Bot returned an invalid property value. """

    def __init__(self, tool_name : str, property_name : str, why : str = "") -> None:
        self.tool_name = tool_name
        self.property_name = property_name
        self.why = why
        super().__init__("property '%s' is invalid for tool '%s'" % (self.property_name, self.tool_name))

    def retry_message(self):
        return "Property '%s' was invalid in your call to the '%s' tool. %sPlease try again." % (
                self.property_name, ((self.why.capitalize() + ".") if self.why else ""), self.tool_name)

class ToolPropertyMissingError(AttributeError, MalformedBotResponseError):
    
    """ Bot didn't provide a required property. """

    def __init__(self, tool_name : str, property_name : str) -> None:
        self.tool_name = tool_name
        self.property_name = property_name
        super().__init__("required property '%s' is missing for tool '%s'" % (self.property_name, self.tool_name))

    def retry_message(self):
        return "A required property, '%s', was missing in your call to the '%s' tool. Please try again." % (
                self.property_name, self.tool_name)

class ToolNotDefinedError(MalformedBotResponseError):

    """ Bot tried to call a tool that doesn't exist. """

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