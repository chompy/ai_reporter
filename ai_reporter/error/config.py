class ConfigError(Exception):
    pass

class ConfigParameterTypeError(TypeError, ConfigError):
    pass

class ConfigParameterValueError(ValueError, ConfigError):
    pass