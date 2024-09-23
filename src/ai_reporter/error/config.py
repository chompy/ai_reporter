class ConfigError(Exception):
    """ An error with a configuration parameter. """
    pass

class ConfigParameterTypeError(TypeError, ConfigError):
    """ Configuration parameter is an unexpected type. """
    pass

class ConfigParameterValueError(ValueError, ConfigError):
    """ Configuration parameter is invalid. """
    pass